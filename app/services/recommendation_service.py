import uuid
from datetime import datetime, timezone
from time import time

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db_models import ClosetItem, OutfitImage, RecommendationExposure, UserPreference
from app.models.schemas import (
    Constraints,
    Intent,
    OutfitImageOut,
    OutfitItem,
    OutfitOut,
    OutfitSearchRequest,
    RecommendationContext,
    RecommendationHistoryItem,
    RecommendationOut,
    RecommendationRequest,
    ShopLink,
    ShoppingSuggestion,
    Weather,
)


def _make_request_id() -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    return f"req_{ts}_{uuid.uuid4().hex[:6]}"


def _score_item(item: ClosetItem, intent: Intent | None, constraints: Constraints | None, prefs: UserPreference | None) -> float:
    """Simple rule-based scoring for a single closet item."""
    score = 0.5

    # Style match
    if intent and intent.style_goal and item.style_tags:
        if intent.style_goal in item.style_tags:
            score += 0.15

    # Occasion match
    if intent and intent.occasion and item.occasion_tags:
        if intent.occasion in item.occasion_tags:
            score += 0.15

    # Color avoidance
    if constraints and constraints.avoid_colors and item.colors:
        if any(c in constraints.avoid_colors for c in item.colors):
            score -= 0.3

    # Warmth alignment
    target_warmth = None
    if constraints and constraints.pref_warmth:
        target_warmth = constraints.pref_warmth
    elif prefs and prefs.warmth_preference:
        target_warmth = prefs.warmth_preference

    if target_warmth and item.warmth is not None:
        diff = abs(item.warmth - target_warmth)
        score -= diff * 0.05

    # Preference style boost
    if prefs and prefs.style_distribution and item.style_tags:
        for tag in item.style_tags:
            score += prefs.style_distribution.get(tag, 0) * 0.1

    return round(min(max(score, 0.0), 1.0), 4)


def _build_outfit(
    items: list[ClosetItem],
    outfit_id: str,
    intent: Intent | None,
    constraints: Constraints | None,
    prefs: UserPreference | None,
) -> OutfitOut:
    scored = sorted(items, key=lambda i: _score_item(i, intent, constraints, prefs), reverse=True)
    outfit_score = round(sum(_score_item(i, intent, constraints, prefs) for i in scored) / max(len(scored), 1), 4)
    tags: set[str] = set()
    for item in scored:
        if item.style_tags:
            tags.update(item.style_tags)
        if item.occasion_tags:
            tags.update(item.occasion_tags)
    return OutfitOut(
        outfit_id=outfit_id,
        items=[
            OutfitItem(
                item_id=i.item_id,
                category=i.category,
                name=i.name,
                image_url=i.image_url,
            )
            for i in scored
        ],
        summary_tags=list(tags)[:5],
        score=outfit_score,
    )


def _pick_items_for_outfit(
    by_category: dict[str, list[ClosetItem]],
    intent: Intent | None,
    constraints: Constraints | None,
    prefs: UserPreference | None,
    exclude_ids: set[uuid.UUID] | None = None,
) -> list[ClosetItem]:
    """Pick one item per essential category, scored by rules."""
    essential = ["top", "bottom", "shoes"]
    outfit_items: list[ClosetItem] = []
    exclude_ids = exclude_ids or set()

    for cat in essential:
        candidates = [i for i in by_category.get(cat, []) if i.item_id not in exclude_ids]
        if not candidates:
            candidates = by_category.get(cat, [])
        if candidates:
            best = max(candidates, key=lambda i: _score_item(i, intent, constraints, prefs))
            outfit_items.append(best)
            exclude_ids.add(best.item_id)

    # Add outerwear if warmth suggests it
    if constraints and constraints.pref_warmth and constraints.pref_warmth >= 3.5:
        outerwear = [i for i in by_category.get("outerwear", []) if i.item_id not in exclude_ids]
        if outerwear:
            outfit_items.append(max(outerwear, key=lambda i: _score_item(i, intent, constraints, prefs)))

    return outfit_items


class RecommendationService:
    @staticmethod
    async def generate(db: AsyncSession, req: RecommendationRequest) -> RecommendationOut:
        t_start = time()

        # Fetch closet items
        result = await db.execute(select(ClosetItem).where(ClosetItem.user_id == req.user_id))
        all_items: list[ClosetItem] = list(result.scalars().all())

        # Fetch preferences
        pref_result = await db.execute(select(UserPreference).where(UserPreference.user_id == req.user_id))
        prefs: UserPreference | None = pref_result.scalar_one_or_none()

        # Group by category
        by_category: dict[str, list[ClosetItem]] = {}
        for item in all_items:
            by_category.setdefault(item.category, []).append(item)

        intent = req.intent
        constraints = req.constraints
        weather = req.weather

        # Build primary outfit
        used_ids: set[uuid.UUID] = set()
        primary_items = _pick_items_for_outfit(by_category, intent, constraints, prefs)
        used_ids.update(i.item_id for i in primary_items)
        primary = _build_outfit(primary_items, "o1", intent, constraints, prefs)

        # Build 2 alternatives using remaining items
        alternatives: list[OutfitOut] = []
        for alt_idx in range(2):
            alt_items = _pick_items_for_outfit(by_category, intent, constraints, prefs, exclude_ids=set(used_ids))
            if alt_items:
                alt = _build_outfit(alt_items, f"o{alt_idx + 2}", intent, constraints, prefs)
                alternatives.append(alt)
                used_ids.update(i.item_id for i in alt_items)

        # Build explanation
        explanation: list[str] = []
        if prefs and prefs.style_distribution:
            top_style = max(prefs.style_distribution, key=prefs.style_distribution.get)  # type: ignore[arg-type]
            explanation.append(f"Matches your {top_style} preference.")
        if weather and weather.tempMaxC is not None:
            explanation.append(f"Suitable for today's temperature ({weather.tempMinC}–{weather.tempMaxC}°C).")
        if intent and intent.occasion:
            explanation.append(f"Works well for {intent.occasion}.")
        if not explanation:
            explanation.append("Outfit selected based on your wardrobe.")

        # Shopping suggestion placeholder
        shopping: list[ShoppingSuggestion] = []
        if intent and intent.style_goal:
            shopping.append(
                ShoppingSuggestion(
                    item_type="accessories",
                    reason=f"complete the {intent.style_goal} look",
                    search_queries=[f"{intent.style_goal} accessories"],
                    shop_links=[],
                )
            )

        latency_ms = round((time() - t_start) * 1000)
        request_id = _make_request_id()
        now = datetime.now(timezone.utc)

        context_dict = {
            "intent": intent.model_dump() if intent else None,
            "weather": weather.model_dump() if weather else None,
            "constraints": constraints.model_dump() if constraints else None,
        }

        # Persist exposure record
        exposure = RecommendationExposure(
            request_id=request_id,
            user_id=req.user_id,
            session_id=req.session_id,
            model_name="ranker",
            model_version="baseline_rule_v1",
            context=context_dict,
            candidates={"item_ids": [str(i.item_id) for i in all_items]},
            served={
                "outfits": [
                    {"outfit_id": primary.outfit_id, "items": [str(i.item_id) for i in primary_items]},
                    *[{"outfit_id": a.outfit_id, "items": a.items} for a in alternatives],
                ]
            },
            latency_ms={"total": latency_ms},
            ts=now,
        )
        db.add(exposure)
        await db.commit()

        return RecommendationOut(
            request_id=request_id,
            user_id=req.user_id,
            generated_at=now,
            context=RecommendationContext(intent=intent, weather=weather, constraints=constraints),
            primary_outfit=primary,
            alternatives=alternatives,
            explanation=explanation,
            shopping_suggestions=shopping,
        )

    @staticmethod
    async def get_history(
        db: AsyncSession,
        user_id: uuid.UUID,
        *,
        limit: int = 20,
        offset: int = 0,
    ) -> list[RecommendationHistoryItem]:
        stmt = (
            select(RecommendationExposure)
            .where(RecommendationExposure.user_id == user_id)
            .order_by(RecommendationExposure.ts.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await db.execute(stmt)
        rows = result.scalars().all()
        return [
            RecommendationHistoryItem(
                request_id=r.request_id,
                ts=r.ts,
                context=r.context,
                served=r.served,
                model_name=r.model_name,
                model_version=r.model_version,
            )
            for r in rows
        ]

    @staticmethod
    async def get_exposure(db: AsyncSession, request_id: str) -> RecommendationExposure | None:
        result = await db.execute(
            select(RecommendationExposure).where(RecommendationExposure.request_id == request_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def search_outfits(db: AsyncSession, req: OutfitSearchRequest) -> list[OutfitImage]:
        stmt = select(OutfitImage)
        if req.style_tags:
            stmt = stmt.where(OutfitImage.style_tags.overlap(req.style_tags))  # type: ignore[attr-defined]
        if req.occasion_tags:
            stmt = stmt.where(OutfitImage.occasion_tags.overlap(req.occasion_tags))  # type: ignore[attr-defined]
        if req.season_tags:
            stmt = stmt.where(OutfitImage.season_tags.overlap(req.season_tags))  # type: ignore[attr-defined]
        stmt = stmt.limit(req.limit)
        result = await db.execute(stmt)
        return list(result.scalars().all())

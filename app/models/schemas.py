import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, EmailStr, field_validator


# ── Shared ────────────────────────────────────────────────────────────────────

class SuccessResponse(BaseModel):
    success: bool = True
    data: Any


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorDetail


class PaginationMeta(BaseModel):
    limit: int
    offset: int


# ── Users ─────────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    email: str | None = None
    username: str | None = None
    profile: dict | None = None


class UserProfileUpdate(BaseModel):
    preferred_styles: list[str] | None = None
    disliked_colors: list[str] | None = None
    daily_occasions: list[str] | None = None

    model_config = {"extra": "allow"}


class UserOut(BaseModel):
    user_id: uuid.UUID
    email: str | None
    username: str | None
    profile: dict | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserProfileOut(BaseModel):
    user_id: uuid.UUID
    profile: dict | None
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── User Preferences ──────────────────────────────────────────────────────────

class UserPreferenceUpsert(BaseModel):
    style_distribution: dict[str, float] | None = None
    color_distribution: dict[str, float] | None = None
    warmth_preference: float | None = None


class UserPreferenceOut(BaseModel):
    user_id: uuid.UUID
    style_distribution: dict | None
    color_distribution: dict | None
    warmth_preference: float | None
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── Closet Items ──────────────────────────────────────────────────────────────

VALID_CATEGORIES = {"top", "bottom", "outerwear", "shoes", "accessory"}


class ClosetItemCreate(BaseModel):
    user_id: uuid.UUID
    name: str
    category: str
    colors: list[str] | None = None
    style_tags: list[str] | None = None
    occasion_tags: list[str] | None = None
    warmth: int | None = None
    image_url: str | None = None

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        if v not in VALID_CATEGORIES:
            raise ValueError(f"category must be one of {VALID_CATEGORIES}")
        return v

    @field_validator("warmth")
    @classmethod
    def validate_warmth(cls, v: int | None) -> int | None:
        if v is not None and not (1 <= v <= 5):
            raise ValueError("warmth must be between 1 and 5")
        return v


class ClosetItemUpdate(BaseModel):
    name: str | None = None
    category: str | None = None
    colors: list[str] | None = None
    style_tags: list[str] | None = None
    occasion_tags: list[str] | None = None
    warmth: int | None = None
    image_url: str | None = None

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str | None) -> str | None:
        if v is not None and v not in VALID_CATEGORIES:
            raise ValueError(f"category must be one of {VALID_CATEGORIES}")
        return v

    @field_validator("warmth")
    @classmethod
    def validate_warmth(cls, v: int | None) -> int | None:
        if v is not None and not (1 <= v <= 5):
            raise ValueError("warmth must be between 1 and 5")
        return v


class ClosetItemOut(BaseModel):
    item_id: uuid.UUID
    user_id: uuid.UUID
    name: str
    category: str
    colors: list[str] | None
    style_tags: list[str] | None
    occasion_tags: list[str] | None
    warmth: int | None
    image_url: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ClosetItemListOut(BaseModel):
    items: list[ClosetItemOut]
    pagination: PaginationMeta


# ── Recommendations ───────────────────────────────────────────────────────────

class Intent(BaseModel):
    occasion: str | None = None
    mood: str | None = None
    style_goal: str | None = None


class Weather(BaseModel):
    tempMinC: float | None = None
    tempMaxC: float | None = None
    rainProb: float | None = None
    windKph: float | None = None


class Constraints(BaseModel):
    pref_warmth: float | None = None
    avoid_colors: list[str] | None = None


class RecommendationRequest(BaseModel):
    user_id: uuid.UUID
    session_id: str | None = None
    intent: Intent | None = None
    weather: Weather | None = None
    constraints: Constraints | None = None


class OutfitItem(BaseModel):
    item_id: uuid.UUID
    category: str
    name: str
    image_url: str | None


class OutfitOut(BaseModel):
    outfit_id: str
    items: list[OutfitItem] | list[str]
    summary_tags: list[str]
    score: float


class ShopLink(BaseModel):
    shop: str
    url: str


class ShoppingSuggestion(BaseModel):
    item_type: str
    reason: str
    search_queries: list[str]
    shop_links: list[ShopLink]


class RecommendationContext(BaseModel):
    intent: Intent | None = None
    weather: Weather | None = None
    constraints: Constraints | None = None


class RecommendationOut(BaseModel):
    request_id: str
    user_id: uuid.UUID
    generated_at: datetime
    context: RecommendationContext
    primary_outfit: OutfitOut
    alternatives: list[OutfitOut]
    explanation: list[str]
    shopping_suggestions: list[ShoppingSuggestion]


class RecommendationHistoryItem(BaseModel):
    request_id: str
    ts: datetime
    context: dict | None
    served: dict | None
    model_name: str | None
    model_version: str | None


class RecommendationHistoryOut(BaseModel):
    items: list[RecommendationHistoryItem]
    pagination: PaginationMeta


class ExposureDetailOut(BaseModel):
    request_id: str
    user_id: uuid.UUID
    session_id: str | None
    ts: datetime
    ab_bucket: str | None
    model_name: str | None
    model_version: str | None
    context: dict | None
    candidates: dict | None
    served: dict | None
    outfit: dict | None
    latency_ms: dict | None

    model_config = {"from_attributes": True}


# ── Feedback ──────────────────────────────────────────────────────────────────

VALID_SIGNALS = {"like", "dislike"}


class FeedbackCreate(BaseModel):
    user_id: uuid.UUID
    outfit_id: str | None = None
    signal: str
    reason: str | None = None
    request_id: str | None = None

    @field_validator("signal")
    @classmethod
    def validate_signal(cls, v: str) -> str:
        if v not in VALID_SIGNALS:
            raise ValueError(f"signal must be one of {VALID_SIGNALS}")
        return v


class FeedbackOut(BaseModel):
    feedback_id: uuid.UUID
    user_id: uuid.UUID
    outfit_id: str | None
    signal: str
    reason: str | None
    request_id: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class FeedbackListOut(BaseModel):
    items: list[FeedbackOut]
    pagination: PaginationMeta


# ── Events ────────────────────────────────────────────────────────────────────

class EventCreate(BaseModel):
    user_id: uuid.UUID
    session_id: str | None = None
    event_type: str
    payload: dict | None = None


class EventOut(BaseModel):
    event_id: uuid.UUID
    user_id: uuid.UUID
    session_id: str | None
    event_type: str
    payload: dict | None
    ts: datetime

    model_config = {"from_attributes": True}


# ── Outfit Images / Inspiration ───────────────────────────────────────────────

class OutfitSearchRequest(BaseModel):
    style_tags: list[str] | None = None
    occasion_tags: list[str] | None = None
    season_tags: list[str] | None = None
    limit: int = 10


class OutfitImageOut(BaseModel):
    outfit_id: int
    source: str | None
    image_url: str | None
    style_tags: list[str] | None
    occasion_tags: list[str] | None
    season_tags: list[str] | None
    palette: dict | None
    silhouette_tags: list[str] | None
    key_items: dict | None
    quality_score: float | None

    model_config = {"from_attributes": True}

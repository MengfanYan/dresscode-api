
# Backend Development TODO

# Phase 1 — Backend Project Setup

## 1. Create FastAPI project structure

app/
    main.py
    api/
        users.py
        closet.py
        recommendations.py
        feedback.py
        events.py
    services/
        recommendation_service.py
        closet_service.py
        preference_service.py
    models/
        db_models.py
        schemas.py
    core/
        config.py
        database.py
    utils/

Tasks
- initialize FastAPI app
- connect PostgreSQL
- enable OpenAPI docs
- create base routers

---

# Phase 2 — Database Integration

Tables already defined:
- users
- closet_items
- user_preferences
- feedback
- events_raw
- recommendation_exposures
- model_registry
- outfit_images
- embedding tables

Tasks
- create SQLAlchemy / SQLModel models
- test DB connection
- implement CRUD for core tables

---

# Phase 3 — User APIs

Endpoints

POST /users
GET /users/{user_id}
PATCH /users/{user_id}/profile

Tasks
- create user
- read user profile
- update profile JSON

---

# Phase 4 — Closet APIs

Endpoints

POST /closet-items
GET /users/{user_id}/closet-items
PATCH /closet-items/{item_id}
DELETE /closet-items/{item_id}

Tasks
- store clothing metadata
- return wardrobe list
- allow item updates

---

# Phase 5 — Recommendation API (MVP)

Endpoint

POST /recommendations/today

Input
- user_id
- session_id
- intent
- weather
- constraints

Output
- primary outfit
- alternatives
- explanation
- shopping suggestions
- request_id

Tasks
- implement rule-based ranking
- generate outfit combinations
- build response structure

---

# Phase 6 — Feedback APIs

POST /feedback

Tasks
- store explicit feedback
- link feedback to request_id

---

# Phase 7 — Event Logging

POST /events

Tasks
- log behavioral events
- store event payload

---

# Phase 8 — Exposure Logging

When recommendation generated:

write record to

recommendation_exposures

Fields
- request_id
- user_id
- context
- candidates
- served outfits
- model_name
- latency_ms

---

# Phase 9 — Image Upload

Tasks
- upload clothing images
- store image_url
- connect to closet_items

---

# Phase 10 — End‑to‑End Test

Full flow

User
→ upload clothing
→ request recommendation
→ receive outfit
→ give feedback
→ events logged

Verify:
- DB writes
- response format
- exposure logging

---

# Phase 11 — Future AI Improvements

After MVP works:

- inspiration retrieval
- embedding similarity search
- feature engineering pipeline
- ranking model
- A/B testing

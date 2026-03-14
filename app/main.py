from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import Base, engine
from app.api import closet, events, feedback, recommendations, users

app = FastAPI(
    title="Dresscode API",
    description="AI Closet Stylist Agent — Backend",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": {"code": "INTERNAL_ERROR", "message": str(exc)}},
    )


prefix = settings.API_PREFIX
app.include_router(users.router, prefix=prefix)
app.include_router(closet.router, prefix=prefix)
app.include_router(recommendations.router, prefix=prefix)
app.include_router(feedback.router, prefix=prefix)
app.include_router(events.router, prefix=prefix)


@app.get("/health")
async def health():
    return {"status": "ok"}

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.database import init_db
from app.routers import admin, auth, dashboard, meta, missions, modules, navigator, passport, submissions, waitlist


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Hong Kong FTOS API",
    version="0.1.0",
    summary="Frontier Talent Operating System — skills, missions, passports, and employer certification.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_error_handler(_, exc: RequestValidationError) -> JSONResponse:
    messages: list[str] = []
    for error in exc.errors():
        location = " ".join(str(part) for part in error.get("loc", []) if part != "body")
        message = error.get("msg", "Invalid value")
        messages.append(f"{location}: {message}" if location else message)
    detail = "; ".join(messages) if messages else "Check the form and try again."
    return JSONResponse(status_code=422, content={"detail": detail})


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok"}


for router in (
    auth.router,
    meta.router,
    dashboard.router,
    modules.router,
    missions.router,
    submissions.router,
    passport.router,
    navigator.router,
    admin.router,
    waitlist.router,
):
    app.include_router(router, prefix="/api/v1")

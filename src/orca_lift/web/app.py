"""FastAPI application for orca-lift web interface."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.base import BaseHTTPMiddleware

from ..db.engine import init_db, seed_exercises
from ..db.repositories import UserProfileRepository
from .routers import equipment, profile, programs, progress, users
from .routers import api_auth, api_exercises, api_programs, api_workouts, api_profile


# Template and static file paths
TEMPLATES_DIR = Path(__file__).parent / "templates"
STATIC_DIR = Path(__file__).parent / "static"

# Paths that don't require a selected user
PUBLIC_PATHS = (
    "/users", "/health", "/static",
    "/api/v1/",  # All API routes use JWT auth, not cookie-based middleware
    "/docs", "/openapi.json"
)


class CurrentUserMiddleware(BaseHTTPMiddleware):
    """Middleware to enforce user selection and inject current profile."""

    async def dispatch(self, request: Request, call_next):
        # Allow public paths through without a selected user
        path = request.url.path
        if any(path.startswith(p) for p in PUBLIC_PATHS):
            response = await call_next(request)
            return response

        # Check for current_profile_id cookie
        profile_id_str = request.cookies.get("current_profile_id")
        if not profile_id_str:
            return RedirectResponse(url="/users", status_code=302)

        try:
            profile_id = int(profile_id_str)
        except (ValueError, TypeError):
            return RedirectResponse(url="/users", status_code=302)

        # Verify the profile still exists
        profile_repo = UserProfileRepository()
        profile = await profile_repo.get(profile_id)
        if not profile:
            # Profile was deleted; clear cookie and redirect
            response = RedirectResponse(url="/users", status_code=302)
            response.delete_cookie("current_profile_id")
            return response

        # Inject the current profile into request state
        request.state.current_profile = profile
        request.state.current_profile_id = profile_id

        response = await call_next(request)
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler - runs on startup and shutdown."""
    # Startup: Initialize database (always run to apply migrations)
    await init_db()
    await seed_exercises()
    yield
    # Shutdown: cleanup if needed


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="OrcaFit",
        description="AI-Powered Fitness Program Generator & Workout Tracker",
        version="0.2.0",
        lifespan=lifespan,
    )

    # Add current user middleware
    app.add_middleware(CurrentUserMiddleware)

    # Mount static files
    if STATIC_DIR.exists():
        app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    # Setup templates
    templates = Jinja2Templates(directory=TEMPLATES_DIR)

    # Store templates in app state for use in routers
    app.state.templates = templates

    # Include web UI routers
    app.include_router(users.router)
    app.include_router(equipment.router)
    app.include_router(profile.router)
    app.include_router(programs.router)
    app.include_router(progress.router)

    # Include API routers (for mobile app)
    app.include_router(api_auth.router)
    app.include_router(api_exercises.router)
    app.include_router(api_programs.router)
    app.include_router(api_workouts.router)
    app.include_router(api_profile.router)

    @app.get("/", response_class=HTMLResponse)
    async def root(request: Request):
        """Root redirect - go to programs if user selected, otherwise users page."""
        profile_id = request.cookies.get("current_profile_id")
        if profile_id:
            return RedirectResponse(url="/programs", status_code=302)
        return RedirectResponse(url="/users", status_code=302)

    @app.get("/health")
    async def health():
        """Health check endpoint."""
        return {"status": "healthy", "version": "0.2.0"}

    return app


def get_templates(request: Request) -> Jinja2Templates:
    """Get templates from app state."""
    return request.app.state.templates

"""FastAPI application for orca-lift web interface."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from ..db.engine import init_db, get_db_path
from .routers import equipment, profile, programs, progress


# Template and static file paths
TEMPLATES_DIR = Path(__file__).parent / "templates"
STATIC_DIR = Path(__file__).parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler - runs on startup and shutdown."""
    # Startup: Initialize database
    db_path = get_db_path()
    if not db_path.exists():
        await init_db()
    yield
    # Shutdown: cleanup if needed


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="orca-lift",
        description="AI-Powered Liftosaur Program Generator",
        version="0.1.0",
        lifespan=lifespan,
    )

    # Mount static files
    if STATIC_DIR.exists():
        app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    # Setup templates
    templates = Jinja2Templates(directory=TEMPLATES_DIR)

    # Store templates in app state for use in routers
    app.state.templates = templates

    # Include routers
    app.include_router(equipment.router)
    app.include_router(profile.router)
    app.include_router(programs.router)
    app.include_router(progress.router)

    @app.get("/", response_class=HTMLResponse)
    async def root(request: Request):
        """Root redirect to programs page."""
        return RedirectResponse(url="/programs", status_code=302)

    @app.get("/health")
    async def health():
        """Health check endpoint."""
        return {"status": "healthy", "version": "0.1.0"}

    return app


def get_templates(request: Request) -> Jinja2Templates:
    """Get templates from app state."""
    return request.app.state.templates

"""User management routes - selection, creation, switching."""

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from ...db.repositories import (
    EquipmentConfigRepository,
    FitnessDataRepository,
    ProgramProgressRepository,
    ProgramRepository,
    UserProfileRepository,
)
from ...models.exercises import EquipmentType
from ...models.user_profile import ExperienceLevel, FitnessGoal, UserProfile

router = APIRouter(prefix="/users", tags=["users"])


def get_templates(request: Request):
    """Get templates from app state."""
    return request.app.state.templates


@router.get("", response_class=HTMLResponse)
async def users_page(request: Request):
    """User selection / landing page."""
    templates = get_templates(request)

    profile_repo = UserProfileRepository()
    program_repo = ProgramRepository()

    profiles = await profile_repo.list_all()

    # Enrich each profile with program count
    users_data = []
    for profile in profiles:
        programs = await program_repo.list_by_profile(profile.id)
        users_data.append({
            "profile": profile,
            "program_count": len(programs),
        })

    # Check which user is currently selected
    current_profile_id = request.cookies.get("current_profile_id")

    return templates.TemplateResponse(
        "users.html",
        {
            "request": request,
            "users": users_data,
            "current_profile_id": int(current_profile_id) if current_profile_id else None,
            "experience_levels": [e.value for e in ExperienceLevel],
        },
    )


@router.post("")
async def create_user(
    request: Request,
    name: str = Form(...),
    experience_level: str = Form("intermediate"),
    schedule_days: int = Form(4),
):
    """Quick-create a new user profile."""
    profile = UserProfile(
        name=name,
        experience_level=ExperienceLevel(experience_level),
        goals=[FitnessGoal.GENERAL_FITNESS],
        available_equipment=[
            EquipmentType.BARBELL,
            EquipmentType.DUMBBELL,
            EquipmentType.BODYWEIGHT,
        ],
        schedule_days=schedule_days,
        session_duration=60,
    )

    profile_repo = UserProfileRepository()
    profile_id = await profile_repo.create(profile)

    # Set the new user as current and redirect to their profile for full setup
    response = RedirectResponse(url="/profile", status_code=302)
    response.set_cookie(
        key="current_profile_id",
        value=str(profile_id),
        httponly=True,
        samesite="lax",
    )
    return response


@router.post("/{profile_id}/select")
async def select_user(profile_id: int):
    """Set the current active user."""
    profile_repo = UserProfileRepository()
    profile = await profile_repo.get(profile_id)

    if not profile:
        return RedirectResponse(url="/users?error=not_found", status_code=302)

    response = RedirectResponse(url="/programs", status_code=302)
    response.set_cookie(
        key="current_profile_id",
        value=str(profile_id),
        httponly=True,
        samesite="lax",
    )
    return response


@router.delete("/{profile_id}")
async def delete_user(profile_id: int, request: Request):
    """Delete a user and all their associated data."""
    profile_repo = UserProfileRepository()
    program_repo = ProgramRepository()
    progress_repo = ProgramProgressRepository()
    equipment_repo = EquipmentConfigRepository()
    fitness_repo = FitnessDataRepository()

    # Delete associated programs and their progress
    programs = await program_repo.list_by_profile(profile_id)
    for program in programs:
        await progress_repo.delete(program.id)
        await program_repo.delete(program.id)

    # Delete equipment config
    await equipment_repo.delete(profile_id)

    # Delete fitness data
    await fitness_repo.delete_by_profile(profile_id)

    # Delete the profile itself
    await profile_repo.delete(profile_id)

    # If this was the current user, clear the cookie
    current_profile_id = request.cookies.get("current_profile_id")
    response_data = {"status": "deleted"}

    if current_profile_id and int(current_profile_id) == profile_id:
        # We return JSON; the JS frontend will handle the redirect
        pass

    return response_data

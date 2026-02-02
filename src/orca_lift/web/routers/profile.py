"""User profile routes."""

import tempfile
from pathlib import Path

from fastapi import APIRouter, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse

from ...clients.health_connect import HealthConnectClient
from ...db.repositories import FitnessDataRepository, UserProfileRepository
from ...models.exercises import EquipmentType
from ...models.user_profile import ExperienceLevel, FitnessGoal, UserProfile

router = APIRouter(prefix="/profile", tags=["profile"])


def get_templates(request: Request):
    """Get templates from app state."""
    return request.app.state.templates


@router.get("", response_class=HTMLResponse)
async def profile_page(request: Request):
    """User profile page."""
    templates = get_templates(request)

    profile_repo = UserProfileRepository()
    profile = await profile_repo.get_latest()

    # Pre-compute selected values for template
    selected_goals = []
    selected_equipment = []
    if profile:
        selected_goals = [g.value for g in profile.goals]
        selected_equipment = [e.value for e in profile.available_equipment]

    return templates.TemplateResponse(
        "profile.html",
        {
            "request": request,
            "profile": profile,
            "experience_levels": [e.value for e in ExperienceLevel],
            "fitness_goals": [g.value for g in FitnessGoal],
            "equipment_types": [e.value for e in EquipmentType],
            "selected_goals": selected_goals,
            "selected_equipment": selected_equipment,
        },
    )


@router.post("")
async def save_profile(
    request: Request,
    name: str = Form(...),
    experience_level: str = Form(...),
    goals: list[str] = Form(default=[]),
    equipment: list[str] = Form(default=[]),
    schedule_days: int = Form(...),
    session_duration: int = Form(60),
    age: int | None = Form(None),
    body_weight: float | None = Form(None),
    notes: str = Form(""),
):
    """Save or update user profile."""
    profile = UserProfile(
        name=name,
        experience_level=ExperienceLevel(experience_level),
        goals=[FitnessGoal(g) for g in goals],
        available_equipment=[EquipmentType(e) for e in equipment],
        schedule_days=schedule_days,
        session_duration=session_duration,
        age=age if age else None,
        body_weight=body_weight if body_weight else None,
        notes=notes,
    )

    profile_repo = UserProfileRepository()

    # Check if profile exists
    existing = await profile_repo.get_latest()
    if existing:
        profile.id = existing.id
        await profile_repo.update(profile)
    else:
        await profile_repo.create(profile)

    return RedirectResponse(url="/profile?saved=true", status_code=302)


@router.post("/sync")
async def sync_health_connect(
    backup: UploadFile = File(...),
):
    """Sync fitness data from Health Connect backup upload."""
    profile_repo = UserProfileRepository()
    profile = await profile_repo.get_latest()

    if not profile:
        return {"error": "No profile found. Please create a profile first."}

    # Save uploaded file to temp location
    with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp:
        content = await backup.read()
        tmp.write(content)
        tmp_path = Path(tmp.name)

    try:
        # Parse Health Connect backup
        client = HealthConnectClient()
        fitness_data = await client.parse(str(tmp_path))

        # Save fitness data to database
        data_repo = FitnessDataRepository()
        workouts_imported = 0
        body_metrics_imported = 0

        # Store each workout as fitness data
        for workout in fitness_data.workouts:
            workout_data = {
                "session_type": workout.session_type,
                "start_time": workout.start_time.isoformat(),
                "end_time": workout.end_time.isoformat(),
                "exercises": [
                    {
                        "name": ex.name,
                        "sets": [{"reps": s.reps, "weight": s.weight} for s in ex.sets],
                    }
                    for ex in workout.exercises
                ],
            }
            await data_repo.create(
                source="health_connect",
                data_type="workout",
                data=workout_data,
                profile_id=profile.id,
                recorded_at=workout.start_time,
            )
            workouts_imported += 1

        # Store body metrics
        for metric in fitness_data.body_metrics:
            metric_data = {
                "metric_type": metric.metric_type,
                "value": metric.value,
                "unit": metric.unit,
            }
            await data_repo.create(
                source="health_connect",
                data_type="body_metric",
                data=metric_data,
                profile_id=profile.id,
                recorded_at=metric.recorded_at,
            )
            body_metrics_imported += 1

        return {
            "status": "synced",
            "workouts_imported": workouts_imported,
            "body_metrics_imported": body_metrics_imported,
        }

    except Exception as e:
        return {"error": str(e)}

    finally:
        # Clean up temp file
        tmp_path.unlink(missing_ok=True)

"""Profile and stats API endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ...db.repositories import (
    EquipmentConfigRepository,
    PersonalRecordRepository,
    UserProfileRepository,
    WorkoutRepository,
)
from ...models.auth import User
from ...models.equipment import EquipmentConfig
from ..deps import get_current_user

router = APIRouter(prefix="/api/v1/profile", tags=["profile"])


class UpdateProfileRequest(BaseModel):
    name: str | None = None
    experience_level: str | None = None
    goals: list[str] | None = None
    available_equipment: list[str] | None = None
    schedule_days: int | None = None
    session_duration: int | None = None
    age: int | None = None
    body_weight: float | None = None
    height: float | None = None


@router.get("")
async def get_profile(user: User = Depends(get_current_user)):
    """Get user profile."""
    repo = UserProfileRepository()
    profile = await repo.get(user.id)
    if not profile:
        return {"has_profile": False, "user_id": user.id, "email": user.email}
    return {"has_profile": True, "profile": profile.to_dict() | {"id": profile.id}}


@router.get("/stats")
async def get_stats(user: User = Depends(get_current_user)):
    """Get aggregated user stats (PRs, volume trends)."""
    workout_repo = WorkoutRepository()
    pr_repo = PersonalRecordRepository()
    
    workouts = await workout_repo.list_by_user(user.id, limit=100)
    prs = await pr_repo.list_all_for_user(user.id)
    
    completed = [w for w in workouts if w.status.value == "completed"]
    total_volume = sum(w.total_volume_kg for w in completed)
    total_workouts = len(completed)
    
    return {
        "total_workouts": total_workouts,
        "total_volume_kg": round(total_volume, 1),
    }


@router.get("/equipment")
async def get_equipment(user: User = Depends(get_current_user)):
    """Get equipment configuration."""
    repo = EquipmentConfigRepository()
    config = await repo.get_by_profile(user.id)
    if not config:
        return {"has_config": False}
    return {
        "has_config": True,
        "weight_unit": config.weight_unit,
        "barbell_weight": config.barbell_weight,
        "dumbbell_max": config.dumbbell_max,
        "plate_inventory": config.plate_inventory,
    }

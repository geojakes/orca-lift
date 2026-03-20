"""Exercise library API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query

from ...db.repositories import ExerciseRepository
from ...models.auth import User
from ...models.exercises import ExerciseCategory
from ..deps import get_optional_user

router = APIRouter(prefix="/api/v1/exercises", tags=["exercises"])


@router.get("")
async def list_exercises(
    category: str | None = Query(None, description="Filter by category: resistance, cardio, plyometric"),
    muscle_group: str | None = Query(None, description="Filter by muscle group"),
    equipment: str | None = Query(None, description="Filter by equipment type"),
    search: str | None = Query(None, description="Search by name or alias"),
    compound_only: bool = False,
    user: User | None = Depends(get_optional_user),
):
    """List exercises with optional filters."""
    repo = ExerciseRepository()
    
    if search:
        exercises = await repo.search(search)
    else:
        exercises = await repo.list_all()
    
    # Apply filters
    results = []
    for ex in exercises:
        if category and ex.category.value != category:
            continue
        if muscle_group and not any(mg.value == muscle_group for mg in ex.muscle_groups):
            continue
        if equipment and not any(eq.value == equipment for eq in ex.equipment):
            continue
        if compound_only and not ex.is_compound:
            continue
        results.append(ex.to_dict())
    
    return {"exercises": results, "total": len(results)}


@router.get("/{exercise_name}")
async def get_exercise(exercise_name: str):
    """Get exercise details by name."""
    repo = ExerciseRepository()
    exercise = await repo.get_by_name(exercise_name)
    if not exercise:
        # Try search
        results = await repo.search(exercise_name)
        if results:
            exercise = results[0]
    
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    
    return exercise.to_dict()

"""Workout tracking API endpoints."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ...db.repositories import (
    ActiveProgramRepository,
    PersonalRecordRepository,
    ProgramRepository,
    WorkoutRepository,
)
from ...models.auth import User
from ...models.workout import (
    LoggedSet,
    Workout,
    WorkoutExercise,
    WorkoutStatus,
)
from ..deps import get_current_user

router = APIRouter(prefix="/api/v1/workouts", tags=["workouts"])


class StartWorkoutRequest(BaseModel):
    program_id: int | None = None  # Uses active program if not specified
    week_number: int = 1
    day_number: int = 1


class LogSetRequest(BaseModel):
    exercise_index: int  # Index into workout exercises list
    set_number: int
    weight_kg: float | None = None
    reps: int | None = None
    rpe: float | None = None
    duration_seconds: int | None = None
    distance_meters: float | None = None
    heart_rate_avg: int | None = None
    heart_rate_max: int | None = None
    pace_per_km_seconds: int | None = None
    calories: int | None = None
    rest_seconds: int | None = None
    notes: str | None = None
    is_warmup: bool = False


@router.post("/start", status_code=201)
async def start_workout(
    req: StartWorkoutRequest,
    user: User = Depends(get_current_user),
):
    """Start a workout from the active program."""
    workout_repo = WorkoutRepository()
    
    # Check for existing active workout
    active = await workout_repo.get_active(user.id)
    if active:
        raise HTTPException(
            status_code=409,
            detail="Already have an active workout. Complete or skip it first.",
        )
    
    # Determine program
    program_id = req.program_id
    if not program_id:
        active_repo = ActiveProgramRepository()
        program_id = await active_repo.get_active(user.id)
        if not program_id:
            raise HTTPException(
                status_code=400,
                detail="No active program. Activate a program or specify program_id.",
            )
    
    # Load the program to get today's exercises
    prog_repo = ProgramRepository()
    program = await prog_repo.get(program_id)
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")
    
    # Find the target day
    target_week = None
    for week in program.weeks:
        if week.week_number == req.week_number:
            target_week = week
            break
    
    if not target_week or req.day_number > len(target_week.days):
        raise HTTPException(status_code=400, detail="Invalid week/day number")
    
    target_day = target_week.days[req.day_number - 1]
    
    # Build workout exercises from program day
    workout_exercises = []
    for i, ex in enumerate(target_day.exercises):
        workout_exercises.append(WorkoutExercise(
            exercise_id=ex.name.lower().replace(" ", "-").replace(",", ""),
            exercise_name=ex.name,
            order=i + 1,
            target_sets=len([s for s in ex.sets if not s.is_warmup]),
        ))
    
    workout = Workout(
        user_id=user.id,
        program_id=program_id,
        week_number=req.week_number,
        day_number=req.day_number,
        day_name=f"{target_day.name}" + (f" - {target_day.focus}" if target_day.focus else ""),
        status=WorkoutStatus.IN_PROGRESS,
        exercises=workout_exercises,
        started_at=datetime.now(timezone.utc),
    )
    
    workout_id = await workout_repo.create(workout)
    workout.id = workout_id
    
    return workout.to_dict() | {"id": workout_id}


@router.get("/active")
async def get_active_workout(user: User = Depends(get_current_user)):
    """Get current active workout."""
    repo = WorkoutRepository()
    workout = await repo.get_active(user.id)
    if not workout:
        return {"active": False}
    return {"active": True, "workout": workout.to_dict() | {"id": workout.id}}


@router.put("/{workout_id}/log")
async def log_set(
    workout_id: int,
    req: LogSetRequest,
    user: User = Depends(get_current_user),
):
    """Log a set in real-time during a workout."""
    repo = WorkoutRepository()
    workout = await repo.get(workout_id)
    
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")
    if workout.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not your workout")
    if not workout.is_active:
        raise HTTPException(status_code=400, detail="Workout is not active")
    
    if req.exercise_index >= len(workout.exercises):
        raise HTTPException(status_code=400, detail="Invalid exercise index")
    
    exercise = workout.exercises[req.exercise_index]
    
    logged_set = LoggedSet(
        set_number=req.set_number,
        weight_kg=req.weight_kg,
        reps=req.reps,
        rpe=req.rpe,
        duration_seconds=req.duration_seconds,
        distance_meters=req.distance_meters,
        heart_rate_avg=req.heart_rate_avg,
        heart_rate_max=req.heart_rate_max,
        pace_per_km_seconds=req.pace_per_km_seconds,
        calories=req.calories,
        rest_seconds=req.rest_seconds,
        completed_at=datetime.now(timezone.utc),
        notes=req.notes,
        is_warmup=req.is_warmup,
    )
    
    exercise.logged_sets.append(logged_set)
    await repo.update(workout)
    
    return {
        "status": "logged",
        "exercise": exercise.exercise_name,
        "set_number": req.set_number,
        "sets_completed": exercise.completed_sets,
        "sets_target": exercise.target_sets,
    }


@router.post("/{workout_id}/complete")
async def complete_workout(
    workout_id: int,
    user: User = Depends(get_current_user),
):
    """Complete a workout."""
    repo = WorkoutRepository()
    workout = await repo.get(workout_id)
    
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")
    if workout.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not your workout")
    
    now = datetime.now(timezone.utc)
    workout.status = WorkoutStatus.COMPLETED
    workout.completed_at = now
    
    if workout.started_at:
        workout.total_duration_seconds = int((now - workout.started_at).total_seconds())
    
    await repo.update(workout)
    
    # Summary
    return {
        "status": "completed",
        "duration_minutes": (workout.total_duration_seconds or 0) // 60,
        "exercises_completed": workout.exercises_completed,
        "total_exercises": len(workout.exercises),
        "total_volume_kg": workout.total_volume_kg,
    }


@router.get("")
async def list_workouts(
    limit: int = 50,
    user: User = Depends(get_current_user),
):
    """List workout history."""
    repo = WorkoutRepository()
    workouts = await repo.list_by_user(user.id, limit=limit)
    return {
        "workouts": [
            {
                "id": w.id,
                "program_id": w.program_id,
                "day_name": w.day_name,
                "status": w.status.value,
                "started_at": w.started_at.isoformat() if w.started_at else None,
                "completed_at": w.completed_at.isoformat() if w.completed_at else None,
                "duration_minutes": (w.total_duration_seconds or 0) // 60,
                "exercises_completed": w.exercises_completed,
                "total_volume_kg": w.total_volume_kg,
            }
            for w in workouts
        ]
    }


@router.get("/{workout_id}")
async def get_workout(workout_id: int, user: User = Depends(get_current_user)):
    """Get full workout detail with all logged sets."""
    repo = WorkoutRepository()
    workout = await repo.get(workout_id)
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")
    if workout.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not your workout")
    return workout.to_dict() | {"id": workout.id}

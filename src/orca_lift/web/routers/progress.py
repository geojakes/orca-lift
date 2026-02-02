"""Progress tracking routes."""

from datetime import datetime

from fastapi import APIRouter, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse

from ...db.repositories import ProgramProgressRepository, ProgramRepository
from ...models.progress import ProgramProgress
from ...services.progress_sync import ProgressSyncService

router = APIRouter(prefix="/progress", tags=["progress"])


def get_templates(request: Request):
    """Get templates from app state."""
    return request.app.state.templates


@router.get("/{program_id}", response_class=HTMLResponse)
async def progress_page(request: Request, program_id: int):
    """Progress tracking page for a program."""
    templates = get_templates(request)

    program_repo = ProgramRepository()
    program = await program_repo.get(program_id)

    if not program:
        return RedirectResponse(url="/programs?error=not_found", status_code=302)

    progress_repo = ProgramProgressRepository()
    progress = await progress_repo.get_by_program(program_id)

    return templates.TemplateResponse(
        "progress.html",
        {
            "request": request,
            "program": program,
            "progress": progress,
        },
    )


@router.post("/{program_id}/start")
async def start_program(program_id: int):
    """Start tracking a program."""
    program_repo = ProgramRepository()
    program = await program_repo.get(program_id)

    if not program:
        return {"error": "Program not found"}

    progress_repo = ProgramProgressRepository()
    progress = ProgramProgress(program_id=program_id)
    progress.start()

    await progress_repo.upsert(progress)

    return {
        "status": "started",
        "week": progress.current_week,
        "day": progress.current_day,
    }


@router.post("/{program_id}/advance")
async def advance_progress(program_id: int):
    """Mark current workout as complete and advance."""
    program_repo = ProgramRepository()
    program = await program_repo.get(program_id)

    if not program:
        return {"error": "Program not found"}

    progress_repo = ProgramProgressRepository()
    progress = await progress_repo.get_by_program(program_id)

    if not progress:
        return {"error": "Program not started"}

    # Get current week info
    total_weeks = len(program.weeks)
    current_week = program.weeks[progress.current_week - 1]
    days_this_week = len(current_week.days)

    # Advance
    completed = not progress.advance(days_this_week, total_weeks)

    await progress_repo.update(progress)

    return {
        "status": "completed" if completed else "advanced",
        "week": progress.current_week,
        "day": progress.current_day,
        "program_completed": completed,
    }


@router.post("/{program_id}/set")
async def set_position(
    program_id: int,
    week: int = Form(...),
    day: int = Form(...),
):
    """Set position to a specific week and day."""
    program_repo = ProgramRepository()
    program = await program_repo.get(program_id)

    if not program:
        return {"error": "Program not found"}

    # Validate position
    if week < 1 or week > len(program.weeks):
        return {"error": f"Invalid week {week}"}

    week_obj = program.weeks[week - 1]
    if day < 1 or day > len(week_obj.days):
        return {"error": f"Invalid day {day}"}

    progress_repo = ProgramProgressRepository()
    progress = await progress_repo.get_by_program(program_id)

    if not progress:
        progress = ProgramProgress(program_id=program_id)
        progress.start()

    progress.set_position(week, day)
    await progress_repo.upsert(progress)

    return {
        "status": "set",
        "week": week,
        "day": day,
    }


@router.post("/{program_id}/sync")
async def sync_from_health_connect(
    program_id: int,
    backup: UploadFile = File(...),
):
    """Sync progress from Health Connect backup upload."""
    import tempfile
    from pathlib import Path

    program_repo = ProgramRepository()
    program = await program_repo.get(program_id)

    if not program:
        return {"error": "Program not found"}

    progress_repo = ProgramProgressRepository()
    progress = await progress_repo.get_by_program(program_id)

    if not progress:
        return {"error": "Program not started"}

    # Save uploaded file to temp location
    with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp:
        content = await backup.read()
        tmp.write(content)
        tmp_path = Path(tmp.name)

    try:
        sync_service = ProgressSyncService()
        completed = await sync_service.sync_from_health_connect(
            program=program,
            progress=progress,
            health_connect_backup=tmp_path,
        )

        if completed:
            # Update progress to furthest completed point
            last = completed[-1]
            progress.set_position(last.week, last.day)

            # Advance past completed day
            total_weeks = len(program.weeks)
            days_this_week = len(program.weeks[last.week - 1].days)
            progress.advance(days_this_week, total_weeks)

            await progress_repo.update(progress)

        return {
            "status": "synced",
            "completed_workouts": len(completed),
            "current_week": progress.current_week,
            "current_day": progress.current_day,
            "workouts": [w.to_dict() for w in completed],
        }

    except Exception as e:
        return {"error": str(e)}

    finally:
        # Clean up temp file
        tmp_path.unlink(missing_ok=True)

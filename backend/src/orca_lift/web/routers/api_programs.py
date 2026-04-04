"""Program management API endpoints."""

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from pydantic import BaseModel

from ...db.repositories import ActiveProgramRepository, ProgramRepository
from ...formats import LiftoscriptFormat, OrcaFitFormat
from ...models.auth import User
from ...web.job_tracker import JobTracker
from ..deps import get_current_user

router = APIRouter(prefix="/api/v1/programs", tags=["programs"])

# Shared job tracker for generation status
_job_tracker = JobTracker()


class GenerateRequest(BaseModel):
    goals: str
    days_per_week: int = 4
    weeks: int = 4
    format: str = "orcafit"  # "orcafit" or "liftoscript"


class GenerateResponse(BaseModel):
    job_id: str
    status: str = "pending"


@router.post("/generate", response_model=GenerateResponse, status_code=202)
async def generate_program(
    req: GenerateRequest,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
):
    """Start async program generation. Poll /generate/{job_id}/status for result."""
    job = await _job_tracker.create_job(goals=req.goals, weeks=req.weeks)

    # In a full implementation, this would kick off the congregation pipeline
    # For now, we create a placeholder
    async def _generate():
        try:
            await _job_tracker.start_job(job.id)
            # TODO: Wire up actual ProgramGenerator from agents/executor.py
            # For now, mark as completed with a note
            await _job_tracker.complete_job(job.id, program_id=0, name="placeholder")
        except Exception as e:
            await _job_tracker.fail_job(job.id, error=str(e))

    background_tasks.add_task(_generate)
    return GenerateResponse(job_id=job.id)


@router.get("/generate/{job_id}/status")
async def generation_status(job_id: str, user: User = Depends(get_current_user)):
    """Check program generation status."""
    job = await _job_tracker.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job.to_dict()


@router.get("")
async def list_programs(user: User = Depends(get_current_user)):
    """List user's programs."""
    repo = ProgramRepository()
    programs = await repo.list_by_profile(user.id)
    return {
        "programs": [
            {
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "goals": p.goals,
                "weeks": p.total_weeks,
                "days_per_week": p.days_per_week,
                "created_at": p.created_at.isoformat() if p.created_at else None,
            }
            for p in programs
        ]
    }


@router.get("/{program_id}")
async def get_program(program_id: int, user: User = Depends(get_current_user)):
    """Get full program detail."""
    repo = ProgramRepository()
    program = await repo.get(program_id)
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")
    
    # Return in OrcaFit format
    fmt = OrcaFitFormat()
    return fmt.generate(program)


@router.post("/{program_id}/activate")
async def activate_program(program_id: int, user: User = Depends(get_current_user)):
    """Set a program as the active program."""
    prog_repo = ProgramRepository()
    program = await prog_repo.get(program_id)
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")
    
    active_repo = ActiveProgramRepository()
    await active_repo.set_active(user.id, program_id)
    return {"status": "activated", "program_id": program_id}


@router.post("/{program_id}/export")
async def export_program(
    program_id: int,
    format: str = "orcafit",
    user: User = Depends(get_current_user),
):
    """Export program in specified format."""
    repo = ProgramRepository()
    program = await repo.get(program_id)
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")
    
    if format == "liftoscript":
        fmt = LiftoscriptFormat()
        output = fmt.generate(program)
        return {"format": "liftoscript", "content": output}
    else:
        fmt = OrcaFitFormat()
        return fmt.generate(program)


@router.delete("/{program_id}")
async def delete_program(program_id: int, user: User = Depends(get_current_user)):
    """Delete a program."""
    repo = ProgramRepository()
    await repo.delete(program_id)
    return {"status": "deleted"}

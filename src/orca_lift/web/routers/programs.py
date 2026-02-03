"""Program management routes."""

import asyncio
import json
from typing import AsyncGenerator

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse

from ...agents import ProgramExecutor
from ...agents.prompts import format_equipment_constraints
from ...agents.tools import answer_question
from ...db.repositories import (
    EquipmentConfigRepository,
    ExerciseRepository,
    ProgramProgressRepository,
    ProgramRepository,
    UserProfileRepository,
)
from ...services.refine import RefinementService
from ..job_tracker import job_tracker, JobStatus

router = APIRouter(prefix="/programs", tags=["programs"])

# Store active job event queues for reconnection
_job_queues: dict[str, asyncio.Queue] = {}


def get_templates(request: Request):
    """Get templates from app state."""
    return request.app.state.templates


@router.get("", response_class=HTMLResponse)
async def programs_list(request: Request):
    """List all programs."""
    templates = get_templates(request)

    program_repo = ProgramRepository()
    progress_repo = ProgramProgressRepository()

    programs = await program_repo.list_all()

    # Add progress info to each program
    programs_with_progress = []
    for program in programs:
        progress = await progress_repo.get_by_program(program.id)
        programs_with_progress.append({
            "program": program,
            "progress": progress,
        })

    return templates.TemplateResponse(
        "programs/list.html",
        {
            "request": request,
            "programs": programs_with_progress,
        },
    )


@router.get("/new", response_class=HTMLResponse)
async def new_program_form(request: Request):
    """Show program generation form."""
    templates = get_templates(request)

    profile_repo = UserProfileRepository()
    profile = await profile_repo.get_latest()

    return templates.TemplateResponse(
        "programs/new.html",
        {
            "request": request,
            "profile": profile,
        },
    )


@router.get("/jobs")
async def list_jobs():
    """List all tracked generation jobs."""
    jobs = await job_tracker.list_jobs()
    return {"jobs": [j.to_dict() for j in jobs]}


@router.get("/jobs/{job_id}")
async def get_job(job_id: str):
    """Get a specific job's status and events."""
    job = await job_tracker.get_job(job_id)
    if not job:
        return {"error": "Job not found"}

    return {
        **job.to_dict(),
        "events": [
            {
                "type": e.event_type,
                "message": e.message,
                "data": e.data,
                "timestamp": e.timestamp.isoformat(),
            }
            for e in job.events
        ],
    }


@router.get("/jobs/{job_id}/stream")
async def stream_job(job_id: str):
    """Stream events from a running job (for reconnection)."""
    job = await job_tracker.get_job(job_id)
    if not job:
        return {"error": "Job not found"}

    async def event_stream() -> AsyncGenerator[str, None]:
        # First, replay all existing events with proper formatting
        for event in job.events:
            if event.event_type == "specialist":
                yield f"data: {json.dumps({'type': 'specialist', 'name': event.message, 'preview': event.data.get('preview', '') if event.data else '', 'full': event.data.get('full', '') if event.data else '', 'aligned': event.data.get('aligned') if event.data else None})}\n\n"
            elif event.event_type == "info_request":
                yield f"data: {json.dumps({'type': 'info_request', 'name': event.message, 'functions': event.data.get('functions', []) if event.data else []})}\n\n"
            elif event.event_type == "human_question":
                yield f"data: {json.dumps({'type': 'human_question', 'name': event.message, 'question_id': event.data.get('question_id', '') if event.data else '', 'question': event.data.get('question', '') if event.data else ''})}\n\n"
            else:
                yield f"data: {json.dumps({'type': event.event_type, 'message': event.message, **(event.data or {})})}\n\n"

        # If job is already done, send completion
        if job.status == JobStatus.COMPLETED:
            yield f"data: {json.dumps({'type': 'complete', 'program_id': job.result['program_id'], 'name': job.result['name']})}\n\n"
            return
        elif job.status == JobStatus.FAILED:
            yield f"data: {json.dumps({'type': 'error', 'message': job.error})}\n\n"
            return

        # Otherwise, stream new events from the queue
        queue = _job_queues.get(job_id)
        if queue:
            while True:
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=60.0)
                    event_type, message, data = event

                    if event_type == "done":
                        break
                    elif event_type == "error":
                        yield f"data: {json.dumps({'type': 'error', 'message': message})}\n\n"
                        break
                    elif event_type == "complete":
                        yield f"data: {json.dumps({'type': 'complete', 'program_id': data['program_id'], 'name': message})}\n\n"
                        break
                    elif event_type == "specialist":
                        yield f"data: {json.dumps({'type': 'specialist', 'name': message, 'preview': data.get('preview', '') if data else '', 'full': data.get('full', '') if data else '', 'aligned': data.get('aligned') if data else None})}\n\n"
                    elif event_type == "info_request":
                        yield f"data: {json.dumps({'type': 'info_request', 'name': message, 'functions': data.get('functions', []) if data else []})}\n\n"
                    else:
                        yield f"data: {json.dumps({'type': 'status', 'message': message})}\n\n"
                except asyncio.TimeoutError:
                    # Send keepalive
                    yield f": keepalive\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


@router.post("/answer")
async def submit_answer(
    question_id: str = Form(...),
    answer: str = Form(...),
):
    """Submit an answer to a specialist's question.

    This endpoint receives answers from the modal dialog when a specialist
    uses the ask_human tool during deliberation.
    """
    success = answer_question(question_id, answer)
    return {"success": success, "question_id": question_id}


@router.post("/generate")
async def generate_program(
    request: Request,
    goals: str = Form(...),
    weeks: int = Form(4),
):
    """Generate a new program with streaming progress.

    Returns Server-Sent Events for real-time progress updates.
    """
    # Create tracked job
    job = await job_tracker.create_job(goals, weeks)
    job_id = job.id

    # Create queue for this job
    progress_queue: asyncio.Queue = asyncio.Queue()
    _job_queues[job_id] = progress_queue

    async def on_progress(event_type: str, message: str, data: dict | None = None):
        """Callback for executor progress updates."""
        await job_tracker.add_event(job_id, event_type, message, data)
        await progress_queue.put((event_type, message, data))

    async def run_generation():
        """Run the generation in background."""
        try:
            await job_tracker.start_job(job_id)

            # Get profile
            profile_repo = UserProfileRepository()
            profile = await profile_repo.get_latest()

            if not profile:
                await on_progress("error", "No profile found", None)
                await job_tracker.fail_job(job_id, "No profile found")
                return None

            await on_progress("status", "Loading profile...", None)

            # Get equipment constraints
            equipment_constraints = None
            config_repo = EquipmentConfigRepository()
            config = await config_repo.get_by_profile(profile.id)

            if config:
                exercise_repo = ExerciseRepository()
                exercises = await exercise_repo.get_by_equipment(profile.available_equipment)
                exercise_names = [ex.name for ex in exercises]

                equipment_constraints = format_equipment_constraints(
                    equipment_types=profile.available_equipment,
                    available_exercises=exercise_names,
                    min_increment=config.min_increment(),
                    weight_unit=config.weight_unit,
                )

            # Create executor with progress callback
            executor = ProgramExecutor(verbose=False)

            # Execute program generation
            result = await executor.execute(
                user_profile=profile,
                goals=goals,
                fitness_data_summary="",
                num_weeks=weeks,
                equipment_constraints=equipment_constraints,
                on_progress=on_progress,
            )

            # Save program
            program_repo = ProgramRepository()
            program_id = await program_repo.create(result.program)

            await on_progress("complete", result.program.name, {"program_id": program_id})
            await job_tracker.complete_job(job_id, program_id, result.program.name)
            return result

        except Exception as e:
            await on_progress("error", str(e), None)
            await job_tracker.fail_job(job_id, str(e))
            return None
        finally:
            await progress_queue.put(("done", "", None))
            # Clean up queue after a delay
            await asyncio.sleep(60)
            _job_queues.pop(job_id, None)

    async def event_stream() -> AsyncGenerator[str, None]:
        # Send job ID first so client can reconnect
        yield f"data: {json.dumps({'type': 'job_started', 'job_id': job_id})}\n\n"

        # Start generation task
        generation_task = asyncio.create_task(run_generation())

        try:
            # Stream events from queue
            while True:
                event = await progress_queue.get()
                event_type, message, data = event

                if event_type == "done":
                    break
                elif event_type == "error":
                    yield f"data: {json.dumps({'type': 'error', 'message': message})}\n\n"
                    break
                elif event_type == "complete":
                    yield f"data: {json.dumps({'type': 'complete', 'program_id': data['program_id'], 'name': message})}\n\n"
                elif event_type == "specialist":
                    yield f"data: {json.dumps({'type': 'specialist', 'name': message, 'preview': data.get('preview', '') if data else '', 'full': data.get('full', '') if data else '', 'aligned': data.get('aligned') if data else None})}\n\n"
                elif event_type == "info_request":
                    yield f"data: {json.dumps({'type': 'info_request', 'name': message, 'functions': data.get('functions', []) if data else []})}\n\n"
                elif event_type == "human_question":
                    yield f"data: {json.dumps({'type': 'human_question', 'name': message, 'question_id': data.get('question_id', '') if data else '', 'question': data.get('question', '') if data else ''})}\n\n"
                else:
                    yield f"data: {json.dumps({'type': 'status', 'message': message})}\n\n"

        finally:
            # Don't await task here - let it continue in background
            pass

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


@router.get("/{program_id}", response_class=HTMLResponse)
async def view_program(request: Request, program_id: int):
    """View a program with chat interface."""
    templates = get_templates(request)

    program_repo = ProgramRepository()
    program = await program_repo.get(program_id)

    if not program:
        return RedirectResponse(url="/programs?error=not_found", status_code=302)

    progress_repo = ProgramProgressRepository()
    progress = await progress_repo.get_by_program(program_id)

    return templates.TemplateResponse(
        "programs/view.html",
        {
            "request": request,
            "program": program,
            "progress": progress,
        },
    )


@router.get("/{program_id}/liftoscript")
async def get_liftoscript(program_id: int):
    """Get Liftoscript for clipboard copy."""
    program_repo = ProgramRepository()
    program = await program_repo.get(program_id)

    if not program:
        return {"error": "Program not found"}

    return {
        "liftoscript": program.liftoscript,
        "name": program.name,
    }


@router.post("/{program_id}/chat")
async def chat_refine(
    request: Request,
    program_id: int,
    message: str = Form(...),
):
    """Refine program via chat message with streaming response."""
    async def event_stream() -> AsyncGenerator[str, None]:
        try:
            program_repo = ProgramRepository()
            program = await program_repo.get(program_id)

            if not program:
                yield f"data: {json.dumps({'type': 'error', 'message': 'Program not found'})}\n\n"
                return

            yield f"data: {json.dumps({'type': 'status', 'message': 'Consulting specialists...'})}\n\n"

            # Refine program
            service = RefinementService()
            refined = await service.refine(program, message)

            # Save changes
            await program_repo.update(refined)

            yield f"data: {json.dumps({'type': 'status', 'message': 'Program updated!'})}\n\n"
            yield f"data: {json.dumps({'type': 'complete', 'summary': refined.get_summary()})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


@router.delete("/{program_id}")
async def delete_program(program_id: int):
    """Delete a program."""
    program_repo = ProgramRepository()
    progress_repo = ProgramProgressRepository()

    # Delete progress first (foreign key)
    await progress_repo.delete(program_id)
    await program_repo.delete(program_id)

    return {"status": "deleted"}

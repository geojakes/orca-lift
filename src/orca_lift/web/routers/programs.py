"""Program management routes."""

import asyncio
import json
from typing import AsyncGenerator

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse

from ...agents import ProgramExecutor
from ...agents.prompts import format_equipment_constraints
from ...db.repositories import (
    EquipmentConfigRepository,
    ExerciseRepository,
    ProgramProgressRepository,
    ProgramRepository,
    UserProfileRepository,
)
from ...services.refine import RefinementService

router = APIRouter(prefix="/programs", tags=["programs"])


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


@router.post("/generate")
async def generate_program(
    request: Request,
    goals: str = Form(...),
    weeks: int = Form(4),
):
    """Generate a new program with streaming progress.

    Returns Server-Sent Events for real-time progress updates.
    """
    async def event_stream() -> AsyncGenerator[str, None]:
        # Queue for progress events from the executor callback
        progress_queue: asyncio.Queue = asyncio.Queue()

        async def on_progress(event_type: str, message: str, data: dict | None = None):
            """Callback for executor progress updates."""
            await progress_queue.put((event_type, message, data))

        async def run_generation():
            """Run the generation in background and signal completion."""
            try:
                # Get profile
                profile_repo = UserProfileRepository()
                profile = await profile_repo.get_latest()

                if not profile:
                    await progress_queue.put(("error", "No profile found", None))
                    return None

                await progress_queue.put(("status", "Loading profile...", None))

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

                await progress_queue.put(("complete", result.program.name, {"program_id": program_id}))
                return result

            except Exception as e:
                await progress_queue.put(("error", str(e), None))
                return None
            finally:
                await progress_queue.put(("done", "", None))

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
                    # Specialist deliberation message with preview and full content
                    yield f"data: {json.dumps({'type': 'specialist', 'name': message, 'preview': data.get('preview', '') if data else '', 'full': data.get('full', '') if data else '', 'aligned': data.get('aligned') if data else None})}\n\n"
                else:
                    # Phase/status message
                    yield f"data: {json.dumps({'type': 'status', 'message': message})}\n\n"

        finally:
            # Ensure task completes
            await generation_task

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

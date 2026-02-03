"""Job tracking for long-running program generation."""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4


class JobStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class JobEvent:
    """An event from a running job."""
    event_type: str
    message: str
    data: dict | None = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Job:
    """A tracked generation job."""
    id: str
    status: JobStatus
    goals: str
    weeks: int
    created_at: datetime = field(default_factory=datetime.now)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    events: list[JobEvent] = field(default_factory=list)
    result: dict | None = None  # program_id, name on completion
    error: str | None = None

    def add_event(self, event_type: str, message: str, data: dict | None = None):
        self.events.append(JobEvent(event_type, message, data))

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "status": self.status.value,
            "goals": self.goals,
            "weeks": self.weeks,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "event_count": len(self.events),
            "result": self.result,
            "error": self.error,
        }


class JobTracker:
    """Tracks active and recent generation jobs."""

    def __init__(self, max_completed_jobs: int = 20):
        self._jobs: dict[str, Job] = {}
        self._max_completed = max_completed_jobs
        self._lock = asyncio.Lock()

    async def create_job(self, goals: str, weeks: int) -> Job:
        """Create a new job."""
        async with self._lock:
            job = Job(
                id=str(uuid4())[:8],
                status=JobStatus.PENDING,
                goals=goals,
                weeks=weeks,
            )
            self._jobs[job.id] = job
            self._cleanup_old_jobs()
            return job

    async def get_job(self, job_id: str) -> Job | None:
        """Get a job by ID."""
        return self._jobs.get(job_id)

    async def list_jobs(self) -> list[Job]:
        """List all tracked jobs."""
        return list(self._jobs.values())

    async def start_job(self, job_id: str):
        """Mark a job as started."""
        job = self._jobs.get(job_id)
        if job:
            job.status = JobStatus.RUNNING
            job.started_at = datetime.now()

    async def complete_job(self, job_id: str, program_id: int, name: str):
        """Mark a job as completed."""
        job = self._jobs.get(job_id)
        if job:
            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.now()
            job.result = {"program_id": program_id, "name": name}

    async def fail_job(self, job_id: str, error: str):
        """Mark a job as failed."""
        job = self._jobs.get(job_id)
        if job:
            job.status = JobStatus.FAILED
            job.completed_at = datetime.now()
            job.error = error

    async def add_event(self, job_id: str, event_type: str, message: str, data: dict | None = None):
        """Add an event to a job."""
        job = self._jobs.get(job_id)
        if job:
            job.add_event(event_type, message, data)

    def _cleanup_old_jobs(self):
        """Remove old completed jobs if over limit."""
        completed = [j for j in self._jobs.values() if j.status in (JobStatus.COMPLETED, JobStatus.FAILED)]
        if len(completed) > self._max_completed:
            # Sort by completion time and remove oldest
            completed.sort(key=lambda j: j.completed_at or datetime.min)
            for job in completed[:-self._max_completed]:
                del self._jobs[job.id]


# Global job tracker instance
job_tracker = JobTracker()

"""Base protocol for fitness data clients."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol, runtime_checkable


@dataclass
class WorkoutSession:
    """Represents a workout session."""

    start_time: datetime
    end_time: datetime
    session_type: str  # e.g., "strength_training", "cardio"
    exercises: list["ExerciseRecord"]
    notes: str = ""
    source: str = ""


@dataclass
class ExerciseRecord:
    """Represents a recorded exercise within a workout."""

    name: str
    sets: list["SetRecord"]
    segment_type: str | None = None  # Original segment type from source


@dataclass
class SetRecord:
    """Represents a single set of an exercise."""

    reps: int
    weight: float | None = None  # in kg
    duration_seconds: float | None = None  # for timed exercises
    rpe: float | None = None


@dataclass
class BodyMetric:
    """Represents a body measurement."""

    metric_type: str  # "weight", "body_fat", etc.
    value: float
    unit: str
    recorded_at: datetime


@dataclass
class SleepRecord:
    """Represents a sleep session."""

    start_time: datetime
    end_time: datetime
    stages: dict[str, int]  # stage name -> minutes
    quality_score: float | None = None


@dataclass
class FitnessData:
    """Aggregated fitness data from a source."""

    source: str
    workouts: list[WorkoutSession]
    body_metrics: list[BodyMetric]
    sleep_records: list[SleepRecord]
    raw_data: dict | None = None  # Original parsed data for debugging


@runtime_checkable
class FitnessDataClient(Protocol):
    """Protocol for fitness data clients."""

    @property
    def source_name(self) -> str:
        """Return the name of this data source."""
        ...

    async def parse(self, path: str) -> FitnessData:
        """Parse fitness data from the given path.

        Args:
            path: Path to the data file or directory

        Returns:
            Parsed fitness data
        """
        ...

    def get_workout_summary(self, data: FitnessData) -> str:
        """Generate a text summary of workout data for AI context."""
        ...


class BaseFitnessClient(ABC):
    """Base class for fitness data clients with common functionality."""

    @property
    @abstractmethod
    def source_name(self) -> str:
        """Return the name of this data source."""
        pass

    @abstractmethod
    async def parse(self, path: str) -> FitnessData:
        """Parse fitness data from the given path."""
        pass

    def get_workout_summary(self, data: FitnessData) -> str:
        """Generate a text summary of workout data for AI context."""
        lines = [f"Fitness Data from {self.source_name}"]
        lines.append("=" * 40)

        # Workout summary
        if data.workouts:
            lines.append(f"\nWorkouts: {len(data.workouts)} sessions")

            # Group by exercise
            exercise_counts: dict[str, int] = {}
            exercise_volume: dict[str, int] = {}  # total sets

            for workout in data.workouts:
                for exercise in workout.exercises:
                    name = exercise.name
                    exercise_counts[name] = exercise_counts.get(name, 0) + 1
                    exercise_volume[name] = exercise_volume.get(name, 0) + len(
                        exercise.sets
                    )

            if exercise_counts:
                lines.append("\nMost frequent exercises:")
                sorted_exercises = sorted(
                    exercise_counts.items(), key=lambda x: x[1], reverse=True
                )[:10]
                for name, count in sorted_exercises:
                    sets = exercise_volume.get(name, 0)
                    lines.append(f"  - {name}: {count} sessions, {sets} total sets")

            # Recent workouts
            if len(data.workouts) > 0:
                lines.append("\nRecent workouts:")
                recent = sorted(data.workouts, key=lambda w: w.start_time, reverse=True)[
                    :5
                ]
                for workout in recent:
                    date = workout.start_time.strftime("%Y-%m-%d")
                    exercises = ", ".join(e.name for e in workout.exercises[:3])
                    if len(workout.exercises) > 3:
                        exercises += f" (+{len(workout.exercises) - 3} more)"
                    lines.append(f"  - {date}: {exercises}")

        # Body metrics summary
        if data.body_metrics:
            lines.append(f"\nBody Metrics: {len(data.body_metrics)} records")

            # Latest of each type
            latest_by_type: dict[str, BodyMetric] = {}
            for metric in data.body_metrics:
                if (
                    metric.metric_type not in latest_by_type
                    or metric.recorded_at > latest_by_type[metric.metric_type].recorded_at
                ):
                    latest_by_type[metric.metric_type] = metric

            for metric_type, metric in latest_by_type.items():
                lines.append(
                    f"  - Latest {metric_type}: {metric.value} {metric.unit} "
                    f"({metric.recorded_at.strftime('%Y-%m-%d')})"
                )

        # Sleep summary
        if data.sleep_records:
            lines.append(f"\nSleep Records: {len(data.sleep_records)} nights")

            # Calculate averages
            total_sleep = sum(
                (r.end_time - r.start_time).total_seconds() / 3600
                for r in data.sleep_records
            )
            avg_sleep = total_sleep / len(data.sleep_records)
            lines.append(f"  - Average sleep: {avg_sleep:.1f} hours")

        return "\n".join(lines)

"""Data access layer for orca-lift."""

import json
from datetime import datetime
from pathlib import Path

import aiosqlite

from ..models.equipment import EquipmentConfig
from ..models.exercises import (
    COMMON_EXERCISES,
    Exercise,
    EquipmentType,
    MovementPattern,
    MuscleGroup,
)
from ..models.program import Program
from ..models.progress import ProgramProgress, ProgramStatus
from ..models.user_profile import UserProfile
from .engine import get_db_path


class UserProfileRepository:
    """Repository for user profiles."""

    def __init__(self, db_path: Path | None = None):
        self.db_path = db_path or get_db_path()

    async def create(self, profile: UserProfile) -> int:
        """Create a new user profile."""
        data = profile.to_dict()
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """
                INSERT INTO user_profiles
                (name, experience_level, goals, available_equipment, schedule_days,
                 session_duration, strength_levels, limitations, age, body_weight, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["name"],
                    data["experience_level"],
                    json.dumps(data["goals"]),
                    json.dumps(data["available_equipment"]),
                    data["schedule_days"],
                    data["session_duration"],
                    json.dumps(data["strength_levels"]),
                    json.dumps(data["limitations"]),
                    data["age"],
                    data["body_weight"],
                    data["notes"],
                ),
            )
            await db.commit()
            return cursor.lastrowid

    async def get(self, profile_id: int) -> UserProfile | None:
        """Get a user profile by ID."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM user_profiles WHERE id = ?", (profile_id,)
            )
            row = await cursor.fetchone()
            if row is None:
                return None
            return self._row_to_profile(row)

    async def get_latest(self) -> UserProfile | None:
        """Get the most recently created/updated profile."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM user_profiles ORDER BY updated_at DESC LIMIT 1"
            )
            row = await cursor.fetchone()
            if row is None:
                return None
            return self._row_to_profile(row)

    async def list_all(self) -> list[UserProfile]:
        """List all user profiles."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM user_profiles ORDER BY updated_at DESC"
            )
            rows = await cursor.fetchall()
            return [self._row_to_profile(row) for row in rows]

    async def update(self, profile: UserProfile) -> None:
        """Update an existing profile."""
        if profile.id is None:
            raise ValueError("Profile must have an ID to update")

        data = profile.to_dict()
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                UPDATE user_profiles SET
                    name = ?, experience_level = ?, goals = ?, available_equipment = ?,
                    schedule_days = ?, session_duration = ?, strength_levels = ?,
                    limitations = ?, age = ?, body_weight = ?, notes = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (
                    data["name"],
                    data["experience_level"],
                    json.dumps(data["goals"]),
                    json.dumps(data["available_equipment"]),
                    data["schedule_days"],
                    data["session_duration"],
                    json.dumps(data["strength_levels"]),
                    json.dumps(data["limitations"]),
                    data["age"],
                    data["body_weight"],
                    data["notes"],
                    profile.id,
                ),
            )
            await db.commit()

    async def delete(self, profile_id: int) -> None:
        """Delete a profile."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM user_profiles WHERE id = ?", (profile_id,))
            await db.commit()

    def _row_to_profile(self, row: aiosqlite.Row) -> UserProfile:
        """Convert a database row to a UserProfile."""
        data = {
            "name": row["name"],
            "experience_level": row["experience_level"],
            "goals": json.loads(row["goals"]),
            "available_equipment": json.loads(row["available_equipment"]),
            "schedule_days": row["schedule_days"],
            "session_duration": row["session_duration"],
            "strength_levels": json.loads(row["strength_levels"]),
            "limitations": json.loads(row["limitations"]),
            "age": row["age"],
            "body_weight": row["body_weight"],
            "notes": row["notes"],
        }
        return UserProfile.from_dict(
            data,
            id=row["id"],
            created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else None,
            updated_at=datetime.fromisoformat(row["updated_at"]) if row["updated_at"] else None,
        )


class FitnessDataRepository:
    """Repository for imported fitness data."""

    def __init__(self, db_path: Path | None = None):
        self.db_path = db_path or get_db_path()

    async def create(
        self,
        source: str,
        data_type: str,
        data: dict,
        profile_id: int | None = None,
        recorded_at: datetime | None = None,
    ) -> int:
        """Store fitness data."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """
                INSERT INTO fitness_data
                (profile_id, source, data_type, data, recorded_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    profile_id,
                    source,
                    data_type,
                    json.dumps(data),
                    recorded_at.isoformat() if recorded_at else None,
                ),
            )
            await db.commit()
            return cursor.lastrowid

    async def get_by_source(
        self, source: str, profile_id: int | None = None
    ) -> list[dict]:
        """Get all fitness data from a specific source."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            if profile_id:
                cursor = await db.execute(
                    """
                    SELECT * FROM fitness_data
                    WHERE source = ? AND profile_id = ?
                    ORDER BY recorded_at DESC
                    """,
                    (source, profile_id),
                )
            else:
                cursor = await db.execute(
                    "SELECT * FROM fitness_data WHERE source = ? ORDER BY recorded_at DESC",
                    (source,),
                )
            rows = await cursor.fetchall()
            return [
                {
                    "id": row["id"],
                    "profile_id": row["profile_id"],
                    "source": row["source"],
                    "data_type": row["data_type"],
                    "data": json.loads(row["data"]),
                    "recorded_at": row["recorded_at"],
                    "imported_at": row["imported_at"],
                }
                for row in rows
            ]

    async def get_by_type(
        self, data_type: str, profile_id: int | None = None
    ) -> list[dict]:
        """Get all fitness data of a specific type."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            if profile_id:
                cursor = await db.execute(
                    """
                    SELECT * FROM fitness_data
                    WHERE data_type = ? AND profile_id = ?
                    ORDER BY recorded_at DESC
                    """,
                    (data_type, profile_id),
                )
            else:
                cursor = await db.execute(
                    "SELECT * FROM fitness_data WHERE data_type = ? ORDER BY recorded_at DESC",
                    (data_type,),
                )
            rows = await cursor.fetchall()
            return [
                {
                    "id": row["id"],
                    "profile_id": row["profile_id"],
                    "source": row["source"],
                    "data_type": row["data_type"],
                    "data": json.loads(row["data"]),
                    "recorded_at": row["recorded_at"],
                    "imported_at": row["imported_at"],
                }
                for row in rows
            ]

    async def delete_by_source(self, source: str) -> int:
        """Delete all fitness data from a source."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "DELETE FROM fitness_data WHERE source = ?", (source,)
            )
            await db.commit()
            return cursor.rowcount


class ProgramRepository:
    """Repository for generated programs."""

    def __init__(self, db_path: Path | None = None):
        self.db_path = db_path or get_db_path()

    async def create(self, program: Program) -> int:
        """Create a new program."""
        data = program.to_dict()
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """
                INSERT INTO programs
                (profile_id, name, description, goals, structure, liftoscript, congregation_log)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    program.profile_id,
                    data["name"],
                    data["description"],
                    data["goals"],
                    json.dumps({"weeks": data["weeks"]}),
                    data["liftoscript"],
                    json.dumps(data["congregation_log"]),
                ),
            )
            await db.commit()
            return cursor.lastrowid

    async def get(self, program_id: int) -> Program | None:
        """Get a program by ID."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM programs WHERE id = ?", (program_id,)
            )
            row = await cursor.fetchone()
            if row is None:
                return None
            return self._row_to_program(row)

    async def list_all(self) -> list[Program]:
        """List all programs."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM programs ORDER BY created_at DESC"
            )
            rows = await cursor.fetchall()
            return [self._row_to_program(row) for row in rows]

    async def update(self, program: Program) -> None:
        """Update an existing program."""
        if program.id is None:
            raise ValueError("Program must have an ID to update")

        data = program.to_dict()
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                UPDATE programs SET
                    name = ?, description = ?, goals = ?, structure = ?,
                    liftoscript = ?, congregation_log = ?
                WHERE id = ?
                """,
                (
                    data["name"],
                    data["description"],
                    data["goals"],
                    json.dumps({"weeks": data["weeks"]}),
                    data["liftoscript"],
                    json.dumps(data["congregation_log"]),
                    program.id,
                ),
            )
            await db.commit()

    async def delete(self, program_id: int) -> None:
        """Delete a program."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM programs WHERE id = ?", (program_id,))
            await db.commit()

    def _row_to_program(self, row: aiosqlite.Row) -> Program:
        """Convert a database row to a Program."""
        structure = json.loads(row["structure"])
        data = {
            "name": row["name"],
            "description": row["description"],
            "goals": row["goals"],
            "weeks": structure.get("weeks", []),
            "liftoscript": row["liftoscript"],
            "congregation_log": json.loads(row["congregation_log"]),
        }
        return Program.from_dict(
            data,
            id=row["id"],
            profile_id=row["profile_id"],
            created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else None,
        )


class ExerciseRepository:
    """Repository for exercise library."""

    def __init__(self, db_path: Path | None = None):
        self.db_path = db_path or get_db_path()

    async def get_by_name(self, name: str) -> Exercise | None:
        """Get an exercise by name."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM exercises WHERE name = ?", (name,)
            )
            row = await cursor.fetchone()
            if row is None:
                return None
            return self._row_to_exercise(row)

    async def search(self, query: str) -> list[Exercise]:
        """Search exercises by name or alias."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            # Search in name and aliases
            cursor = await db.execute(
                """
                SELECT * FROM exercises
                WHERE name LIKE ? OR aliases LIKE ?
                ORDER BY name
                """,
                (f"%{query}%", f"%{query}%"),
            )
            rows = await cursor.fetchall()
            return [self._row_to_exercise(row) for row in rows]

    async def get_by_muscle_group(self, muscle_group: MuscleGroup) -> list[Exercise]:
        """Get exercises targeting a muscle group."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM exercises WHERE muscle_groups LIKE ?",
                (f'%"{muscle_group.value}"%',),
            )
            rows = await cursor.fetchall()
            return [self._row_to_exercise(row) for row in rows]

    async def get_by_movement_pattern(
        self, pattern: MovementPattern
    ) -> list[Exercise]:
        """Get exercises with a specific movement pattern."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM exercises WHERE movement_pattern = ?",
                (pattern.value,),
            )
            rows = await cursor.fetchall()
            return [self._row_to_exercise(row) for row in rows]

    async def list_all(self) -> list[Exercise]:
        """List all exercises."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("SELECT * FROM exercises ORDER BY name")
            rows = await cursor.fetchall()
            return [self._row_to_exercise(row) for row in rows]

    async def add(self, exercise: Exercise) -> int:
        """Add a new exercise."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """
                INSERT INTO exercises
                (name, aliases, muscle_groups, equipment, movement_pattern)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    exercise.name,
                    json.dumps(exercise.aliases),
                    json.dumps([mg.value for mg in exercise.muscle_groups]),
                    json.dumps([eq.value for eq in exercise.equipment]),
                    exercise.movement_pattern.value,
                ),
            )
            await db.commit()
            return cursor.lastrowid

    async def get_by_equipment(
        self, equipment_types: list[EquipmentType]
    ) -> list[Exercise]:
        """Get exercises that can be performed with the given equipment types."""
        all_exercises = await self.list_all()
        filtered = []
        for exercise in all_exercises:
            # Exercise is available if ANY of its equipment options is available
            if any(eq in equipment_types for eq in exercise.equipment):
                filtered.append(exercise)
        return filtered

    async def get_compound_exercises(self) -> list[Exercise]:
        """Get all compound exercises."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM exercises WHERE is_compound = 1 ORDER BY name"
            )
            rows = await cursor.fetchall()
            return [self._row_to_exercise(row) for row in rows]

    def _row_to_exercise(self, row: aiosqlite.Row) -> Exercise:
        """Convert a database row to an Exercise."""
        return Exercise(
            id=row["id"],
            name=row["name"],
            aliases=json.loads(row["aliases"]),
            muscle_groups=[MuscleGroup(mg) for mg in json.loads(row["muscle_groups"])],
            equipment=[EquipmentType(eq) for eq in json.loads(row["equipment"])],
            movement_pattern=MovementPattern(row["movement_pattern"]),
            liftosaur_id=row["liftosaur_id"] if "liftosaur_id" in row.keys() else None,
            is_compound=bool(row["is_compound"]) if "is_compound" in row.keys() else False,
        )

    def get_common_exercises(self) -> list[Exercise]:
        """Get the built-in common exercises (no DB access)."""
        return COMMON_EXERCISES


class EquipmentConfigRepository:
    """Repository for equipment configuration."""

    def __init__(self, db_path: Path | None = None):
        self.db_path = db_path or get_db_path()

    async def create(self, config: EquipmentConfig) -> int:
        """Create a new equipment configuration."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """
                INSERT INTO equipment_config
                (profile_id, plate_inventory, weight_unit, barbell_weight, dumbbell_max)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    config.profile_id,
                    json.dumps(config.plate_inventory) if config.plate_inventory else "{}",
                    config.weight_unit,
                    config.barbell_weight,
                    config.dumbbell_max,
                ),
            )
            await db.commit()
            return cursor.lastrowid

    async def get_by_profile(self, profile_id: int) -> EquipmentConfig | None:
        """Get equipment config for a profile."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM equipment_config WHERE profile_id = ?", (profile_id,)
            )
            row = await cursor.fetchone()
            if row is None:
                return None
            return self._row_to_config(row)

    async def upsert(self, config: EquipmentConfig) -> int:
        """Create or update equipment configuration."""
        existing = await self.get_by_profile(config.profile_id)
        if existing:
            config.id = existing.id
            await self.update(config)
            return existing.id
        return await self.create(config)

    async def update(self, config: EquipmentConfig) -> None:
        """Update an existing equipment configuration."""
        if config.id is None:
            raise ValueError("Config must have an ID to update")

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                UPDATE equipment_config SET
                    plate_inventory = ?, weight_unit = ?,
                    barbell_weight = ?, dumbbell_max = ?
                WHERE id = ?
                """,
                (
                    json.dumps(config.plate_inventory) if config.plate_inventory else "{}",
                    config.weight_unit,
                    config.barbell_weight,
                    config.dumbbell_max,
                    config.id,
                ),
            )
            await db.commit()

    async def delete(self, profile_id: int) -> None:
        """Delete equipment config for a profile."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "DELETE FROM equipment_config WHERE profile_id = ?", (profile_id,)
            )
            await db.commit()

    def _row_to_config(self, row: aiosqlite.Row) -> EquipmentConfig:
        """Convert a database row to an EquipmentConfig."""
        plate_inventory = json.loads(row["plate_inventory"]) if row["plate_inventory"] else None
        # Convert string keys back to floats
        if plate_inventory:
            plate_inventory = {float(k): v for k, v in plate_inventory.items()}
        return EquipmentConfig(
            id=row["id"],
            profile_id=row["profile_id"],
            plate_inventory=plate_inventory if plate_inventory else None,
            weight_unit=row["weight_unit"],
            barbell_weight=row["barbell_weight"],
            dumbbell_max=row["dumbbell_max"],
        )


class ProgramProgressRepository:
    """Repository for program progress tracking."""

    def __init__(self, db_path: Path | None = None):
        self.db_path = db_path or get_db_path()

    async def create(self, progress: ProgramProgress) -> int:
        """Create a new progress record."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """
                INSERT INTO program_progress
                (program_id, current_week, current_day, started_at, last_workout_at, status)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    progress.program_id,
                    progress.current_week,
                    progress.current_day,
                    progress.started_at.isoformat() if progress.started_at else None,
                    progress.last_workout_at.isoformat() if progress.last_workout_at else None,
                    progress.status.value,
                ),
            )
            await db.commit()
            return cursor.lastrowid

    async def get_by_program(self, program_id: int) -> ProgramProgress | None:
        """Get progress for a program."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM program_progress WHERE program_id = ?", (program_id,)
            )
            row = await cursor.fetchone()
            if row is None:
                return None
            return self._row_to_progress(row)

    async def upsert(self, progress: ProgramProgress) -> int:
        """Create or update progress record."""
        existing = await self.get_by_program(progress.program_id)
        if existing:
            progress.id = existing.id
            await self.update(progress)
            return existing.id
        return await self.create(progress)

    async def update(self, progress: ProgramProgress) -> None:
        """Update an existing progress record."""
        if progress.id is None:
            raise ValueError("Progress must have an ID to update")

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                UPDATE program_progress SET
                    current_week = ?, current_day = ?,
                    started_at = ?, last_workout_at = ?, status = ?
                WHERE id = ?
                """,
                (
                    progress.current_week,
                    progress.current_day,
                    progress.started_at.isoformat() if progress.started_at else None,
                    progress.last_workout_at.isoformat() if progress.last_workout_at else None,
                    progress.status.value,
                    progress.id,
                ),
            )
            await db.commit()

    async def delete(self, program_id: int) -> None:
        """Delete progress for a program."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "DELETE FROM program_progress WHERE program_id = ?", (program_id,)
            )
            await db.commit()

    async def list_active(self) -> list[ProgramProgress]:
        """List all active program progress records."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM program_progress WHERE status = ? ORDER BY last_workout_at DESC",
                (ProgramStatus.ACTIVE.value,),
            )
            rows = await cursor.fetchall()
            return [self._row_to_progress(row) for row in rows]

    def _row_to_progress(self, row: aiosqlite.Row) -> ProgramProgress:
        """Convert a database row to a ProgramProgress."""
        started_at = None
        if row["started_at"]:
            started_at = datetime.fromisoformat(row["started_at"])

        last_workout_at = None
        if row["last_workout_at"]:
            last_workout_at = datetime.fromisoformat(row["last_workout_at"])

        return ProgramProgress(
            id=row["id"],
            program_id=row["program_id"],
            current_week=row["current_week"],
            current_day=row["current_day"],
            started_at=started_at,
            last_workout_at=last_workout_at,
            status=ProgramStatus(row["status"]),
        )

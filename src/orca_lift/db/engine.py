"""Database engine setup and initialization."""

import json
from pathlib import Path

import aiosqlite

# Default data directory
DATA_DIR = Path(__file__).parent.parent.parent.parent / "data"


def get_db_path(data_dir: Path | None = None) -> Path:
    """Get the database file path."""
    if data_dir is None:
        data_dir = DATA_DIR
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / "orca_lift.db"


async def _run_migrations(db: aiosqlite.Connection) -> None:
    """Run database migrations for schema updates."""
    # Check if user_profiles table has the 1RM columns
    cursor = await db.execute("PRAGMA table_info(user_profiles)")
    columns = await cursor.fetchall()
    profile_columns = {col[1] for col in columns}

    for col in ["one_rm_ohp", "one_rm_squat", "one_rm_bench_press", "one_rm_deadlift", "height"]:
        if col not in profile_columns:
            await db.execute(f"ALTER TABLE user_profiles ADD COLUMN {col} REAL")

    await db.commit()

    # Check if exercises table has the new columns
    cursor = await db.execute("PRAGMA table_info(exercises)")
    columns = await cursor.fetchall()
    column_names = {col[1] for col in columns}

    # Add liftosaur_id column if missing
    if "liftosaur_id" not in column_names:
        await db.execute("ALTER TABLE exercises ADD COLUMN liftosaur_id TEXT")

    # Add is_compound column if missing
    if "is_compound" not in column_names:
        await db.execute("ALTER TABLE exercises ADD COLUMN is_compound INTEGER DEFAULT 0")

    await db.commit()


async def init_db(db_path: Path | None = None) -> None:
    """Initialize the database schema."""
    if db_path is None:
        db_path = get_db_path()

    async with aiosqlite.connect(db_path) as db:
        # User profiles table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS user_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                experience_level TEXT NOT NULL,
                goals TEXT NOT NULL,
                available_equipment TEXT NOT NULL,
                schedule_days INTEGER NOT NULL,
                session_duration INTEGER DEFAULT 60,
                strength_levels TEXT DEFAULT '[]',
                limitations TEXT DEFAULT '[]',
                age INTEGER,
                body_weight REAL,
                height REAL,
                one_rm_ohp REAL,
                one_rm_squat REAL,
                one_rm_bench_press REAL,
                one_rm_deadlift REAL,
                notes TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Fitness data table (imported from various sources)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS fitness_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_id INTEGER,
                source TEXT NOT NULL,
                data_type TEXT NOT NULL,
                data TEXT NOT NULL,
                recorded_at TIMESTAMP,
                imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (profile_id) REFERENCES user_profiles(id)
            )
        """)

        # Programs table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS programs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_id INTEGER,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                goals TEXT NOT NULL,
                structure TEXT NOT NULL,
                liftoscript TEXT DEFAULT '',
                congregation_log TEXT DEFAULT '[]',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (profile_id) REFERENCES user_profiles(id)
            )
        """)

        # Exercises library table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS exercises (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                aliases TEXT DEFAULT '[]',
                muscle_groups TEXT NOT NULL,
                equipment TEXT NOT NULL,
                movement_pattern TEXT NOT NULL,
                liftosaur_id TEXT,
                is_compound INTEGER DEFAULT 0
            )
        """)

        # Equipment configuration (extends user profile)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS equipment_config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_id INTEGER NOT NULL UNIQUE,
                plate_inventory TEXT DEFAULT '{}',
                weight_unit TEXT DEFAULT 'lb',
                barbell_weight REAL DEFAULT 45,
                dumbbell_max REAL,
                FOREIGN KEY (profile_id) REFERENCES user_profiles(id) ON DELETE CASCADE
            )
        """)

        # Program progress tracking
        await db.execute("""
            CREATE TABLE IF NOT EXISTS program_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                program_id INTEGER NOT NULL UNIQUE,
                current_week INTEGER DEFAULT 1,
                current_day INTEGER DEFAULT 1,
                started_at TIMESTAMP,
                last_workout_at TIMESTAMP,
                status TEXT DEFAULT 'active',
                FOREIGN KEY (program_id) REFERENCES programs(id) ON DELETE CASCADE
            )
        """)

        # Create indexes for common queries
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_fitness_data_profile
            ON fitness_data(profile_id)
        """)
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_fitness_data_source
            ON fitness_data(source)
        """)
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_programs_profile
            ON programs(profile_id)
        """)
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_exercises_name
            ON exercises(name)
        """)
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_equipment_config_profile
            ON equipment_config(profile_id)
        """)
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_program_progress_program
            ON program_progress(program_id)
        """)

        await db.commit()

        # Run migrations for existing databases
        await _run_migrations(db)


async def seed_exercises(db_path: Path | None = None) -> None:
    """Seed the database with common exercises."""
    from ..models.exercises import COMMON_EXERCISES

    if db_path is None:
        db_path = get_db_path()

    async with aiosqlite.connect(db_path) as db:
        for exercise in COMMON_EXERCISES:
            try:
                await db.execute(
                    """
                    INSERT OR IGNORE INTO exercises
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
            except aiosqlite.IntegrityError:
                # Exercise already exists, skip
                pass

        await db.commit()

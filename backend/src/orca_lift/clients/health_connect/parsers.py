"""SQLite table parsers for Health Connect backup."""

import sqlite3
from datetime import datetime


def _parse_timestamp(value: int | str | None) -> datetime:
    """Parse a timestamp value to datetime."""
    if value is None:
        return datetime.now()

    if isinstance(value, str):
        # Try ISO format
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            pass

        # Try parsing as integer string
        try:
            value = int(value)
        except ValueError:
            return datetime.now()

    if isinstance(value, int):
        # Assume milliseconds since epoch
        if value > 1e12:
            value = value / 1000
        return datetime.fromtimestamp(value)

    return datetime.now()


def _find_table(tables: list[str], patterns: list[str]) -> str | None:
    """Find a table matching one of the patterns."""
    for pattern in patterns:
        for table in tables:
            if pattern.lower() in table.lower():
                return table
    return None


def _get_columns(conn: sqlite3.Connection, table: str) -> list[str]:
    """Get column names for a table."""
    cursor = conn.execute(f"PRAGMA table_info({table})")
    return [row[1] for row in cursor.fetchall()]


def parse_exercise_sessions(
    conn: sqlite3.Connection, tables: list[str]
) -> list[dict]:
    """Parse exercise session records."""
    sessions = []

    # Try different table names
    table = _find_table(tables, ["exercise_session_record", "exercise_session"])
    if not table:
        return sessions

    columns = _get_columns(conn, table)

    try:
        cursor = conn.execute(f"SELECT * FROM {table}")
        for row in cursor.fetchall():
            row_dict = dict(zip(columns, row))

            # Map common column names
            session = {
                "id": row_dict.get("id") or row_dict.get("_id"),
                "start_time": _parse_timestamp(
                    row_dict.get("start_time")
                    or row_dict.get("startTime")
                    or row_dict.get("start_zoned_time")
                ),
                "end_time": _parse_timestamp(
                    row_dict.get("end_time")
                    or row_dict.get("endTime")
                    or row_dict.get("end_zoned_time")
                ),
                "exercise_type": (
                    row_dict.get("exercise_type")
                    or row_dict.get("exerciseType")
                    or row_dict.get("type")
                ),
                "title": row_dict.get("title") or row_dict.get("name"),
                "notes": row_dict.get("notes") or "",
            }
            sessions.append(session)

    except sqlite3.OperationalError:
        pass

    return sessions


def parse_exercise_segments(
    conn: sqlite3.Connection, tables: list[str]
) -> list[dict]:
    """Parse exercise segment records."""
    segments = []

    table = _find_table(tables, ["exercise_segment", "exercise_lap"])
    if not table:
        return segments

    columns = _get_columns(conn, table)

    try:
        cursor = conn.execute(f"SELECT * FROM {table}")
        for row in cursor.fetchall():
            row_dict = dict(zip(columns, row))

            segment = {
                "id": row_dict.get("id") or row_dict.get("_id"),
                "session_id": (
                    row_dict.get("session_id")
                    or row_dict.get("sessionId")
                    or row_dict.get("parent_id")
                ),
                "start_time": _parse_timestamp(
                    row_dict.get("start_time") or row_dict.get("startTime")
                ),
                "end_time": _parse_timestamp(
                    row_dict.get("end_time") or row_dict.get("endTime")
                ),
                "segment_type": (
                    row_dict.get("segment_type")
                    or row_dict.get("segmentType")
                    or row_dict.get("type")
                ),
                "repetitions": (
                    row_dict.get("repetitions")
                    or row_dict.get("reps")
                    or row_dict.get("rep_count")
                    or 0
                ),
            }
            segments.append(segment)

    except sqlite3.OperationalError:
        pass

    return segments


def parse_weight_records(conn: sqlite3.Connection, tables: list[str]) -> list[dict]:
    """Parse body weight records."""
    records = []

    table = _find_table(tables, ["weight_record", "weight", "body_weight"])
    if not table:
        return records

    columns = _get_columns(conn, table)

    try:
        cursor = conn.execute(f"SELECT * FROM {table}")
        for row in cursor.fetchall():
            row_dict = dict(zip(columns, row))

            # Weight is usually stored in kilograms
            weight = (
                row_dict.get("weight")
                or row_dict.get("weight_kg")
                or row_dict.get("value")
            )

            if weight:
                record = {
                    "weight": float(weight),
                    "time": _parse_timestamp(
                        row_dict.get("time")
                        or row_dict.get("timestamp")
                        or row_dict.get("recorded_at")
                    ),
                }
                records.append(record)

    except sqlite3.OperationalError:
        pass

    return records


def parse_sleep_records(conn: sqlite3.Connection, tables: list[str]) -> list[dict]:
    """Parse sleep session records."""
    records = []

    table = _find_table(tables, ["sleep_session_record", "sleep_session", "sleep"])
    if not table:
        return records

    columns = _get_columns(conn, table)

    try:
        cursor = conn.execute(f"SELECT * FROM {table}")
        for row in cursor.fetchall():
            row_dict = dict(zip(columns, row))

            record = {
                "start_time": _parse_timestamp(
                    row_dict.get("start_time") or row_dict.get("startTime")
                ),
                "end_time": _parse_timestamp(
                    row_dict.get("end_time") or row_dict.get("endTime")
                ),
                "stages": {},  # Would need to parse stage records separately
                "quality_score": row_dict.get("quality_score"),
            }
            records.append(record)

    except sqlite3.OperationalError:
        pass

    # Try to parse sleep stages if available
    stage_table = _find_table(tables, ["sleep_stage", "sleep_segment"])
    if stage_table:
        try:
            stage_columns = _get_columns(conn, stage_table)
            cursor = conn.execute(f"SELECT * FROM {stage_table}")
            stages_by_session: dict[str, dict[str, int]] = {}

            for row in cursor.fetchall():
                row_dict = dict(zip(stage_columns, row))
                session_id = row_dict.get("session_id") or row_dict.get("parent_id")
                stage_type = row_dict.get("stage") or row_dict.get("type") or "unknown"

                # Calculate duration in minutes
                start = _parse_timestamp(row_dict.get("start_time"))
                end = _parse_timestamp(row_dict.get("end_time"))
                duration = int((end - start).total_seconds() / 60)

                if session_id not in stages_by_session:
                    stages_by_session[session_id] = {}

                current = stages_by_session[session_id].get(stage_type, 0)
                stages_by_session[session_id][stage_type] = current + duration

            # Match stages to records (simplified - would need session IDs)
            for i, record in enumerate(records):
                if str(i) in stages_by_session:
                    record["stages"] = stages_by_session[str(i)]

        except sqlite3.OperationalError:
            pass

    return records


def parse_heart_rate_records(
    conn: sqlite3.Connection, tables: list[str]
) -> list[dict]:
    """Parse heart rate records."""
    records = []

    table = _find_table(tables, ["heart_rate_record", "heart_rate", "heartrate"])
    if not table:
        return records

    columns = _get_columns(conn, table)

    try:
        cursor = conn.execute(f"SELECT * FROM {table} LIMIT 1000")  # Limit for performance
        for row in cursor.fetchall():
            row_dict = dict(zip(columns, row))

            bpm = row_dict.get("bpm") or row_dict.get("beats_per_minute") or row_dict.get("value")

            if bpm:
                record = {
                    "bpm": int(bpm),
                    "time": _parse_timestamp(
                        row_dict.get("time") or row_dict.get("timestamp")
                    ),
                }
                records.append(record)

    except sqlite3.OperationalError:
        pass

    return records

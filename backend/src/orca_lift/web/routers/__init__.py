"""Web routers for orca-lift."""

from . import equipment, profile, programs, progress, users
from . import api_auth, api_exercises, api_programs, api_workouts, api_profile

__all__ = [
    "equipment", "profile", "programs", "progress", "users",
    "api_auth", "api_exercises", "api_programs", "api_workouts", "api_profile"
]

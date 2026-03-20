"""Authentication models for OrcaFit."""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class User:
    """Application user."""
    email: str
    hashed_password: str
    name: str = ""
    is_active: bool = True
    created_at: datetime | None = None
    id: int | None = None

    def to_dict(self) -> dict:
        return {
            "email": self.email,
            "name": self.name,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


@dataclass
class TokenPair:
    """JWT token pair."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 3600  # seconds

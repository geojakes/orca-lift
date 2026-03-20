"""Base protocol for workout output formats."""

from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable


@dataclass
class ValidationResult:
    """Result of format validation."""
    is_valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@runtime_checkable
class WorkoutFormat(Protocol):
    """Protocol for pluggable workout formats.
    
    Implementations convert between Program models and format-specific output.
    Both Liftoscript (for Liftosaur) and OrcaFit JSON implement this.
    """
    
    @property
    def name(self) -> str:
        """Format identifier (e.g., 'liftoscript', 'orcafit')."""
        ...
    
    @property
    def file_extension(self) -> str:
        """File extension for this format (e.g., '.txt', '.json')."""
        ...
    
    def generate(self, program: Any) -> str | dict:
        """Convert a Program model into this format's output.
        
        Args:
            program: A Program dataclass instance
            
        Returns:
            str for text formats (Liftoscript), dict for structured formats (OrcaFit JSON)
        """
        ...
    
    def validate(self, output: str | dict) -> ValidationResult:
        """Validate output against this format's rules.
        
        Args:
            output: The format output to validate
            
        Returns:
            ValidationResult with is_valid flag and any errors/warnings
        """
        ...
    
    def parse(self, raw: str | dict) -> Any:
        """Parse this format's output back into a Program model.
        
        Args:
            raw: Raw format output (str or dict)
            
        Returns:
            A Program dataclass instance
        """
        ...

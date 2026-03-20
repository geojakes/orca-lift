"""Equipment configuration model."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class EquipmentConfig:
    """Equipment configuration for a user profile.

    Stores equipment availability and plate inventory for
    accurate weight calculation and exercise filtering.
    """

    profile_id: int
    plate_inventory: dict[float, int] | None = None  # weight -> pairs count
    weight_unit: str = "lb"
    barbell_weight: float = 45.0
    dumbbell_max: float | None = None
    id: int | None = None

    def min_increment(self) -> float:
        """Calculate the smallest weight increase possible.

        Returns the smallest plate weight that can be added to both sides.
        If no plate inventory is set, returns standard 2.5 (lb) or 1.25 (kg).
        """
        if not self.plate_inventory:
            return 2.5 if self.weight_unit == "lb" else 1.25

        if not self.plate_inventory:
            return 2.5 if self.weight_unit == "lb" else 1.25

        # Smallest plate that has at least 1 pair available
        available_plates = [
            weight for weight, pairs in self.plate_inventory.items() if pairs >= 1
        ]
        if not available_plates:
            return 2.5 if self.weight_unit == "lb" else 1.25

        return min(available_plates) * 2  # Both sides

    def round_weight(self, target: float) -> float:
        """Round a target weight to an achievable weight based on plate inventory.

        Uses a greedy algorithm to find the closest achievable weight
        without exceeding available plates.

        Args:
            target: The desired weight (including barbell)

        Returns:
            The closest achievable weight using available plates
        """
        if not self.plate_inventory:
            # No inventory set - round to standard increments
            increment = 5.0 if self.weight_unit == "lb" else 2.5
            return round(target / increment) * increment

        # Weight on the bar (excluding barbell itself)
        plate_weight_needed = target - self.barbell_weight
        if plate_weight_needed <= 0:
            return self.barbell_weight

        # Weight needed per side
        weight_per_side = plate_weight_needed / 2

        # Greedy algorithm: use largest plates first
        sorted_plates = sorted(self.plate_inventory.keys(), reverse=True)
        achieved_per_side = 0.0
        plates_used: dict[float, int] = {}

        for plate_weight in sorted_plates:
            available_pairs = self.plate_inventory.get(plate_weight, 0)
            if available_pairs <= 0:
                continue

            # How many of this plate can we use per side?
            remaining = weight_per_side - achieved_per_side
            plates_needed = int(remaining // plate_weight)
            plates_to_use = min(plates_needed, available_pairs)

            if plates_to_use > 0:
                plates_used[plate_weight] = plates_to_use
                achieved_per_side += plate_weight * plates_to_use

        return self.barbell_weight + (achieved_per_side * 2)

    def can_achieve_weight(self, target: float) -> bool:
        """Check if the exact target weight is achievable with available plates."""
        return abs(self.round_weight(target) - target) < 0.01

    def to_dict(self) -> dict:
        """Convert to dictionary for storage."""
        return {
            "profile_id": self.profile_id,
            "plate_inventory": self.plate_inventory,
            "weight_unit": self.weight_unit,
            "barbell_weight": self.barbell_weight,
            "dumbbell_max": self.dumbbell_max,
        }

    @classmethod
    def from_dict(cls, data: dict, id: int | None = None) -> "EquipmentConfig":
        """Create from dictionary."""
        return cls(
            id=id,
            profile_id=data["profile_id"],
            plate_inventory=data.get("plate_inventory"),
            weight_unit=data.get("weight_unit", "lb"),
            barbell_weight=data.get("barbell_weight", 45.0),
            dumbbell_max=data.get("dumbbell_max"),
        )

    def get_summary(self) -> str:
        """Generate a summary for display or AI context."""
        lines = [f"Weight Unit: {self.weight_unit}"]
        lines.append(f"Barbell Weight: {self.barbell_weight}{self.weight_unit}")

        if self.dumbbell_max:
            lines.append(f"Max Dumbbell: {self.dumbbell_max}{self.weight_unit}")

        if self.plate_inventory:
            plates_str = ", ".join(
                f"{weight}{self.weight_unit}x{pairs*2}"
                for weight, pairs in sorted(
                    self.plate_inventory.items(), reverse=True
                )
            )
            lines.append(f"Plates: {plates_str}")
            lines.append(f"Min Increment: {self.min_increment()}{self.weight_unit}")

        return "\n".join(lines)


# Standard plate inventories for quick setup
STANDARD_PLATE_SETS = {
    "home_basic_lb": {
        45: 2,
        25: 2,
        10: 2,
        5: 2,
        2.5: 2,
    },
    "home_full_lb": {
        45: 4,
        35: 2,
        25: 4,
        10: 4,
        5: 4,
        2.5: 2,
    },
    "commercial_gym_lb": {
        45: 10,
        35: 4,
        25: 6,
        10: 6,
        5: 4,
        2.5: 4,
    },
    "home_basic_kg": {
        20: 2,
        15: 2,
        10: 2,
        5: 2,
        2.5: 2,
        1.25: 2,
    },
    "home_full_kg": {
        20: 4,
        15: 2,
        10: 4,
        5: 4,
        2.5: 4,
        1.25: 2,
    },
}

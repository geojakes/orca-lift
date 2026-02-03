"""Structured output definitions for AI agents."""

from orca import OutputSpec


# Output specs for plan nodes
# Using Orca's OutputSpec with simple types

# User analysis outputs
user_analysis_specs = [
    OutputSpec(
        name="experience_assessment",
        type="string",
        description="Assessment of user's training experience and readiness",
    ),
    OutputSpec(
        name="primary_goals",
        type="list[string]",
        description="Prioritized list of training goals",
    ),
    OutputSpec(
        name="days_per_week",
        type="int",
        description="Number of training days per week",
    ),
    OutputSpec(
        name="session_duration",
        type="int",
        description="Session duration in minutes",
    ),
    OutputSpec(
        name="recovery_capacity",
        type="string",
        description="Recovery capacity: low, moderate, or high",
    ),
    OutputSpec(
        name="limitations",
        type="list[string]",
        description="Movement limitations or exercises to avoid",
    ),
    OutputSpec(
        name="recommendations",
        type="string",
        description="Initial recommendations for program design",
    ),
]

# Equipment assessment outputs
equipment_assessment_specs = [
    OutputSpec(
        name="gym_type",
        type="string",
        description="Classification: full_gym, home_gym, minimal, or bodyweight_only",
    ),
    OutputSpec(
        name="compound_movements",
        type="list[string]",
        description="List of compound movements available",
    ),
    OutputSpec(
        name="isolation_movements",
        type="list[string]",
        description="List of isolation movements available",
    ),
    OutputSpec(
        name="equipment_limitations",
        type="list[string]",
        description="Exercises that cannot be performed due to equipment",
    ),
]

# Program framework outputs
program_framework_specs = [
    OutputSpec(
        name="split_type",
        type="string",
        description="Training split: full_body, upper_lower, push_pull_legs, etc.",
    ),
    OutputSpec(
        name="days_per_week",
        type="int",
        description="Number of training days per week",
    ),
    OutputSpec(
        name="day_focuses",
        type="list[string]",
        description="Focus for each training day (e.g., Push, Pull, Legs)",
    ),
    OutputSpec(
        name="periodization",
        type="string",
        description="Periodization approach: linear, undulating, block, or none",
    ),
    OutputSpec(
        name="progression_philosophy",
        type="string",
        description="How progression will be handled",
    ),
    OutputSpec(
        name="deload_strategy",
        type="string",
        description="When and how deloads will be implemented",
    ),
]

# Exercise spec for nested structure
_exercise_spec = OutputSpec(
    name="exercise",
    type="object",
    description="Exercise configuration",
    source=[
        OutputSpec(name="name", type="string", description="Exercise name"),
        OutputSpec(name="sets", type="int", description="Number of sets"),
        OutputSpec(name="reps_min", type="int", description="Minimum reps per set"),
        OutputSpec(name="reps_max", type="int", description="Maximum reps per set"),
        OutputSpec(name="progression", type="string", description="Progression type: lp, dp, or sum"),
        OutputSpec(name="increment", type="float", description="Weight increment in lbs"),
    ],
)

# Day spec for nested structure
_day_spec = OutputSpec(
    name="day",
    type="object",
    description="Training day configuration",
    source=[
        OutputSpec(name="name", type="string", description="Day name (e.g., Monday, Day 1)"),
        OutputSpec(name="focus", type="string", description="Day focus (e.g., Upper, Lower, Push)"),
        OutputSpec(
            name="exercises",
            type="list",
            description="List of exercises for this day",
            source=_exercise_spec,
        ),
    ],
)

# Week spec for nested structure
_week_spec = OutputSpec(
    name="week",
    type="object",
    description="Training week configuration",
    source=[
        OutputSpec(name="week_number", type="int", description="Week number (1, 2, 3, etc.)"),
        OutputSpec(name="is_deload", type="bool", description="Whether this is a deload week"),
        OutputSpec(
            name="days",
            type="list",
            description="List of training days in this week",
            source=_day_spec,
        ),
    ],
)

# Final program structure output (for mediator)
final_program_specs = [
    OutputSpec(
        name="program_name",
        type="string",
        description="Name of the program",
    ),
    OutputSpec(
        name="program_description",
        type="string",
        description="Brief description of the program",
    ),
    OutputSpec(
        name="periodization_type",
        type="string",
        description="Type of periodization: linear, undulating, block, or none",
    ),
    OutputSpec(
        name="weeks",
        type="list",
        description="List of training weeks",
        source=_week_spec,
    ),
    OutputSpec(
        name="rationale",
        type="string",
        description="Explanation of program design choices and specialist contributions",
    ),
]

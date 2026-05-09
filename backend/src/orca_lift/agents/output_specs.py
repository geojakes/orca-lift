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

# Constraint extraction outputs
_constraint_spec = OutputSpec(
    name="constraint",
    type="object",
    description="A single extracted constraint",
    source=[
        OutputSpec(
            name="type",
            type="string",
            description="Constraint type: equipment, schedule, exercise_restriction, exercise_requirement, cardio, other",
        ),
        OutputSpec(
            name="rule",
            type="string",
            description="Clear constraint rule statement (e.g., 'Only treadmill for cardio exercises')",
        ),
        OutputSpec(
            name="violations",
            type="list[string]",
            description="Examples of what would violate this constraint (e.g., ['elliptical', 'stationary bike', 'rowing machine'])",
        ),
    ],
)

constraint_extraction_specs = [
    OutputSpec(
        name="constraints",
        type="list",
        description="List of all extracted constraints from user request and profile",
        source=_constraint_spec,
    ),
    OutputSpec(
        name="constraint_summary",
        type="string",
        description="Human-readable summary of all constraints for the mediator checklist",
    ),
]


# Exercise spec for nested structure
_exercise_spec = OutputSpec(
    name="exercise",
    type="object",
    description="Exercise configuration",
    source=[
        OutputSpec(name="name", type="string", description="Exercise name from the Liftosaur built-in list"),
        OutputSpec(name="sets", type="int", description="Number of working sets"),
        OutputSpec(name="reps_min", type="int", description="Minimum reps per set"),
        OutputSpec(name="reps_max", type="int", description="Maximum reps per set"),
        OutputSpec(name="progression", type="string", description="Progression type: lp, dp, sum, or custom"),
        OutputSpec(name="increment", type="float", description="Weight increment in lbs"),
        OutputSpec(
            name="rpe_per_set",
            type="list[float]",
            description="RPE target for each set (e.g., [9, 10] for two sets at @9 and @10). Use numeric values 7-10.",
        ),
        OutputSpec(
            name="rest_seconds",
            type="int",
            description="Rest time between sets in seconds (e.g., 60, 120, 180)",
        ),
        OutputSpec(
            name="notes",
            type="string",
            description="Coaching cues and exercise execution notes",
        ),
        OutputSpec(
            name="substitutions",
            type="list[string]",
            description="Alternative exercises that can replace this one",
        ),
        OutputSpec(
            name="techniques",
            type="list[string]",
            description="Intensification techniques to apply: dropset, myorep, lengthened_partial",
        ),
        OutputSpec(
            name="grouping_prefix",
            type="string",
            description="Superset/circuit grouping label (e.g., 'A', 'B') when exercises are paired",
        ),
    ],
)

# Day spec for nested structure
_day_spec = OutputSpec(
    name="day",
    type="object",
    description="Training day configuration",
    source=[
        OutputSpec(name="name", type="string", description="Day name (e.g., Monday, Day 1)"),
        OutputSpec(name="focus", type="string", description="Descriptive day focus like 'Full Body', 'Upper', 'Lower', 'Arms/Delts', 'Push', 'Pull', 'Legs'"),
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
            name="phase_name",
            type="string",
            description="Training phase name: 'Introduction', 'Accumulation', 'Intensification', 'Deload'",
        ),
        OutputSpec(
            name="techniques_enabled",
            type="list[string]",
            description="Intensification techniques active this week: 'dropsets', 'myoreps', 'lengthened_partials'",
        ),
        OutputSpec(
            name="days",
            type="list",
            description="List of training days in this week",
            source=_day_spec,
        ),
    ],
)

# Per-exercise enrichment output (form notes + demo video)
exercise_enrichment_specs = [
    OutputSpec(
        name="posture",
        type="string",
        description="One concise sentence on setup posture and starting stance (e.g., grip, foot placement, spinal alignment, breath bracing).",
    ),
    OutputSpec(
        name="position",
        type="string",
        description="One concise sentence on body positioning through the working range (joint angles, bar/handle path, what to keep stacked or stable).",
    ),
    OutputSpec(
        name="cues",
        type="list[string]",
        description="3-5 short execution cues a lifter can rehearse mid-set (e.g., 'spread the floor', 'crush the bar', 'rib cage down').",
    ),
    OutputSpec(
        name="video_url",
        type="string",
        description="A single YouTube demonstration URL found via WebSearch. Prefer reputable coaching channels (Squat University, Jeff Nippard, Athlean-X, Renaissance Periodization, Alan Thrall, etc.). Must be a real youtube.com or youtu.be link verified via search results — do NOT fabricate. If no good link is found, return an empty string.",
    ),
]


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
        name="progression_strategy",
        type="string",
        description="Description of progression approach: template names (e.g., 'progression', 'dropsets', 'myoreps'), phase transitions, RPE ramping strategy, and deload structure. The Liftoscript converter uses this to generate reusable custom() templates.",
    ),
    OutputSpec(
        name="rationale",
        type="string",
        description="Explanation of program design choices and specialist contributions",
    ),
]

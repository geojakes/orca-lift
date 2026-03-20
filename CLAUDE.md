# orca-lift Development Guide

## Overview

orca-lift is a monorepo containing:
- **backend/** — Python CLI + REST API that generates personalized Liftosaur weightlifting programs using the Orca multi-agent AI framework
- **orcafit-android/** — Android companion app (Kotlin/Jetpack Compose)

## Project Structure

```
orca-lift/
├── backend/                        # Python backend
│   ├── src/orca_lift/
│   │   ├── cli.py                  # Click CLI entry point
│   │   ├── agents/                 # AI agent pipeline
│   │   │   ├── output_specs.py     # Structured output definitions
│   │   │   ├── prompts.py          # Agent prompt templates
│   │   │   ├── congregation.py     # Multi-agent deliberation
│   │   │   ├── plan_builder.py     # DAG plan construction
│   │   │   └── executor.py         # Pipeline orchestration
│   │   ├── clients/                # Fitness data parsers
│   │   │   ├── base.py             # FitnessDataClient protocol
│   │   │   ├── health_connect/     # Health Connect SQLite parser
│   │   │   ├── google_fit/         # Google Fit Takeout parser
│   │   │   └── manual/             # Interactive questionnaire
│   │   ├── generators/
│   │   │   └── liftoscript.py      # Liftoscript DSL generator
│   │   ├── models/                 # Data models
│   │   │   ├── user_profile.py     # User fitness profile
│   │   │   ├── program.py          # Training program structure
│   │   │   └── exercises.py        # Exercise library
│   │   ├── db/                     # Database layer
│   │   │   ├── engine.py           # SQLite setup
│   │   │   └── repositories.py     # Data access
│   │   ├── services/
│   │   │   └── refine.py           # Program refinement
│   │   ├── web/                    # FastAPI REST API + templates
│   │   └── commands/               # CLI commands
│   ├── tests/
│   ├── integration_tests/
│   ├── scripts/
│   ├── data/                       # Runtime data (SQLite DB)
│   └── pyproject.toml
├── orcafit-android/                # Android app
│   ├── app/src/                    # Kotlin source
│   ├── build.gradle.kts
│   └── ...
├── CLAUDE.md
└── README.md
```

## Backend

### Multi-Agent Congregation

The program generation uses 4 specialist agents (Sonnet) plus a mediator (Opus):

1. **Strength Coach** - Compound movements, progressive overload
2. **Hypertrophy Expert** - Volume optimization, muscle growth
3. **Periodization Specialist** - Long-term planning, fatigue management
4. **Recovery Analyst** - Injury prevention, sustainability

The mediator synthesizes their recommendations into a cohesive program.

### DAG Workflow

```
Phase 1 (Parallel):
├── User Analysis
├── Equipment Assessment
        ↓
Phase 2:
├── Program Framework
        ↓
Phase 3 (Congregation):
├── Multi-Agent Deliberation
        ↓
Phase 4:
├── Liftoscript Generation
```

### Liftoscript Output

Programs are output in Liftoscript format for Liftosaur:

```
# Week 1
## Day 1 - Push
Bench Press / 4x5 / progress: lp(5lb)
Overhead Press / 3x8-10 / progress: dp(2.5lb, 8, 10)
```

### Setup & Running

```bash
cd backend
uv sync

# Initialize
uv run orcafit init

# Generate a program
uv run orcafit generate "Build strength, 4 days/week"

# Run tests
uv run pytest tests/
```

### Key Files for Modifications

- **Add new progression scheme**: `backend/src/orca_lift/generators/liftoscript.py`
- **Modify agent prompts**: `backend/src/orca_lift/agents/prompts.py`
- **Add fitness data source**: Create new client in `backend/src/orca_lift/clients/`
- **Change output format**: `backend/src/orca_lift/agents/output_specs.py`

## Data Sources

1. **Health Connect** (primary) - SQLite backup from Android 14+
2. **Google Fit Takeout** (legacy) - Has weight data that Health Connect lacks
3. **Manual Input** - Interactive questionnaire

## Notes

- Health Connect doesn't store weight lifted per exercise - only reps
- Google Fit has `resistance_weight` field - use this when available
- The congregation verbose mode shows full deliberation (useful for debugging)
- Liftoscript validation catches common syntax errors before export

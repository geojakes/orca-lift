# orca-lift

AI-Powered Liftosaur Program Generator using multi-agent deliberation.

## Overview

orca-lift generates personalized weightlifting programs using a congregation of AI specialists that deliberate on optimal program design. Programs are output in [Liftoscript](https://www.liftosaur.com/docs/docs/liftoscript/) format, ready to import into [Liftosaur](https://www.liftosaur.com/).

## Features

- **Multi-Agent AI Design**: 4 specialist agents (strength coach, hypertrophy expert, periodization specialist, recovery analyst) deliberate to create balanced programs
- **Fitness Data Integration**: Import data from Health Connect backups or Google Fit Takeout
- **Natural Language Goals**: Describe your goals in plain English
- **Interactive Refinement**: Tweak your program through conversation
- **Liftoscript Export**: Copy directly to Liftosaur

## Installation

```bash
# Clone the repository
git clone https://github.com/geojakes/orca-lift.git
cd orca-lift

# Install with uv
uv sync
```

## Quick Start

```bash
# 1. Initialize the project
orca-lift init

# 2. Create your fitness profile
orca-lift import manual

# 3. Generate a program
orca-lift generate "Build strength for powerlifting, 4 days per week"

# 4. Export to Liftosaur
orca-lift export 1 --clipboard
```

## Usage

### Initialize

```bash
orca-lift init
```

Creates the database and populates the exercise library.

### Import Fitness Data

```bash
# Interactive questionnaire
orca-lift import manual

# Health Connect backup (Android 14+)
orca-lift import health-connect "Health Connect.zip"

# Google Fit Takeout (legacy)
orca-lift import google-fit takeout.zip
```

### Generate Programs

```bash
# With explicit goals
orca-lift generate "Hypertrophy focus, 5 days per week, limited equipment"

# Using imported profile
orca-lift generate --from-profile

# Verbose mode (see full AI deliberation)
orca-lift generate "Goals here" --verbose
```

### Refine Programs

```bash
orca-lift refine 1
# > Add more tricep work
# > Make Friday a lighter day
# > done
```

### Export

```bash
# Print to terminal
orca-lift export 1

# Copy to clipboard
orca-lift export 1 --clipboard

# Save to file
orca-lift export 1 -o program.txt

# Export as JSON
orca-lift export 1 --format json
```

### Manage Programs

```bash
# List all programs
orca-lift programs list

# Show program details
orca-lift programs show 1

# Show with Liftoscript
orca-lift programs show 1 --liftoscript

# Show AI deliberation
orca-lift programs show 1 --deliberation

# Delete a program
orca-lift programs delete 1
```

## Example Output

```liftoscript
// Strength Builder
// 4-day upper/lower split focused on compound movements

# Week 1
## Day 1 - Upper A
Bench Press / 4x5 / progress: lp(5lb)
Barbell Row / 4x5 / progress: lp(5lb)
Overhead Press / 3x8-10 / progress: dp(2.5lb, 8, 10)
Dumbbell Curl / 3x10-12 / progress: dp(5lb, 10, 12)
Tricep Pushdown / 3x12-15 / progress: dp(5lb, 12, 15)

## Day 2 - Lower A
Squat / 4x5 / progress: lp(5lb)
Romanian Deadlift / 3x8-10 / progress: dp(5lb, 8, 10)
Leg Press / 3x10-12 / progress: dp(10lb, 10, 12)
Leg Curl / 3x12-15 / progress: dp(5lb, 12, 15)
Calf Raise / 4x12-15 / progress: dp(5lb, 12, 15)
```

## How It Works

1. **User Analysis**: Analyzes your profile, goals, and constraints
2. **Equipment Assessment**: Determines available exercises
3. **Program Framework**: Designs the split and periodization
4. **Congregation**: 4 specialists debate program details
5. **Synthesis**: Mediator creates final balanced program
6. **Generation**: Converts to valid Liftoscript

## Data Sources

### Health Connect (Recommended)
- Android 14+ native backup
- Settings → Health Connect → Export data
- Tracks exercise sessions, sleep, body weight

### Google Fit Takeout
- https://takeout.google.com
- Legacy option (API deprecated 2026)
- Has weight lifted data that Health Connect lacks

### Manual Input
- Interactive questionnaire
- Best for strength levels since Health Connect doesn't track weight lifted

## Requirements

- Python 3.13+
- [Orca framework](https://github.com/geojakes/orca) (installed automatically)
- Anthropic API key (set `ANTHROPIC_API_KEY` environment variable)

## License

MIT

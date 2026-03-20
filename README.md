# OrcaFit

AI-powered fitness program generator and workout tracker. Uses a multi-agent AI congregation to design personalized training programs, with full workout tracking via a native Android app.

## Architecture

- **Server**: FastAPI (Python) with async SQLite — generates programs, tracks workouts, REST API for mobile
- **AI Agents**: Orca multi-agent framework with 4 specialist agents + mediator
- **Android App**: Kotlin + Jetpack Compose with Material 3, Hilt DI, Retrofit networking
- **Format System**: Pluggable workout formats (OrcaFit JSON native, Liftoscript for Liftosaur compat)

## Quick Start

### Server

```bash
uv sync
uv run orcafit init
uv run orcafit serve --host 0.0.0.0 --port 8000
```

### Android

Open `orcafit-android/` in Android Studio. Update `API_BASE_URL` in `app/build.gradle.kts` to point to your server.

## Project Structure

```
src/orca_lift/
├── agents/          # AI agent congregation pipeline
├── clients/         # Fitness data importers (Health Connect, Google Fit)
├── commands/        # CLI commands
├── db/              # SQLite database layer
├── formats/         # Pluggable output formats (OrcaFit JSON, Liftoscript)
├── models/          # Data models (exercises, programs, workouts, auth)
├── services/        # Business logic
├── validators/      # Program constraint validation
└── web/             # FastAPI server + REST API

orcafit-android/
├── app/src/main/java/com/orcafit/
│   ├── data/        # API client, local storage, repositories
│   ├── di/          # Hilt dependency injection
│   └── ui/          # Compose screens + ViewModels
```

## API Endpoints

| Area | Endpoints |
|------|-----------|
| Auth | `POST /api/v1/auth/register`, `POST /api/v1/auth/login`, `GET /api/v1/auth/me` |
| Exercises | `GET /api/v1/exercises`, `GET /api/v1/exercises/{name}` |
| Programs | `POST /api/v1/programs/generate`, `GET /api/v1/programs`, `POST /api/v1/programs/{id}/activate` |
| Workouts | `POST /api/v1/workouts/start`, `PUT /api/v1/workouts/{id}/log`, `POST /api/v1/workouts/{id}/complete` |
| Profile | `GET /api/v1/profile/stats`, `GET /api/v1/profile/equipment` |

## Exercise Library

80+ exercises across categories:
- **Resistance**: Compound and isolation movements with all major equipment types
- **Cardio**: Running, cycling, rowing, swimming, HIIT, and more
- **Plyometric**: Box jumps, burpees, kettlebell swings

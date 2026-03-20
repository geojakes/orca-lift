# OrcaFit REST API Implementation

## Overview
Complete REST API endpoints for the OrcaFit mobile app have been created. The API provides authentication, program generation, workout tracking, exercise library access, and user profile management.

## New Files Created

### 1. Core Authentication & Dependencies

#### `/src/orca_lift/web/auth.py`
JWT authentication utilities with:
- Simple JWT token creation and validation
- Password hashing (SHA-256 with salt)
- Token pair generation (access + refresh)
- Token expiration handling
- Constants: `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_SECONDS` (3600s), `REFRESH_TOKEN_EXPIRE_SECONDS` (30 days)

Key functions:
- `hash_password(password: str) -> str` - Hash passwords securely
- `verify_password(password: str, hashed: str) -> bool` - Verify password
- `create_token(user_id: int, expires_in: int) -> str` - Create JWT token
- `decode_token(token: str) -> dict | None` - Decode and validate token
- `create_token_pair(user_id: int) -> dict` - Create access + refresh token pair

#### `/src/orca_lift/web/deps.py`
FastAPI dependency injection for route protection:
- `get_current_user()` - Extract and validate JWT token, returns authenticated User
- `get_optional_user()` - Get user if authenticated, None otherwise
- `security` - HTTP Bearer token scheme

### 2. API Routers

#### `/src/orca_lift/web/routers/api_auth.py` - Authentication Endpoints
- `POST /api/v1/auth/register` - Register new user with email/password
- `POST /api/v1/auth/login` - Login and receive JWT tokens
- `GET /api/v1/auth/me` - Get current authenticated user info

Request/Response Models:
- `RegisterRequest` - email, password, name
- `LoginRequest` - email, password
- `TokenResponse` - access_token, refresh_token, token_type, expires_in
- `MeResponse` - id, email, name

#### `/src/orca_lift/web/routers/api_exercises.py` - Exercise Library
- `GET /api/v1/exercises` - List exercises with optional filters
  - Query parameters: category, muscle_group, equipment, search, compound_only
  - Returns: exercises array with total count
- `GET /api/v1/exercises/{exercise_name}` - Get single exercise details

#### `/src/orca_lift/web/routers/api_programs.py` - Program Management
- `POST /api/v1/programs/generate` - Start async program generation (returns job_id)
- `GET /api/v1/programs/generate/{job_id}/status` - Poll generation status
- `GET /api/v1/programs` - List user's programs
- `GET /api/v1/programs/{program_id}` - Get full program details (OrcaFit format)
- `POST /api/v1/programs/{program_id}/activate` - Set active program
- `POST /api/v1/programs/{program_id}/export` - Export program (orcafit or liftoscript format)
- `DELETE /api/v1/programs/{program_id}` - Delete program

Request Models:
- `GenerateRequest` - goals, days_per_week, weeks, format
- `GenerateResponse` - job_id, status

#### `/src/orca_lift/web/routers/api_workouts.py` - Workout Tracking
- `POST /api/v1/workouts/start` - Start a new workout session (201 Created)
  - Builds exercises from program day specification
- `GET /api/v1/workouts/active` - Get current active workout
- `PUT /api/v1/workouts/{workout_id}/log` - Log a set in real-time
  - Supports resistance: weight_kg, reps, rpe
  - Supports cardio: duration_seconds, distance_meters, heart_rate, pace, calories
  - Supports metadata: rest_seconds, notes, is_warmup
- `POST /api/v1/workouts/{workout_id}/complete` - Mark workout complete
- `GET /api/v1/workouts` - List workout history (paginated, limit=50)
- `GET /api/v1/workouts/{workout_id}` - Get full workout with all logged sets

Request Models:
- `StartWorkoutRequest` - program_id (optional), week_number, day_number
- `LogSetRequest` - exercise_index, set_number, weight_kg, reps, rpe, duration_seconds, distance_meters, heart_rate_avg, heart_rate_max, pace_per_km_seconds, calories, rest_seconds, notes, is_warmup

#### `/src/orca_lift/web/routers/api_profile.py` - Profile & Stats
- `GET /api/v1/profile` - Get user profile
- `GET /api/v1/profile/stats` - Get aggregated stats (PRs, volume, trends)
- `GET /api/v1/profile/equipment` - Get equipment configuration

Returns:
- Profile data with experience level, goals, available equipment
- Stats: total_workouts, total_volume_kg, personal_records (top 20), recent_workouts (last 10)
- Equipment: weight_unit, barbell_weight, dumbbell_max, plate_inventory

### 3. Updated Files

#### `/src/orca_lift/web/app.py` - Main FastAPI Application
**Changes:**
- Updated title to "OrcaFit"
- Updated description to "AI-Powered Fitness Program Generator & Workout Tracker"
- Updated version to "0.2.0"
- Added imports for API routers: api_auth, api_exercises, api_programs, api_workouts, api_profile
- Added imports for seed_exercises() from db.engine
- Updated PUBLIC_PATHS to include API paths: `/api/v1/auth`, `/api/v1/exercises`, `/docs`, `/openapi.json`
- Added router includes for all API routers
- Updated health check version to "0.2.0"
- Updated lifespan to call `seed_exercises()`

#### `/src/orca_lift/web/routers/__init__.py`
- Added imports for all new API routers: api_auth, api_exercises, api_programs, api_workouts, api_profile
- Updated __all__ to export new routers

## API Base URL
All endpoints are under `/api/v1/` prefix

## Authentication
- Public endpoints: `/api/v1/auth/register`, `/api/v1/auth/login`, `/api/v1/exercises`
- Protected endpoints: Require `Authorization: Bearer {access_token}` header
- Token expiration: 1 hour (3600 seconds)

## Database Integration
- Uses existing repositories from `orca_lift.db.repositories`:
  - UserRepository
  - ProgramRepository
  - ActiveProgramRepository
  - ExerciseRepository
  - WorkoutRepository
  - PersonalRecordRepository
  - UserProfileRepository
  - EquipmentConfigRepository

## Error Handling
- 400 Bad Request - Invalid input
- 401 Unauthorized - Missing/invalid token
- 403 Forbidden - Access denied (not your resource)
- 404 Not Found - Resource doesn't exist
- 409 Conflict - Resource already exists (e.g., email registered, active workout exists)

## Async Operations
- Program generation uses `BackgroundTasks` for async processing
- Job tracking with status polling via `/api/v1/programs/generate/{job_id}/status`
- Future: Wire up actual congregation pipeline from agents/executor.py

## Models Used
- `User` - Authentication user
- `Workout` - Workout session with exercises and logged sets
- `WorkoutExercise` - Exercise within workout
- `LoggedSet` - Single logged set
- `Program` - Training program
- `Exercise` - Exercise from library
- `PersonalRecord` - PR tracking

## Status Codes
- 200 OK - Successful GET/PUT
- 201 Created - Successful POST (registration, workout start)
- 202 Accepted - Async operation started (program generation)
- 204 No Content - Successful DELETE
- 400 Bad Request - Validation error
- 401 Unauthorized - Auth failure
- 403 Forbidden - Permission denied
- 404 Not Found - Resource not found
- 409 Conflict - Conflict (duplicate, active workout exists)

## Notes for Production
1. Change `SECRET_KEY` in auth.py to environment variable
2. Implement actual JWT library (PyJWT) instead of custom implementation
3. Add rate limiting
4. Add request logging/monitoring
5. Add CORS configuration if serving mobile app from different domain
6. Wire up actual program generation pipeline
7. Implement token refresh endpoint
8. Add email verification for registration
9. Add password reset flow
10. Consider database connection pooling

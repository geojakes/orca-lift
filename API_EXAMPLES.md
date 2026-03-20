# OrcaFit REST API Examples

## Authentication Flow

### 1. Register a New User
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "secure_password",
    "name": "John Doe"
  }'
```

Response (201 Created):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### 2. Login
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "secure_password"
  }'
```

### 3. Get Current User
```bash
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer {access_token}"
```

Response:
```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "John Doe"
}
```

## Exercise Library

### 1. List All Exercises
```bash
curl -X GET "http://localhost:8000/api/v1/exercises"
```

### 2. Filter Exercises by Category
```bash
curl -X GET "http://localhost:8000/api/v1/exercises?category=resistance&compound_only=true"
```

### 3. Search Exercises
```bash
curl -X GET "http://localhost:8000/api/v1/exercises?search=bench%20press"
```

### 4. Get Exercise Details
```bash
curl -X GET "http://localhost:8000/api/v1/exercises/Bench%20Press"
```

## Program Management

### 1. Generate a New Program (Async)
```bash
curl -X POST "http://localhost:8000/api/v1/programs/generate" \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "goals": "Build strength and muscle mass",
    "days_per_week": 4,
    "weeks": 8,
    "format": "orcafit"
  }'
```

Response (202 Accepted):
```json
{
  "job_id": "abc12345",
  "status": "pending"
}
```

### 2. Check Generation Status
```bash
curl -X GET "http://localhost:8000/api/v1/programs/generate/abc12345/status" \
  -H "Authorization: Bearer {access_token}"
```

Response:
```json
{
  "job_id": "abc12345",
  "status": "completed",
  "created_at": "2026-03-10T12:30:00Z",
  "metadata": {
    "user_id": 1,
    "goals": "Build strength and muscle mass"
  },
  "result": {
    "message": "Generation pipeline ready to be wired up"
  },
  "error": null,
  "updated_at": "2026-03-10T12:35:00Z"
}
```

### 3. List User's Programs
```bash
curl -X GET "http://localhost:8000/api/v1/programs" \
  -H "Authorization: Bearer {access_token}"
```

Response:
```json
{
  "programs": [
    {
      "id": 1,
      "name": "Strength Focus",
      "description": "4-day upper/lower split",
      "goals": "Build strength and muscle mass",
      "weeks": 8,
      "days_per_week": 4,
      "created_at": "2026-03-10T10:00:00Z"
    }
  ]
}
```

### 4. Get Full Program Detail
```bash
curl -X GET "http://localhost:8000/api/v1/programs/1" \
  -H "Authorization: Bearer {access_token}"
```

### 5. Activate a Program
```bash
curl -X POST "http://localhost:8000/api/v1/programs/1/activate" \
  -H "Authorization: Bearer {access_token}"
```

Response:
```json
{
  "status": "activated",
  "program_id": 1
}
```

### 6. Export Program
```bash
curl -X POST "http://localhost:8000/api/v1/programs/1/export?format=liftoscript" \
  -H "Authorization: Bearer {access_token}"
```

### 7. Delete Program
```bash
curl -X DELETE "http://localhost:8000/api/v1/programs/1" \
  -H "Authorization: Bearer {access_token}"
```

## Workout Tracking

### 1. Start a Workout
```bash
curl -X POST "http://localhost:8000/api/v1/workouts/start" \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "program_id": 1,
    "week_number": 1,
    "day_number": 1
  }'
```

Response (201 Created):
```json
{
  "id": 42,
  "program_id": 1,
  "week_number": 1,
  "day_number": 1,
  "day_name": "Push - Chest & Triceps",
  "status": "in_progress",
  "exercises": [
    {
      "exercise_id": "bench-press",
      "exercise_name": "Bench Press",
      "order": 1,
      "target_sets": 4,
      "logged_sets": [],
      "skipped": false,
      "notes": ""
    }
  ],
  "started_at": "2026-03-10T14:30:00Z",
  "completed_at": null,
  "notes": "",
  "total_duration_seconds": null
}
```

### 2. Get Active Workout
```bash
curl -X GET "http://localhost:8000/api/v1/workouts/active" \
  -H "Authorization: Bearer {access_token}"
```

### 3. Log a Set
```bash
curl -X PUT "http://localhost:8000/api/v1/workouts/42/log" \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "exercise_index": 0,
    "set_number": 1,
    "weight_kg": 100.0,
    "reps": 5,
    "rpe": 7.5,
    "rest_seconds": 120,
    "is_warmup": false
  }'
```

Response:
```json
{
  "status": "logged",
  "exercise": "Bench Press",
  "set_number": 1,
  "sets_completed": 1,
  "sets_target": 4
}
```

### 4. Log a Cardio Set
```bash
curl -X PUT "http://localhost:8000/api/v1/workouts/42/log" \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "exercise_index": 1,
    "set_number": 1,
    "duration_seconds": 1800,
    "distance_meters": 5000,
    "heart_rate_avg": 145,
    "heart_rate_max": 165,
    "calories": 450,
    "pace_per_km_seconds": 360
  }'
```

### 5. Complete a Workout
```bash
curl -X POST "http://localhost:8000/api/v1/workouts/42/complete" \
  -H "Authorization: Bearer {access_token}"
```

Response:
```json
{
  "status": "completed",
  "duration_minutes": 45,
  "exercises_completed": 4,
  "total_exercises": 5,
  "total_volume_kg": 2400.0
}
```

### 6. List Workout History
```bash
curl -X GET "http://localhost:8000/api/v1/workouts?limit=10" \
  -H "Authorization: Bearer {access_token}"
```

Response:
```json
{
  "workouts": [
    {
      "id": 42,
      "program_id": 1,
      "day_name": "Push - Chest & Triceps",
      "status": "completed",
      "started_at": "2026-03-10T14:30:00Z",
      "completed_at": "2026-03-10T15:15:00Z",
      "duration_minutes": 45,
      "exercises_completed": 4,
      "total_volume_kg": 2400.0
    }
  ]
}
```

### 7. Get Full Workout Details
```bash
curl -X GET "http://localhost:8000/api/v1/workouts/42" \
  -H "Authorization: Bearer {access_token}"
```

## User Profile & Stats

### 1. Get Profile
```bash
curl -X GET "http://localhost:8000/api/v1/profile" \
  -H "Authorization: Bearer {access_token}"
```

Response:
```json
{
  "has_profile": true,
  "profile": {
    "id": 1,
    "user_id": 1,
    "experience_level": "intermediate",
    "goals": ["strength", "hypertrophy"],
    "available_equipment": ["barbell", "dumbbells", "bench"],
    "age": 28,
    "body_weight": 85.5,
    "height": 180.0
  }
}
```

### 2. Get User Stats
```bash
curl -X GET "http://localhost:8000/api/v1/profile/stats" \
  -H "Authorization: Bearer {access_token}"
```

Response:
```json
{
  "total_workouts": 42,
  "total_volume_kg": 125000.0,
  "personal_records": [
    {
      "exercise_id": "bench-press",
      "exercise_name": "Bench Press",
      "record_type": "1rm",
      "value": 140.0,
      "unit": "kg",
      "achieved_at": "2026-03-09T15:30:00Z",
      "workout_id": 40,
      "previous_value": 135.0
    }
  ],
  "recent_workouts": [
    {
      "id": 42,
      "day_name": "Push - Chest & Triceps",
      "completed_at": "2026-03-10T15:15:00Z",
      "volume_kg": 2400.0
    }
  ]
}
```

### 3. Get Equipment Configuration
```bash
curl -X GET "http://localhost:8000/api/v1/profile/equipment" \
  -H "Authorization: Bearer {access_token}"
```

Response:
```json
{
  "has_config": true,
  "weight_unit": "kg",
  "barbell_weight": 20.0,
  "dumbbell_max": 50.0,
  "plate_inventory": {
    "20kg": 4,
    "15kg": 4,
    "10kg": 6,
    "5kg": 8,
    "2.5kg": 4,
    "1.25kg": 2
  }
}
```

## API Documentation

Access interactive API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

## Error Examples

### 401 Unauthorized (Missing Token)
```json
{
  "detail": "Not authenticated"
}
```

### 401 Unauthorized (Invalid Token)
```json
{
  "detail": "Invalid or expired token"
}
```

### 404 Not Found
```json
{
  "detail": "Program not found"
}
```

### 409 Conflict (Email Already Registered)
```json
{
  "detail": "Email already registered"
}
```

### 409 Conflict (Active Workout Exists)
```json
{
  "detail": "Already have an active workout. Complete or skip it first."
}
```

## Notes

- Replace `{access_token}` with actual JWT token from login/register
- All timestamps are in ISO 8601 format with UTC timezone
- Pagination defaults: limit=50 for workouts
- Use HTTP Bearer scheme for all protected endpoints
- Job IDs are 8-character alphanumeric strings

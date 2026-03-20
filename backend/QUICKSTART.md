# OrcaFit REST API - Quick Start Guide

## Files Overview

### Authentication & Security
- **`src/orca_lift/web/auth.py`** - JWT token creation, password hashing
- **`src/orca_lift/web/deps.py`** - FastAPI dependencies for route protection

### API Endpoints
- **`src/orca_lift/web/routers/api_auth.py`** - Login/register (3 endpoints)
- **`src/orca_lift/web/routers/api_exercises.py`** - Exercise library (2 endpoints)
- **`src/orca_lift/web/routers/api_programs.py`** - Program management (7 endpoints)
- **`src/orca_lift/web/routers/api_workouts.py`** - Workout tracking (6 endpoints)
- **`src/orca_lift/web/routers/api_profile.py`** - User stats (3 endpoints)

### Updated Files
- **`src/orca_lift/web/app.py`** - Main FastAPI app with new routes
- **`src/orca_lift/web/routers/__init__.py`** - Router exports

## API Base URL
```
http://localhost:8000/api/v1
```

## Quick Examples

### Register & Login
```bash
# Register
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com", "password":"pass123", "name":"John"}'

# Login (returns tokens)
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com", "password":"pass123"}'

# Use token in subsequent requests
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Browse Exercises
```bash
# List all exercises
curl "http://localhost:8000/api/v1/exercises"

# Search
curl "http://localhost:8000/api/v1/exercises?search=bench"

# Filter by category
curl "http://localhost:8000/api/v1/exercises?category=resistance&compound_only=true"
```

### Generate Programs
```bash
# Start generation (async)
curl -X POST "http://localhost:8000/api/v1/programs/generate" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"goals":"Build strength", "days_per_week":4, "weeks":8}'

# Check status
curl "http://localhost:8000/api/v1/programs/generate/abc12345/status" \
  -H "Authorization: Bearer $TOKEN"

# List programs
curl "http://localhost:8000/api/v1/programs" \
  -H "Authorization: Bearer $TOKEN"
```

### Track Workouts
```bash
# Start workout
curl -X POST "http://localhost:8000/api/v1/workouts/start" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"program_id":1, "week_number":1, "day_number":1}'

# Log a set
curl -X PUT "http://localhost:8000/api/v1/workouts/42/log" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"exercise_index":0, "set_number":1, "weight_kg":100, "reps":5}'

# Complete workout
curl -X POST "http://localhost:8000/api/v1/workouts/42/complete" \
  -H "Authorization: Bearer $TOKEN"
```

### Get Stats
```bash
# User profile
curl "http://localhost:8000/api/v1/profile" \
  -H "Authorization: Bearer $TOKEN"

# Stats & PRs
curl "http://localhost:8000/api/v1/profile/stats" \
  -H "Authorization: Bearer $TOKEN"
```

## Endpoints by Category

### Auth (Public)
- `POST /auth/register` - Register user
- `POST /auth/login` - Login user
- `GET /auth/me` - Get current user (requires auth)

### Exercises (Public)
- `GET /exercises` - List exercises
- `GET /exercises/{name}` - Get exercise details

### Programs (Auth Required)
- `POST /programs/generate` - Start program generation
- `GET /programs/generate/{job_id}/status` - Check status
- `GET /programs` - List user's programs
- `GET /programs/{id}` - Get program details
- `POST /programs/{id}/activate` - Activate program
- `POST /programs/{id}/export` - Export program
- `DELETE /programs/{id}` - Delete program

### Workouts (Auth Required)
- `POST /workouts/start` - Start workout
- `GET /workouts/active` - Get active workout
- `PUT /workouts/{id}/log` - Log a set
- `POST /workouts/{id}/complete` - Complete workout
- `GET /workouts` - List workouts
- `GET /workouts/{id}` - Get workout details

### Profile (Auth Required)
- `GET /profile` - Get user profile
- `GET /profile/stats` - Get stats
- `GET /profile/equipment` - Get equipment config

## Key Features

### Authentication
- JWT tokens (1-hour access, 30-day refresh)
- SHA-256 password hashing with salt
- Bearer token scheme

### Data Models
- Supports resistance training (weight, reps, RPE)
- Supports cardio (duration, distance, HR, pace, calories)
- Personal record tracking
- Volume calculations

### Status Codes
- `200` OK
- `201` Created (register, start workout)
- `202` Accepted (async program generation)
- `400` Bad Request
- `401` Unauthorized
- `403` Forbidden
- `404` Not Found
- `409` Conflict

## Interactive Documentation

Access API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Important Notes

1. **Token Expiration**: Access tokens expire after 1 hour
2. **Public Paths**: Auth and exercise endpoints are public
3. **Protected Paths**: Programs, workouts, profile require auth
4. **Resource Ownership**: Users can only access their own workouts
5. **Async Operations**: Program generation returns immediately with job ID

## Production Checklist

- [ ] Move `SECRET_KEY` to environment variable
- [ ] Use production JWT library (PyJWT)
- [ ] Add rate limiting
- [ ] Configure CORS for mobile app domain
- [ ] Set up HTTPS/SSL
- [ ] Add request logging
- [ ] Configure database pooling
- [ ] Add monitoring/alerts
- [ ] Implement refresh token endpoint
- [ ] Add email verification

## File Locations

All Python files are in: `/src/orca_lift/web/`

```
src/orca_lift/web/
├── auth.py                          # JWT utilities
├── deps.py                          # FastAPI dependencies
├── app.py                           # Main app (UPDATED)
├── job_tracker.py                   # Async job tracking
└── routers/
    ├── __init__.py                  # (UPDATED)
    ├── api_auth.py                  # Authentication endpoints
    ├── api_exercises.py             # Exercise library
    ├── api_programs.py              # Program management
    ├── api_workouts.py              # Workout tracking
    ├── api_profile.py               # User stats
    └── [existing routers]           # Web UI routers
```

## Database Integration

Uses existing repositories:
- `UserRepository` - User account management
- `ProgramRepository` - Training programs
- `ExerciseRepository` - Exercise library
- `WorkoutRepository` - Workout sessions
- `PersonalRecordRepository` - PR tracking
- `UserProfileRepository` - User details
- `EquipmentConfigRepository` - Equipment inventory

## Next Steps

1. Read `REST_API_SUMMARY.md` for full documentation
2. Review `API_EXAMPLES.md` for detailed curl examples
3. Check `FILES_CREATED.md` for complete file listing
4. Start implementing mobile app client
5. Wire up actual program generation pipeline
6. Add production security measures

## Support

For implementation details, see:
- `REST_API_SUMMARY.md` - Complete API documentation
- `API_EXAMPLES.md` - Working code examples
- `FILES_CREATED.md` - File listing and stats
- Code comments in each router file

All files use type hints and follow FastAPI best practices.

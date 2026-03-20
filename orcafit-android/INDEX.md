# OrcaFit Android - Project Index

Complete navigation guide for the OrcaFit Android project.

## Documentation

Start here to understand the project:

1. **[README.md](README.md)** - Project overview and getting started
   - Technology stack
   - API integration
   - Configuration
   - Development commands

2. **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** - Detailed project layout
   - Directory structure
   - Component descriptions
   - Dependencies
   - Architecture notes

3. **[FILES_MANIFEST.md](FILES_MANIFEST.md)** - Complete file listing
   - All 28 files documented
   - File purposes and contents
   - Quick reference by feature

4. **[INDEX.md](INDEX.md)** - This file

## Key Source Files

### Application Entry Points
- [OrcaFitApp.kt](/sessions/determined-great-hypatia/mnt/orca-lift/orcafit-android/app/src/main/java/com/orcafit/OrcaFitApp.kt) - Hilt initialization
- [MainActivity.kt](/sessions/determined-great-hypatia/mnt/orca-lift/orcafit-android/app/src/main/java/com/orcafit/MainActivity.kt) - Compose entry point

### Build Configuration
- [build.gradle.kts](/sessions/determined-great-hypatia/mnt/orca-lift/orcafit-android/build.gradle.kts) - Root build file
- [settings.gradle.kts](/sessions/determined-great-hypatia/mnt/orca-lift/orcafit-android/settings.gradle.kts) - Project settings
- [gradle.properties](/sessions/determined-great-hypatia/mnt/orca-lift/orcafit-android/gradle.properties) - Gradle config
- [app/build.gradle.kts](/sessions/determined-great-hypatia/mnt/orca-lift/orcafit-android/app/build.gradle.kts) - App dependencies

### Dependency Injection
- [AppModule.kt](/sessions/determined-great-hypatia/mnt/orca-lift/orcafit-android/app/src/main/java/com/orcafit/di/AppModule.kt) - DI setup

### Data Layer

#### API
- [OrcaFitApi.kt](/sessions/determined-great-hypatia/mnt/orca-lift/orcafit-android/app/src/main/java/com/orcafit/data/api/OrcaFitApi.kt) - 18 Retrofit endpoints
- [AuthInterceptor.kt](/sessions/determined-great-hypatia/mnt/orca-lift/orcafit-android/app/src/main/java/com/orcafit/data/api/AuthInterceptor.kt) - Token injection
- [ApiModels.kt](/sessions/determined-great-hypatia/mnt/orca-lift/orcafit-android/app/src/main/java/com/orcafit/data/api/models/ApiModels.kt) - 30+ data classes

#### Local Storage
- [TokenManager.kt](/sessions/determined-great-hypatia/mnt/orca-lift/orcafit-android/app/src/main/java/com/orcafit/data/local/TokenManager.kt) - DataStore token persistence

### UI Layer

#### Theme
- [Color.kt](/sessions/determined-great-hypatia/mnt/orca-lift/orcafit-android/app/src/main/java/com/orcafit/ui/theme/Color.kt) - Brand colors
- [Type.kt](/sessions/determined-great-hypatia/mnt/orca-lift/orcafit-android/app/src/main/java/com/orcafit/ui/theme/Type.kt) - Typography
- [Theme.kt](/sessions/determined-great-hypatia/mnt/orca-lift/orcafit-android/app/src/main/java/com/orcafit/ui/theme/Theme.kt) - Material 3 theme

#### Navigation
- [NavGraph.kt](/sessions/determined-great-hypatia/mnt/orca-lift/orcafit-android/app/src/main/java/com/orcafit/ui/navigation/NavGraph.kt) - 9 routes, type-safe navigation

#### Screens
- [LoginScreen.kt](/sessions/determined-great-hypatia/mnt/orca-lift/orcafit-android/app/src/main/java/com/orcafit/ui/screens/auth/LoginScreen.kt)
- [HomeScreen.kt](/sessions/determined-great-hypatia/mnt/orca-lift/orcafit-android/app/src/main/java/com/orcafit/ui/screens/home/HomeScreen.kt)
- [GenerateScreen.kt](/sessions/determined-great-hypatia/mnt/orca-lift/orcafit-android/app/src/main/java/com/orcafit/ui/screens/generate/GenerateScreen.kt)
- [ProgramListScreen.kt](/sessions/determined-great-hypatia/mnt/orca-lift/orcafit-android/app/src/main/java/com/orcafit/ui/screens/programs/ProgramListScreen.kt)
- [ProgramDetailScreen.kt](/sessions/determined-great-hypatia/mnt/orca-lift/orcafit-android/app/src/main/java/com/orcafit/ui/screens/programs/ProgramDetailScreen.kt)
- [ActiveWorkoutScreen.kt](/sessions/determined-great-hypatia/mnt/orca-lift/orcafit-android/app/src/main/java/com/orcafit/ui/screens/workout/ActiveWorkoutScreen.kt)
- [WorkoutSummaryScreen.kt](/sessions/determined-great-hypatia/mnt/orca-lift/orcafit-android/app/src/main/java/com/orcafit/ui/screens/workout/WorkoutSummaryScreen.kt)
- [HistoryScreen.kt](/sessions/determined-great-hypatia/mnt/orca-lift/orcafit-android/app/src/main/java/com/orcafit/ui/screens/history/HistoryScreen.kt)
- [ExerciseLibraryScreen.kt](/sessions/determined-great-hypatia/mnt/orca-lift/orcafit-android/app/src/main/java/com/orcafit/ui/screens/exercises/ExerciseLibraryScreen.kt)

### Resources & Manifest
- [AndroidManifest.xml](/sessions/determined-great-hypatia/mnt/orca-lift/orcafit-android/app/src/main/AndroidManifest.xml)
- [strings.xml](/sessions/determined-great-hypatia/mnt/orca-lift/orcafit-android/app/src/main/res/values/strings.xml)
- [themes.xml](/sessions/determined-great-hypatia/mnt/orca-lift/orcafit-android/app/src/main/res/values/themes.xml)

## Feature Quick Links

### Authentication
Files related to user authentication:
- `data/api/OrcaFitApi.kt` - register(), login(), getMe()
- `data/api/AuthInterceptor.kt` - Bearer token injection
- `data/local/TokenManager.kt` - Token storage
- `ui/screens/auth/LoginScreen.kt` - Login UI

### Program Generation
Files for AI program generation:
- `data/api/OrcaFitApi.kt` - generateProgram(), getGenerationStatus()
- `ui/screens/generate/GenerateScreen.kt` - Generation UI
- `data/api/models/ApiModels.kt` - GenerateProgramRequest, GenerateResponse

### Program Management
Files for managing training programs:
- `data/api/OrcaFitApi.kt` - listPrograms(), getProgram(), activateProgram()
- `ui/screens/programs/ProgramListScreen.kt` - List view
- `ui/screens/programs/ProgramDetailScreen.kt` - Detail view
- `data/api/models/ApiModels.kt` - ProgramData, WeekData, DayData

### Workout Tracking
Files for live workout logging:
- `data/api/OrcaFitApi.kt` - startWorkout(), logSet(), completeWorkout()
- `ui/screens/workout/ActiveWorkoutScreen.kt` - Active workout UI
- `ui/screens/workout/WorkoutSummaryScreen.kt` - Summary UI
- `data/api/models/ApiModels.kt` - WorkoutResponse, LogSetRequest, LoggedSetDto

### Workout History
Files for viewing past workouts:
- `data/api/OrcaFitApi.kt` - listWorkouts(), getWorkout()
- `ui/screens/history/HistoryScreen.kt` - History view
- `data/api/models/ApiModels.kt` - WorkoutListResponse, WorkoutSummaryDto

### Exercise Library
Files for exercise reference:
- `data/api/OrcaFitApi.kt` - listExercises()
- `ui/screens/exercises/ExerciseLibraryScreen.kt` - Library view
- `data/api/models/ApiModels.kt` - ExerciseDto, ExerciseListResponse

## Project Structure

```
orcafit-android/                          (Root project directory)
├── build.gradle.kts                      (Root build config)
├── settings.gradle.kts                   (Project settings)
├── gradle.properties                     (Gradle configuration)
├── README.md                             (Getting started)
├── PROJECT_STRUCTURE.md                  (Detailed structure)
├── FILES_MANIFEST.md                     (File listing)
├── INDEX.md                              (This file)
│
└── app/                                  (App module)
    ├── build.gradle.kts                  (Dependencies)
    │
    └── src/main/
        ├── AndroidManifest.xml           (App manifest)
        │
        ├── java/com/orcafit/
        │   ├── OrcaFitApp.kt             (Hilt app)
        │   ├── MainActivity.kt           (Entry activity)
        │   │
        │   ├── di/
        │   │   └── AppModule.kt          (DI setup)
        │   │
        │   ├── data/
        │   │   ├── api/
        │   │   │   ├── OrcaFitApi.kt     (API interface)
        │   │   │   ├── AuthInterceptor.kt
        │   │   │   └── models/
        │   │   │       └── ApiModels.kt
        │   │   └── local/
        │   │       └── TokenManager.kt
        │   │
        │   └── ui/
        │       ├── theme/
        │       │   ├── Color.kt
        │       │   ├── Type.kt
        │       │   └── Theme.kt
        │       ├── navigation/
        │       │   └── NavGraph.kt
        │       └── screens/
        │           ├── auth/LoginScreen.kt
        │           ├── home/HomeScreen.kt
        │           ├── generate/GenerateScreen.kt
        │           ├── programs/
        │           │   ├── ProgramListScreen.kt
        │           │   └── ProgramDetailScreen.kt
        │           ├── workout/
        │           │   ├── ActiveWorkoutScreen.kt
        │           │   └── WorkoutSummaryScreen.kt
        │           ├── history/HistoryScreen.kt
        │           └── exercises/ExerciseLibraryScreen.kt
        │
        └── res/values/
            ├── strings.xml
            └── themes.xml
```

## Development Workflow

### Understanding the Architecture

1. Read [README.md](README.md) for project overview
2. Read [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for architecture details
3. Check specific files in the key source files section above

### Adding a New Feature

1. Create API endpoint in `data/api/OrcaFitApi.kt`
2. Add request/response models in `data/api/models/ApiModels.kt`
3. Create screen in `ui/screens/`
4. Add route in `ui/navigation/NavGraph.kt`
5. Create ViewModel (future phase)
6. Create Repository (future phase)

### Building & Running

```bash
cd /sessions/determined-great-hypatia/mnt/orca-lift/orcafit-android

# Build
./gradlew build

# Run on emulator
./gradlew installDebug

# Clean and rebuild
./gradlew clean build
```

## Dependencies Overview

### Core
- androidx.core:core-ktx (Kotlin extensions)
- androidx.lifecycle:lifecycle-runtime-ktx (Lifecycle management)
- androidx.activity:activity-compose (Activity + Compose)

### UI (Compose)
- androidx.compose.ui:ui (Compose runtime)
- androidx.compose.material3:material3 (Material Design)
- androidx.compose.material:material-icons-extended (Icon library)

### Navigation
- androidx.navigation:navigation-compose (Type-safe navigation)
- androidx.hilt:hilt-navigation-compose (Hilt integration)

### Networking
- com.squareup.retrofit2:retrofit (HTTP client)
- com.squareup.retrofit2:converter-moshi (JSON serialization)
- com.squareup.okhttp3:logging-interceptor (HTTP logging)

### DI & Storage
- com.google.dagger:hilt-android (Dependency injection)
- androidx.datastore:datastore-preferences (Token storage)
- androidx.room:room-runtime (Database - optional)

## Common Tasks

### Find Authentication Code
See [Authentication](#authentication) section

### Add New API Endpoint
1. Add method to `OrcaFitApi.kt`
2. Add models to `ApiModels.kt`
3. Inject API in screen/ViewModel

### Update Theme Colors
Edit `ui/theme/Color.kt`

### Add New Navigation Route
1. Add route constant in `NavGraph.kt` Routes object
2. Add composable() in NavHost
3. Create corresponding screen file

### Debug API Calls
HttpLoggingInterceptor in `AppModule.kt` logs all HTTP traffic

## Getting Help

### Documentation
- Jetpack Compose: developer.android.com/jetpack/compose
- Material 3: material.io
- Retrofit: square.github.io/retrofit
- Hilt: dagger.dev/hilt

### Project Files
- See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for detailed explanations
- See [FILES_MANIFEST.md](FILES_MANIFEST.md) for individual file documentation


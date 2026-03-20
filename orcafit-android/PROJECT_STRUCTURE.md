# OrcaFit Android Project Structure

## Project Layout

```
orcafit-android/
├── build.gradle.kts                          # Root build configuration
├── settings.gradle.kts                       # Project settings & module inclusion
├── gradle.properties                         # Gradle properties
├── PROJECT_STRUCTURE.md                      # This file
│
└── app/
    ├── build.gradle.kts                      # App module build configuration
    │
    └── src/
        └── main/
            ├── AndroidManifest.xml           # Android app manifest
            │
            ├── java/com/orcafit/
            │   ├── MainActivity.kt            # Main activity (Compose)
            │   ├── OrcaFitApp.kt             # Hilt application class
            │   │
            │   ├── di/
            │   │   └── AppModule.kt           # Dependency injection module
            │   │
            │   ├── data/
            │   │   ├── api/
            │   │   │   ├── OrcaFitApi.kt     # Retrofit API interface
            │   │   │   ├── AuthInterceptor.kt # OkHttp auth interceptor
            │   │   │   └── models/
            │   │   │       └── ApiModels.kt  # Moshi data classes
            │   │   │
            │   │   └── local/
            │   │       └── TokenManager.kt   # Token storage with DataStore
            │   │
            │   └── ui/
            │       ├── theme/
            │       │   ├── Color.kt          # Brand colors
            │       │   ├── Type.kt           # Typography definitions
            │       │   └── Theme.kt          # Material 3 theme setup
            │       │
            │       ├── navigation/
            │       │   └── NavGraph.kt       # Jetpack Compose Navigation
            │       │
            │       └── screens/
            │           ├── auth/
            │           │   └── LoginScreen.kt
            │           ├── home/
            │           │   └── HomeScreen.kt
            │           ├── generate/
            │           │   └── GenerateScreen.kt
            │           ├── programs/
            │           │   ├── ProgramListScreen.kt
            │           │   └── ProgramDetailScreen.kt
            │           ├── workout/
            │           │   ├── ActiveWorkoutScreen.kt
            │           │   └── WorkoutSummaryScreen.kt
            │           ├── history/
            │           │   └── HistoryScreen.kt
            │           └── exercises/
            │               └── ExerciseLibraryScreen.kt
            │
            └── res/
                └── values/
                    ├── strings.xml
                    └── themes.xml
```

## Key Files

### Root Configuration

- **build.gradle.kts**: Top-level build file with plugin versions
- **settings.gradle.kts**: Root project name and module inclusion
- **gradle.properties**: Global Gradle configuration

### App Module Build

- **app/build.gradle.kts**: Dependency declarations and Android configuration
  - Target SDK: 34
  - Min SDK: 26
  - Compose support enabled
  - Hilt DI setup
  - Retrofit + Moshi networking
  - Room database support (future)

### Application Core

- **OrcaFitApp.kt**: Hilt-annotated Application class
- **MainActivity.kt**: Entry point with Compose setup
- **AppModule.kt**: Dependency injection for API, tokenManager, Retrofit

### Networking

- **OrcaFitApi.kt**: Retrofit interface with endpoints for:
  - Authentication (register, login, getMe)
  - Exercises (list with filters)
  - Programs (generate, list, get, activate)
  - Workouts (start, log, complete, history)
  - Profile stats

- **ApiModels.kt**: Moshi-annotated data classes for all API requests/responses
  - Auth: RegisterRequest, LoginRequest, TokenResponse
  - Exercises: ExerciseDto, ExerciseListResponse
  - Programs: GenerateProgramRequest, ProgramData, WeekData, DayData
  - Workouts: StartWorkoutRequest, WorkoutResponse, LogSetRequest
  - Stats: StatsResponse

- **AuthInterceptor.kt**: OkHttp interceptor for adding Bearer tokens

### Local Storage

- **TokenManager.kt**: DataStore-based token persistence
  - Save/clear access and refresh tokens
  - isLoggedIn flow for navigation

### UI Layer

#### Theme
- **Color.kt**: OrcaFit brand colors (deep green primary, teal secondary)
- **Type.kt**: Material 3 typography system
- **Theme.kt**: Dynamic color support with dark theme

#### Navigation
- **NavGraph.kt**: Jetpack Compose Navigation with routes:
  - Authentication flow (login → home)
  - Program generation
  - Program browsing (list & details)
  - Active workout tracking
  - Workout history
  - Exercise library

#### Screens (Placeholder Implementation)
- **LoginScreen**: Authentication
- **HomeScreen**: Dashboard
- **GenerateScreen**: AI program generation
- **ProgramListScreen**: Browse saved programs
- **ProgramDetailScreen**: Program details & activation
- **ActiveWorkoutScreen**: Live workout tracking
- **WorkoutSummaryScreen**: Post-workout stats
- **HistoryScreen**: Workout history
- **ExerciseLibraryScreen**: Exercise reference

## Dependencies

### Core Android
- androidx.core:core-ktx
- androidx.lifecycle:lifecycle-runtime-ktx
- androidx.activity:activity-compose

### Compose
- Material 3 (latest)
- Compose UI
- Material Icons Extended

### Navigation
- androidx.navigation:navigation-compose
- androidx.hilt:hilt-navigation-compose

### Dependency Injection
- com.google.dagger:hilt-android
- com.google.dagger:hilt-android-compiler (kapt)

### Networking
- com.squareup.retrofit2:retrofit
- com.squareup.retrofit2:converter-moshi
- com.squareup.okhttp3:okhttp
- com.squareup.okhttp3:logging-interceptor
- com.squareup.moshi:moshi-kotlin
- com.squareup.moshi:moshi-kotlin-codegen (kapt)

### Local Storage
- androidx.datastore:datastore-preferences
- androidx.room:room-runtime
- androidx.room:room-ktx

### Testing
- junit:junit
- androidx.compose.ui:ui-test-junit4

## Next Steps

1. **Implement Screen Layouts**: Replace placeholder composables with actual UI
2. **Add ViewModels**: MVVM architecture for state management
3. **Implement Repositories**: Data access layer between UI and API
4. **Add Database**: Room for caching programs and workouts
5. **Error Handling**: Global error handling and retry logic
6. **Authentication Flow**: Login/registration UI and token refresh
7. **Image Assets**: Add app icons and launcher images

## Build Commands

```bash
# Build debug APK
./gradlew build

# Run on emulator
./gradlew installDebug
```

## Architecture Notes

- **UI Framework**: Jetpack Compose (100% modern)
- **DI**: Hilt for dependency injection
- **Networking**: Retrofit + Moshi
- **Storage**: DataStore (Preferences) for tokens, Room for data
- **Navigation**: Compose Navigation
- **Async**: Kotlin Coroutines via suspend functions

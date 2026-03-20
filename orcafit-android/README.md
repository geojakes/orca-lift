# OrcaFit Android Application

Mobile client for OrcaFit - AI-powered weightlifting program generation using Liftosaur integration.

## Project Overview

OrcaFit Android is a native Kotlin/Compose application that provides:
- User authentication (register/login)
- AI-powered program generation with multi-agent deliberation
- Program browsing and management
- Live workout tracking and logging
- Workout history and personal records
- Exercise library reference

## Technology Stack

### Build & Android Framework
- **Kotlin 1.9.22** - Modern Kotlin language
- **Android 14** (Target SDK 34) - Latest Android features
- **Gradle 8.2** - Build system with KTS configuration

### UI Framework
- **Jetpack Compose** - Modern declarative UI framework
- **Material 3** - Latest Material design system
- **Compose Navigation** - Type-safe navigation

### Architecture & Patterns
- **MVVM** (future) - ViewModel-based architecture
- **Hilt** - Dependency injection
- **Repository Pattern** - Data access abstraction
- **Clean Architecture** - Separation of concerns

### Data & Networking
- **Retrofit 2.9** - HTTP client
- **Moshi** - JSON serialization/deserialization
- **OkHttp 4.12** - HTTP interceptors and logging
- **DataStore** - Secure token storage
- **Room** (optional) - Local caching

### Async & Concurrency
- **Kotlin Coroutines** - Asynchronous operations
- **Flow** - Reactive data streams

## Project Structure

```
orcafit-android/
├── build.gradle.kts              # Root build configuration
├── settings.gradle.kts           # Module configuration
├── gradle.properties             # Gradle settings
├── README.md                     # This file
├── PROJECT_STRUCTURE.md          # Detailed structure documentation
│
└── app/
    ├── build.gradle.kts          # App module dependencies
    └── src/main/
        ├── AndroidManifest.xml
        ├── java/com/orcafit/
        │   ├── MainActivity.kt
        │   ├── OrcaFitApp.kt
        │   ├── di/               # Dependency injection
        │   ├── data/             # API & local storage
        │   └── ui/               # UI components & screens
        └── res/                  # Resources
```

For detailed structure documentation, see [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)

## File Statistics

- **Total files**: 28
- **Kotlin source files**: 20
- **Gradle configuration files**: 4
- **Resource/XML files**: 4

## Key Components

### Networking Layer
- **OrcaFitApi.kt** - Retrofit interface with complete API coverage
- **ApiModels.kt** - 30+ Moshi-annotated data classes
- **AuthInterceptor.kt** - Automatic bearer token injection
- **TokenManager.kt** - Secure token persistence via DataStore

### UI Components
- **Theme** - OrcaFit brand colors (deep green + teal) with dark mode support
- **Navigation** - 9 main routes with type-safe navigation
- **Screens** - Placeholder implementations for all major features

### Application Entry
- **OrcaFitApp.kt** - Hilt-annotated Application class
- **MainActivity.kt** - Compose-based main activity
- **AppModule.kt** - Central dependency injection setup

## Dependencies Included

### Core Android
```
androidx.core:core-ktx:1.12.0
androidx.lifecycle:lifecycle-runtime-ktx:2.7.0
androidx.activity:activity-compose:1.8.2
```

### Compose UI
```
androidx.compose.ui:ui (from BOM 2024.01.00)
androidx.compose.material3:material3
androidx.compose.material:material-icons-extended
```

### Networking
```
com.squareup.retrofit2:retrofit:2.9.0
com.squareup.moshi:moshi-kotlin:1.15.0
com.squareup.okhttp3:logging-interceptor:4.12.0
```

### DI & Storage
```
com.google.dagger:hilt-android:2.50
androidx.datastore:datastore-preferences:1.0.0
androidx.room:room-runtime:2.6.1
```

## Getting Started

### Prerequisites
- Android Studio (latest)
- JDK 17+
- Android SDK 34+

### Build & Run
```bash
# Sync Gradle files
./gradlew sync

# Build debug APK
./gradlew build

# Install on emulator/device
./gradlew installDebug

# Run unit tests
./gradlew test
```

### Development Commands
```bash
# Clean build
./gradlew clean build

# Build release APK
./gradlew assembleRelease

# Run linter/formatter
./gradlew spotlessApply  # (when added)

# Generate API documentation
./gradlew dokka  # (when added)
```

## API Integration

The app connects to the OrcaFit backend at `http://10.0.2.2:8000` (Android emulator localhost).

### Key Endpoints

**Authentication**
- `POST /api/v1/auth/register` - Create account
- `POST /api/v1/auth/login` - Login & get tokens
- `GET /api/v1/auth/me` - Get current user

**Programs**
- `POST /api/v1/programs/generate` - Start AI generation
- `GET /api/v1/programs/generate/{jobId}/status` - Check generation status
- `GET /api/v1/programs` - List user's programs
- `GET /api/v1/programs/{id}` - Get program details
- `POST /api/v1/programs/{id}/activate` - Activate program

**Workouts**
- `POST /api/v1/workouts/start` - Begin workout session
- `GET /api/v1/workouts/active` - Get current workout
- `PUT /api/v1/workouts/{id}/log` - Log set results
- `POST /api/v1/workouts/{id}/complete` - End workout
- `GET /api/v1/workouts` - Get workout history

**Exercises**
- `GET /api/v1/exercises` - Browse exercise library

**Stats**
- `GET /api/v1/profile/stats` - Get user statistics

## Configuration

### Build Configuration
Located in `app/build.gradle.kts`:
- Application ID: `com.orcafit`
- Min SDK: 26 (Android 8.0)
- Target SDK: 34 (Android 14)
- Version: 0.1.0

### API Configuration
Located in `app/build.gradle.kts` (buildConfigField):
- Base URL: `http://10.0.2.2:8000` (for emulator)
- Can be overridden for production at build time

## Authentication Flow

1. User launches app → LoginScreen
2. Credentials sent to `/api/v1/auth/login`
3. Tokens stored in DataStore via TokenManager
4. AuthInterceptor adds Bearer token to all requests
5. On success → Navigate to HomeScreen
6. Token refresh handled on 401 responses (future)

## Next Development Steps

1. **Implement UI Screens**
   - Design comprehensive layouts for each screen
   - Add form validation and error handling
   - Implement loading states and transitions

2. **Add ViewModels**
   - Create MVVM ViewModels for each screen
   - Implement state management with Flow
   - Add repository layer for data access

3. **Error Handling**
   - Global error handler
   - Retry logic with exponential backoff
   - User-friendly error messages

4. **Local Caching**
   - Room database for programs and workouts
   - Offline support
   - Sync on reconnection

5. **Advanced Features**
   - Real-time notification updates
   - Biometric authentication
   - Data export/import
   - Integration with fitness wearables

## Architecture Decisions

### Why Jetpack Compose?
- Modern, declarative UI framework
- Type-safe with hot reloading
- Better testability
- Future-proof for Android development

### Why Hilt?
- Compile-time safety
- Reduces boilerplate code
- Excellent Compose integration
- Standard in modern Android apps

### Why DataStore?
- Replaces SharedPreferences
- Type-safe
- Coroutine-based
- Better encryption support

### Why Moshi?
- Lightweight JSON adapter
- Kotlin support with code generation
- Better null-safety than Gson
- Faster serialization

## Known Limitations

- Placeholder screen implementations (UI only)
- No offline support yet
- No token refresh implementation
- No biometric authentication
- No push notifications

## Contributing

1. Follow Kotlin style guide
2. Use meaningful commit messages
3. Test new features
4. Document complex logic
5. Keep dependencies updated

## License

Part of the OrcaFit project. See parent project license.

## Support

For issues or questions about the Android app, see the main OrcaFit project documentation.

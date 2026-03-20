# OrcaFit Android - Jetpack Compose Screens Implementation

## Overview
This document outlines the Jetpack Compose UI implementation for the OrcaFit Android application. All screens include corresponding ViewModels with state management using Kotlin Flow.

## Directory Structure

```
app/src/main/java/com/orcafit/ui/screens/
├── auth/
│   ├── LoginViewModel.kt
│   └── LoginScreen.kt
├── home/
│   ├── HomeViewModel.kt
│   └── HomeScreen.kt
├── generate/
│   ├── GenerateViewModel.kt
│   └── GenerateScreen.kt
├── programs/
│   ├── ProgramViewModel.kt
│   ├── ProgramListScreen.kt
│   └── ProgramDetailScreen.kt
├── workout/
│   ├── WorkoutViewModel.kt
│   ├── ActiveWorkoutScreen.kt
│   └── WorkoutSummaryScreen.kt
├── history/
│   ├── HistoryViewModel.kt
│   └── HistoryScreen.kt
└── exercises/
    ├── ExerciseViewModel.kt
    └── ExerciseLibraryScreen.kt
```

## Screen Details

### 1. Authentication (auth/)

**LoginViewModel.kt**
- Manages login and registration state
- Validates email/password input
- Handles authentication API calls
- Stores tokens via TokenManager

**LoginScreen.kt**
- Toggle between login and registration modes
- Animated visibility for name field
- Password visibility toggle
- Error display and loading states

### 2. Home (home/)

**HomeViewModel.kt**
- Loads user dashboard data on init
- Fetches user profile, stats, and active workout status
- Displays total workouts and volume metrics

**HomeScreen.kt**
- Stats cards showing workout count and total volume
- Active workout banner with continuation option
- Quick action cards for main features
- TopAppBar with personalized greeting

### 3. Generate Program (generate/)

**GenerateViewModel.kt**
- Manages program generation workflow
- Polls for generation job completion
- Validates goal input
- Handles days/week and weeks constraints (2-7, 1-12)

**GenerateScreen.kt**
- Text area for fitness goals input
- Adjustable parameters (days/week, weeks)
- Progress display during generation
- Error handling and loading states

### 4. Programs (programs/)

**ProgramViewModel.kt**
- Two separate ViewModels: ProgramListViewModel and ProgramDetailViewModel
- List: Loads all user programs
- Detail: Loads specific program with activation capability

**ProgramListScreen.kt**
- Grid of user's programs
- Program name, duration, and description
- Empty state when no programs exist

**ProgramDetailScreen.kt**
- Detailed program structure with week and day breakdowns
- Deload week indicators
- Exercise lists with set counts
- Floating action button to activate/start workout

### 5. Active Workout (workout/)

**WorkoutViewModel.kt**
- Loads active workout session
- Manages elapsed time timer
- Manages rest period timer (90 seconds default)
- Logs individual sets with weight, reps, RPE
- Handles workout completion
- Calculates completed workout summary

**ActiveWorkoutScreen.kt**
- Displays current exercise with set tracking
- Set input fields (weight, reps, RPE)
- Rest timer with skip option
- Logged sets display
- Elapsed workout time in TopAppBar
- Finish button to complete workout

**WorkoutSummaryScreen.kt**
- Success message with checkmark icon
- Return to home button

### 6. History (history/)

**HistoryViewModel.kt**
- Loads past workouts on initialization
- Displays list of completed workouts

**HistoryScreen.kt**
- List of past workouts
- Displays duration, exercise count, and total volume
- Completion date
- Empty state message

### 7. Exercise Library (exercises/)

**ExerciseViewModel.kt**
- Filters exercises by category and search query
- Reactive search with debouncing via viewModelScope
- Categories: All, Resistance, Cardio, Plyometric

**ExerciseLibraryScreen.kt**
- Search bar with leading search icon
- Horizontal scrolling filter chips
- Exercise cards with name, category, muscle groups, and equipment
- Loading and empty states

## State Management

All ViewModels use:
- **MutableStateFlow** for mutable state
- **StateFlow** for read-only state exposure
- **collectAsState()** Compose integration
- Proper scope management with viewModelScope
- Cancellation of coroutines in onCleared()

## Key Features

1. **Hilt Dependency Injection**
   - All ViewModels use @HiltViewModel annotation
   - SavedStateHandle for navigation arguments
   - Proper scope management

2. **Material Design 3**
   - TopAppBar with various configurations
   - Card components for content grouping
   - Buttons, TextButtons, ExtendedFloatingActionButton
   - Loading indicators and progress displays

3. **Forms & Input**
   - OutlinedTextField components
   - Keyboard options (email, password, number, decimal)
   - Visual password toggle
   - Numeric range constraints with +/- buttons

4. **Timers**
   - Elapsed workout timer (hours:minutes:seconds)
   - Rest period countdown timer
   - Proper cancellation on screen close

5. **Navigation Integration**
   - Callback parameters for navigation
   - LaunchedEffect for navigation triggers
   - Proper back handling

## API Integration

All screens integrate with OrcaFitApi for:
- User authentication
- Program generation and management
- Workout session management
- Set logging and tracking
- User stats and history
- Exercise library data

## Future Enhancements

- Add haptic feedback on button presses
- Implement sound notifications for timers
- Add animations for state transitions
- Offline support with local caching
- Dark mode theme support

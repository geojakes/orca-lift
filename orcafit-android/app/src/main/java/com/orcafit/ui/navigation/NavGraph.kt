package com.orcafit.ui.navigation

import androidx.compose.runtime.Composable
import androidx.navigation.NavHostController
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument
import com.orcafit.ui.screens.auth.LoginScreen
import com.orcafit.ui.screens.home.HomeScreen
import com.orcafit.ui.screens.generate.GenerateScreen
import com.orcafit.ui.screens.programs.ProgramListScreen
import com.orcafit.ui.screens.programs.ProgramDetailScreen
import com.orcafit.ui.screens.workout.ActiveWorkoutScreen
import com.orcafit.ui.screens.workout.WorkoutSummaryScreen
import com.orcafit.ui.screens.history.HistoryScreen
import com.orcafit.ui.screens.exercises.ExerciseLibraryScreen

object Routes {
    const val LOGIN = "login"
    const val HOME = "home"
    const val GENERATE = "generate"
    const val PROGRAMS = "programs"
    const val PROGRAM_DETAIL = "programs/{programId}"
    const val ACTIVE_WORKOUT = "workout/active"
    const val WORKOUT_SUMMARY = "workout/summary/{workoutId}"
    const val HISTORY = "history"
    const val EXERCISES = "exercises"
}

@Composable
fun OrcaFitNavHost(
    navController: NavHostController = rememberNavController(),
    startDestination: String = Routes.LOGIN
) {
    NavHost(navController = navController, startDestination = startDestination) {
        composable(Routes.LOGIN) {
            LoginScreen(
                onLoginSuccess = {
                    navController.navigate(Routes.HOME) {
                        popUpTo(Routes.LOGIN) { inclusive = true }
                    }
                }
            )
        }
        composable(Routes.HOME) {
            HomeScreen(
                onNavigateToGenerate = { navController.navigate(Routes.GENERATE) },
                onNavigateToPrograms = { navController.navigate(Routes.PROGRAMS) },
                onNavigateToWorkout = { navController.navigate(Routes.ACTIVE_WORKOUT) },
                onNavigateToHistory = { navController.navigate(Routes.HISTORY) },
                onNavigateToExercises = { navController.navigate(Routes.EXERCISES) },
            )
        }
        composable(Routes.GENERATE) {
            GenerateScreen(
                onBack = { navController.popBackStack() },
                onProgramGenerated = { programId ->
                    navController.navigate("programs/$programId")
                }
            )
        }
        composable(Routes.PROGRAMS) {
            ProgramListScreen(
                onBack = { navController.popBackStack() },
                onProgramClick = { id -> navController.navigate("programs/$id") }
            )
        }
        composable(
            Routes.PROGRAM_DETAIL,
            arguments = listOf(navArgument("programId") { type = NavType.IntType })
        ) {
            ProgramDetailScreen(
                onBack = { navController.popBackStack() },
                onStartWorkout = { navController.navigate(Routes.ACTIVE_WORKOUT) }
            )
        }
        composable(Routes.ACTIVE_WORKOUT) {
            ActiveWorkoutScreen(
                onBack = { navController.popBackStack() },
                onWorkoutComplete = { workoutId ->
                    navController.navigate("workout/summary/$workoutId") {
                        popUpTo(Routes.HOME)
                    }
                }
            )
        }
        composable(
            Routes.WORKOUT_SUMMARY,
            arguments = listOf(navArgument("workoutId") { type = NavType.IntType })
        ) {
            WorkoutSummaryScreen(
                onDone = {
                    navController.navigate(Routes.HOME) {
                        popUpTo(Routes.HOME) { inclusive = true }
                    }
                }
            )
        }
        composable(Routes.HISTORY) {
            HistoryScreen(onBack = { navController.popBackStack() })
        }
        composable(Routes.EXERCISES) {
            ExerciseLibraryScreen(onBack = { navController.popBackStack() })
        }
    }
}

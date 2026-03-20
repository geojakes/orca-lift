package com.orcafit.ui.screens.workout

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.itemsIndexed
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ActiveWorkoutScreen(
    onBack: () -> Unit,
    onWorkoutComplete: (Int) -> Unit,
    viewModel: WorkoutViewModel = hiltViewModel(),
) {
    val uiState by viewModel.uiState.collectAsState()

    LaunchedEffect(uiState.completedWorkoutId) {
        uiState.completedWorkoutId?.let { onWorkoutComplete(it) }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Column {
                        Text(uiState.workout?.dayName ?: "Workout")
                        Text(formatTime(uiState.elapsedSeconds), style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    }
                },
                navigationIcon = { IconButton(onClick = onBack) { Icon(Icons.Default.ArrowBack, "Back") } },
                actions = {
                    TextButton(onClick = viewModel::completeWorkout, enabled = !uiState.isSaving) {
                        Text("Finish", color = MaterialTheme.colorScheme.primary)
                    }
                },
            )
        }
    ) { padding ->
        when {
            uiState.isLoading -> Box(Modifier.fillMaxSize().padding(padding), contentAlignment = Alignment.Center) { CircularProgressIndicator() }
            uiState.error != null && uiState.workout == null -> Box(Modifier.fillMaxSize().padding(padding), contentAlignment = Alignment.Center) {
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Text(uiState.error!!, style = MaterialTheme.typography.bodyLarge)
                    Spacer(Modifier.height(16.dp))
                    Button(onClick = onBack) { Text("Go Back") }
                }
            }
            else -> {
                val workout = uiState.workout ?: return@Scaffold
                val exercises = workout.exercises

                LazyColumn(modifier = Modifier.fillMaxSize().padding(padding), contentPadding = PaddingValues(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    // Rest timer
                    if (uiState.isRestTimerRunning) {
                        item {
                            Card(colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.secondaryContainer)) {
                                Row(Modifier.padding(16.dp).fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
                                    Icon(Icons.Default.Timer, null)
                                    Spacer(Modifier.width(12.dp))
                                    Text("Rest: ${uiState.restTimerSeconds}s", style = MaterialTheme.typography.titleMedium, modifier = Modifier.weight(1f))
                                    TextButton(onClick = viewModel::skipRest) { Text("Skip") }
                                }
                            }
                        }
                    }

                    // Exercise list
                    itemsIndexed(exercises) { index, exercise ->
                        val isActive = index == uiState.currentExerciseIndex
                        val setsLogged = exercise.loggedSets.size
                        val setsTarget = exercise.targetSets

                        Card(
                            onClick = { viewModel.setCurrentExercise(index) },
                            modifier = Modifier.fillMaxWidth(),
                            colors = if (isActive) CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.primaryContainer) else CardDefaults.cardColors(),
                        ) {
                            Column(Modifier.padding(12.dp)) {
                                Row(verticalAlignment = Alignment.CenterVertically) {
                                    Text(exercise.exerciseName, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold, modifier = Modifier.weight(1f))
                                    Text("$setsLogged/$setsTarget", style = MaterialTheme.typography.bodyMedium, color = if (setsLogged >= setsTarget) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.onSurfaceVariant)
                                }

                                // Show logged sets
                                exercise.loggedSets.forEach { set ->
                                    val info = buildString {
                                        if (set.weightKg != null) append("${set.weightKg}kg ")
                                        if (set.reps != null) append("x ${set.reps} ")
                                        if (set.rpe != null) append("@${set.rpe} ")
                                        if (set.durationSeconds != null) append("${set.durationSeconds}s ")
                                    }
                                    Text("  Set ${set.setNumber}: $info", style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                                }

                                // Input row for active exercise
                                if (isActive) {
                                    Spacer(Modifier.height(8.dp))
                                    Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp), verticalAlignment = Alignment.CenterVertically) {
                                        OutlinedTextField(
                                            value = uiState.inputWeight,
                                            onValueChange = viewModel::updateInputWeight,
                                            label = { Text("kg") },
                                            modifier = Modifier.weight(1f),
                                            singleLine = true,
                                            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal),
                                        )
                                        OutlinedTextField(
                                            value = uiState.inputReps,
                                            onValueChange = viewModel::updateInputReps,
                                            label = { Text("Reps") },
                                            modifier = Modifier.weight(1f),
                                            singleLine = true,
                                            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                                        )
                                        OutlinedTextField(
                                            value = uiState.inputRpe,
                                            onValueChange = viewModel::updateInputRpe,
                                            label = { Text("RPE") },
                                            modifier = Modifier.weight(0.7f),
                                            singleLine = true,
                                            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal),
                                        )
                                    }
                                    Spacer(Modifier.height(8.dp))
                                    Button(onClick = viewModel::logSet, modifier = Modifier.fillMaxWidth(), enabled = !uiState.isSaving) {
                                        Text("Log Set ${setsLogged + 1}")
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

private fun formatTime(seconds: Int): String {
    val h = seconds / 3600
    val m = (seconds % 3600) / 60
    val s = seconds % 60
    return if (h > 0) "%d:%02d:%02d".format(h, m, s) else "%02d:%02d".format(m, s)
}

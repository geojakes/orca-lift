package com.orcafit.ui.screens.workout

import androidx.compose.animation.animateColorAsState
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.itemsIndexed
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
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
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Icon(
                                Icons.Default.Timer, "Elapsed time",
                                modifier = Modifier.size(14.dp),
                                tint = MaterialTheme.colorScheme.onSurfaceVariant,
                            )
                            Spacer(Modifier.width(4.dp))
                            Text(
                                formatTime(uiState.elapsedSeconds),
                                style = MaterialTheme.typography.bodySmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant,
                            )
                            // Mini progress
                            uiState.workout?.let { workout ->
                                val totalSets = workout.exercises.sumOf { it.targetSets }
                                val completedSets = workout.exercises.sumOf { it.loggedSets.size }
                                if (totalSets > 0) {
                                    Spacer(Modifier.width(12.dp))
                                    Text(
                                        "$completedSets/$totalSets sets",
                                        style = MaterialTheme.typography.labelSmall,
                                        color = MaterialTheme.colorScheme.primary,
                                    )
                                }
                            }
                        }
                    }
                },
                navigationIcon = { IconButton(onClick = onBack) { Icon(Icons.Default.ArrowBack, "Back") } },
                actions = {
                    FilledTonalButton(
                        onClick = viewModel::completeWorkout,
                        enabled = !uiState.isSaving,
                        shape = RoundedCornerShape(8.dp),
                    ) {
                        Icon(Icons.Default.Check, "Finish workout", modifier = Modifier.size(16.dp))
                        Spacer(Modifier.width(4.dp))
                        Text("Finish")
                    }
                },
            )
        }
    ) { padding ->
        when {
            uiState.isLoading -> Box(
                Modifier.fillMaxSize().padding(padding),
                contentAlignment = Alignment.Center,
            ) { CircularProgressIndicator() }

            uiState.error != null && uiState.workout == null -> Box(
                Modifier.fillMaxSize().padding(padding),
                contentAlignment = Alignment.Center,
            ) {
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Text(uiState.error!!, style = MaterialTheme.typography.bodyLarge)
                    Spacer(Modifier.height(16.dp))
                    Button(onClick = onBack) { Text("Go Back") }
                }
            }

            else -> {
                val workout = uiState.workout ?: return@Scaffold
                val exercises = workout.exercises

                LazyColumn(
                    modifier = Modifier.fillMaxSize().padding(padding),
                    contentPadding = PaddingValues(16.dp),
                    verticalArrangement = Arrangement.spacedBy(10.dp),
                ) {
                    // Rest timer
                    if (uiState.isRestTimerRunning) {
                        item {
                            Card(
                                colors = CardDefaults.cardColors(
                                    containerColor = MaterialTheme.colorScheme.secondaryContainer,
                                ),
                                shape = RoundedCornerShape(16.dp),
                            ) {
                                Column(
                                    modifier = Modifier.padding(20.dp).fillMaxWidth(),
                                    horizontalAlignment = Alignment.CenterHorizontally,
                                ) {
                                    // Circular rest timer
                                    Box(contentAlignment = Alignment.Center) {
                                        CircularProgressIndicator(
                                            progress = { uiState.restTimerSeconds / 90f },
                                            modifier = Modifier.size(80.dp),
                                            strokeWidth = 6.dp,
                                            color = MaterialTheme.colorScheme.secondary,
                                            trackColor = MaterialTheme.colorScheme.secondaryContainer,
                                        )
                                        Text(
                                            "${uiState.restTimerSeconds}s",
                                            style = MaterialTheme.typography.headlineMedium,
                                            fontWeight = FontWeight.Bold,
                                            color = MaterialTheme.colorScheme.onSecondaryContainer,
                                        )
                                    }
                                    Spacer(Modifier.height(8.dp))
                                    Text(
                                        "Rest",
                                        style = MaterialTheme.typography.labelLarge,
                                        color = MaterialTheme.colorScheme.onSecondaryContainer,
                                    )
                                    Spacer(Modifier.height(12.dp))
                                    TextButton(onClick = viewModel::skipRest) {
                                        Icon(Icons.Default.SkipNext, "Skip rest", modifier = Modifier.size(18.dp))
                                        Spacer(Modifier.width(4.dp))
                                        Text("Skip Rest")
                                    }
                                }
                            }
                        }
                    }

                    // Exercise list
                    itemsIndexed(exercises) { index, exercise ->
                        val isActive = index == uiState.currentExerciseIndex
                        val setsLogged = exercise.loggedSets.size
                        val setsTarget = exercise.targetSets
                        val isComplete = setsLogged >= setsTarget

                        val cardColor by animateColorAsState(
                            targetValue = when {
                                isActive -> MaterialTheme.colorScheme.primaryContainer
                                isComplete -> MaterialTheme.colorScheme.surfaceVariant
                                else -> MaterialTheme.colorScheme.surface
                            },
                            label = "cardColor",
                        )

                        Card(
                            onClick = { viewModel.setCurrentExercise(index) },
                            modifier = Modifier
                                .fillMaxWidth()
                                .alpha(if (isComplete && !isActive) 0.7f else 1f),
                            colors = CardDefaults.cardColors(containerColor = cardColor),
                            shape = RoundedCornerShape(12.dp),
                        ) {
                            Column(Modifier.padding(14.dp)) {
                                Row(verticalAlignment = Alignment.CenterVertically) {
                                    // Completion indicator
                                    if (isComplete) {
                                        Icon(
                                            Icons.Default.CheckCircle, "Exercise complete",
                                            modifier = Modifier.size(20.dp),
                                            tint = MaterialTheme.colorScheme.primary,
                                        )
                                        Spacer(Modifier.width(8.dp))
                                    }
                                    Text(
                                        exercise.exerciseName,
                                        style = MaterialTheme.typography.titleMedium,
                                        fontWeight = FontWeight.Bold,
                                        modifier = Modifier.weight(1f),
                                    )
                                    // Set progress dots
                                    Row(horizontalArrangement = Arrangement.spacedBy(3.dp)) {
                                        repeat(setsTarget) { i ->
                                            Box(
                                                modifier = Modifier
                                                    .size(8.dp)
                                                    .clip(CircleShape)
                                                    .background(
                                                        if (i < setsLogged) MaterialTheme.colorScheme.primary
                                                        else MaterialTheme.colorScheme.outlineVariant
                                                    ),
                                            )
                                        }
                                    }
                                    Spacer(Modifier.width(8.dp))
                                    Text(
                                        "$setsLogged/$setsTarget",
                                        style = MaterialTheme.typography.labelMedium,
                                        color = if (isComplete) MaterialTheme.colorScheme.primary
                                        else MaterialTheme.colorScheme.onSurfaceVariant,
                                    )
                                }

                                // Show logged sets
                                if (exercise.loggedSets.isNotEmpty()) {
                                    Spacer(Modifier.height(6.dp))
                                    exercise.loggedSets.forEach { set ->
                                        val info = buildString {
                                            if (set.weightKg != null) append("${set.weightKg}kg")
                                            if (set.reps != null) append(" x ${set.reps}")
                                            if (set.rpe != null) append(" @${set.rpe}")
                                            if (set.durationSeconds != null) append(" ${set.durationSeconds}s")
                                        }
                                        Text(
                                            "Set ${set.setNumber}: $info",
                                            style = MaterialTheme.typography.bodySmall,
                                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                                            modifier = Modifier.padding(start = if (isComplete) 28.dp else 0.dp),
                                        )
                                    }
                                }

                                // Input row for active exercise
                                if (isActive) {
                                    Spacer(Modifier.height(12.dp))
                                    HorizontalDivider(color = MaterialTheme.colorScheme.outlineVariant.copy(alpha = 0.5f))
                                    Spacer(Modifier.height(12.dp))

                                    Row(
                                        Modifier.fillMaxWidth(),
                                        horizontalArrangement = Arrangement.spacedBy(8.dp),
                                        verticalAlignment = Alignment.CenterVertically,
                                    ) {
                                        TextField(
                                            value = uiState.inputWeight,
                                            onValueChange = viewModel::updateInputWeight,
                                            label = { Text("Weight") },
                                            suffix = { Text("kg", style = MaterialTheme.typography.labelSmall) },
                                            modifier = Modifier.weight(1f),
                                            singleLine = true,
                                            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal),
                                            shape = RoundedCornerShape(8.dp),
                                            colors = TextFieldDefaults.colors(
                                                unfocusedIndicatorColor = MaterialTheme.colorScheme.outline.copy(alpha = 0f),
                                                focusedIndicatorColor = MaterialTheme.colorScheme.outline.copy(alpha = 0f),
                                            ),
                                        )
                                        TextField(
                                            value = uiState.inputReps,
                                            onValueChange = viewModel::updateInputReps,
                                            label = { Text("Reps") },
                                            modifier = Modifier.weight(1f),
                                            singleLine = true,
                                            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                                            shape = RoundedCornerShape(8.dp),
                                            colors = TextFieldDefaults.colors(
                                                unfocusedIndicatorColor = MaterialTheme.colorScheme.outline.copy(alpha = 0f),
                                                focusedIndicatorColor = MaterialTheme.colorScheme.outline.copy(alpha = 0f),
                                            ),
                                        )
                                        TextField(
                                            value = uiState.inputRpe,
                                            onValueChange = viewModel::updateInputRpe,
                                            label = { Text("RPE") },
                                            modifier = Modifier.weight(0.7f),
                                            singleLine = true,
                                            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal),
                                            shape = RoundedCornerShape(8.dp),
                                            colors = TextFieldDefaults.colors(
                                                unfocusedIndicatorColor = MaterialTheme.colorScheme.outline.copy(alpha = 0f),
                                                focusedIndicatorColor = MaterialTheme.colorScheme.outline.copy(alpha = 0f),
                                            ),
                                        )
                                    }
                                    Spacer(Modifier.height(10.dp))
                                    Button(
                                        onClick = viewModel::logSet,
                                        modifier = Modifier.fillMaxWidth(),
                                        enabled = !uiState.isSaving,
                                        shape = RoundedCornerShape(10.dp),
                                    ) {
                                        Icon(Icons.Default.Add, "Log set", modifier = Modifier.size(18.dp))
                                        Spacer(Modifier.width(6.dp))
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

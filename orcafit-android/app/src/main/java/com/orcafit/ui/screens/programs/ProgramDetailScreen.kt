package com.orcafit.ui.screens.programs

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ProgramDetailScreen(
    onBack: () -> Unit,
    onStartWorkout: () -> Unit,
    viewModel: ProgramDetailViewModel = hiltViewModel(),
) {
    val uiState by viewModel.uiState.collectAsState()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text(uiState.program?.program?.name ?: "Program") },
                navigationIcon = { IconButton(onClick = onBack) { Icon(Icons.Default.ArrowBack, "Back") } },
            )
        },
        floatingActionButton = {
            if (uiState.program != null) {
                ExtendedFloatingActionButton(
                    onClick = {
                        if (!uiState.activated) viewModel.activate()
                        else onStartWorkout()
                    },
                    icon = { Icon(Icons.Default.PlayArrow, null) },
                    text = { Text(if (uiState.activated) "Start Workout" else "Activate Program") },
                )
            }
        }
    ) { padding ->
        when {
            uiState.isLoading -> Box(Modifier.fillMaxSize().padding(padding), contentAlignment = Alignment.Center) { CircularProgressIndicator() }
            uiState.error != null -> Box(Modifier.fillMaxSize().padding(padding), contentAlignment = Alignment.Center) { Text(uiState.error!!) }
            else -> {
                val programData = uiState.program?.program ?: return@Scaffold
                LazyColumn(modifier = Modifier.fillMaxSize().padding(padding).padding(16.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
                    item {
                        Text(programData.description, style = MaterialTheme.typography.bodyLarge)
                        Spacer(Modifier.height(4.dp))
                        Text("${programData.durationWeeks} weeks \u2022 ${programData.daysPerWeek} days/week", style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    }
                    programData.weeks.forEach { week ->
                        item {
                            Text("Week ${week.weekNumber}${if (week.isDeload) " (Deload)" else ""}", style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Bold, modifier = Modifier.padding(top = 8.dp))
                        }
                        week.days.forEach { day ->
                            item {
                                Card(modifier = Modifier.fillMaxWidth()) {
                                    Column(Modifier.padding(12.dp)) {
                                        Text("${day.name}${if (day.focus.isNotBlank()) " - ${day.focus}" else ""}", style = MaterialTheme.typography.titleMedium)
                                        Spacer(Modifier.height(8.dp))
                                        day.exercises.forEach { ex ->
                                            val setsInfo = "${ex.sets.size} sets"
                                            Text("\u2022 ${ex.exerciseName} \u2014 $setsInfo", style = MaterialTheme.typography.bodyMedium)
                                        }
                                    }
                                }
                            }
                        }
                    }
                    item { Spacer(Modifier.height(80.dp)) } // FAB clearance
                }
            }
        }
    }
}

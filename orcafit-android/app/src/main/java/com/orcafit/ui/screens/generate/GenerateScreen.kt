package com.orcafit.ui.screens.generate

import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.AutoAwesome
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun GenerateScreen(
    onBack: () -> Unit,
    onProgramGenerated: (Int) -> Unit,
    viewModel: GenerateViewModel = hiltViewModel(),
) {
    val uiState by viewModel.uiState.collectAsState()

    LaunchedEffect(uiState.generatedProgramId) {
        uiState.generatedProgramId?.let { onProgramGenerated(it) }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Generate Program") },
                navigationIcon = { IconButton(onClick = onBack) { Icon(Icons.Default.ArrowBack, "Back") } },
            )
        }
    ) { padding ->
        Column(
            modifier = Modifier.fillMaxSize().padding(padding).padding(24.dp),
            verticalArrangement = Arrangement.spacedBy(20.dp),
        ) {
            Icon(Icons.Default.AutoAwesome, null, Modifier.size(48.dp).align(Alignment.CenterHorizontally), tint = MaterialTheme.colorScheme.primary)
            Text("Describe your fitness goals and our AI agents will design a personalized program.", style = MaterialTheme.typography.bodyLarge)

            OutlinedTextField(
                value = uiState.goals,
                onValueChange = viewModel::updateGoals,
                label = { Text("Goals") },
                placeholder = { Text("e.g., Build strength, focus on upper body, 4 days/week") },
                modifier = Modifier.fillMaxWidth().height(120.dp),
                maxLines = 5,
            )

            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(16.dp)) {
                Column(Modifier.weight(1f)) {
                    Text("Days/week", style = MaterialTheme.typography.labelLarge)
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        IconButton(onClick = { viewModel.updateDays(uiState.daysPerWeek - 1) }) { Text("-", style = MaterialTheme.typography.titleLarge) }
                        Text("${uiState.daysPerWeek}", style = MaterialTheme.typography.headlineMedium, modifier = Modifier.padding(horizontal = 8.dp))
                        IconButton(onClick = { viewModel.updateDays(uiState.daysPerWeek + 1) }) { Text("+", style = MaterialTheme.typography.titleLarge) }
                    }
                }
                Column(Modifier.weight(1f)) {
                    Text("Weeks", style = MaterialTheme.typography.labelLarge)
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        IconButton(onClick = { viewModel.updateWeeks(uiState.weeks - 1) }) { Text("-", style = MaterialTheme.typography.titleLarge) }
                        Text("${uiState.weeks}", style = MaterialTheme.typography.headlineMedium, modifier = Modifier.padding(horizontal = 8.dp))
                        IconButton(onClick = { viewModel.updateWeeks(uiState.weeks + 1) }) { Text("+", style = MaterialTheme.typography.titleLarge) }
                    }
                }
            }

            if (uiState.error != null) {
                Text(uiState.error!!, color = MaterialTheme.colorScheme.error, style = MaterialTheme.typography.bodySmall)
            }

            if (uiState.isGenerating) {
                Column(horizontalAlignment = Alignment.CenterHorizontally, modifier = Modifier.fillMaxWidth()) {
                    CircularProgressIndicator()
                    Spacer(Modifier.height(8.dp))
                    Text(uiState.progress, style = MaterialTheme.typography.bodyMedium)
                }
            }

            Spacer(Modifier.weight(1f))

            Button(
                onClick = viewModel::generate,
                modifier = Modifier.fillMaxWidth().height(50.dp),
                enabled = !uiState.isGenerating,
            ) { Text("Generate Program") }
        }
    }
}

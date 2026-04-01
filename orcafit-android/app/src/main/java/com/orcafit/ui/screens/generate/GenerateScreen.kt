package com.orcafit.ui.screens.generate

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.tween
import androidx.compose.animation.fadeIn
import androidx.compose.animation.slideInVertically
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.AutoAwesome
import androidx.compose.material.icons.filled.Check
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.text.font.FontWeight
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
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .verticalScroll(rememberScrollState())
                .padding(24.dp),
            verticalArrangement = Arrangement.spacedBy(20.dp),
        ) {
            // Header
            Column(
                modifier = Modifier.fillMaxWidth(),
                horizontalAlignment = Alignment.CenterHorizontally,
            ) {
                Box(
                    modifier = Modifier
                        .size(64.dp)
                        .clip(CircleShape)
                        .background(
                            Brush.linearGradient(
                                colors = listOf(
                                    MaterialTheme.colorScheme.primary,
                                    MaterialTheme.colorScheme.tertiary,
                                )
                            )
                        ),
                    contentAlignment = Alignment.Center,
                ) {
                    Icon(
                        Icons.Default.AutoAwesome, "AI Generation",
                        modifier = Modifier.size(32.dp),
                        tint = MaterialTheme.colorScheme.onPrimary,
                    )
                }
                Spacer(Modifier.height(12.dp))
                Text(
                    "AI Program Generator",
                    style = MaterialTheme.typography.titleLarge,
                    fontWeight = FontWeight.Bold,
                )
                Text(
                    "Our AI agents will design your perfect program",
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }

            // Goals input
            OutlinedTextField(
                value = uiState.goals,
                onValueChange = viewModel::updateGoals,
                label = { Text("Goals") },
                placeholder = { Text("e.g., Build strength, focus on upper body, 4 days/week") },
                modifier = Modifier.fillMaxWidth().height(120.dp),
                maxLines = 5,
                shape = RoundedCornerShape(12.dp),
            )

            // Suggestion chips
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                val suggestions = listOf("Build strength", "Hypertrophy", "Lose fat", "Athletic")
                suggestions.forEach { suggestion ->
                    SuggestionChip(
                        onClick = {
                            val current = uiState.goals
                            val sep = if (current.isBlank()) "" else ", "
                            viewModel.updateGoals(current + sep + suggestion.lowercase())
                        },
                        label = { Text(suggestion, style = MaterialTheme.typography.labelSmall) },
                        shape = RoundedCornerShape(20.dp),
                    )
                }
            }

            // Days & Weeks controls
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(16.dp)) {
                NumberControl(
                    label = "Days/week",
                    hint = "3-6 recommended",
                    value = uiState.daysPerWeek,
                    onDecrease = { viewModel.updateDays(uiState.daysPerWeek - 1) },
                    onIncrease = { viewModel.updateDays(uiState.daysPerWeek + 1) },
                    modifier = Modifier.weight(1f),
                )
                NumberControl(
                    label = "Weeks",
                    hint = "4-6 typical",
                    value = uiState.weeks,
                    onDecrease = { viewModel.updateWeeks(uiState.weeks - 1) },
                    onIncrease = { viewModel.updateWeeks(uiState.weeks + 1) },
                    modifier = Modifier.weight(1f),
                )
            }

            if (uiState.error != null) {
                Card(
                    colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.errorContainer),
                ) {
                    Text(
                        uiState.error!!,
                        modifier = Modifier.padding(12.dp),
                        color = MaterialTheme.colorScheme.onErrorContainer,
                        style = MaterialTheme.typography.bodySmall,
                    )
                }
            }

            // Generation progress stepper
            AnimatedVisibility(
                visible = uiState.isGenerating,
                enter = fadeIn() + slideInVertically(),
            ) {
                GenerationStepper(progress = uiState.progress)
            }

            Spacer(Modifier.weight(1f))

            // Generate button
            Button(
                onClick = viewModel::generate,
                modifier = Modifier.fillMaxWidth().height(54.dp),
                enabled = !uiState.isGenerating,
                shape = RoundedCornerShape(12.dp),
            ) {
                Icon(Icons.Default.AutoAwesome, "Generate", modifier = Modifier.size(20.dp))
                Spacer(Modifier.width(8.dp))
                Text("Generate Program", style = MaterialTheme.typography.titleMedium)
            }
        }
    }
}

@Composable
private fun NumberControl(
    label: String,
    hint: String,
    value: Int,
    onDecrease: () -> Unit,
    onIncrease: () -> Unit,
    modifier: Modifier = Modifier,
) {
    Card(modifier = modifier) {
        Column(
            modifier = Modifier.padding(12.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            Text(label, style = MaterialTheme.typography.labelLarge)
            Row(verticalAlignment = Alignment.CenterVertically) {
                FilledIconButton(
                    onClick = onDecrease,
                    modifier = Modifier.size(36.dp),
                    colors = IconButtonDefaults.filledIconButtonColors(
                        containerColor = MaterialTheme.colorScheme.surfaceVariant,
                    ),
                ) { Text("-", style = MaterialTheme.typography.titleLarge) }
                Text(
                    "$value",
                    style = MaterialTheme.typography.headlineMedium,
                    fontWeight = FontWeight.Bold,
                    modifier = Modifier.padding(horizontal = 16.dp),
                )
                FilledIconButton(
                    onClick = onIncrease,
                    modifier = Modifier.size(36.dp),
                    colors = IconButtonDefaults.filledIconButtonColors(
                        containerColor = MaterialTheme.colorScheme.surfaceVariant,
                    ),
                ) { Text("+", style = MaterialTheme.typography.titleLarge) }
            }
            Text(hint, style = MaterialTheme.typography.labelSmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
        }
    }
}

@Composable
private fun GenerationStepper(progress: String) {
    val steps = listOf(
        "Analyzing profile",
        "Designing framework",
        "Expert consultation",
        "Building program",
    )

    // Determine current step from progress text
    val currentStep = when {
        progress.contains("build", ignoreCase = true) || progress.contains("generat", ignoreCase = true) -> 3
        progress.contains("consult", ignoreCase = true) || progress.contains("deliberat", ignoreCase = true) || progress.contains("specialist", ignoreCase = true) -> 2
        progress.contains("framework", ignoreCase = true) || progress.contains("design", ignoreCase = true) -> 1
        else -> 0
    }

    Card(
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant),
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            steps.forEachIndexed { index, step ->
                val isComplete = index < currentStep
                val isActive = index == currentStep
                val animatedAlpha by animateFloatAsState(
                    targetValue = if (isComplete || isActive) 1f else 0.4f,
                    animationSpec = tween(300),
                    label = "stepAlpha",
                )

                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    modifier = Modifier.padding(vertical = 4.dp),
                ) {
                    // Step indicator
                    Box(
                        modifier = Modifier
                            .size(28.dp)
                            .clip(CircleShape)
                            .background(
                                when {
                                    isComplete -> MaterialTheme.colorScheme.primary
                                    isActive -> MaterialTheme.colorScheme.tertiary
                                    else -> MaterialTheme.colorScheme.outline.copy(alpha = 0.3f)
                                }
                            ),
                        contentAlignment = Alignment.Center,
                    ) {
                        if (isComplete) {
                            Icon(
                                Icons.Default.Check, "Complete",
                                modifier = Modifier.size(16.dp),
                                tint = MaterialTheme.colorScheme.onPrimary,
                            )
                        } else {
                            Text(
                                "${index + 1}",
                                style = MaterialTheme.typography.labelSmall,
                                fontWeight = FontWeight.Bold,
                                color = if (isActive) MaterialTheme.colorScheme.onTertiary
                                else MaterialTheme.colorScheme.onSurface.copy(alpha = 0.5f),
                            )
                        }
                    }

                    Spacer(Modifier.width(12.dp))

                    Column {
                        Text(
                            step,
                            style = MaterialTheme.typography.bodyMedium,
                            fontWeight = if (isActive) FontWeight.SemiBold else FontWeight.Normal,
                            color = MaterialTheme.colorScheme.onSurface.copy(alpha = animatedAlpha),
                        )
                        if (isActive) {
                            Text(
                                progress,
                                style = MaterialTheme.typography.labelSmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant,
                            )
                        }
                    }
                }

                // Connecting line between steps
                if (index < steps.lastIndex) {
                    Box(
                        modifier = Modifier
                            .padding(start = 13.dp)
                            .width(2.dp)
                            .height(8.dp)
                            .background(
                                if (isComplete) MaterialTheme.colorScheme.primary.copy(alpha = 0.5f)
                                else MaterialTheme.colorScheme.outline.copy(alpha = 0.2f)
                            ),
                    )
                }
            }
        }
    }
}

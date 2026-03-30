package com.orcafit.ui.screens.workout

import androidx.compose.animation.core.InfiniteTransition
import androidx.compose.animation.core.LinearEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.scale
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import com.orcafit.ui.theme.GradientPrimaryEnd
import com.orcafit.ui.theme.GradientPrimaryStart
import com.orcafit.ui.theme.OrcaSuccess
import com.orcafit.ui.theme.OrcaWarning
import com.orcafit.ui.theme.WorkoutActive
import com.orcafit.ui.theme.WorkoutComplete

@Composable
fun WorkoutSummaryScreen(onDone: () -> Unit) {
    val infiniteTransition = rememberInfiniteTransition(label = "confetti")

    // Icon pulse animation
    var iconVisible by remember { mutableStateOf(false) }
    val iconScale by animateFloatAsState(
        targetValue = if (iconVisible) 1f else 0.5f,
        animationSpec = tween(durationMillis = 600),
        label = "iconPulse",
    )
    LaunchedEffect(Unit) { iconVisible = true }

    val motivationalQuotes = remember {
        listOf(
            "Every rep counts. You showed up and crushed it!",
            "Consistency beats perfection. Keep going!",
            "Stronger than yesterday, ready for tomorrow.",
            "You just invested in a better version of yourself.",
            "The only bad workout is the one that didn't happen.",
        )
    }
    val randomQuote = remember { motivationalQuotes.random() }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(
                Brush.verticalGradient(
                    colors = listOf(GradientPrimaryStart, GradientPrimaryEnd),
                )
            ),
    ) {
        // Confetti-style animated dots
        ConfettiOverlay(infiniteTransition)

        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(32.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center,
        ) {
            Icon(
                Icons.Default.CheckCircle,
                null,
                modifier = Modifier
                    .size(112.dp)
                    .scale(iconScale),
                tint = Color.White,
            )
            Spacer(Modifier.height(24.dp))
            Text(
                "Workout Complete!",
                style = MaterialTheme.typography.headlineLarge,
                fontWeight = FontWeight.Bold,
                textAlign = TextAlign.Center,
                color = Color.White,
            )
            Spacer(Modifier.height(16.dp))
            Text(
                "Great job! Your workout has been recorded.",
                style = MaterialTheme.typography.bodyLarge,
                textAlign = TextAlign.Center,
                color = Color.White.copy(alpha = 0.85f),
            )
            Spacer(Modifier.height(32.dp))

            // Stats summary placeholder
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(
                    containerColor = Color.White.copy(alpha = 0.15f),
                ),
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(20.dp),
                    horizontalArrangement = Arrangement.SpaceEvenly,
                ) {
                    SummaryStatItem("Duration", "Great work!")
                    SummaryStatItem("Sets", "Completed")
                }
            }

            Spacer(Modifier.height(24.dp))

            // Motivational quote
            Text(
                text = "\"$randomQuote\"",
                style = MaterialTheme.typography.bodyMedium,
                textAlign = TextAlign.Center,
                color = Color.White.copy(alpha = 0.75f),
            )

            Spacer(Modifier.height(48.dp))

            FilledTonalButton(
                onClick = onDone,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(52.dp),
                shape = RoundedCornerShape(16.dp),
            ) {
                Text("Back to Home")
            }
        }
    }
}

@Composable
private fun SummaryStatItem(label: String, value: String) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(
            value,
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.Bold,
            color = Color.White,
        )
        Text(
            label,
            style = MaterialTheme.typography.labelSmall,
            color = Color.White.copy(alpha = 0.7f),
        )
    }
}

@Composable
private fun ConfettiOverlay(infiniteTransition: InfiniteTransition) {
    val confettiColors = listOf(OrcaSuccess, OrcaWarning, WorkoutActive, WorkoutComplete)

    // Create several animated particles
    val particles = (0 until 8).map { index ->
        val yOffset by infiniteTransition.animateFloat(
            initialValue = 1f,
            targetValue = -0.2f,
            animationSpec = infiniteRepeatable(
                animation = tween(
                    durationMillis = 3000 + (index * 400),
                    easing = LinearEasing,
                ),
                repeatMode = RepeatMode.Restart,
            ),
            label = "particle_$index",
        )
        val xPosition = remember { (index * 0.12f) + 0.05f }
        Triple(xPosition, yOffset, confettiColors[index % confettiColors.size])
    }

    Canvas(modifier = Modifier.fillMaxSize()) {
        particles.forEach { (xFraction, yFraction, color) ->
            val x = size.width * xFraction
            val y = size.height * yFraction
            drawCircle(
                color = color.copy(alpha = 0.4f),
                radius = 6.dp.toPx(),
                center = Offset(x, y),
            )
        }
    }
}

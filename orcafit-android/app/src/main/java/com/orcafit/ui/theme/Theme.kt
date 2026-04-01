package com.orcafit.ui.theme

import android.app.Activity
import android.os.Build
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.SideEffect
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.platform.LocalView
import androidx.core.view.WindowCompat

private val DarkColorScheme = darkColorScheme(
    primary = OrcaPrimaryDark_DT,
    secondary = OrcaSecondaryDark_DT,
    tertiary = OrcaTertiaryDark_DT,
    tertiaryContainer = OrcaTertiaryContainerDark,
    background = OrcaBackgroundDark,
    surface = OrcaSurfaceDark,
    surfaceVariant = OrcaSurfaceVariantDark,
    surfaceTint = OrcaPrimaryDark_DT,
    error = OrcaError,
    onPrimary = OrcaOnBackground,
    onSecondary = OrcaOnSecondary,
    onBackground = OrcaOnPrimary,
    onSurface = OrcaOnPrimary,
)

private val LightColorScheme = lightColorScheme(
    primary = OrcaPrimary,
    secondary = OrcaSecondary,
    tertiary = OrcaTertiary,
    tertiaryContainer = OrcaTertiaryContainer,
    background = OrcaBackground,
    surface = OrcaSurface,
    surfaceVariant = OrcaSurfaceVariant,
    surfaceTint = OrcaSurfaceTint,
    error = OrcaError,
    onPrimary = OrcaOnPrimary,
    onSecondary = OrcaOnSecondary,
    onBackground = OrcaOnBackground,
    onSurface = OrcaOnSurface,
)

@Composable
fun OrcaFitTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    dynamicColor: Boolean = true,
    content: @Composable () -> Unit
) {
    val colorScheme = when {
        dynamicColor && Build.VERSION.SDK_INT >= Build.VERSION_CODES.S -> {
            val context = LocalView.current.context
            if (darkTheme) dynamicDarkColorScheme(context) else dynamicLightColorScheme(context)
        }
        darkTheme -> DarkColorScheme
        else -> LightColorScheme
    }

    val view = LocalView.current
    if (!view.isInEditMode) {
        SideEffect {
            val window = (view.context as Activity).window
            window.statusBarColor = colorScheme.surface.toArgb()
            WindowCompat.getInsetsController(window, view).isAppearanceLightStatusBars = !darkTheme
        }
    }

    MaterialTheme(
        colorScheme = colorScheme,
        typography = Typography,
        content = content,
    )
}

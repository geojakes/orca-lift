package com.orcafit.ui.navigation;

import androidx.compose.runtime.Composable;
import androidx.navigation.NavHostController;
import androidx.navigation.NavType;

@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000\u0014\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0002\b\u0002\n\u0002\u0010\u000e\n\u0002\b\t\b\u00c6\u0002\u0018\u00002\u00020\u0001B\u0007\b\u0002\u00a2\u0006\u0002\u0010\u0002R\u000e\u0010\u0003\u001a\u00020\u0004X\u0086T\u00a2\u0006\u0002\n\u0000R\u000e\u0010\u0005\u001a\u00020\u0004X\u0086T\u00a2\u0006\u0002\n\u0000R\u000e\u0010\u0006\u001a\u00020\u0004X\u0086T\u00a2\u0006\u0002\n\u0000R\u000e\u0010\u0007\u001a\u00020\u0004X\u0086T\u00a2\u0006\u0002\n\u0000R\u000e\u0010\b\u001a\u00020\u0004X\u0086T\u00a2\u0006\u0002\n\u0000R\u000e\u0010\t\u001a\u00020\u0004X\u0086T\u00a2\u0006\u0002\n\u0000R\u000e\u0010\n\u001a\u00020\u0004X\u0086T\u00a2\u0006\u0002\n\u0000R\u000e\u0010\u000b\u001a\u00020\u0004X\u0086T\u00a2\u0006\u0002\n\u0000R\u000e\u0010\f\u001a\u00020\u0004X\u0086T\u00a2\u0006\u0002\n\u0000\u00a8\u0006\r"}, d2 = {"Lcom/orcafit/ui/navigation/Routes;", "", "()V", "ACTIVE_WORKOUT", "", "EXERCISES", "GENERATE", "HISTORY", "HOME", "LOGIN", "PROGRAMS", "PROGRAM_DETAIL", "WORKOUT_SUMMARY", "app_debug"})
public final class Routes {
    @org.jetbrains.annotations.NotNull()
    public static final java.lang.String LOGIN = "login";
    @org.jetbrains.annotations.NotNull()
    public static final java.lang.String HOME = "home";
    @org.jetbrains.annotations.NotNull()
    public static final java.lang.String GENERATE = "generate";
    @org.jetbrains.annotations.NotNull()
    public static final java.lang.String PROGRAMS = "programs";
    @org.jetbrains.annotations.NotNull()
    public static final java.lang.String PROGRAM_DETAIL = "programs/{programId}";
    @org.jetbrains.annotations.NotNull()
    public static final java.lang.String ACTIVE_WORKOUT = "workout/active";
    @org.jetbrains.annotations.NotNull()
    public static final java.lang.String WORKOUT_SUMMARY = "workout/summary/{workoutId}";
    @org.jetbrains.annotations.NotNull()
    public static final java.lang.String HISTORY = "history";
    @org.jetbrains.annotations.NotNull()
    public static final java.lang.String EXERCISES = "exercises";
    @org.jetbrains.annotations.NotNull()
    public static final com.orcafit.ui.navigation.Routes INSTANCE = null;
    
    private Routes() {
        super();
    }
}
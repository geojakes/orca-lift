package com.orcafit.ui.screens.workout;

import androidx.lifecycle.ViewModel;
import com.orcafit.data.api.OrcaFitApi;
import com.orcafit.data.api.models.*;
import dagger.hilt.android.lifecycle.HiltViewModel;
import kotlinx.coroutines.flow.StateFlow;
import javax.inject.Inject;

@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000.\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\b\n\u0002\b\u0003\n\u0002\u0010\u000b\n\u0002\b\u0004\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\u000e\n\u0002\b/\b\u0086\b\u0018\u00002\u00020\u0001B\u00a3\u0001\u0012\n\b\u0002\u0010\u0002\u001a\u0004\u0018\u00010\u0003\u0012\b\b\u0002\u0010\u0004\u001a\u00020\u0005\u0012\b\b\u0002\u0010\u0006\u001a\u00020\u0005\u0012\b\b\u0002\u0010\u0007\u001a\u00020\u0005\u0012\b\b\u0002\u0010\b\u001a\u00020\t\u0012\b\b\u0002\u0010\n\u001a\u00020\t\u0012\b\b\u0002\u0010\u000b\u001a\u00020\t\u0012\n\b\u0002\u0010\f\u001a\u0004\u0018\u00010\u0005\u0012\n\b\u0002\u0010\r\u001a\u0004\u0018\u00010\u000e\u0012\n\b\u0002\u0010\u000f\u001a\u0004\u0018\u00010\u0010\u0012\b\b\u0002\u0010\u0011\u001a\u00020\u0010\u0012\b\b\u0002\u0010\u0012\u001a\u00020\u0010\u0012\b\b\u0002\u0010\u0013\u001a\u00020\u0010\u0012\b\b\u0002\u0010\u0014\u001a\u00020\u0010\u0012\b\b\u0002\u0010\u0015\u001a\u00020\u0010\u00a2\u0006\u0002\u0010\u0016J\u000b\u0010*\u001a\u0004\u0018\u00010\u0003H\u00c6\u0003J\u000b\u0010+\u001a\u0004\u0018\u00010\u0010H\u00c6\u0003J\t\u0010,\u001a\u00020\u0010H\u00c6\u0003J\t\u0010-\u001a\u00020\u0010H\u00c6\u0003J\t\u0010.\u001a\u00020\u0010H\u00c6\u0003J\t\u0010/\u001a\u00020\u0010H\u00c6\u0003J\t\u00100\u001a\u00020\u0010H\u00c6\u0003J\t\u00101\u001a\u00020\u0005H\u00c6\u0003J\t\u00102\u001a\u00020\u0005H\u00c6\u0003J\t\u00103\u001a\u00020\u0005H\u00c6\u0003J\t\u00104\u001a\u00020\tH\u00c6\u0003J\t\u00105\u001a\u00020\tH\u00c6\u0003J\t\u00106\u001a\u00020\tH\u00c6\u0003J\u0010\u00107\u001a\u0004\u0018\u00010\u0005H\u00c6\u0003\u00a2\u0006\u0002\u0010\u0018J\u000b\u00108\u001a\u0004\u0018\u00010\u000eH\u00c6\u0003J\u00ac\u0001\u00109\u001a\u00020\u00002\n\b\u0002\u0010\u0002\u001a\u0004\u0018\u00010\u00032\b\b\u0002\u0010\u0004\u001a\u00020\u00052\b\b\u0002\u0010\u0006\u001a\u00020\u00052\b\b\u0002\u0010\u0007\u001a\u00020\u00052\b\b\u0002\u0010\b\u001a\u00020\t2\b\b\u0002\u0010\n\u001a\u00020\t2\b\b\u0002\u0010\u000b\u001a\u00020\t2\n\b\u0002\u0010\f\u001a\u0004\u0018\u00010\u00052\n\b\u0002\u0010\r\u001a\u0004\u0018\u00010\u000e2\n\b\u0002\u0010\u000f\u001a\u0004\u0018\u00010\u00102\b\b\u0002\u0010\u0011\u001a\u00020\u00102\b\b\u0002\u0010\u0012\u001a\u00020\u00102\b\b\u0002\u0010\u0013\u001a\u00020\u00102\b\b\u0002\u0010\u0014\u001a\u00020\u00102\b\b\u0002\u0010\u0015\u001a\u00020\u0010H\u00c6\u0001\u00a2\u0006\u0002\u0010:J\u0013\u0010;\u001a\u00020\t2\b\u0010<\u001a\u0004\u0018\u00010\u0001H\u00d6\u0003J\t\u0010=\u001a\u00020\u0005H\u00d6\u0001J\t\u0010>\u001a\u00020\u0010H\u00d6\u0001R\u0015\u0010\f\u001a\u0004\u0018\u00010\u0005\u00a2\u0006\n\n\u0002\u0010\u0019\u001a\u0004\b\u0017\u0010\u0018R\u0011\u0010\u0004\u001a\u00020\u0005\u00a2\u0006\b\n\u0000\u001a\u0004\b\u001a\u0010\u001bR\u0011\u0010\u0006\u001a\u00020\u0005\u00a2\u0006\b\n\u0000\u001a\u0004\b\u001c\u0010\u001bR\u0013\u0010\u000f\u001a\u0004\u0018\u00010\u0010\u00a2\u0006\b\n\u0000\u001a\u0004\b\u001d\u0010\u001eR\u0011\u0010\u0015\u001a\u00020\u0010\u00a2\u0006\b\n\u0000\u001a\u0004\b\u001f\u0010\u001eR\u0011\u0010\u0014\u001a\u00020\u0010\u00a2\u0006\b\n\u0000\u001a\u0004\b \u0010\u001eR\u0011\u0010\u0012\u001a\u00020\u0010\u00a2\u0006\b\n\u0000\u001a\u0004\b!\u0010\u001eR\u0011\u0010\u0013\u001a\u00020\u0010\u00a2\u0006\b\n\u0000\u001a\u0004\b\"\u0010\u001eR\u0011\u0010\u0011\u001a\u00020\u0010\u00a2\u0006\b\n\u0000\u001a\u0004\b#\u0010\u001eR\u0011\u0010\n\u001a\u00020\t\u00a2\u0006\b\n\u0000\u001a\u0004\b\n\u0010$R\u0011\u0010\b\u001a\u00020\t\u00a2\u0006\b\n\u0000\u001a\u0004\b\b\u0010$R\u0011\u0010\u000b\u001a\u00020\t\u00a2\u0006\b\n\u0000\u001a\u0004\b\u000b\u0010$R\u0011\u0010\u0007\u001a\u00020\u0005\u00a2\u0006\b\n\u0000\u001a\u0004\b%\u0010\u001bR\u0013\u0010\r\u001a\u0004\u0018\u00010\u000e\u00a2\u0006\b\n\u0000\u001a\u0004\b&\u0010\'R\u0013\u0010\u0002\u001a\u0004\u0018\u00010\u0003\u00a2\u0006\b\n\u0000\u001a\u0004\b(\u0010)\u00a8\u0006?"}, d2 = {"Lcom/orcafit/ui/screens/workout/WorkoutUiState;", "", "workout", "Lcom/orcafit/data/api/models/WorkoutResponse;", "currentExerciseIndex", "", "elapsedSeconds", "restTimerSeconds", "isRestTimerRunning", "", "isLoading", "isSaving", "completedWorkoutId", "summary", "Lcom/orcafit/data/api/models/WorkoutSummaryResponse;", "error", "", "inputWeight", "inputReps", "inputRpe", "inputDuration", "inputDistance", "(Lcom/orcafit/data/api/models/WorkoutResponse;IIIZZZLjava/lang/Integer;Lcom/orcafit/data/api/models/WorkoutSummaryResponse;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)V", "getCompletedWorkoutId", "()Ljava/lang/Integer;", "Ljava/lang/Integer;", "getCurrentExerciseIndex", "()I", "getElapsedSeconds", "getError", "()Ljava/lang/String;", "getInputDistance", "getInputDuration", "getInputReps", "getInputRpe", "getInputWeight", "()Z", "getRestTimerSeconds", "getSummary", "()Lcom/orcafit/data/api/models/WorkoutSummaryResponse;", "getWorkout", "()Lcom/orcafit/data/api/models/WorkoutResponse;", "component1", "component10", "component11", "component12", "component13", "component14", "component15", "component2", "component3", "component4", "component5", "component6", "component7", "component8", "component9", "copy", "(Lcom/orcafit/data/api/models/WorkoutResponse;IIIZZZLjava/lang/Integer;Lcom/orcafit/data/api/models/WorkoutSummaryResponse;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)Lcom/orcafit/ui/screens/workout/WorkoutUiState;", "equals", "other", "hashCode", "toString", "app_debug"})
public final class WorkoutUiState {
    @org.jetbrains.annotations.Nullable()
    private final com.orcafit.data.api.models.WorkoutResponse workout = null;
    private final int currentExerciseIndex = 0;
    private final int elapsedSeconds = 0;
    private final int restTimerSeconds = 0;
    private final boolean isRestTimerRunning = false;
    private final boolean isLoading = false;
    private final boolean isSaving = false;
    @org.jetbrains.annotations.Nullable()
    private final java.lang.Integer completedWorkoutId = null;
    @org.jetbrains.annotations.Nullable()
    private final com.orcafit.data.api.models.WorkoutSummaryResponse summary = null;
    @org.jetbrains.annotations.Nullable()
    private final java.lang.String error = null;
    @org.jetbrains.annotations.NotNull()
    private final java.lang.String inputWeight = null;
    @org.jetbrains.annotations.NotNull()
    private final java.lang.String inputReps = null;
    @org.jetbrains.annotations.NotNull()
    private final java.lang.String inputRpe = null;
    @org.jetbrains.annotations.NotNull()
    private final java.lang.String inputDuration = null;
    @org.jetbrains.annotations.NotNull()
    private final java.lang.String inputDistance = null;
    
    public WorkoutUiState(@org.jetbrains.annotations.Nullable()
    com.orcafit.data.api.models.WorkoutResponse workout, int currentExerciseIndex, int elapsedSeconds, int restTimerSeconds, boolean isRestTimerRunning, boolean isLoading, boolean isSaving, @org.jetbrains.annotations.Nullable()
    java.lang.Integer completedWorkoutId, @org.jetbrains.annotations.Nullable()
    com.orcafit.data.api.models.WorkoutSummaryResponse summary, @org.jetbrains.annotations.Nullable()
    java.lang.String error, @org.jetbrains.annotations.NotNull()
    java.lang.String inputWeight, @org.jetbrains.annotations.NotNull()
    java.lang.String inputReps, @org.jetbrains.annotations.NotNull()
    java.lang.String inputRpe, @org.jetbrains.annotations.NotNull()
    java.lang.String inputDuration, @org.jetbrains.annotations.NotNull()
    java.lang.String inputDistance) {
        super();
    }
    
    @org.jetbrains.annotations.Nullable()
    public final com.orcafit.data.api.models.WorkoutResponse getWorkout() {
        return null;
    }
    
    public final int getCurrentExerciseIndex() {
        return 0;
    }
    
    public final int getElapsedSeconds() {
        return 0;
    }
    
    public final int getRestTimerSeconds() {
        return 0;
    }
    
    public final boolean isRestTimerRunning() {
        return false;
    }
    
    public final boolean isLoading() {
        return false;
    }
    
    public final boolean isSaving() {
        return false;
    }
    
    @org.jetbrains.annotations.Nullable()
    public final java.lang.Integer getCompletedWorkoutId() {
        return null;
    }
    
    @org.jetbrains.annotations.Nullable()
    public final com.orcafit.data.api.models.WorkoutSummaryResponse getSummary() {
        return null;
    }
    
    @org.jetbrains.annotations.Nullable()
    public final java.lang.String getError() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final java.lang.String getInputWeight() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final java.lang.String getInputReps() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final java.lang.String getInputRpe() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final java.lang.String getInputDuration() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final java.lang.String getInputDistance() {
        return null;
    }
    
    public WorkoutUiState() {
        super();
    }
    
    @org.jetbrains.annotations.Nullable()
    public final com.orcafit.data.api.models.WorkoutResponse component1() {
        return null;
    }
    
    @org.jetbrains.annotations.Nullable()
    public final java.lang.String component10() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final java.lang.String component11() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final java.lang.String component12() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final java.lang.String component13() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final java.lang.String component14() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final java.lang.String component15() {
        return null;
    }
    
    public final int component2() {
        return 0;
    }
    
    public final int component3() {
        return 0;
    }
    
    public final int component4() {
        return 0;
    }
    
    public final boolean component5() {
        return false;
    }
    
    public final boolean component6() {
        return false;
    }
    
    public final boolean component7() {
        return false;
    }
    
    @org.jetbrains.annotations.Nullable()
    public final java.lang.Integer component8() {
        return null;
    }
    
    @org.jetbrains.annotations.Nullable()
    public final com.orcafit.data.api.models.WorkoutSummaryResponse component9() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final com.orcafit.ui.screens.workout.WorkoutUiState copy(@org.jetbrains.annotations.Nullable()
    com.orcafit.data.api.models.WorkoutResponse workout, int currentExerciseIndex, int elapsedSeconds, int restTimerSeconds, boolean isRestTimerRunning, boolean isLoading, boolean isSaving, @org.jetbrains.annotations.Nullable()
    java.lang.Integer completedWorkoutId, @org.jetbrains.annotations.Nullable()
    com.orcafit.data.api.models.WorkoutSummaryResponse summary, @org.jetbrains.annotations.Nullable()
    java.lang.String error, @org.jetbrains.annotations.NotNull()
    java.lang.String inputWeight, @org.jetbrains.annotations.NotNull()
    java.lang.String inputReps, @org.jetbrains.annotations.NotNull()
    java.lang.String inputRpe, @org.jetbrains.annotations.NotNull()
    java.lang.String inputDuration, @org.jetbrains.annotations.NotNull()
    java.lang.String inputDistance) {
        return null;
    }
    
    @java.lang.Override()
    public boolean equals(@org.jetbrains.annotations.Nullable()
    java.lang.Object other) {
        return false;
    }
    
    @java.lang.Override()
    public int hashCode() {
        return 0;
    }
    
    @java.lang.Override()
    @org.jetbrains.annotations.NotNull()
    public java.lang.String toString() {
        return null;
    }
}
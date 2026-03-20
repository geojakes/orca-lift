package com.orcafit.ui.screens.workout;

import androidx.lifecycle.ViewModel;
import com.orcafit.data.api.OrcaFitApi;
import com.orcafit.data.api.models.*;
import dagger.hilt.android.lifecycle.HiltViewModel;
import kotlinx.coroutines.flow.StateFlow;
import javax.inject.Inject;

@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000D\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0002\b\u0003\n\u0002\u0010\u0002\n\u0002\b\u0005\n\u0002\u0010\b\n\u0002\b\u0006\n\u0002\u0010\u000e\n\u0002\b\u0005\b\u0007\u0018\u00002\u00020\u0001B\u000f\b\u0007\u0012\u0006\u0010\u0002\u001a\u00020\u0003\u00a2\u0006\u0002\u0010\u0004J\u0006\u0010\u000f\u001a\u00020\u0010J\u0006\u0010\u0011\u001a\u00020\u0010J\u0006\u0010\u0012\u001a\u00020\u0010J\b\u0010\u0013\u001a\u00020\u0010H\u0014J\u000e\u0010\u0014\u001a\u00020\u00102\u0006\u0010\u0015\u001a\u00020\u0016J\u0006\u0010\u0017\u001a\u00020\u0010J\u000e\u0010\u0018\u001a\u00020\u00102\u0006\u0010\u0019\u001a\u00020\u0016J\b\u0010\u001a\u001a\u00020\u0010H\u0002J\u000e\u0010\u001b\u001a\u00020\u00102\u0006\u0010\u001c\u001a\u00020\u001dJ\u000e\u0010\u001e\u001a\u00020\u00102\u0006\u0010\u001c\u001a\u00020\u001dJ\u000e\u0010\u001f\u001a\u00020\u00102\u0006\u0010\u001c\u001a\u00020\u001dJ\u000e\u0010 \u001a\u00020\u00102\u0006\u0010\u001c\u001a\u00020\u001dJ\u000e\u0010!\u001a\u00020\u00102\u0006\u0010\u001c\u001a\u00020\u001dR\u0014\u0010\u0005\u001a\b\u0012\u0004\u0012\u00020\u00070\u0006X\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u000e\u0010\u0002\u001a\u00020\u0003X\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u0010\u0010\b\u001a\u0004\u0018\u00010\tX\u0082\u000e\u00a2\u0006\u0002\n\u0000R\u0010\u0010\n\u001a\u0004\u0018\u00010\tX\u0082\u000e\u00a2\u0006\u0002\n\u0000R\u0017\u0010\u000b\u001a\b\u0012\u0004\u0012\u00020\u00070\f\u00a2\u0006\b\n\u0000\u001a\u0004\b\r\u0010\u000e\u00a8\u0006\""}, d2 = {"Lcom/orcafit/ui/screens/workout/WorkoutViewModel;", "Landroidx/lifecycle/ViewModel;", "api", "Lcom/orcafit/data/api/OrcaFitApi;", "(Lcom/orcafit/data/api/OrcaFitApi;)V", "_uiState", "Lkotlinx/coroutines/flow/MutableStateFlow;", "Lcom/orcafit/ui/screens/workout/WorkoutUiState;", "restJob", "Lkotlinx/coroutines/Job;", "timerJob", "uiState", "Lkotlinx/coroutines/flow/StateFlow;", "getUiState", "()Lkotlinx/coroutines/flow/StateFlow;", "completeWorkout", "", "loadActiveWorkout", "logSet", "onCleared", "setCurrentExercise", "index", "", "skipRest", "startRestTimer", "seconds", "startTimer", "updateInputDistance", "v", "", "updateInputDuration", "updateInputReps", "updateInputRpe", "updateInputWeight", "app_debug"})
@dagger.hilt.android.lifecycle.HiltViewModel()
public final class WorkoutViewModel extends androidx.lifecycle.ViewModel {
    @org.jetbrains.annotations.NotNull()
    private final com.orcafit.data.api.OrcaFitApi api = null;
    @org.jetbrains.annotations.NotNull()
    private final kotlinx.coroutines.flow.MutableStateFlow<com.orcafit.ui.screens.workout.WorkoutUiState> _uiState = null;
    @org.jetbrains.annotations.NotNull()
    private final kotlinx.coroutines.flow.StateFlow<com.orcafit.ui.screens.workout.WorkoutUiState> uiState = null;
    @org.jetbrains.annotations.Nullable()
    private kotlinx.coroutines.Job timerJob;
    @org.jetbrains.annotations.Nullable()
    private kotlinx.coroutines.Job restJob;
    
    @javax.inject.Inject()
    public WorkoutViewModel(@org.jetbrains.annotations.NotNull()
    com.orcafit.data.api.OrcaFitApi api) {
        super();
    }
    
    @org.jetbrains.annotations.NotNull()
    public final kotlinx.coroutines.flow.StateFlow<com.orcafit.ui.screens.workout.WorkoutUiState> getUiState() {
        return null;
    }
    
    public final void loadActiveWorkout() {
    }
    
    private final void startTimer() {
    }
    
    public final void updateInputWeight(@org.jetbrains.annotations.NotNull()
    java.lang.String v) {
    }
    
    public final void updateInputReps(@org.jetbrains.annotations.NotNull()
    java.lang.String v) {
    }
    
    public final void updateInputRpe(@org.jetbrains.annotations.NotNull()
    java.lang.String v) {
    }
    
    public final void updateInputDuration(@org.jetbrains.annotations.NotNull()
    java.lang.String v) {
    }
    
    public final void updateInputDistance(@org.jetbrains.annotations.NotNull()
    java.lang.String v) {
    }
    
    public final void setCurrentExercise(int index) {
    }
    
    public final void logSet() {
    }
    
    public final void startRestTimer(int seconds) {
    }
    
    public final void skipRest() {
    }
    
    public final void completeWorkout() {
    }
    
    @java.lang.Override()
    protected void onCleared() {
    }
}
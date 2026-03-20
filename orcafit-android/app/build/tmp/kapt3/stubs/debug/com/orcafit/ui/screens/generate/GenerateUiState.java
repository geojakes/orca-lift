package com.orcafit.ui.screens.generate;

import androidx.lifecycle.ViewModel;
import com.orcafit.data.api.OrcaFitApi;
import com.orcafit.data.api.models.GenerateProgramRequest;
import dagger.hilt.android.lifecycle.HiltViewModel;
import kotlinx.coroutines.flow.StateFlow;
import javax.inject.Inject;

@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000 \n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0000\n\u0002\u0010\u000e\n\u0000\n\u0002\u0010\b\n\u0002\b\u0002\n\u0002\u0010\u000b\n\u0002\b\u001d\b\u0086\b\u0018\u00002\u00020\u0001BO\u0012\b\b\u0002\u0010\u0002\u001a\u00020\u0003\u0012\b\b\u0002\u0010\u0004\u001a\u00020\u0005\u0012\b\b\u0002\u0010\u0006\u001a\u00020\u0005\u0012\b\b\u0002\u0010\u0007\u001a\u00020\b\u0012\b\b\u0002\u0010\t\u001a\u00020\u0003\u0012\n\b\u0002\u0010\n\u001a\u0004\u0018\u00010\u0005\u0012\n\b\u0002\u0010\u000b\u001a\u0004\u0018\u00010\u0003\u00a2\u0006\u0002\u0010\fJ\t\u0010\u0018\u001a\u00020\u0003H\u00c6\u0003J\t\u0010\u0019\u001a\u00020\u0005H\u00c6\u0003J\t\u0010\u001a\u001a\u00020\u0005H\u00c6\u0003J\t\u0010\u001b\u001a\u00020\bH\u00c6\u0003J\t\u0010\u001c\u001a\u00020\u0003H\u00c6\u0003J\u0010\u0010\u001d\u001a\u0004\u0018\u00010\u0005H\u00c6\u0003\u00a2\u0006\u0002\u0010\u0012J\u000b\u0010\u001e\u001a\u0004\u0018\u00010\u0003H\u00c6\u0003JX\u0010\u001f\u001a\u00020\u00002\b\b\u0002\u0010\u0002\u001a\u00020\u00032\b\b\u0002\u0010\u0004\u001a\u00020\u00052\b\b\u0002\u0010\u0006\u001a\u00020\u00052\b\b\u0002\u0010\u0007\u001a\u00020\b2\b\b\u0002\u0010\t\u001a\u00020\u00032\n\b\u0002\u0010\n\u001a\u0004\u0018\u00010\u00052\n\b\u0002\u0010\u000b\u001a\u0004\u0018\u00010\u0003H\u00c6\u0001\u00a2\u0006\u0002\u0010 J\u0013\u0010!\u001a\u00020\b2\b\u0010\"\u001a\u0004\u0018\u00010\u0001H\u00d6\u0003J\t\u0010#\u001a\u00020\u0005H\u00d6\u0001J\t\u0010$\u001a\u00020\u0003H\u00d6\u0001R\u0011\u0010\u0004\u001a\u00020\u0005\u00a2\u0006\b\n\u0000\u001a\u0004\b\r\u0010\u000eR\u0013\u0010\u000b\u001a\u0004\u0018\u00010\u0003\u00a2\u0006\b\n\u0000\u001a\u0004\b\u000f\u0010\u0010R\u0015\u0010\n\u001a\u0004\u0018\u00010\u0005\u00a2\u0006\n\n\u0002\u0010\u0013\u001a\u0004\b\u0011\u0010\u0012R\u0011\u0010\u0002\u001a\u00020\u0003\u00a2\u0006\b\n\u0000\u001a\u0004\b\u0014\u0010\u0010R\u0011\u0010\u0007\u001a\u00020\b\u00a2\u0006\b\n\u0000\u001a\u0004\b\u0007\u0010\u0015R\u0011\u0010\t\u001a\u00020\u0003\u00a2\u0006\b\n\u0000\u001a\u0004\b\u0016\u0010\u0010R\u0011\u0010\u0006\u001a\u00020\u0005\u00a2\u0006\b\n\u0000\u001a\u0004\b\u0017\u0010\u000e\u00a8\u0006%"}, d2 = {"Lcom/orcafit/ui/screens/generate/GenerateUiState;", "", "goals", "", "daysPerWeek", "", "weeks", "isGenerating", "", "progress", "generatedProgramId", "error", "(Ljava/lang/String;IIZLjava/lang/String;Ljava/lang/Integer;Ljava/lang/String;)V", "getDaysPerWeek", "()I", "getError", "()Ljava/lang/String;", "getGeneratedProgramId", "()Ljava/lang/Integer;", "Ljava/lang/Integer;", "getGoals", "()Z", "getProgress", "getWeeks", "component1", "component2", "component3", "component4", "component5", "component6", "component7", "copy", "(Ljava/lang/String;IIZLjava/lang/String;Ljava/lang/Integer;Ljava/lang/String;)Lcom/orcafit/ui/screens/generate/GenerateUiState;", "equals", "other", "hashCode", "toString", "app_debug"})
public final class GenerateUiState {
    @org.jetbrains.annotations.NotNull()
    private final java.lang.String goals = null;
    private final int daysPerWeek = 0;
    private final int weeks = 0;
    private final boolean isGenerating = false;
    @org.jetbrains.annotations.NotNull()
    private final java.lang.String progress = null;
    @org.jetbrains.annotations.Nullable()
    private final java.lang.Integer generatedProgramId = null;
    @org.jetbrains.annotations.Nullable()
    private final java.lang.String error = null;
    
    public GenerateUiState(@org.jetbrains.annotations.NotNull()
    java.lang.String goals, int daysPerWeek, int weeks, boolean isGenerating, @org.jetbrains.annotations.NotNull()
    java.lang.String progress, @org.jetbrains.annotations.Nullable()
    java.lang.Integer generatedProgramId, @org.jetbrains.annotations.Nullable()
    java.lang.String error) {
        super();
    }
    
    @org.jetbrains.annotations.NotNull()
    public final java.lang.String getGoals() {
        return null;
    }
    
    public final int getDaysPerWeek() {
        return 0;
    }
    
    public final int getWeeks() {
        return 0;
    }
    
    public final boolean isGenerating() {
        return false;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final java.lang.String getProgress() {
        return null;
    }
    
    @org.jetbrains.annotations.Nullable()
    public final java.lang.Integer getGeneratedProgramId() {
        return null;
    }
    
    @org.jetbrains.annotations.Nullable()
    public final java.lang.String getError() {
        return null;
    }
    
    public GenerateUiState() {
        super();
    }
    
    @org.jetbrains.annotations.NotNull()
    public final java.lang.String component1() {
        return null;
    }
    
    public final int component2() {
        return 0;
    }
    
    public final int component3() {
        return 0;
    }
    
    public final boolean component4() {
        return false;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final java.lang.String component5() {
        return null;
    }
    
    @org.jetbrains.annotations.Nullable()
    public final java.lang.Integer component6() {
        return null;
    }
    
    @org.jetbrains.annotations.Nullable()
    public final java.lang.String component7() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final com.orcafit.ui.screens.generate.GenerateUiState copy(@org.jetbrains.annotations.NotNull()
    java.lang.String goals, int daysPerWeek, int weeks, boolean isGenerating, @org.jetbrains.annotations.NotNull()
    java.lang.String progress, @org.jetbrains.annotations.Nullable()
    java.lang.Integer generatedProgramId, @org.jetbrains.annotations.Nullable()
    java.lang.String error) {
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
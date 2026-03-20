package com.orcafit.data.api.models;

import com.squareup.moshi.Json;
import com.squareup.moshi.JsonClass;

@com.squareup.moshi.JsonClass(generateAdapter = true)
@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000,\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0000\n\u0002\u0010\u000e\n\u0002\b\u0002\n\u0002\u0010\b\n\u0002\b\u0002\n\u0002\u0010 \n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\u000b\n\u0002\b\u001a\b\u0087\b\u0018\u00002\u00020\u0001BQ\u0012\b\b\u0001\u0010\u0002\u001a\u00020\u0003\u0012\b\b\u0003\u0010\u0004\u001a\u00020\u0003\u0012\b\b\u0002\u0010\u0005\u001a\u00020\u0006\u0012\b\b\u0003\u0010\u0007\u001a\u00020\u0006\u0012\u000e\b\u0003\u0010\b\u001a\b\u0012\u0004\u0012\u00020\n0\t\u0012\b\b\u0002\u0010\u000b\u001a\u00020\f\u0012\b\b\u0002\u0010\r\u001a\u00020\u0003\u00a2\u0006\u0002\u0010\u000eJ\t\u0010\u001a\u001a\u00020\u0003H\u00c6\u0003J\t\u0010\u001b\u001a\u00020\u0003H\u00c6\u0003J\t\u0010\u001c\u001a\u00020\u0006H\u00c6\u0003J\t\u0010\u001d\u001a\u00020\u0006H\u00c6\u0003J\u000f\u0010\u001e\u001a\b\u0012\u0004\u0012\u00020\n0\tH\u00c6\u0003J\t\u0010\u001f\u001a\u00020\fH\u00c6\u0003J\t\u0010 \u001a\u00020\u0003H\u00c6\u0003JU\u0010!\u001a\u00020\u00002\b\b\u0003\u0010\u0002\u001a\u00020\u00032\b\b\u0003\u0010\u0004\u001a\u00020\u00032\b\b\u0002\u0010\u0005\u001a\u00020\u00062\b\b\u0003\u0010\u0007\u001a\u00020\u00062\u000e\b\u0003\u0010\b\u001a\b\u0012\u0004\u0012\u00020\n0\t2\b\b\u0002\u0010\u000b\u001a\u00020\f2\b\b\u0002\u0010\r\u001a\u00020\u0003H\u00c6\u0001J\u0013\u0010\"\u001a\u00020\f2\b\u0010#\u001a\u0004\u0018\u00010\u0001H\u00d6\u0003J\t\u0010$\u001a\u00020\u0006H\u00d6\u0001J\t\u0010%\u001a\u00020\u0003H\u00d6\u0001R\u0011\u0010\u0002\u001a\u00020\u0003\u00a2\u0006\b\n\u0000\u001a\u0004\b\u000f\u0010\u0010R\u0011\u0010\u0004\u001a\u00020\u0003\u00a2\u0006\b\n\u0000\u001a\u0004\b\u0011\u0010\u0010R\u0017\u0010\b\u001a\b\u0012\u0004\u0012\u00020\n0\t\u00a2\u0006\b\n\u0000\u001a\u0004\b\u0012\u0010\u0013R\u0011\u0010\r\u001a\u00020\u0003\u00a2\u0006\b\n\u0000\u001a\u0004\b\u0014\u0010\u0010R\u0011\u0010\u0005\u001a\u00020\u0006\u00a2\u0006\b\n\u0000\u001a\u0004\b\u0015\u0010\u0016R\u0011\u0010\u000b\u001a\u00020\f\u00a2\u0006\b\n\u0000\u001a\u0004\b\u0017\u0010\u0018R\u0011\u0010\u0007\u001a\u00020\u0006\u00a2\u0006\b\n\u0000\u001a\u0004\b\u0019\u0010\u0016\u00a8\u0006&"}, d2 = {"Lcom/orcafit/data/api/models/WorkoutExerciseDto;", "", "exerciseId", "", "exerciseName", "order", "", "targetSets", "loggedSets", "", "Lcom/orcafit/data/api/models/LoggedSetDto;", "skipped", "", "notes", "(Ljava/lang/String;Ljava/lang/String;IILjava/util/List;ZLjava/lang/String;)V", "getExerciseId", "()Ljava/lang/String;", "getExerciseName", "getLoggedSets", "()Ljava/util/List;", "getNotes", "getOrder", "()I", "getSkipped", "()Z", "getTargetSets", "component1", "component2", "component3", "component4", "component5", "component6", "component7", "copy", "equals", "other", "hashCode", "toString", "app_debug"})
public final class WorkoutExerciseDto {
    @org.jetbrains.annotations.NotNull()
    private final java.lang.String exerciseId = null;
    @org.jetbrains.annotations.NotNull()
    private final java.lang.String exerciseName = null;
    private final int order = 0;
    private final int targetSets = 0;
    @org.jetbrains.annotations.NotNull()
    private final java.util.List<com.orcafit.data.api.models.LoggedSetDto> loggedSets = null;
    private final boolean skipped = false;
    @org.jetbrains.annotations.NotNull()
    private final java.lang.String notes = null;
    
    public WorkoutExerciseDto(@com.squareup.moshi.Json(name = "exercise_id")
    @org.jetbrains.annotations.NotNull()
    java.lang.String exerciseId, @com.squareup.moshi.Json(name = "exercise_name")
    @org.jetbrains.annotations.NotNull()
    java.lang.String exerciseName, int order, @com.squareup.moshi.Json(name = "target_sets")
    int targetSets, @com.squareup.moshi.Json(name = "logged_sets")
    @org.jetbrains.annotations.NotNull()
    java.util.List<com.orcafit.data.api.models.LoggedSetDto> loggedSets, boolean skipped, @org.jetbrains.annotations.NotNull()
    java.lang.String notes) {
        super();
    }
    
    @org.jetbrains.annotations.NotNull()
    public final java.lang.String getExerciseId() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final java.lang.String getExerciseName() {
        return null;
    }
    
    public final int getOrder() {
        return 0;
    }
    
    public final int getTargetSets() {
        return 0;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final java.util.List<com.orcafit.data.api.models.LoggedSetDto> getLoggedSets() {
        return null;
    }
    
    public final boolean getSkipped() {
        return false;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final java.lang.String getNotes() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final java.lang.String component1() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final java.lang.String component2() {
        return null;
    }
    
    public final int component3() {
        return 0;
    }
    
    public final int component4() {
        return 0;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final java.util.List<com.orcafit.data.api.models.LoggedSetDto> component5() {
        return null;
    }
    
    public final boolean component6() {
        return false;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final java.lang.String component7() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final com.orcafit.data.api.models.WorkoutExerciseDto copy(@com.squareup.moshi.Json(name = "exercise_id")
    @org.jetbrains.annotations.NotNull()
    java.lang.String exerciseId, @com.squareup.moshi.Json(name = "exercise_name")
    @org.jetbrains.annotations.NotNull()
    java.lang.String exerciseName, int order, @com.squareup.moshi.Json(name = "target_sets")
    int targetSets, @com.squareup.moshi.Json(name = "logged_sets")
    @org.jetbrains.annotations.NotNull()
    java.util.List<com.orcafit.data.api.models.LoggedSetDto> loggedSets, boolean skipped, @org.jetbrains.annotations.NotNull()
    java.lang.String notes) {
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
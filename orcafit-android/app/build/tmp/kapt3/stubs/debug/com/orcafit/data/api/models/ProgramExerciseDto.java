package com.orcafit.data.api.models;

import com.squareup.moshi.Json;
import com.squareup.moshi.JsonClass;

@com.squareup.moshi.JsonClass(generateAdapter = true)
@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u00002\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0000\n\u0002\u0010\u000e\n\u0002\b\u0002\n\u0002\u0010\b\n\u0000\n\u0002\u0010 \n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0014\n\u0002\u0010\u000b\n\u0002\b\u0004\b\u0087\b\u0018\u00002\u00020\u0001BI\u0012\b\b\u0003\u0010\u0002\u001a\u00020\u0003\u0012\b\b\u0003\u0010\u0004\u001a\u00020\u0003\u0012\b\b\u0002\u0010\u0005\u001a\u00020\u0006\u0012\u000e\b\u0002\u0010\u0007\u001a\b\u0012\u0004\u0012\u00020\t0\b\u0012\n\b\u0002\u0010\n\u001a\u0004\u0018\u00010\u000b\u0012\b\b\u0002\u0010\f\u001a\u00020\u0003\u00a2\u0006\u0002\u0010\rJ\t\u0010\u0018\u001a\u00020\u0003H\u00c6\u0003J\t\u0010\u0019\u001a\u00020\u0003H\u00c6\u0003J\t\u0010\u001a\u001a\u00020\u0006H\u00c6\u0003J\u000f\u0010\u001b\u001a\b\u0012\u0004\u0012\u00020\t0\bH\u00c6\u0003J\u000b\u0010\u001c\u001a\u0004\u0018\u00010\u000bH\u00c6\u0003J\t\u0010\u001d\u001a\u00020\u0003H\u00c6\u0003JM\u0010\u001e\u001a\u00020\u00002\b\b\u0003\u0010\u0002\u001a\u00020\u00032\b\b\u0003\u0010\u0004\u001a\u00020\u00032\b\b\u0002\u0010\u0005\u001a\u00020\u00062\u000e\b\u0002\u0010\u0007\u001a\b\u0012\u0004\u0012\u00020\t0\b2\n\b\u0002\u0010\n\u001a\u0004\u0018\u00010\u000b2\b\b\u0002\u0010\f\u001a\u00020\u0003H\u00c6\u0001J\u0013\u0010\u001f\u001a\u00020 2\b\u0010!\u001a\u0004\u0018\u00010\u0001H\u00d6\u0003J\t\u0010\"\u001a\u00020\u0006H\u00d6\u0001J\t\u0010#\u001a\u00020\u0003H\u00d6\u0001R\u0011\u0010\u0002\u001a\u00020\u0003\u00a2\u0006\b\n\u0000\u001a\u0004\b\u000e\u0010\u000fR\u0011\u0010\u0004\u001a\u00020\u0003\u00a2\u0006\b\n\u0000\u001a\u0004\b\u0010\u0010\u000fR\u0011\u0010\f\u001a\u00020\u0003\u00a2\u0006\b\n\u0000\u001a\u0004\b\u0011\u0010\u000fR\u0011\u0010\u0005\u001a\u00020\u0006\u00a2\u0006\b\n\u0000\u001a\u0004\b\u0012\u0010\u0013R\u0013\u0010\n\u001a\u0004\u0018\u00010\u000b\u00a2\u0006\b\n\u0000\u001a\u0004\b\u0014\u0010\u0015R\u0017\u0010\u0007\u001a\b\u0012\u0004\u0012\u00020\t0\b\u00a2\u0006\b\n\u0000\u001a\u0004\b\u0016\u0010\u0017\u00a8\u0006$"}, d2 = {"Lcom/orcafit/data/api/models/ProgramExerciseDto;", "", "exerciseId", "", "exerciseName", "order", "", "sets", "", "Lcom/orcafit/data/api/models/SetDto;", "progression", "Lcom/orcafit/data/api/models/ProgressionDto;", "notes", "(Ljava/lang/String;Ljava/lang/String;ILjava/util/List;Lcom/orcafit/data/api/models/ProgressionDto;Ljava/lang/String;)V", "getExerciseId", "()Ljava/lang/String;", "getExerciseName", "getNotes", "getOrder", "()I", "getProgression", "()Lcom/orcafit/data/api/models/ProgressionDto;", "getSets", "()Ljava/util/List;", "component1", "component2", "component3", "component4", "component5", "component6", "copy", "equals", "", "other", "hashCode", "toString", "app_debug"})
public final class ProgramExerciseDto {
    @org.jetbrains.annotations.NotNull()
    private final java.lang.String exerciseId = null;
    @org.jetbrains.annotations.NotNull()
    private final java.lang.String exerciseName = null;
    private final int order = 0;
    @org.jetbrains.annotations.NotNull()
    private final java.util.List<com.orcafit.data.api.models.SetDto> sets = null;
    @org.jetbrains.annotations.Nullable()
    private final com.orcafit.data.api.models.ProgressionDto progression = null;
    @org.jetbrains.annotations.NotNull()
    private final java.lang.String notes = null;
    
    public ProgramExerciseDto(@com.squareup.moshi.Json(name = "exercise_id")
    @org.jetbrains.annotations.NotNull()
    java.lang.String exerciseId, @com.squareup.moshi.Json(name = "exercise_name")
    @org.jetbrains.annotations.NotNull()
    java.lang.String exerciseName, int order, @org.jetbrains.annotations.NotNull()
    java.util.List<com.orcafit.data.api.models.SetDto> sets, @org.jetbrains.annotations.Nullable()
    com.orcafit.data.api.models.ProgressionDto progression, @org.jetbrains.annotations.NotNull()
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
    
    @org.jetbrains.annotations.NotNull()
    public final java.util.List<com.orcafit.data.api.models.SetDto> getSets() {
        return null;
    }
    
    @org.jetbrains.annotations.Nullable()
    public final com.orcafit.data.api.models.ProgressionDto getProgression() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final java.lang.String getNotes() {
        return null;
    }
    
    public ProgramExerciseDto() {
        super();
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
    
    @org.jetbrains.annotations.NotNull()
    public final java.util.List<com.orcafit.data.api.models.SetDto> component4() {
        return null;
    }
    
    @org.jetbrains.annotations.Nullable()
    public final com.orcafit.data.api.models.ProgressionDto component5() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final java.lang.String component6() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final com.orcafit.data.api.models.ProgramExerciseDto copy(@com.squareup.moshi.Json(name = "exercise_id")
    @org.jetbrains.annotations.NotNull()
    java.lang.String exerciseId, @com.squareup.moshi.Json(name = "exercise_name")
    @org.jetbrains.annotations.NotNull()
    java.lang.String exerciseName, int order, @org.jetbrains.annotations.NotNull()
    java.util.List<com.orcafit.data.api.models.SetDto> sets, @org.jetbrains.annotations.Nullable()
    com.orcafit.data.api.models.ProgressionDto progression, @org.jetbrains.annotations.NotNull()
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
package com.orcafit.data.api.models;

import com.squareup.moshi.Json;
import com.squareup.moshi.JsonClass;

@com.squareup.moshi.JsonClass(generateAdapter = true)
@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000(\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0000\n\u0002\u0010\b\n\u0000\n\u0002\u0010\u0007\n\u0002\b\u0006\n\u0002\u0010\u000e\n\u0002\b\u0002\n\u0002\u0010\u000b\n\u0002\b$\b\u0087\b\u0018\u00002\u00020\u0001B\u0083\u0001\u0012\b\b\u0001\u0010\u0002\u001a\u00020\u0003\u0012\n\b\u0003\u0010\u0004\u001a\u0004\u0018\u00010\u0005\u0012\n\b\u0002\u0010\u0006\u001a\u0004\u0018\u00010\u0003\u0012\n\b\u0002\u0010\u0007\u001a\u0004\u0018\u00010\u0005\u0012\n\b\u0003\u0010\b\u001a\u0004\u0018\u00010\u0003\u0012\n\b\u0003\u0010\t\u001a\u0004\u0018\u00010\u0005\u0012\n\b\u0003\u0010\n\u001a\u0004\u0018\u00010\u0003\u0012\n\b\u0003\u0010\u000b\u001a\u0004\u0018\u00010\f\u0012\n\b\u0002\u0010\r\u001a\u0004\u0018\u00010\f\u0012\b\b\u0003\u0010\u000e\u001a\u00020\u000f\u0012\b\b\u0003\u0010\u0010\u001a\u00020\u000f\u00a2\u0006\u0002\u0010\u0011J\t\u0010\"\u001a\u00020\u0003H\u00c6\u0003J\t\u0010#\u001a\u00020\u000fH\u00c6\u0003J\t\u0010$\u001a\u00020\u000fH\u00c6\u0003J\u0010\u0010%\u001a\u0004\u0018\u00010\u0005H\u00c6\u0003\u00a2\u0006\u0002\u0010\u0015J\u0010\u0010&\u001a\u0004\u0018\u00010\u0003H\u00c6\u0003\u00a2\u0006\u0002\u0010\u0018J\u0010\u0010\'\u001a\u0004\u0018\u00010\u0005H\u00c6\u0003\u00a2\u0006\u0002\u0010\u0015J\u0010\u0010(\u001a\u0004\u0018\u00010\u0003H\u00c6\u0003\u00a2\u0006\u0002\u0010\u0018J\u0010\u0010)\u001a\u0004\u0018\u00010\u0005H\u00c6\u0003\u00a2\u0006\u0002\u0010\u0015J\u0010\u0010*\u001a\u0004\u0018\u00010\u0003H\u00c6\u0003\u00a2\u0006\u0002\u0010\u0018J\u000b\u0010+\u001a\u0004\u0018\u00010\fH\u00c6\u0003J\u000b\u0010,\u001a\u0004\u0018\u00010\fH\u00c6\u0003J\u008c\u0001\u0010-\u001a\u00020\u00002\b\b\u0003\u0010\u0002\u001a\u00020\u00032\n\b\u0003\u0010\u0004\u001a\u0004\u0018\u00010\u00052\n\b\u0002\u0010\u0006\u001a\u0004\u0018\u00010\u00032\n\b\u0002\u0010\u0007\u001a\u0004\u0018\u00010\u00052\n\b\u0003\u0010\b\u001a\u0004\u0018\u00010\u00032\n\b\u0003\u0010\t\u001a\u0004\u0018\u00010\u00052\n\b\u0003\u0010\n\u001a\u0004\u0018\u00010\u00032\n\b\u0003\u0010\u000b\u001a\u0004\u0018\u00010\f2\n\b\u0002\u0010\r\u001a\u0004\u0018\u00010\f2\b\b\u0003\u0010\u000e\u001a\u00020\u000f2\b\b\u0003\u0010\u0010\u001a\u00020\u000fH\u00c6\u0001\u00a2\u0006\u0002\u0010.J\u0013\u0010/\u001a\u00020\u000f2\b\u00100\u001a\u0004\u0018\u00010\u0001H\u00d6\u0003J\t\u00101\u001a\u00020\u0003H\u00d6\u0001J\t\u00102\u001a\u00020\fH\u00d6\u0001R\u0013\u0010\u000b\u001a\u0004\u0018\u00010\f\u00a2\u0006\b\n\u0000\u001a\u0004\b\u0012\u0010\u0013R\u0015\u0010\t\u001a\u0004\u0018\u00010\u0005\u00a2\u0006\n\n\u0002\u0010\u0016\u001a\u0004\b\u0014\u0010\u0015R\u0015\u0010\b\u001a\u0004\u0018\u00010\u0003\u00a2\u0006\n\n\u0002\u0010\u0019\u001a\u0004\b\u0017\u0010\u0018R\u0015\u0010\n\u001a\u0004\u0018\u00010\u0003\u00a2\u0006\n\n\u0002\u0010\u0019\u001a\u0004\b\u001a\u0010\u0018R\u0011\u0010\u000e\u001a\u00020\u000f\u00a2\u0006\b\n\u0000\u001a\u0004\b\u000e\u0010\u001bR\u0011\u0010\u0010\u001a\u00020\u000f\u00a2\u0006\b\n\u0000\u001a\u0004\b\u0010\u0010\u001bR\u0013\u0010\r\u001a\u0004\u0018\u00010\f\u00a2\u0006\b\n\u0000\u001a\u0004\b\u001c\u0010\u0013R\u0015\u0010\u0006\u001a\u0004\u0018\u00010\u0003\u00a2\u0006\n\n\u0002\u0010\u0019\u001a\u0004\b\u001d\u0010\u0018R\u0015\u0010\u0007\u001a\u0004\u0018\u00010\u0005\u00a2\u0006\n\n\u0002\u0010\u0016\u001a\u0004\b\u001e\u0010\u0015R\u0011\u0010\u0002\u001a\u00020\u0003\u00a2\u0006\b\n\u0000\u001a\u0004\b\u001f\u0010 R\u0015\u0010\u0004\u001a\u0004\u0018\u00010\u0005\u00a2\u0006\n\n\u0002\u0010\u0016\u001a\u0004\b!\u0010\u0015\u00a8\u00063"}, d2 = {"Lcom/orcafit/data/api/models/LoggedSetDto;", "", "setNumber", "", "weightKg", "", "reps", "rpe", "durationSeconds", "distanceMeters", "heartRateAvg", "completedAt", "", "notes", "isPr", "", "isWarmup", "(ILjava/lang/Float;Ljava/lang/Integer;Ljava/lang/Float;Ljava/lang/Integer;Ljava/lang/Float;Ljava/lang/Integer;Ljava/lang/String;Ljava/lang/String;ZZ)V", "getCompletedAt", "()Ljava/lang/String;", "getDistanceMeters", "()Ljava/lang/Float;", "Ljava/lang/Float;", "getDurationSeconds", "()Ljava/lang/Integer;", "Ljava/lang/Integer;", "getHeartRateAvg", "()Z", "getNotes", "getReps", "getRpe", "getSetNumber", "()I", "getWeightKg", "component1", "component10", "component11", "component2", "component3", "component4", "component5", "component6", "component7", "component8", "component9", "copy", "(ILjava/lang/Float;Ljava/lang/Integer;Ljava/lang/Float;Ljava/lang/Integer;Ljava/lang/Float;Ljava/lang/Integer;Ljava/lang/String;Ljava/lang/String;ZZ)Lcom/orcafit/data/api/models/LoggedSetDto;", "equals", "other", "hashCode", "toString", "app_debug"})
public final class LoggedSetDto {
    private final int setNumber = 0;
    @org.jetbrains.annotations.Nullable()
    private final java.lang.Float weightKg = null;
    @org.jetbrains.annotations.Nullable()
    private final java.lang.Integer reps = null;
    @org.jetbrains.annotations.Nullable()
    private final java.lang.Float rpe = null;
    @org.jetbrains.annotations.Nullable()
    private final java.lang.Integer durationSeconds = null;
    @org.jetbrains.annotations.Nullable()
    private final java.lang.Float distanceMeters = null;
    @org.jetbrains.annotations.Nullable()
    private final java.lang.Integer heartRateAvg = null;
    @org.jetbrains.annotations.Nullable()
    private final java.lang.String completedAt = null;
    @org.jetbrains.annotations.Nullable()
    private final java.lang.String notes = null;
    private final boolean isPr = false;
    private final boolean isWarmup = false;
    
    public LoggedSetDto(@com.squareup.moshi.Json(name = "set_number")
    int setNumber, @com.squareup.moshi.Json(name = "weight_kg")
    @org.jetbrains.annotations.Nullable()
    java.lang.Float weightKg, @org.jetbrains.annotations.Nullable()
    java.lang.Integer reps, @org.jetbrains.annotations.Nullable()
    java.lang.Float rpe, @com.squareup.moshi.Json(name = "duration_seconds")
    @org.jetbrains.annotations.Nullable()
    java.lang.Integer durationSeconds, @com.squareup.moshi.Json(name = "distance_meters")
    @org.jetbrains.annotations.Nullable()
    java.lang.Float distanceMeters, @com.squareup.moshi.Json(name = "heart_rate_avg")
    @org.jetbrains.annotations.Nullable()
    java.lang.Integer heartRateAvg, @com.squareup.moshi.Json(name = "completed_at")
    @org.jetbrains.annotations.Nullable()
    java.lang.String completedAt, @org.jetbrains.annotations.Nullable()
    java.lang.String notes, @com.squareup.moshi.Json(name = "is_pr")
    boolean isPr, @com.squareup.moshi.Json(name = "is_warmup")
    boolean isWarmup) {
        super();
    }
    
    public final int getSetNumber() {
        return 0;
    }
    
    @org.jetbrains.annotations.Nullable()
    public final java.lang.Float getWeightKg() {
        return null;
    }
    
    @org.jetbrains.annotations.Nullable()
    public final java.lang.Integer getReps() {
        return null;
    }
    
    @org.jetbrains.annotations.Nullable()
    public final java.lang.Float getRpe() {
        return null;
    }
    
    @org.jetbrains.annotations.Nullable()
    public final java.lang.Integer getDurationSeconds() {
        return null;
    }
    
    @org.jetbrains.annotations.Nullable()
    public final java.lang.Float getDistanceMeters() {
        return null;
    }
    
    @org.jetbrains.annotations.Nullable()
    public final java.lang.Integer getHeartRateAvg() {
        return null;
    }
    
    @org.jetbrains.annotations.Nullable()
    public final java.lang.String getCompletedAt() {
        return null;
    }
    
    @org.jetbrains.annotations.Nullable()
    public final java.lang.String getNotes() {
        return null;
    }
    
    public final boolean isPr() {
        return false;
    }
    
    public final boolean isWarmup() {
        return false;
    }
    
    public final int component1() {
        return 0;
    }
    
    public final boolean component10() {
        return false;
    }
    
    public final boolean component11() {
        return false;
    }
    
    @org.jetbrains.annotations.Nullable()
    public final java.lang.Float component2() {
        return null;
    }
    
    @org.jetbrains.annotations.Nullable()
    public final java.lang.Integer component3() {
        return null;
    }
    
    @org.jetbrains.annotations.Nullable()
    public final java.lang.Float component4() {
        return null;
    }
    
    @org.jetbrains.annotations.Nullable()
    public final java.lang.Integer component5() {
        return null;
    }
    
    @org.jetbrains.annotations.Nullable()
    public final java.lang.Float component6() {
        return null;
    }
    
    @org.jetbrains.annotations.Nullable()
    public final java.lang.Integer component7() {
        return null;
    }
    
    @org.jetbrains.annotations.Nullable()
    public final java.lang.String component8() {
        return null;
    }
    
    @org.jetbrains.annotations.Nullable()
    public final java.lang.String component9() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final com.orcafit.data.api.models.LoggedSetDto copy(@com.squareup.moshi.Json(name = "set_number")
    int setNumber, @com.squareup.moshi.Json(name = "weight_kg")
    @org.jetbrains.annotations.Nullable()
    java.lang.Float weightKg, @org.jetbrains.annotations.Nullable()
    java.lang.Integer reps, @org.jetbrains.annotations.Nullable()
    java.lang.Float rpe, @com.squareup.moshi.Json(name = "duration_seconds")
    @org.jetbrains.annotations.Nullable()
    java.lang.Integer durationSeconds, @com.squareup.moshi.Json(name = "distance_meters")
    @org.jetbrains.annotations.Nullable()
    java.lang.Float distanceMeters, @com.squareup.moshi.Json(name = "heart_rate_avg")
    @org.jetbrains.annotations.Nullable()
    java.lang.Integer heartRateAvg, @com.squareup.moshi.Json(name = "completed_at")
    @org.jetbrains.annotations.Nullable()
    java.lang.String completedAt, @org.jetbrains.annotations.Nullable()
    java.lang.String notes, @com.squareup.moshi.Json(name = "is_pr")
    boolean isPr, @com.squareup.moshi.Json(name = "is_warmup")
    boolean isWarmup) {
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
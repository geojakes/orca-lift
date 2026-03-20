package com.orcafit.data.api.models;

import com.squareup.moshi.Json;
import com.squareup.moshi.JsonClass;

@com.squareup.moshi.JsonClass(generateAdapter = true)
@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000 \n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0000\n\u0002\u0010\b\n\u0002\b\u000f\n\u0002\u0010\u000b\n\u0002\b\u0003\n\u0002\u0010\u000e\n\u0000\b\u0087\b\u0018\u00002\u00020\u0001B%\u0012\n\b\u0003\u0010\u0002\u001a\u0004\u0018\u00010\u0003\u0012\b\b\u0003\u0010\u0004\u001a\u00020\u0003\u0012\b\b\u0003\u0010\u0005\u001a\u00020\u0003\u00a2\u0006\u0002\u0010\u0006J\u0010\u0010\r\u001a\u0004\u0018\u00010\u0003H\u00c6\u0003\u00a2\u0006\u0002\u0010\nJ\t\u0010\u000e\u001a\u00020\u0003H\u00c6\u0003J\t\u0010\u000f\u001a\u00020\u0003H\u00c6\u0003J.\u0010\u0010\u001a\u00020\u00002\n\b\u0003\u0010\u0002\u001a\u0004\u0018\u00010\u00032\b\b\u0003\u0010\u0004\u001a\u00020\u00032\b\b\u0003\u0010\u0005\u001a\u00020\u0003H\u00c6\u0001\u00a2\u0006\u0002\u0010\u0011J\u0013\u0010\u0012\u001a\u00020\u00132\b\u0010\u0014\u001a\u0004\u0018\u00010\u0001H\u00d6\u0003J\t\u0010\u0015\u001a\u00020\u0003H\u00d6\u0001J\t\u0010\u0016\u001a\u00020\u0017H\u00d6\u0001R\u0011\u0010\u0005\u001a\u00020\u0003\u00a2\u0006\b\n\u0000\u001a\u0004\b\u0007\u0010\bR\u0015\u0010\u0002\u001a\u0004\u0018\u00010\u0003\u00a2\u0006\n\n\u0002\u0010\u000b\u001a\u0004\b\t\u0010\nR\u0011\u0010\u0004\u001a\u00020\u0003\u00a2\u0006\b\n\u0000\u001a\u0004\b\f\u0010\b\u00a8\u0006\u0018"}, d2 = {"Lcom/orcafit/data/api/models/StartWorkoutRequest;", "", "programId", "", "weekNumber", "dayNumber", "(Ljava/lang/Integer;II)V", "getDayNumber", "()I", "getProgramId", "()Ljava/lang/Integer;", "Ljava/lang/Integer;", "getWeekNumber", "component1", "component2", "component3", "copy", "(Ljava/lang/Integer;II)Lcom/orcafit/data/api/models/StartWorkoutRequest;", "equals", "", "other", "hashCode", "toString", "", "app_debug"})
public final class StartWorkoutRequest {
    @org.jetbrains.annotations.Nullable()
    private final java.lang.Integer programId = null;
    private final int weekNumber = 0;
    private final int dayNumber = 0;
    
    public StartWorkoutRequest(@com.squareup.moshi.Json(name = "program_id")
    @org.jetbrains.annotations.Nullable()
    java.lang.Integer programId, @com.squareup.moshi.Json(name = "week_number")
    int weekNumber, @com.squareup.moshi.Json(name = "day_number")
    int dayNumber) {
        super();
    }
    
    @org.jetbrains.annotations.Nullable()
    public final java.lang.Integer getProgramId() {
        return null;
    }
    
    public final int getWeekNumber() {
        return 0;
    }
    
    public final int getDayNumber() {
        return 0;
    }
    
    public StartWorkoutRequest() {
        super();
    }
    
    @org.jetbrains.annotations.Nullable()
    public final java.lang.Integer component1() {
        return null;
    }
    
    public final int component2() {
        return 0;
    }
    
    public final int component3() {
        return 0;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final com.orcafit.data.api.models.StartWorkoutRequest copy(@com.squareup.moshi.Json(name = "program_id")
    @org.jetbrains.annotations.Nullable()
    java.lang.Integer programId, @com.squareup.moshi.Json(name = "week_number")
    int weekNumber, @com.squareup.moshi.Json(name = "day_number")
    int dayNumber) {
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
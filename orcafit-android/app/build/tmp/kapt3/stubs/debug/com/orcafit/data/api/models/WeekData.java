package com.orcafit.data.api.models;

import com.squareup.moshi.Json;
import com.squareup.moshi.JsonClass;

@com.squareup.moshi.JsonClass(generateAdapter = true)
@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000(\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0000\n\u0002\u0010\b\n\u0000\n\u0002\u0010\u000b\n\u0000\n\u0002\u0010 \n\u0002\u0018\u0002\n\u0002\b\u000e\n\u0002\u0010\u000e\n\u0000\b\u0087\b\u0018\u00002\u00020\u0001B)\u0012\b\b\u0001\u0010\u0002\u001a\u00020\u0003\u0012\b\b\u0003\u0010\u0004\u001a\u00020\u0005\u0012\u000e\b\u0002\u0010\u0006\u001a\b\u0012\u0004\u0012\u00020\b0\u0007\u00a2\u0006\u0002\u0010\tJ\t\u0010\u000f\u001a\u00020\u0003H\u00c6\u0003J\t\u0010\u0010\u001a\u00020\u0005H\u00c6\u0003J\u000f\u0010\u0011\u001a\b\u0012\u0004\u0012\u00020\b0\u0007H\u00c6\u0003J-\u0010\u0012\u001a\u00020\u00002\b\b\u0003\u0010\u0002\u001a\u00020\u00032\b\b\u0003\u0010\u0004\u001a\u00020\u00052\u000e\b\u0002\u0010\u0006\u001a\b\u0012\u0004\u0012\u00020\b0\u0007H\u00c6\u0001J\u0013\u0010\u0013\u001a\u00020\u00052\b\u0010\u0014\u001a\u0004\u0018\u00010\u0001H\u00d6\u0003J\t\u0010\u0015\u001a\u00020\u0003H\u00d6\u0001J\t\u0010\u0016\u001a\u00020\u0017H\u00d6\u0001R\u0017\u0010\u0006\u001a\b\u0012\u0004\u0012\u00020\b0\u0007\u00a2\u0006\b\n\u0000\u001a\u0004\b\n\u0010\u000bR\u0011\u0010\u0004\u001a\u00020\u0005\u00a2\u0006\b\n\u0000\u001a\u0004\b\u0004\u0010\fR\u0011\u0010\u0002\u001a\u00020\u0003\u00a2\u0006\b\n\u0000\u001a\u0004\b\r\u0010\u000e\u00a8\u0006\u0018"}, d2 = {"Lcom/orcafit/data/api/models/WeekData;", "", "weekNumber", "", "isDeload", "", "days", "", "Lcom/orcafit/data/api/models/DayData;", "(IZLjava/util/List;)V", "getDays", "()Ljava/util/List;", "()Z", "getWeekNumber", "()I", "component1", "component2", "component3", "copy", "equals", "other", "hashCode", "toString", "", "app_debug"})
public final class WeekData {
    private final int weekNumber = 0;
    private final boolean isDeload = false;
    @org.jetbrains.annotations.NotNull()
    private final java.util.List<com.orcafit.data.api.models.DayData> days = null;
    
    public WeekData(@com.squareup.moshi.Json(name = "week_number")
    int weekNumber, @com.squareup.moshi.Json(name = "is_deload")
    boolean isDeload, @org.jetbrains.annotations.NotNull()
    java.util.List<com.orcafit.data.api.models.DayData> days) {
        super();
    }
    
    public final int getWeekNumber() {
        return 0;
    }
    
    public final boolean isDeload() {
        return false;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final java.util.List<com.orcafit.data.api.models.DayData> getDays() {
        return null;
    }
    
    public final int component1() {
        return 0;
    }
    
    public final boolean component2() {
        return false;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final java.util.List<com.orcafit.data.api.models.DayData> component3() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final com.orcafit.data.api.models.WeekData copy(@com.squareup.moshi.Json(name = "week_number")
    int weekNumber, @com.squareup.moshi.Json(name = "is_deload")
    boolean isDeload, @org.jetbrains.annotations.NotNull()
    java.util.List<com.orcafit.data.api.models.DayData> days) {
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
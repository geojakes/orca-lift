-if class com.orcafit.data.api.models.WorkoutSummaryResponse
-keepnames class com.orcafit.data.api.models.WorkoutSummaryResponse
-if class com.orcafit.data.api.models.WorkoutSummaryResponse
-keep class com.orcafit.data.api.models.WorkoutSummaryResponseJsonAdapter {
    public <init>(com.squareup.moshi.Moshi);
}
-if class com.orcafit.data.api.models.WorkoutSummaryResponse
-keepnames class kotlin.jvm.internal.DefaultConstructorMarker
-if class com.orcafit.data.api.models.WorkoutSummaryResponse
-keepclassmembers class com.orcafit.data.api.models.WorkoutSummaryResponse {
    public synthetic <init>(java.lang.String,int,int,int,float,int,kotlin.jvm.internal.DefaultConstructorMarker);
}

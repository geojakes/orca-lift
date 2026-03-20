-if class com.orcafit.data.api.models.ActiveWorkoutResponse
-keepnames class com.orcafit.data.api.models.ActiveWorkoutResponse
-if class com.orcafit.data.api.models.ActiveWorkoutResponse
-keep class com.orcafit.data.api.models.ActiveWorkoutResponseJsonAdapter {
    public <init>(com.squareup.moshi.Moshi);
}
-if class com.orcafit.data.api.models.ActiveWorkoutResponse
-keepnames class kotlin.jvm.internal.DefaultConstructorMarker
-if class com.orcafit.data.api.models.ActiveWorkoutResponse
-keepclassmembers class com.orcafit.data.api.models.ActiveWorkoutResponse {
    public synthetic <init>(boolean,com.orcafit.data.api.models.WorkoutResponse,int,kotlin.jvm.internal.DefaultConstructorMarker);
}

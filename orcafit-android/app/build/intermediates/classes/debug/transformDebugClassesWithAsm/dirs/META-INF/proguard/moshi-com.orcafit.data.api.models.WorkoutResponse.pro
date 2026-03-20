-if class com.orcafit.data.api.models.WorkoutResponse
-keepnames class com.orcafit.data.api.models.WorkoutResponse
-if class com.orcafit.data.api.models.WorkoutResponse
-keep class com.orcafit.data.api.models.WorkoutResponseJsonAdapter {
    public <init>(com.squareup.moshi.Moshi);
}
-if class com.orcafit.data.api.models.WorkoutResponse
-keepnames class kotlin.jvm.internal.DefaultConstructorMarker
-if class com.orcafit.data.api.models.WorkoutResponse
-keepclassmembers class com.orcafit.data.api.models.WorkoutResponse {
    public synthetic <init>(java.lang.Integer,int,int,int,java.lang.String,java.lang.String,java.util.List,java.lang.String,java.lang.String,java.lang.String,java.lang.Integer,int,kotlin.jvm.internal.DefaultConstructorMarker);
}

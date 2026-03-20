-if class com.orcafit.data.api.models.JobStatusResponse
-keepnames class com.orcafit.data.api.models.JobStatusResponse
-if class com.orcafit.data.api.models.JobStatusResponse
-keep class com.orcafit.data.api.models.JobStatusResponseJsonAdapter {
    public <init>(com.squareup.moshi.Moshi);
}
-if class com.orcafit.data.api.models.JobStatusResponse
-keepnames class kotlin.jvm.internal.DefaultConstructorMarker
-if class com.orcafit.data.api.models.JobStatusResponse
-keepclassmembers class com.orcafit.data.api.models.JobStatusResponse {
    public synthetic <init>(java.lang.String,java.lang.String,java.util.Map,java.lang.String,int,kotlin.jvm.internal.DefaultConstructorMarker);
}

-if class com.orcafit.data.api.models.LogSetResponse
-keepnames class com.orcafit.data.api.models.LogSetResponse
-if class com.orcafit.data.api.models.LogSetResponse
-keep class com.orcafit.data.api.models.LogSetResponseJsonAdapter {
    public <init>(com.squareup.moshi.Moshi);
}
-if class com.orcafit.data.api.models.LogSetResponse
-keepnames class kotlin.jvm.internal.DefaultConstructorMarker
-if class com.orcafit.data.api.models.LogSetResponse
-keepclassmembers class com.orcafit.data.api.models.LogSetResponse {
    public synthetic <init>(java.lang.String,java.lang.String,int,int,int,int,kotlin.jvm.internal.DefaultConstructorMarker);
}

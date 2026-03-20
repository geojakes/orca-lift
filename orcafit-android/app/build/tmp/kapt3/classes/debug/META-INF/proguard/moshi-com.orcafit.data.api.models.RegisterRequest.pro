-if class com.orcafit.data.api.models.RegisterRequest
-keepnames class com.orcafit.data.api.models.RegisterRequest
-if class com.orcafit.data.api.models.RegisterRequest
-keep class com.orcafit.data.api.models.RegisterRequestJsonAdapter {
    public <init>(com.squareup.moshi.Moshi);
}
-if class com.orcafit.data.api.models.RegisterRequest
-keepnames class kotlin.jvm.internal.DefaultConstructorMarker
-if class com.orcafit.data.api.models.RegisterRequest
-keepclassmembers class com.orcafit.data.api.models.RegisterRequest {
    public synthetic <init>(java.lang.String,java.lang.String,java.lang.String,int,kotlin.jvm.internal.DefaultConstructorMarker);
}

-if class com.orcafit.data.api.models.TokenResponse
-keepnames class com.orcafit.data.api.models.TokenResponse
-if class com.orcafit.data.api.models.TokenResponse
-keep class com.orcafit.data.api.models.TokenResponseJsonAdapter {
    public <init>(com.squareup.moshi.Moshi);
}
-if class com.orcafit.data.api.models.TokenResponse
-keepnames class kotlin.jvm.internal.DefaultConstructorMarker
-if class com.orcafit.data.api.models.TokenResponse
-keepclassmembers class com.orcafit.data.api.models.TokenResponse {
    public synthetic <init>(java.lang.String,java.lang.String,java.lang.String,int,int,kotlin.jvm.internal.DefaultConstructorMarker);
}

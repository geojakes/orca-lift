-if class com.orcafit.data.api.models.LoginRequest
-keepnames class com.orcafit.data.api.models.LoginRequest
-if class com.orcafit.data.api.models.LoginRequest
-keep class com.orcafit.data.api.models.LoginRequestJsonAdapter {
    public <init>(com.squareup.moshi.Moshi);
}

-if class com.orcafit.data.api.models.UserResponse
-keepnames class com.orcafit.data.api.models.UserResponse
-if class com.orcafit.data.api.models.UserResponse
-keep class com.orcafit.data.api.models.UserResponseJsonAdapter {
    public <init>(com.squareup.moshi.Moshi);
}

-if class com.orcafit.data.api.models.StatsResponse
-keepnames class com.orcafit.data.api.models.StatsResponse
-if class com.orcafit.data.api.models.StatsResponse
-keep class com.orcafit.data.api.models.StatsResponseJsonAdapter {
    public <init>(com.squareup.moshi.Moshi);
}
-if class com.orcafit.data.api.models.StatsResponse
-keepnames class kotlin.jvm.internal.DefaultConstructorMarker
-if class com.orcafit.data.api.models.StatsResponse
-keepclassmembers class com.orcafit.data.api.models.StatsResponse {
    public synthetic <init>(int,float,int,kotlin.jvm.internal.DefaultConstructorMarker);
}

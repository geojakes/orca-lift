-if class com.orcafit.data.api.models.DayData
-keepnames class com.orcafit.data.api.models.DayData
-if class com.orcafit.data.api.models.DayData
-keep class com.orcafit.data.api.models.DayDataJsonAdapter {
    public <init>(com.squareup.moshi.Moshi);
}
-if class com.orcafit.data.api.models.DayData
-keepnames class kotlin.jvm.internal.DefaultConstructorMarker
-if class com.orcafit.data.api.models.DayData
-keepclassmembers class com.orcafit.data.api.models.DayData {
    public synthetic <init>(int,java.lang.String,java.lang.String,java.util.List,int,kotlin.jvm.internal.DefaultConstructorMarker);
}

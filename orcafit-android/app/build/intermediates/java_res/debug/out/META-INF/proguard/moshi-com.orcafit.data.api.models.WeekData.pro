-if class com.orcafit.data.api.models.WeekData
-keepnames class com.orcafit.data.api.models.WeekData
-if class com.orcafit.data.api.models.WeekData
-keep class com.orcafit.data.api.models.WeekDataJsonAdapter {
    public <init>(com.squareup.moshi.Moshi);
}
-if class com.orcafit.data.api.models.WeekData
-keepnames class kotlin.jvm.internal.DefaultConstructorMarker
-if class com.orcafit.data.api.models.WeekData
-keepclassmembers class com.orcafit.data.api.models.WeekData {
    public synthetic <init>(int,boolean,java.util.List,int,kotlin.jvm.internal.DefaultConstructorMarker);
}

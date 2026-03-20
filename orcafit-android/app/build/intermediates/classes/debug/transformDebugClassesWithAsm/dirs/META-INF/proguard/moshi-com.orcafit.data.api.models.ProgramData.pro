-if class com.orcafit.data.api.models.ProgramData
-keepnames class com.orcafit.data.api.models.ProgramData
-if class com.orcafit.data.api.models.ProgramData
-keep class com.orcafit.data.api.models.ProgramDataJsonAdapter {
    public <init>(com.squareup.moshi.Moshi);
}
-if class com.orcafit.data.api.models.ProgramData
-keepnames class kotlin.jvm.internal.DefaultConstructorMarker
-if class com.orcafit.data.api.models.ProgramData
-keepclassmembers class com.orcafit.data.api.models.ProgramData {
    public synthetic <init>(java.lang.String,java.lang.String,java.lang.String,java.lang.String,int,int,java.util.List,int,kotlin.jvm.internal.DefaultConstructorMarker);
}

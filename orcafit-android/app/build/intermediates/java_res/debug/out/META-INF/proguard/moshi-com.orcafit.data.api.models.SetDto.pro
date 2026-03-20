-if class com.orcafit.data.api.models.SetDto
-keepnames class com.orcafit.data.api.models.SetDto
-if class com.orcafit.data.api.models.SetDto
-keep class com.orcafit.data.api.models.SetDtoJsonAdapter {
    public <init>(com.squareup.moshi.Moshi);
}
-if class com.orcafit.data.api.models.SetDto
-keepnames class kotlin.jvm.internal.DefaultConstructorMarker
-if class com.orcafit.data.api.models.SetDto
-keepclassmembers class com.orcafit.data.api.models.SetDto {
    public synthetic <init>(int,java.lang.String,java.lang.Integer,java.lang.Integer,java.lang.Float,java.lang.Integer,int,kotlin.jvm.internal.DefaultConstructorMarker);
}

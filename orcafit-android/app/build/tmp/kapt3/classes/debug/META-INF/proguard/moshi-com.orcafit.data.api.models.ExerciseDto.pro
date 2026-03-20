-if class com.orcafit.data.api.models.ExerciseDto
-keepnames class com.orcafit.data.api.models.ExerciseDto
-if class com.orcafit.data.api.models.ExerciseDto
-keep class com.orcafit.data.api.models.ExerciseDtoJsonAdapter {
    public <init>(com.squareup.moshi.Moshi);
}
-if class com.orcafit.data.api.models.ExerciseDto
-keepnames class kotlin.jvm.internal.DefaultConstructorMarker
-if class com.orcafit.data.api.models.ExerciseDto
-keepclassmembers class com.orcafit.data.api.models.ExerciseDto {
    public synthetic <init>(java.lang.String,java.util.List,java.lang.String,java.util.List,java.lang.String,java.util.List,boolean,java.lang.String,int,kotlin.jvm.internal.DefaultConstructorMarker);
}

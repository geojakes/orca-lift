package com.orcafit.data.api.models

import com.squareup.moshi.Json
import com.squareup.moshi.JsonClass

// Auth
@JsonClass(generateAdapter = true)
data class RegisterRequest(val email: String, val password: String, val name: String = "")

@JsonClass(generateAdapter = true)
data class LoginRequest(val email: String, val password: String)

@JsonClass(generateAdapter = true)
data class TokenResponse(
    @Json(name = "access_token") val accessToken: String,
    @Json(name = "refresh_token") val refreshToken: String,
    @Json(name = "token_type") val tokenType: String = "bearer",
    @Json(name = "expires_in") val expiresIn: Int = 3600,
)

@JsonClass(generateAdapter = true)
data class UserResponse(val id: Int, val email: String, val name: String)

// Exercises
@JsonClass(generateAdapter = true)
data class ExerciseListResponse(val exercises: List<ExerciseDto>, val total: Int)

@JsonClass(generateAdapter = true)
data class ExerciseDto(
    val name: String,
    @Json(name = "muscle_groups") val muscleGroups: List<String> = emptyList(),
    @Json(name = "movement_pattern") val movementPattern: String = "",
    val equipment: List<String> = emptyList(),
    val category: String = "resistance",
    val aliases: List<String> = emptyList(),
    @Json(name = "is_compound") val isCompound: Boolean = false,
    @Json(name = "cardio_type") val cardioType: String? = null,
)

// Programs
@JsonClass(generateAdapter = true)
data class GenerateProgramRequest(
    val goals: String,
    @Json(name = "days_per_week") val daysPerWeek: Int = 4,
    val weeks: Int = 4,
    val format: String = "orcafit",
)

@JsonClass(generateAdapter = true)
data class GenerateResponse(
    @Json(name = "job_id") val jobId: String,
    val status: String = "pending",
)

@JsonClass(generateAdapter = true)
data class JobStatusResponse(
    @Json(name = "job_id") val jobId: String,
    val status: String,
    val result: Map<String, Any>? = null,
    val error: String? = null,
)

@JsonClass(generateAdapter = true)
data class ProgramListResponse(val programs: List<ProgramSummaryDto>)

@JsonClass(generateAdapter = true)
data class ProgramSummaryDto(
    val id: Int,
    val name: String,
    val description: String = "",
    val goals: String = "",
    val weeks: Int = 0,
    @Json(name = "days_per_week") val daysPerWeek: Int = 0,
    @Json(name = "created_at") val createdAt: String? = null,
)

@JsonClass(generateAdapter = true)
data class ProgramDetailResponse(
    val format: String = "orcafit",
    val version: String = "1.0",
    val program: ProgramData? = null,
)

@JsonClass(generateAdapter = true)
data class ProgramData(
    val id: String = "",
    val name: String = "",
    val description: String = "",
    val goals: String = "",
    @Json(name = "duration_weeks") val durationWeeks: Int = 0,
    @Json(name = "days_per_week") val daysPerWeek: Int = 0,
    val weeks: List<WeekData> = emptyList(),
)

@JsonClass(generateAdapter = true)
data class WeekData(
    @Json(name = "week_number") val weekNumber: Int,
    @Json(name = "is_deload") val isDeload: Boolean = false,
    val days: List<DayData> = emptyList(),
)

@JsonClass(generateAdapter = true)
data class DayData(
    @Json(name = "day_number") val dayNumber: Int,
    val name: String = "",
    val focus: String = "",
    val exercises: List<ProgramExerciseDto> = emptyList(),
)

@JsonClass(generateAdapter = true)
data class ProgramExerciseDto(
    @Json(name = "exercise_id") val exerciseId: String = "",
    @Json(name = "exercise_name") val exerciseName: String = "",
    val order: Int = 0,
    val sets: List<SetDto> = emptyList(),
    val progression: ProgressionDto? = null,
    val notes: String = "",
)

@JsonClass(generateAdapter = true)
data class SetDto(
    @Json(name = "set_number") val setNumber: Int,
    val type: String = "working",
    @Json(name = "target_reps") val targetReps: Int? = null,
    @Json(name = "target_reps_max") val targetRepsMax: Int? = null,
    @Json(name = "target_rpe") val targetRpe: Float? = null,
    @Json(name = "rest_seconds") val restSeconds: Int? = null,
)

@JsonClass(generateAdapter = true)
data class ProgressionDto(val type: String = "double", val params: Map<String, Any> = emptyMap())

@JsonClass(generateAdapter = true)
data class ActivateResponse(val status: String, @Json(name = "program_id") val programId: Int)

// Workouts
@JsonClass(generateAdapter = true)
data class StartWorkoutRequest(
    @Json(name = "program_id") val programId: Int? = null,
    @Json(name = "week_number") val weekNumber: Int = 1,
    @Json(name = "day_number") val dayNumber: Int = 1,
)

@JsonClass(generateAdapter = true)
data class WorkoutResponse(
    val id: Int? = null,
    @Json(name = "program_id") val programId: Int = 0,
    @Json(name = "week_number") val weekNumber: Int = 0,
    @Json(name = "day_number") val dayNumber: Int = 0,
    @Json(name = "day_name") val dayName: String = "",
    val status: String = "planned",
    val exercises: List<WorkoutExerciseDto> = emptyList(),
    @Json(name = "started_at") val startedAt: String? = null,
    @Json(name = "completed_at") val completedAt: String? = null,
    val notes: String = "",
    @Json(name = "total_duration_seconds") val totalDurationSeconds: Int? = null,
)

@JsonClass(generateAdapter = true)
data class WorkoutExerciseDto(
    @Json(name = "exercise_id") val exerciseId: String,
    @Json(name = "exercise_name") val exerciseName: String = "",
    val order: Int = 0,
    @Json(name = "target_sets") val targetSets: Int = 0,
    @Json(name = "logged_sets") val loggedSets: List<LoggedSetDto> = emptyList(),
    val skipped: Boolean = false,
    val notes: String = "",
)

@JsonClass(generateAdapter = true)
data class LoggedSetDto(
    @Json(name = "set_number") val setNumber: Int,
    @Json(name = "weight_kg") val weightKg: Float? = null,
    val reps: Int? = null,
    val rpe: Float? = null,
    @Json(name = "duration_seconds") val durationSeconds: Int? = null,
    @Json(name = "distance_meters") val distanceMeters: Float? = null,
    @Json(name = "heart_rate_avg") val heartRateAvg: Int? = null,
    @Json(name = "completed_at") val completedAt: String? = null,
    val notes: String? = null,
    @Json(name = "is_pr") val isPr: Boolean = false,
    @Json(name = "is_warmup") val isWarmup: Boolean = false,
)

@JsonClass(generateAdapter = true)
data class ActiveWorkoutResponse(
    val active: Boolean,
    val workout: WorkoutResponse? = null,
)

@JsonClass(generateAdapter = true)
data class LogSetRequest(
    @Json(name = "exercise_index") val exerciseIndex: Int,
    @Json(name = "set_number") val setNumber: Int,
    @Json(name = "weight_kg") val weightKg: Float? = null,
    val reps: Int? = null,
    val rpe: Float? = null,
    @Json(name = "duration_seconds") val durationSeconds: Int? = null,
    @Json(name = "distance_meters") val distanceMeters: Float? = null,
    @Json(name = "heart_rate_avg") val heartRateAvg: Int? = null,
    @Json(name = "heart_rate_max") val heartRateMax: Int? = null,
    @Json(name = "rest_seconds") val restSeconds: Int? = null,
    val notes: String? = null,
    @Json(name = "is_warmup") val isWarmup: Boolean = false,
)

@JsonClass(generateAdapter = true)
data class LogSetResponse(
    val status: String,
    val exercise: String = "",
    @Json(name = "set_number") val setNumber: Int = 0,
    @Json(name = "sets_completed") val setsCompleted: Int = 0,
    @Json(name = "sets_target") val setsTarget: Int = 0,
)

@JsonClass(generateAdapter = true)
data class WorkoutSummaryResponse(
    val status: String,
    @Json(name = "duration_minutes") val durationMinutes: Int = 0,
    @Json(name = "exercises_completed") val exercisesCompleted: Int = 0,
    @Json(name = "total_exercises") val totalExercises: Int = 0,
    @Json(name = "total_volume_kg") val totalVolumeKg: Float = 0f,
)

@JsonClass(generateAdapter = true)
data class WorkoutListResponse(val workouts: List<WorkoutSummaryDto>)

@JsonClass(generateAdapter = true)
data class WorkoutSummaryDto(
    val id: Int,
    @Json(name = "program_id") val programId: Int = 0,
    @Json(name = "day_name") val dayName: String = "",
    val status: String = "",
    @Json(name = "started_at") val startedAt: String? = null,
    @Json(name = "completed_at") val completedAt: String? = null,
    @Json(name = "duration_minutes") val durationMinutes: Int = 0,
    @Json(name = "exercises_completed") val exercisesCompleted: Int = 0,
    @Json(name = "total_volume_kg") val totalVolumeKg: Float = 0f,
)

// Stats
@JsonClass(generateAdapter = true)
data class StatsResponse(
    @Json(name = "total_workouts") val totalWorkouts: Int = 0,
    @Json(name = "total_volume_kg") val totalVolumeKg: Float = 0f,
)

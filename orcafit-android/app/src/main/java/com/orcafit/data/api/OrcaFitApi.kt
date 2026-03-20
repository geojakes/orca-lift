package com.orcafit.data.api

import com.orcafit.data.api.models.*
import retrofit2.Response
import retrofit2.http.*

interface OrcaFitApi {

    // Auth
    @POST("api/v1/auth/register")
    suspend fun register(@Body request: RegisterRequest): Response<TokenResponse>

    @POST("api/v1/auth/login")
    suspend fun login(@Body request: LoginRequest): Response<TokenResponse>

    @GET("api/v1/auth/me")
    suspend fun getMe(): Response<UserResponse>

    // Exercises
    @GET("api/v1/exercises")
    suspend fun listExercises(
        @Query("category") category: String? = null,
        @Query("muscle_group") muscleGroup: String? = null,
        @Query("search") search: String? = null,
    ): Response<ExerciseListResponse>

    // Programs
    @POST("api/v1/programs/generate")
    suspend fun generateProgram(@Body request: GenerateProgramRequest): Response<GenerateResponse>

    @GET("api/v1/programs/generate/{jobId}/status")
    suspend fun getGenerationStatus(@Path("jobId") jobId: String): Response<JobStatusResponse>

    @GET("api/v1/programs")
    suspend fun listPrograms(): Response<ProgramListResponse>

    @GET("api/v1/programs/{id}")
    suspend fun getProgram(@Path("id") id: Int): Response<ProgramDetailResponse>

    @POST("api/v1/programs/{id}/activate")
    suspend fun activateProgram(@Path("id") id: Int): Response<ActivateResponse>

    // Workouts
    @POST("api/v1/workouts/start")
    suspend fun startWorkout(@Body request: StartWorkoutRequest): Response<WorkoutResponse>

    @GET("api/v1/workouts/active")
    suspend fun getActiveWorkout(): Response<ActiveWorkoutResponse>

    @PUT("api/v1/workouts/{id}/log")
    suspend fun logSet(@Path("id") id: Int, @Body request: LogSetRequest): Response<LogSetResponse>

    @POST("api/v1/workouts/{id}/complete")
    suspend fun completeWorkout(@Path("id") id: Int): Response<WorkoutSummaryResponse>

    @GET("api/v1/workouts")
    suspend fun listWorkouts(@Query("limit") limit: Int = 50): Response<WorkoutListResponse>

    @GET("api/v1/workouts/{id}")
    suspend fun getWorkout(@Path("id") id: Int): Response<WorkoutResponse>

    // Profile
    @GET("api/v1/profile/stats")
    suspend fun getStats(): Response<StatsResponse>
}

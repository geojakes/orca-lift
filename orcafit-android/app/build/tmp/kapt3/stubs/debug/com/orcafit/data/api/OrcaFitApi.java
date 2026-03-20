package com.orcafit.data.api;

import com.orcafit.data.api.models.*;
import retrofit2.Response;
import retrofit2.http.*;

@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000\u009c\u0001\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0000\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\b\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\u000e\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0005\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0002\b\u0002\bf\u0018\u00002\u00020\u0001J\u001e\u0010\u0002\u001a\b\u0012\u0004\u0012\u00020\u00040\u00032\b\b\u0001\u0010\u0005\u001a\u00020\u0006H\u00a7@\u00a2\u0006\u0002\u0010\u0007J\u001e\u0010\b\u001a\b\u0012\u0004\u0012\u00020\t0\u00032\b\b\u0001\u0010\u0005\u001a\u00020\u0006H\u00a7@\u00a2\u0006\u0002\u0010\u0007J\u001e\u0010\n\u001a\b\u0012\u0004\u0012\u00020\u000b0\u00032\b\b\u0001\u0010\f\u001a\u00020\rH\u00a7@\u00a2\u0006\u0002\u0010\u000eJ\u0014\u0010\u000f\u001a\b\u0012\u0004\u0012\u00020\u00100\u0003H\u00a7@\u00a2\u0006\u0002\u0010\u0011J\u001e\u0010\u0012\u001a\b\u0012\u0004\u0012\u00020\u00130\u00032\b\b\u0001\u0010\u0014\u001a\u00020\u0015H\u00a7@\u00a2\u0006\u0002\u0010\u0016J\u0014\u0010\u0017\u001a\b\u0012\u0004\u0012\u00020\u00180\u0003H\u00a7@\u00a2\u0006\u0002\u0010\u0011J\u001e\u0010\u0019\u001a\b\u0012\u0004\u0012\u00020\u001a0\u00032\b\b\u0001\u0010\u0005\u001a\u00020\u0006H\u00a7@\u00a2\u0006\u0002\u0010\u0007J\u0014\u0010\u001b\u001a\b\u0012\u0004\u0012\u00020\u001c0\u0003H\u00a7@\u00a2\u0006\u0002\u0010\u0011J\u001e\u0010\u001d\u001a\b\u0012\u0004\u0012\u00020\u001e0\u00032\b\b\u0001\u0010\u0005\u001a\u00020\u0006H\u00a7@\u00a2\u0006\u0002\u0010\u0007J8\u0010\u001f\u001a\b\u0012\u0004\u0012\u00020 0\u00032\n\b\u0003\u0010!\u001a\u0004\u0018\u00010\u00152\n\b\u0003\u0010\"\u001a\u0004\u0018\u00010\u00152\n\b\u0003\u0010#\u001a\u0004\u0018\u00010\u0015H\u00a7@\u00a2\u0006\u0002\u0010$J\u0014\u0010%\u001a\b\u0012\u0004\u0012\u00020&0\u0003H\u00a7@\u00a2\u0006\u0002\u0010\u0011J\u001e\u0010\'\u001a\b\u0012\u0004\u0012\u00020(0\u00032\b\b\u0003\u0010)\u001a\u00020\u0006H\u00a7@\u00a2\u0006\u0002\u0010\u0007J(\u0010*\u001a\b\u0012\u0004\u0012\u00020+0\u00032\b\b\u0001\u0010\u0005\u001a\u00020\u00062\b\b\u0001\u0010\f\u001a\u00020,H\u00a7@\u00a2\u0006\u0002\u0010-J\u001e\u0010.\u001a\b\u0012\u0004\u0012\u00020/0\u00032\b\b\u0001\u0010\f\u001a\u000200H\u00a7@\u00a2\u0006\u0002\u00101J\u001e\u00102\u001a\b\u0012\u0004\u0012\u00020/0\u00032\b\b\u0001\u0010\f\u001a\u000203H\u00a7@\u00a2\u0006\u0002\u00104J\u001e\u00105\u001a\b\u0012\u0004\u0012\u00020\u001e0\u00032\b\b\u0001\u0010\f\u001a\u000206H\u00a7@\u00a2\u0006\u0002\u00107\u00a8\u00068"}, d2 = {"Lcom/orcafit/data/api/OrcaFitApi;", "", "activateProgram", "Lretrofit2/Response;", "Lcom/orcafit/data/api/models/ActivateResponse;", "id", "", "(ILkotlin/coroutines/Continuation;)Ljava/lang/Object;", "completeWorkout", "Lcom/orcafit/data/api/models/WorkoutSummaryResponse;", "generateProgram", "Lcom/orcafit/data/api/models/GenerateResponse;", "request", "Lcom/orcafit/data/api/models/GenerateProgramRequest;", "(Lcom/orcafit/data/api/models/GenerateProgramRequest;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;", "getActiveWorkout", "Lcom/orcafit/data/api/models/ActiveWorkoutResponse;", "(Lkotlin/coroutines/Continuation;)Ljava/lang/Object;", "getGenerationStatus", "Lcom/orcafit/data/api/models/JobStatusResponse;", "jobId", "", "(Ljava/lang/String;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;", "getMe", "Lcom/orcafit/data/api/models/UserResponse;", "getProgram", "Lcom/orcafit/data/api/models/ProgramDetailResponse;", "getStats", "Lcom/orcafit/data/api/models/StatsResponse;", "getWorkout", "Lcom/orcafit/data/api/models/WorkoutResponse;", "listExercises", "Lcom/orcafit/data/api/models/ExerciseListResponse;", "category", "muscleGroup", "search", "(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;", "listPrograms", "Lcom/orcafit/data/api/models/ProgramListResponse;", "listWorkouts", "Lcom/orcafit/data/api/models/WorkoutListResponse;", "limit", "logSet", "Lcom/orcafit/data/api/models/LogSetResponse;", "Lcom/orcafit/data/api/models/LogSetRequest;", "(ILcom/orcafit/data/api/models/LogSetRequest;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;", "login", "Lcom/orcafit/data/api/models/TokenResponse;", "Lcom/orcafit/data/api/models/LoginRequest;", "(Lcom/orcafit/data/api/models/LoginRequest;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;", "register", "Lcom/orcafit/data/api/models/RegisterRequest;", "(Lcom/orcafit/data/api/models/RegisterRequest;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;", "startWorkout", "Lcom/orcafit/data/api/models/StartWorkoutRequest;", "(Lcom/orcafit/data/api/models/StartWorkoutRequest;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;", "app_debug"})
public abstract interface OrcaFitApi {
    
    @retrofit2.http.POST(value = "api/v1/auth/register")
    @org.jetbrains.annotations.Nullable()
    public abstract java.lang.Object register(@retrofit2.http.Body()
    @org.jetbrains.annotations.NotNull()
    com.orcafit.data.api.models.RegisterRequest request, @org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super retrofit2.Response<com.orcafit.data.api.models.TokenResponse>> $completion);
    
    @retrofit2.http.POST(value = "api/v1/auth/login")
    @org.jetbrains.annotations.Nullable()
    public abstract java.lang.Object login(@retrofit2.http.Body()
    @org.jetbrains.annotations.NotNull()
    com.orcafit.data.api.models.LoginRequest request, @org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super retrofit2.Response<com.orcafit.data.api.models.TokenResponse>> $completion);
    
    @retrofit2.http.GET(value = "api/v1/auth/me")
    @org.jetbrains.annotations.Nullable()
    public abstract java.lang.Object getMe(@org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super retrofit2.Response<com.orcafit.data.api.models.UserResponse>> $completion);
    
    @retrofit2.http.GET(value = "api/v1/exercises")
    @org.jetbrains.annotations.Nullable()
    public abstract java.lang.Object listExercises(@retrofit2.http.Query(value = "category")
    @org.jetbrains.annotations.Nullable()
    java.lang.String category, @retrofit2.http.Query(value = "muscle_group")
    @org.jetbrains.annotations.Nullable()
    java.lang.String muscleGroup, @retrofit2.http.Query(value = "search")
    @org.jetbrains.annotations.Nullable()
    java.lang.String search, @org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super retrofit2.Response<com.orcafit.data.api.models.ExerciseListResponse>> $completion);
    
    @retrofit2.http.POST(value = "api/v1/programs/generate")
    @org.jetbrains.annotations.Nullable()
    public abstract java.lang.Object generateProgram(@retrofit2.http.Body()
    @org.jetbrains.annotations.NotNull()
    com.orcafit.data.api.models.GenerateProgramRequest request, @org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super retrofit2.Response<com.orcafit.data.api.models.GenerateResponse>> $completion);
    
    @retrofit2.http.GET(value = "api/v1/programs/generate/{jobId}/status")
    @org.jetbrains.annotations.Nullable()
    public abstract java.lang.Object getGenerationStatus(@retrofit2.http.Path(value = "jobId")
    @org.jetbrains.annotations.NotNull()
    java.lang.String jobId, @org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super retrofit2.Response<com.orcafit.data.api.models.JobStatusResponse>> $completion);
    
    @retrofit2.http.GET(value = "api/v1/programs")
    @org.jetbrains.annotations.Nullable()
    public abstract java.lang.Object listPrograms(@org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super retrofit2.Response<com.orcafit.data.api.models.ProgramListResponse>> $completion);
    
    @retrofit2.http.GET(value = "api/v1/programs/{id}")
    @org.jetbrains.annotations.Nullable()
    public abstract java.lang.Object getProgram(@retrofit2.http.Path(value = "id")
    int id, @org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super retrofit2.Response<com.orcafit.data.api.models.ProgramDetailResponse>> $completion);
    
    @retrofit2.http.POST(value = "api/v1/programs/{id}/activate")
    @org.jetbrains.annotations.Nullable()
    public abstract java.lang.Object activateProgram(@retrofit2.http.Path(value = "id")
    int id, @org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super retrofit2.Response<com.orcafit.data.api.models.ActivateResponse>> $completion);
    
    @retrofit2.http.POST(value = "api/v1/workouts/start")
    @org.jetbrains.annotations.Nullable()
    public abstract java.lang.Object startWorkout(@retrofit2.http.Body()
    @org.jetbrains.annotations.NotNull()
    com.orcafit.data.api.models.StartWorkoutRequest request, @org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super retrofit2.Response<com.orcafit.data.api.models.WorkoutResponse>> $completion);
    
    @retrofit2.http.GET(value = "api/v1/workouts/active")
    @org.jetbrains.annotations.Nullable()
    public abstract java.lang.Object getActiveWorkout(@org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super retrofit2.Response<com.orcafit.data.api.models.ActiveWorkoutResponse>> $completion);
    
    @retrofit2.http.PUT(value = "api/v1/workouts/{id}/log")
    @org.jetbrains.annotations.Nullable()
    public abstract java.lang.Object logSet(@retrofit2.http.Path(value = "id")
    int id, @retrofit2.http.Body()
    @org.jetbrains.annotations.NotNull()
    com.orcafit.data.api.models.LogSetRequest request, @org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super retrofit2.Response<com.orcafit.data.api.models.LogSetResponse>> $completion);
    
    @retrofit2.http.POST(value = "api/v1/workouts/{id}/complete")
    @org.jetbrains.annotations.Nullable()
    public abstract java.lang.Object completeWorkout(@retrofit2.http.Path(value = "id")
    int id, @org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super retrofit2.Response<com.orcafit.data.api.models.WorkoutSummaryResponse>> $completion);
    
    @retrofit2.http.GET(value = "api/v1/workouts")
    @org.jetbrains.annotations.Nullable()
    public abstract java.lang.Object listWorkouts(@retrofit2.http.Query(value = "limit")
    int limit, @org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super retrofit2.Response<com.orcafit.data.api.models.WorkoutListResponse>> $completion);
    
    @retrofit2.http.GET(value = "api/v1/workouts/{id}")
    @org.jetbrains.annotations.Nullable()
    public abstract java.lang.Object getWorkout(@retrofit2.http.Path(value = "id")
    int id, @org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super retrofit2.Response<com.orcafit.data.api.models.WorkoutResponse>> $completion);
    
    @retrofit2.http.GET(value = "api/v1/profile/stats")
    @org.jetbrains.annotations.Nullable()
    public abstract java.lang.Object getStats(@org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super retrofit2.Response<com.orcafit.data.api.models.StatsResponse>> $completion);
    
    @kotlin.Metadata(mv = {1, 9, 0}, k = 3, xi = 48)
    public static final class DefaultImpls {
    }
}
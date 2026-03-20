package com.orcafit.ui.screens.workout

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.orcafit.data.api.OrcaFitApi
import com.orcafit.data.api.models.*
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

data class WorkoutUiState(
    val workout: WorkoutResponse? = null,
    val currentExerciseIndex: Int = 0,
    val elapsedSeconds: Int = 0,
    val restTimerSeconds: Int = 0,
    val isRestTimerRunning: Boolean = false,
    val isLoading: Boolean = true,
    val isSaving: Boolean = false,
    val completedWorkoutId: Int? = null,
    val summary: WorkoutSummaryResponse? = null,
    val error: String? = null,
    // Current set input
    val inputWeight: String = "",
    val inputReps: String = "",
    val inputRpe: String = "",
    val inputDuration: String = "",
    val inputDistance: String = "",
)

@HiltViewModel
class WorkoutViewModel @Inject constructor(
    private val api: OrcaFitApi,
) : ViewModel() {

    private val _uiState = MutableStateFlow(WorkoutUiState())
    val uiState: StateFlow<WorkoutUiState> = _uiState.asStateFlow()
    private var timerJob: Job? = null
    private var restJob: Job? = null

    init { loadActiveWorkout() }

    fun loadActiveWorkout() {
        viewModelScope.launch {
            _uiState.value = WorkoutUiState(isLoading = true)
            try {
                val response = api.getActiveWorkout()
                val body = response.body()
                if (body?.active == true && body.workout != null) {
                    _uiState.value = WorkoutUiState(workout = body.workout, isLoading = false)
                    startTimer()
                } else {
                    // Try to start a new one
                    val startResponse = api.startWorkout(StartWorkoutRequest())
                    if (startResponse.isSuccessful) {
                        _uiState.value = WorkoutUiState(workout = startResponse.body(), isLoading = false)
                        startTimer()
                    } else {
                        _uiState.value = WorkoutUiState(isLoading = false, error = "No active program. Activate a program first.")
                    }
                }
            } catch (e: Exception) {
                _uiState.value = WorkoutUiState(isLoading = false, error = e.message)
            }
        }
    }

    private fun startTimer() {
        timerJob?.cancel()
        timerJob = viewModelScope.launch {
            while (true) {
                delay(1000)
                _uiState.value = _uiState.value.copy(elapsedSeconds = _uiState.value.elapsedSeconds + 1)
            }
        }
    }

    fun updateInputWeight(v: String) { _uiState.value = _uiState.value.copy(inputWeight = v) }
    fun updateInputReps(v: String) { _uiState.value = _uiState.value.copy(inputReps = v) }
    fun updateInputRpe(v: String) { _uiState.value = _uiState.value.copy(inputRpe = v) }
    fun updateInputDuration(v: String) { _uiState.value = _uiState.value.copy(inputDuration = v) }
    fun updateInputDistance(v: String) { _uiState.value = _uiState.value.copy(inputDistance = v) }

    fun setCurrentExercise(index: Int) {
        _uiState.value = _uiState.value.copy(currentExerciseIndex = index, inputWeight = "", inputReps = "", inputRpe = "")
    }

    fun logSet() {
        val state = _uiState.value
        val workout = state.workout ?: return
        val workoutId = workout.id ?: return
        val exerciseIndex = state.currentExerciseIndex
        val exercise = workout.exercises.getOrNull(exerciseIndex) ?: return

        val setNumber = exercise.loggedSets.size + 1

        viewModelScope.launch {
            _uiState.value = state.copy(isSaving = true)
            try {
                val request = LogSetRequest(
                    exerciseIndex = exerciseIndex,
                    setNumber = setNumber,
                    weightKg = state.inputWeight.toFloatOrNull(),
                    reps = state.inputReps.toIntOrNull(),
                    rpe = state.inputRpe.toFloatOrNull(),
                    durationSeconds = state.inputDuration.toIntOrNull(),
                    distanceMeters = state.inputDistance.toFloatOrNull(),
                )
                api.logSet(workoutId, request)

                // Refresh workout data
                val refreshed = api.getActiveWorkout()
                _uiState.value = _uiState.value.copy(
                    workout = refreshed.body()?.workout ?: workout,
                    isSaving = false,
                    inputWeight = state.inputWeight, // Keep weight for next set
                    inputReps = "",
                    inputRpe = "",
                )

                // Start rest timer (90 seconds default)
                startRestTimer(90)
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(isSaving = false, error = e.message)
            }
        }
    }

    fun startRestTimer(seconds: Int) {
        restJob?.cancel()
        _uiState.value = _uiState.value.copy(restTimerSeconds = seconds, isRestTimerRunning = true)
        restJob = viewModelScope.launch {
            var remaining = seconds
            while (remaining > 0) {
                delay(1000)
                remaining--
                _uiState.value = _uiState.value.copy(restTimerSeconds = remaining)
            }
            _uiState.value = _uiState.value.copy(isRestTimerRunning = false)
        }
    }

    fun skipRest() {
        restJob?.cancel()
        _uiState.value = _uiState.value.copy(restTimerSeconds = 0, isRestTimerRunning = false)
    }

    fun completeWorkout() {
        val workoutId = _uiState.value.workout?.id ?: return
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isSaving = true)
            try {
                val response = api.completeWorkout(workoutId)
                timerJob?.cancel()
                restJob?.cancel()
                _uiState.value = _uiState.value.copy(
                    isSaving = false,
                    completedWorkoutId = workoutId,
                    summary = response.body(),
                )
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(isSaving = false, error = e.message)
            }
        }
    }

    override fun onCleared() {
        timerJob?.cancel()
        restJob?.cancel()
        super.onCleared()
    }
}

package com.orcafit.ui.screens.generate

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.orcafit.data.api.OrcaFitApi
import com.orcafit.data.api.models.GenerateProgramRequest
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

data class GenerateUiState(
    val goals: String = "",
    val daysPerWeek: Int = 4,
    val weeks: Int = 4,
    val isGenerating: Boolean = false,
    val progress: String = "",
    val generatedProgramId: Int? = null,
    val error: String? = null,
)

@HiltViewModel
class GenerateViewModel @Inject constructor(
    private val api: OrcaFitApi,
) : ViewModel() {

    private val _uiState = MutableStateFlow(GenerateUiState())
    val uiState: StateFlow<GenerateUiState> = _uiState.asStateFlow()

    fun updateGoals(goals: String) { _uiState.value = _uiState.value.copy(goals = goals) }
    fun updateDays(days: Int) { _uiState.value = _uiState.value.copy(daysPerWeek = days.coerceIn(2, 7)) }
    fun updateWeeks(weeks: Int) { _uiState.value = _uiState.value.copy(weeks = weeks.coerceIn(1, 12)) }

    fun generate() {
        val state = _uiState.value
        if (state.goals.isBlank()) {
            _uiState.value = state.copy(error = "Describe your fitness goals")
            return
        }
        viewModelScope.launch {
            _uiState.value = state.copy(isGenerating = true, progress = "Starting generation...", error = null)
            try {
                val response = api.generateProgram(
                    GenerateProgramRequest(state.goals, state.daysPerWeek, state.weeks)
                )
                if (response.isSuccessful) {
                    val jobId = response.body()!!.jobId
                    _uiState.value = _uiState.value.copy(progress = "AI agents deliberating...")
                    // Poll for completion
                    var attempts = 0
                    while (attempts < 60) {
                        delay(2000)
                        val statusResponse = api.getGenerationStatus(jobId)
                        val status = statusResponse.body()?.status ?: "unknown"
                        when (status) {
                            "completed" -> {
                                _uiState.value = _uiState.value.copy(
                                    isGenerating = false,
                                    progress = "Program ready!",
                                )
                                return@launch
                            }
                            "failed" -> {
                                _uiState.value = _uiState.value.copy(
                                    isGenerating = false,
                                    error = statusResponse.body()?.error ?: "Generation failed",
                                )
                                return@launch
                            }
                            "running" -> {
                                _uiState.value = _uiState.value.copy(progress = "AI agents deliberating... (${attempts * 2}s)")
                            }
                        }
                        attempts++
                    }
                    _uiState.value = _uiState.value.copy(isGenerating = false, error = "Generation timed out")
                } else {
                    _uiState.value = _uiState.value.copy(isGenerating = false, error = "Failed to start generation")
                }
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(isGenerating = false, error = e.message)
            }
        }
    }
}

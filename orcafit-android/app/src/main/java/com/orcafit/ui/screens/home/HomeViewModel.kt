package com.orcafit.ui.screens.home

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.orcafit.data.api.OrcaFitApi
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

data class HomeUiState(
    val userName: String = "",
    val totalWorkouts: Int = 0,
    val totalVolumeKg: Float = 0f,
    val hasActiveWorkout: Boolean = false,
    val activeProgramName: String? = null,
    val isLoading: Boolean = true,
)

@HiltViewModel
class HomeViewModel @Inject constructor(
    private val api: OrcaFitApi,
) : ViewModel() {

    private val _uiState = MutableStateFlow(HomeUiState())
    val uiState: StateFlow<HomeUiState> = _uiState.asStateFlow()

    init { loadDashboard() }

    fun loadDashboard() {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true)

            // Each call is independent — one failure shouldn't block others
            var name = ""
            var totalWorkouts = 0
            var totalVolumeKg = 0f
            var hasActive = false

            try {
                val meResponse = api.getMe()
                if (meResponse.isSuccessful) {
                    name = meResponse.body()?.name ?: ""
                }
            } catch (_: Exception) {}

            try {
                val statsResponse = api.getStats()
                if (statsResponse.isSuccessful) {
                    val stats = statsResponse.body()
                    totalWorkouts = stats?.totalWorkouts ?: 0
                    totalVolumeKg = stats?.totalVolumeKg ?: 0f
                }
            } catch (_: Exception) {}

            try {
                val activeResponse = api.getActiveWorkout()
                if (activeResponse.isSuccessful) {
                    hasActive = activeResponse.body()?.active ?: false
                }
            } catch (_: Exception) {}

            _uiState.value = HomeUiState(
                userName = name,
                totalWorkouts = totalWorkouts,
                totalVolumeKg = totalVolumeKg,
                hasActiveWorkout = hasActive,
                isLoading = false,
            )
        }
    }
}

package com.orcafit.ui.screens.history

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.orcafit.data.api.OrcaFitApi
import com.orcafit.data.api.models.WorkoutSummaryDto
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class HistoryViewModel @Inject constructor(private val api: OrcaFitApi) : ViewModel() {
    private val _workouts = MutableStateFlow<List<WorkoutSummaryDto>>(emptyList())
    val workouts: StateFlow<List<WorkoutSummaryDto>> = _workouts.asStateFlow()

    private val _isLoading = MutableStateFlow(true)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()

    init {
        viewModelScope.launch {
            try {
                val response = api.listWorkouts()
                _workouts.value = response.body()?.workouts ?: emptyList()
            } catch (_: Exception) { }
            _isLoading.value = false
        }
    }
}

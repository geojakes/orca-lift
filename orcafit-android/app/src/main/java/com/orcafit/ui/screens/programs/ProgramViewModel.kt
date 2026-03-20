package com.orcafit.ui.screens.programs

import androidx.lifecycle.SavedStateHandle
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.orcafit.data.api.OrcaFitApi
import com.orcafit.data.api.models.ProgramDetailResponse
import com.orcafit.data.api.models.ProgramSummaryDto
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

data class ProgramListState(
    val programs: List<ProgramSummaryDto> = emptyList(),
    val isLoading: Boolean = true,
    val error: String? = null,
)

data class ProgramDetailState(
    val program: ProgramDetailResponse? = null,
    val isLoading: Boolean = true,
    val isActivating: Boolean = false,
    val activated: Boolean = false,
    val error: String? = null,
)

@HiltViewModel
class ProgramListViewModel @Inject constructor(
    private val api: OrcaFitApi,
) : ViewModel() {

    private val _uiState = MutableStateFlow(ProgramListState())
    val uiState: StateFlow<ProgramListState> = _uiState.asStateFlow()

    init { loadPrograms() }

    fun loadPrograms() {
        viewModelScope.launch {
            _uiState.value = ProgramListState(isLoading = true)
            try {
                val response = api.listPrograms()
                _uiState.value = ProgramListState(
                    programs = response.body()?.programs ?: emptyList(),
                    isLoading = false,
                )
            } catch (e: Exception) {
                _uiState.value = ProgramListState(isLoading = false, error = e.message)
            }
        }
    }
}

@HiltViewModel
class ProgramDetailViewModel @Inject constructor(
    private val api: OrcaFitApi,
    savedStateHandle: SavedStateHandle,
) : ViewModel() {

    private val programId: Int = savedStateHandle["programId"] ?: 0
    private val _uiState = MutableStateFlow(ProgramDetailState())
    val uiState: StateFlow<ProgramDetailState> = _uiState.asStateFlow()

    init { loadProgram() }

    fun loadProgram() {
        viewModelScope.launch {
            _uiState.value = ProgramDetailState(isLoading = true)
            try {
                val response = api.getProgram(programId)
                _uiState.value = ProgramDetailState(program = response.body(), isLoading = false)
            } catch (e: Exception) {
                _uiState.value = ProgramDetailState(isLoading = false, error = e.message)
            }
        }
    }

    fun activate() {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isActivating = true)
            try {
                api.activateProgram(programId)
                _uiState.value = _uiState.value.copy(isActivating = false, activated = true)
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(isActivating = false, error = e.message)
            }
        }
    }
}

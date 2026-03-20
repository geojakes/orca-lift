package com.orcafit.ui.screens.exercises

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.orcafit.data.api.OrcaFitApi
import com.orcafit.data.api.models.ExerciseDto
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class ExerciseViewModel @Inject constructor(private val api: OrcaFitApi) : ViewModel() {
    private val _exercises = MutableStateFlow<List<ExerciseDto>>(emptyList())
    val exercises: StateFlow<List<ExerciseDto>> = _exercises.asStateFlow()

    private val _isLoading = MutableStateFlow(true)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()

    private val _searchQuery = MutableStateFlow("")
    val searchQuery: StateFlow<String> = _searchQuery.asStateFlow()

    private val _selectedCategory = MutableStateFlow<String?>(null)
    val selectedCategory: StateFlow<String?> = _selectedCategory.asStateFlow()

    init { loadExercises() }

    fun updateSearch(query: String) {
        _searchQuery.value = query
        loadExercises()
    }

    fun setCategory(category: String?) {
        _selectedCategory.value = category
        loadExercises()
    }

    private fun loadExercises() {
        viewModelScope.launch {
            _isLoading.value = true
            try {
                val response = api.listExercises(
                    category = _selectedCategory.value,
                    search = _searchQuery.value.ifBlank { null },
                )
                _exercises.value = response.body()?.exercises ?: emptyList()
            } catch (_: Exception) { }
            _isLoading.value = false
        }
    }
}

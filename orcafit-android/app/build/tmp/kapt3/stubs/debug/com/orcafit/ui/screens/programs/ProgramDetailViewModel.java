package com.orcafit.ui.screens.programs;

import androidx.lifecycle.SavedStateHandle;
import androidx.lifecycle.ViewModel;
import com.orcafit.data.api.OrcaFitApi;
import com.orcafit.data.api.models.ProgramDetailResponse;
import com.orcafit.data.api.models.ProgramSummaryDto;
import dagger.hilt.android.lifecycle.HiltViewModel;
import kotlinx.coroutines.flow.StateFlow;
import javax.inject.Inject;

@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u00008\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\b\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0003\n\u0002\u0010\u0002\n\u0002\b\u0002\b\u0007\u0018\u00002\u00020\u0001B\u0017\b\u0007\u0012\u0006\u0010\u0002\u001a\u00020\u0003\u0012\u0006\u0010\u0004\u001a\u00020\u0005\u00a2\u0006\u0002\u0010\u0006J\u0006\u0010\u0010\u001a\u00020\u0011J\u0006\u0010\u0012\u001a\u00020\u0011R\u0014\u0010\u0007\u001a\b\u0012\u0004\u0012\u00020\t0\bX\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u000e\u0010\u0002\u001a\u00020\u0003X\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u000e\u0010\n\u001a\u00020\u000bX\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u0017\u0010\f\u001a\b\u0012\u0004\u0012\u00020\t0\r\u00a2\u0006\b\n\u0000\u001a\u0004\b\u000e\u0010\u000f\u00a8\u0006\u0013"}, d2 = {"Lcom/orcafit/ui/screens/programs/ProgramDetailViewModel;", "Landroidx/lifecycle/ViewModel;", "api", "Lcom/orcafit/data/api/OrcaFitApi;", "savedStateHandle", "Landroidx/lifecycle/SavedStateHandle;", "(Lcom/orcafit/data/api/OrcaFitApi;Landroidx/lifecycle/SavedStateHandle;)V", "_uiState", "Lkotlinx/coroutines/flow/MutableStateFlow;", "Lcom/orcafit/ui/screens/programs/ProgramDetailState;", "programId", "", "uiState", "Lkotlinx/coroutines/flow/StateFlow;", "getUiState", "()Lkotlinx/coroutines/flow/StateFlow;", "activate", "", "loadProgram", "app_debug"})
@dagger.hilt.android.lifecycle.HiltViewModel()
public final class ProgramDetailViewModel extends androidx.lifecycle.ViewModel {
    @org.jetbrains.annotations.NotNull()
    private final com.orcafit.data.api.OrcaFitApi api = null;
    private final int programId = 0;
    @org.jetbrains.annotations.NotNull()
    private final kotlinx.coroutines.flow.MutableStateFlow<com.orcafit.ui.screens.programs.ProgramDetailState> _uiState = null;
    @org.jetbrains.annotations.NotNull()
    private final kotlinx.coroutines.flow.StateFlow<com.orcafit.ui.screens.programs.ProgramDetailState> uiState = null;
    
    @javax.inject.Inject()
    public ProgramDetailViewModel(@org.jetbrains.annotations.NotNull()
    com.orcafit.data.api.OrcaFitApi api, @org.jetbrains.annotations.NotNull()
    androidx.lifecycle.SavedStateHandle savedStateHandle) {
        super();
    }
    
    @org.jetbrains.annotations.NotNull()
    public final kotlinx.coroutines.flow.StateFlow<com.orcafit.ui.screens.programs.ProgramDetailState> getUiState() {
        return null;
    }
    
    public final void loadProgram() {
    }
    
    public final void activate() {
    }
}
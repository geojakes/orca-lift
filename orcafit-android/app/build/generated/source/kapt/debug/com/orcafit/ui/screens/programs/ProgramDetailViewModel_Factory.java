package com.orcafit.ui.screens.programs;

import androidx.lifecycle.SavedStateHandle;
import com.orcafit.data.api.OrcaFitApi;
import dagger.internal.DaggerGenerated;
import dagger.internal.Factory;
import dagger.internal.QualifierMetadata;
import dagger.internal.ScopeMetadata;
import javax.annotation.processing.Generated;
import javax.inject.Provider;

@ScopeMetadata
@QualifierMetadata
@DaggerGenerated
@Generated(
    value = "dagger.internal.codegen.ComponentProcessor",
    comments = "https://dagger.dev"
)
@SuppressWarnings({
    "unchecked",
    "rawtypes",
    "KotlinInternal",
    "KotlinInternalInJava"
})
public final class ProgramDetailViewModel_Factory implements Factory<ProgramDetailViewModel> {
  private final Provider<OrcaFitApi> apiProvider;

  private final Provider<SavedStateHandle> savedStateHandleProvider;

  public ProgramDetailViewModel_Factory(Provider<OrcaFitApi> apiProvider,
      Provider<SavedStateHandle> savedStateHandleProvider) {
    this.apiProvider = apiProvider;
    this.savedStateHandleProvider = savedStateHandleProvider;
  }

  @Override
  public ProgramDetailViewModel get() {
    return newInstance(apiProvider.get(), savedStateHandleProvider.get());
  }

  public static ProgramDetailViewModel_Factory create(Provider<OrcaFitApi> apiProvider,
      Provider<SavedStateHandle> savedStateHandleProvider) {
    return new ProgramDetailViewModel_Factory(apiProvider, savedStateHandleProvider);
  }

  public static ProgramDetailViewModel newInstance(OrcaFitApi api,
      SavedStateHandle savedStateHandle) {
    return new ProgramDetailViewModel(api, savedStateHandle);
  }
}

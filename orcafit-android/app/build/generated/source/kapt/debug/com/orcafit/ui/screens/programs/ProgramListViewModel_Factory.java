package com.orcafit.ui.screens.programs;

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
public final class ProgramListViewModel_Factory implements Factory<ProgramListViewModel> {
  private final Provider<OrcaFitApi> apiProvider;

  public ProgramListViewModel_Factory(Provider<OrcaFitApi> apiProvider) {
    this.apiProvider = apiProvider;
  }

  @Override
  public ProgramListViewModel get() {
    return newInstance(apiProvider.get());
  }

  public static ProgramListViewModel_Factory create(Provider<OrcaFitApi> apiProvider) {
    return new ProgramListViewModel_Factory(apiProvider);
  }

  public static ProgramListViewModel newInstance(OrcaFitApi api) {
    return new ProgramListViewModel(api);
  }
}

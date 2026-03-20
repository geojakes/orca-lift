package com.orcafit.ui.screens.generate;

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
public final class GenerateViewModel_Factory implements Factory<GenerateViewModel> {
  private final Provider<OrcaFitApi> apiProvider;

  public GenerateViewModel_Factory(Provider<OrcaFitApi> apiProvider) {
    this.apiProvider = apiProvider;
  }

  @Override
  public GenerateViewModel get() {
    return newInstance(apiProvider.get());
  }

  public static GenerateViewModel_Factory create(Provider<OrcaFitApi> apiProvider) {
    return new GenerateViewModel_Factory(apiProvider);
  }

  public static GenerateViewModel newInstance(OrcaFitApi api) {
    return new GenerateViewModel(api);
  }
}

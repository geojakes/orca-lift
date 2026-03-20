package com.orcafit.ui.screens.history;

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
public final class HistoryViewModel_Factory implements Factory<HistoryViewModel> {
  private final Provider<OrcaFitApi> apiProvider;

  public HistoryViewModel_Factory(Provider<OrcaFitApi> apiProvider) {
    this.apiProvider = apiProvider;
  }

  @Override
  public HistoryViewModel get() {
    return newInstance(apiProvider.get());
  }

  public static HistoryViewModel_Factory create(Provider<OrcaFitApi> apiProvider) {
    return new HistoryViewModel_Factory(apiProvider);
  }

  public static HistoryViewModel newInstance(OrcaFitApi api) {
    return new HistoryViewModel(api);
  }
}

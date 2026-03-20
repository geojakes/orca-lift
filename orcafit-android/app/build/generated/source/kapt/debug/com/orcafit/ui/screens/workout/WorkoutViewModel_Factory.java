package com.orcafit.ui.screens.workout;

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
public final class WorkoutViewModel_Factory implements Factory<WorkoutViewModel> {
  private final Provider<OrcaFitApi> apiProvider;

  public WorkoutViewModel_Factory(Provider<OrcaFitApi> apiProvider) {
    this.apiProvider = apiProvider;
  }

  @Override
  public WorkoutViewModel get() {
    return newInstance(apiProvider.get());
  }

  public static WorkoutViewModel_Factory create(Provider<OrcaFitApi> apiProvider) {
    return new WorkoutViewModel_Factory(apiProvider);
  }

  public static WorkoutViewModel newInstance(OrcaFitApi api) {
    return new WorkoutViewModel(api);
  }
}

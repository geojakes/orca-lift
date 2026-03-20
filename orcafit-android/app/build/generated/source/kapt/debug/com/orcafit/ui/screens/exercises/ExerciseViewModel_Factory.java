package com.orcafit.ui.screens.exercises;

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
public final class ExerciseViewModel_Factory implements Factory<ExerciseViewModel> {
  private final Provider<OrcaFitApi> apiProvider;

  public ExerciseViewModel_Factory(Provider<OrcaFitApi> apiProvider) {
    this.apiProvider = apiProvider;
  }

  @Override
  public ExerciseViewModel get() {
    return newInstance(apiProvider.get());
  }

  public static ExerciseViewModel_Factory create(Provider<OrcaFitApi> apiProvider) {
    return new ExerciseViewModel_Factory(apiProvider);
  }

  public static ExerciseViewModel newInstance(OrcaFitApi api) {
    return new ExerciseViewModel(api);
  }
}

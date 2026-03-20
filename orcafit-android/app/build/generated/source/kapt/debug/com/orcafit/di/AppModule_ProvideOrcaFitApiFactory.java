package com.orcafit.di;

import com.orcafit.data.api.OrcaFitApi;
import dagger.internal.DaggerGenerated;
import dagger.internal.Factory;
import dagger.internal.Preconditions;
import dagger.internal.QualifierMetadata;
import dagger.internal.ScopeMetadata;
import javax.annotation.processing.Generated;
import javax.inject.Provider;
import retrofit2.Retrofit;

@ScopeMetadata("javax.inject.Singleton")
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
public final class AppModule_ProvideOrcaFitApiFactory implements Factory<OrcaFitApi> {
  private final Provider<Retrofit> retrofitProvider;

  public AppModule_ProvideOrcaFitApiFactory(Provider<Retrofit> retrofitProvider) {
    this.retrofitProvider = retrofitProvider;
  }

  @Override
  public OrcaFitApi get() {
    return provideOrcaFitApi(retrofitProvider.get());
  }

  public static AppModule_ProvideOrcaFitApiFactory create(Provider<Retrofit> retrofitProvider) {
    return new AppModule_ProvideOrcaFitApiFactory(retrofitProvider);
  }

  public static OrcaFitApi provideOrcaFitApi(Retrofit retrofit) {
    return Preconditions.checkNotNullFromProvides(AppModule.INSTANCE.provideOrcaFitApi(retrofit));
  }
}

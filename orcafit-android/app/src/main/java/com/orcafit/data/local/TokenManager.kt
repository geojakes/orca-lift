package com.orcafit.data.local

import android.content.Context
import android.content.SharedPreferences
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.map
import javax.inject.Inject

/**
 * Token manager using SharedPreferences for reliable synchronous access.
 * DataStore's async nature causes race conditions with OkHttp interceptors.
 */
class TokenManager @Inject constructor(context: Context) {

    private val prefs: SharedPreferences =
        context.getSharedPreferences("orcafit_auth", Context.MODE_PRIVATE)

    private val _accessToken = MutableStateFlow(prefs.getString(KEY_ACCESS_TOKEN, null))
    private val _refreshToken = MutableStateFlow(prefs.getString(KEY_REFRESH_TOKEN, null))

    val accessToken: Flow<String?> = _accessToken.asStateFlow()
    val refreshToken: Flow<String?> = _refreshToken.asStateFlow()
    val isLoggedIn: Flow<Boolean> = _accessToken.asStateFlow().map { it != null }

    fun getAccessTokenSync(): String? = _accessToken.value

    suspend fun saveTokens(accessToken: String, refreshToken: String) {
        prefs.edit()
            .putString(KEY_ACCESS_TOKEN, accessToken)
            .putString(KEY_REFRESH_TOKEN, refreshToken)
            .apply()
        _accessToken.value = accessToken
        _refreshToken.value = refreshToken
    }

    suspend fun clearTokens() {
        prefs.edit().clear().apply()
        _accessToken.value = null
        _refreshToken.value = null
    }

    companion object {
        private const val KEY_ACCESS_TOKEN = "access_token"
        private const val KEY_REFRESH_TOKEN = "refresh_token"
    }
}

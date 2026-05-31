package com.uaim.projekt.ui.login

import android.app.Application
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.uaim.projekt.api.LoginData
import com.uaim.projekt.api.LoginRequest
import com.uaim.projekt.api.RetrofitClient
import com.uaim.projekt.auth.TokenManager
import kotlinx.coroutines.launch

class LoginViewModel(application: Application) : AndroidViewModel(application) {
    var email by mutableStateOf("")
    var password by mutableStateOf("")
    var isLoading by mutableStateOf(false)
    var errorMessage by mutableStateOf<String?>(null)

    private val tokenManager = TokenManager(application)

    fun onLoginClick(onSuccess: (LoginData) -> Unit) {
        if (email.isBlank() || password.isBlank()) {
            errorMessage = "Pola nie mogą być puste"
            return
        }

        viewModelScope.launch {
            isLoading = true
            errorMessage = null
            try {
                val api = RetrofitClient.getInstance(getApplication())
                val response = api.login(LoginRequest(email, password))
                
                // Po logowaniu zapisujemy tokeny JWT używane przez AuthInterceptor w kolejnych żądaniach.
                tokenManager.saveTokens(response.data.accessToken, response.data.refreshToken)

                onSuccess(response.data)
            } catch (e: Exception) {
                errorMessage = "Błąd logowania: ${e.localizedMessage ?: "Nieznany błąd"}"
            } finally {
                isLoading = false
            }
        }
    }
}

package com.uaim.projekt.ui.staff

import android.app.Application
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.uaim.projekt.api.RetrofitClient
import com.uaim.projekt.api.StaffAppointmentDto
import com.uaim.projekt.api.StatusUpdateRequest
import com.uaim.projekt.api.SummaryUpdateRequest
import kotlinx.coroutines.launch

class StaffViewModel(application: Application) : AndroidViewModel(application) {
    var appointments by mutableStateOf<List<StaffAppointmentDto>>(emptyList())
    var isLoading by mutableStateOf(false)
    var errorMessage by mutableStateOf<String?>(null)

    fun fetchAppointments() {
        viewModelScope.launch {
            isLoading = true
            errorMessage = null
            try {
                val api = RetrofitClient.getInstance(getApplication())
                val response = api.getStaffAppointments()
                appointments = response.data.sortedBy { it.startAt }
            } catch (e: Exception) {
                errorMessage = "Błąd pobierania wizyt: ${e.localizedMessage}"
            } finally {
                isLoading = false
            }
        }
    }

    fun updateStatus(appointmentId: String, newStatus: String) {
        viewModelScope.launch {
            try {
                val api = RetrofitClient.getInstance(getApplication())
                api.updateAppointmentStatus(appointmentId, StatusUpdateRequest(newStatus))
                fetchAppointments() // Odśwież listę
            } catch (e: Exception) {
                errorMessage = "Błąd zmiany statusu: ${e.localizedMessage}"
            }
        }
    }

    fun addSummary(appointmentId: String, text: String) {
        viewModelScope.launch {
            try {
                val api = RetrofitClient.getInstance(getApplication())
                api.updateConsultationSummary(appointmentId, SummaryUpdateRequest(text))
                errorMessage = "Dodano podsumowanie"
            } catch (e: Exception) {
                errorMessage = "Błąd dodawania podsumowania: ${e.localizedMessage}"
            }
        }
    }
}

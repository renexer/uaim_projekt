package com.uaim.projekt.ui.client

import android.app.Application
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.uaim.projekt.api.AppointmentDto
import com.uaim.projekt.api.AvailabilityResponse
import com.uaim.projekt.api.RetrofitClient
import com.uaim.projekt.api.ReviewRequest
import com.uaim.projekt.api.ServiceDto
import com.uaim.projekt.api.TherapistPublicDto
import kotlinx.coroutines.launch

class ClientViewModel(application: Application) : AndroidViewModel(application) {
    var services by mutableStateOf<List<ServiceDto>>(emptyList())
    var therapists by mutableStateOf<List<TherapistPublicDto>>(emptyList())
    var myAppointments by mutableStateOf<List<AppointmentDto>>(emptyList())
    var myConsultations by mutableStateOf<Map<String, String?>>(emptyMap())
    var availability by mutableStateOf<AvailabilityResponse?>(null)
    var isLoading by mutableStateOf(false)
    var errorMessage by mutableStateOf<String?>(null)

    fun fetchMyAppointments() {
        viewModelScope.launch {
            isLoading = true
            errorMessage = null
            try {
                val api = RetrofitClient.getInstance(getApplication())
                // Dodajemy parametr scope = "all", aby pobrać też wizyty zakończone
                val response = api.getMyAppointments(scope = "all")
                myAppointments = response.data.sortedByDescending { it.startAt }
                
                // Pobierz zalecenia dla wizyt zakończonych
                try {
                    val consultationsResponse = api.getMyConsultations()
                    myConsultations = consultationsResponse.data.associate { it.appointmentId to it.summary?.text }
                } catch (e: Exception) {
                    // Ignorujemy błąd pobierania samych konsultacji
                }
            } catch (e: Exception) {
                errorMessage = "Błąd pobierania wizyt: ${e.localizedMessage}"
            } finally {
                isLoading = false
            }
        }
    }

    fun fetchAvailability(serviceId: String, therapistId: String?, from: String, to: String) {
        viewModelScope.launch {
            isLoading = true
            errorMessage = null
            try {
                val api = RetrofitClient.getInstance(getApplication())
                val response = api.getAvailability(serviceId, therapistId, from, to)
                availability = response.data
            } catch (e: Exception) {
                errorMessage = "Błąd pobierania dostępności: ${e.localizedMessage}"
            } finally {
                isLoading = false
            }
        }
    }

    fun bookAppointment(serviceId: String, therapistId: String, startAt: String, onSuccess: () -> Unit) {
        viewModelScope.launch {
            isLoading = true
            errorMessage = null
            try {
                val api = RetrofitClient.getInstance(getApplication())
                api.createAppointment(com.uaim.projekt.api.CreateAppointmentRequest(serviceId, therapistId, startAt))
                onSuccess()
            } catch (e: Exception) {
                errorMessage = "Błąd rezerwacji: ${e.localizedMessage}"
            } finally {
                isLoading = false
            }
        }
    }

    fun postReview(appointmentId: String, rating: Int, comment: String) {
        viewModelScope.launch {
            try {
                val api = RetrofitClient.getInstance(getApplication())
                api.addReview(appointmentId, ReviewRequest(rating, comment))
                fetchMyAppointments()
            } catch (e: Exception) {
                errorMessage = "Błąd dodawania opinii: ${e.localizedMessage}"
            }
        }
    }

    fun fetchServices() {
        viewModelScope.launch {
            isLoading = true
            errorMessage = null
            try {
                val api = RetrofitClient.getInstance(getApplication())
                val response = api.getServices()
                services = response.data
            } catch (e: Exception) {
                errorMessage = "Błąd pobierania usług: ${e.localizedMessage}"
            } finally {
                isLoading = false
            }
        }
    }

    fun fetchTherapists(serviceId: String) {
        viewModelScope.launch {
            isLoading = true
            errorMessage = null
            try {
                val api = RetrofitClient.getInstance(getApplication())
                val response = api.getTherapistsForService(serviceId)
                therapists = response.data
            } catch (e: Exception) {
                errorMessage = "Błąd pobierania terapeutów: ${e.localizedMessage}"
            } finally {
                isLoading = false
            }
        }
    }
}

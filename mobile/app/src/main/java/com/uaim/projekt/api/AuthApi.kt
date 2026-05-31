package com.uaim.projekt.api

import android.content.Context
import com.uaim.projekt.auth.TokenManager
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.PATCH
import retrofit2.http.POST
import retrofit2.http.PUT
import retrofit2.http.Path
import retrofit2.http.Query

data class LoginRequest(val email: String, val password: String)

data class UserDto(
    val id: String,
    val email: String,
    val firstName: String,
    val lastName: String,
    val roles: List<String>
)

data class LoginData(
    val accessToken: String,
    val refreshToken: String,
    val user: UserDto
)

data class ApiResponse<T>(val data: T)

interface AuthApi {
    @POST("api/v1/auth/login")
    suspend fun login(@Body request: LoginRequest): ApiResponse<LoginData>

    // Usługi
    @GET("api/v1/services")
    suspend fun getServices(): ApiResponse<List<ServiceDto>>

    // Terapeuci dla usługi
    @GET("api/v1/services/{service_id}/therapists")
    suspend fun getTherapistsForService(@Path("service_id") serviceId: String): ApiResponse<List<TherapistPublicDto>>

    // Staff - Wizyty
    @GET("api/v1/staff/appointments")
    suspend fun getStaffAppointments(
        @Query("status") status: String? = null
    ): ApiResponse<List<StaffAppointmentDto>>

    @PATCH("api/v1/staff/appointments/{id}/status")
    suspend fun updateAppointmentStatus(
        @Path("id") id: String,
        @Body request: StatusUpdateRequest
    ): ApiResponse<StaffAppointmentDto>

    @PUT("api/v1/staff/appointments/{id}/consultation-summary")
    suspend fun updateConsultationSummary(
        @Path("id") id: String,
        @Body request: SummaryUpdateRequest
    ): ApiResponse<ConsultationSummaryDto>

    // Klient - Wizyty i Opinie
    @GET("api/v1/appointments/me")
    suspend fun getMyAppointments(
        @Query("scope") scope: String? = null
    ): ApiResponse<List<AppointmentDto>>

    @POST("api/v1/appointments/{id}/review")
    suspend fun addReview(
        @Path("id") id: String,
        @Body request: ReviewRequest
    ): ApiResponse<ReviewDto>

    @GET("api/v1/consultations/me")
    suspend fun getMyConsultations(): ApiResponse<List<ConsultationSummaryDto>>

    // Dostępność i Rezerwacja
    @GET("api/v1/availability")
    suspend fun getAvailability(
        @Query("serviceId") serviceId: String,
        @Query("therapistId") therapistId: String?,
        @Query("from") from: String,
        @Query("to") to: String
    ): ApiResponse<AvailabilityResponse>

    @POST("api/v1/appointments")
    suspend fun createAppointment(@Body request: CreateAppointmentRequest): ApiResponse<AppointmentDto>
}

data class CreateAppointmentRequest(
    val serviceId: String,
    val therapistId: String,
    val startAt: String
)

data class AvailabilityResponse(
    val service: ServiceMinimalDto,
    val range: RangeDto,
    val items: List<AvailabilityItemDto>
)

data class ServiceMinimalDto(val id: String, val name: String, val durationMinutes: Int)
data class RangeDto(val from: String, val to: String)
data class AvailabilityItemDto(val therapist: TherapistPublicDto, val slots: List<SlotDto>)
data class SlotDto(val startAt: String, val endAt: String)

data class AppointmentDto(
    val id: String,
    val status: String,
    val startAt: String,
    val endAt: String,
    val serviceName: String,
    val therapistName: String
)

data class ReviewRequest(val rating: Int, val comment: String)
data class ReviewDto(val id: String, val rating: Int, val comment: String)

data class StaffAppointmentDto(
    val id: String,
    val status: String,
    val startAt: String,
    val endAt: String,
    val patientEmail: String,
    val serviceName: String,
    val therapistName: String
)

data class StatusUpdateRequest(val status: String)
data class SummaryUpdateRequest(val summaryText: String)

data class ConsultationSummaryDto(
    val appointmentId: String,
    val completedAt: String,
    val summary: SummaryTextDto?
)

data class SummaryTextDto(val text: String?)

data class ServiceDto(
    val id: String,
    val code: String,
    val name: String,
    val description: String,
    val durationMinutes: Int,
    val basePrice: String,
    val currency: String,
    val isActive: Boolean
)

data class TherapistPublicDto(
    val id: String,
    val fullName: String,
    val title: String,
    val bio: String,
    val experienceYears: Int?,
    val photoUrl: String?,
    val averageRating: String,
    val reviewsCount: Int,
    val isActive: Boolean
)

object RetrofitClient {
    private const val BASE_URL = "http://10.0.2.2:5000/"
    private var retrofit: Retrofit? = null

    fun getInstance(context: Context): AuthApi {
        if (retrofit == null) {
            val tokenManager = TokenManager(context)
            val logging = HttpLoggingInterceptor().apply {
                level = HttpLoggingInterceptor.Level.BODY
            }
            
            val client = OkHttpClient.Builder()
                .addInterceptor(AuthInterceptor(tokenManager))
                .addInterceptor(logging)
                .build()

            retrofit = Retrofit.Builder()
                .baseUrl(BASE_URL)
                .client(client)
                .addConverterFactory(GsonConverterFactory.create())
                .build()
        }
        return retrofit!!.create(AuthApi::class.java)
    }
}

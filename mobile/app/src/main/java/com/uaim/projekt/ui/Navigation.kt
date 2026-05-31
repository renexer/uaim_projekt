package com.uaim.projekt.ui

import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.height
import androidx.compose.runtime.Composable
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.navigation.NavHostController
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.navArgument
import com.uaim.projekt.auth.TokenManager
import com.uaim.projekt.ui.client.BookingScreen
import com.uaim.projekt.ui.client.ClientViewModel
import com.uaim.projekt.ui.client.MyAppointmentsScreen
import com.uaim.projekt.ui.client.ServicesScreen
import com.uaim.projekt.ui.client.TherapistListScreen
import com.uaim.projekt.ui.login.LoginScreen
import com.uaim.projekt.ui.staff.StaffScheduleScreen
import com.uaim.projekt.ui.staff.StaffViewModel

sealed class Screen(val route: String) {
    object Login : Screen("login")
    object ClientHome : Screen("client_home")
    object StaffHome : Screen("staff_home")
    object MyAppointments : Screen("my_appointments")
    object Booking : Screen("booking/{serviceId}/{therapistId}") {
        fun createRoute(serviceId: String, therapistId: String) = "booking/$serviceId/$therapistId"
    }
    object TherapistList : Screen("therapist_list/{serviceId}/{serviceName}") {
        fun createRoute(serviceId: String, serviceName: String) = "therapist_list/$serviceId/$serviceName"
    }
}

@Composable
fun AppNavigation(navController: NavHostController) {
    val context = LocalContext.current
    val tokenManager = TokenManager(context)
    val clientViewModel: ClientViewModel = androidx.lifecycle.viewmodel.compose.viewModel()
    val staffViewModel: StaffViewModel = androidx.lifecycle.viewmodel.compose.viewModel()
    
    val startDestination = if (tokenManager.getAccessToken() != null) {
        Screen.ClientHome.route
    } else {
        Screen.Login.route
    }

    NavHost(navController = navController, startDestination = startDestination) {
        composable(Screen.Login.route) {
            LoginScreen(onLoginSuccess = { loginData ->
                if (loginData.user.roles.contains("ADMIN") || loginData.user.roles.contains("THERAPIST")) {
                    navController.navigate(Screen.StaffHome.route) {
                        popUpTo(Screen.Login.route) { inclusive = true }
                    }
                } else {
                    navController.navigate(Screen.ClientHome.route) {
                        popUpTo(Screen.Login.route) { inclusive = true }
                    }
                }
            })
        }
        
        composable(Screen.ClientHome.route) {
            ServicesScreen(
                viewModel = clientViewModel,
                onServiceClick = { service ->
                    navController.navigate(Screen.TherapistList.createRoute(service.id, service.name))
                },
                onViewAppointments = {
                    navController.navigate(Screen.MyAppointments.route)
                }
            )
        }

        composable(Screen.MyAppointments.route) {
            MyAppointmentsScreen(
                viewModel = clientViewModel,
                onLogout = {
                    tokenManager.clearTokens()
                    navController.navigate(Screen.Login.route) {
                        popUpTo(Screen.Login.route) { inclusive = true }
                    }
                }
            )
        }

        composable(
            route = Screen.TherapistList.route,
            arguments = listOf(
                navArgument("serviceId") { type = NavType.StringType },
                navArgument("serviceName") { type = NavType.StringType }
            )
        ) { backStackEntry ->
            val serviceId = backStackEntry.arguments?.getString("serviceId") ?: ""
            val serviceName = backStackEntry.arguments?.getString("serviceName") ?: ""
            TherapistListScreen(
                viewModel = clientViewModel,
                serviceId = serviceId,
                serviceName = serviceName,
                onBack = { navController.popBackStack() },
                onTherapistClick = { therapist ->
                    navController.navigate(Screen.Booking.createRoute(serviceId, therapist.id))
                }
            )
        }

        composable(
            route = Screen.Booking.route,
            arguments = listOf(
                navArgument("serviceId") { type = NavType.StringType },
                navArgument("therapistId") { type = NavType.StringType }
            )
        ) { backStackEntry ->
            val serviceId = backStackEntry.arguments?.getString("serviceId") ?: ""
            val therapistId = backStackEntry.arguments?.getString("therapistId") ?: ""
            BookingScreen(
                viewModel = clientViewModel,
                serviceId = serviceId,
                therapistId = therapistId,
                onBack = { navController.popBackStack() },
                onSuccess = {
                    navController.navigate(Screen.MyAppointments.route) {
                        popUpTo(Screen.ClientHome.route)
                    }
                }
            )
        }
        
        composable(Screen.StaffHome.route) {
            StaffScheduleScreen(
                viewModel = staffViewModel,
                onLogout = {
                    tokenManager.clearTokens()
                    navController.navigate(Screen.Login.route) {
                        popUpTo(Screen.StaffHome.route) { inclusive = true }
                    }
                }
            )
        }
    }
}

@Composable
fun PlaceholderScreen(title: String, onLogout: () -> Unit) {
    androidx.compose.foundation.layout.Column(
        modifier = androidx.compose.ui.Modifier.fillMaxSize(),
        verticalArrangement = androidx.compose.foundation.layout.Arrangement.Center,
        horizontalAlignment = androidx.compose.ui.Alignment.CenterHorizontally
    ) {
        androidx.compose.material3.Text(text = title, style = androidx.compose.material3.MaterialTheme.typography.headlineLarge)
        androidx.compose.foundation.layout.Spacer(modifier = androidx.compose.ui.Modifier.height(16.dp))
        androidx.compose.material3.Button(onClick = onLogout) {
            androidx.compose.material3.Text("Wyloguj")
        }
    }
}

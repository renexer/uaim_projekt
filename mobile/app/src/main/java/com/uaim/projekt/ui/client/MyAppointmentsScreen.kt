package com.uaim.projekt.ui.client

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Star
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import com.uaim.projekt.api.AppointmentDto
import java.time.ZonedDateTime
import java.time.format.DateTimeFormatter

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MyAppointmentsScreen(
    viewModel: ClientViewModel,
    onLogout: () -> Unit
) {
    var showReviewDialog by remember { mutableStateOf<String?>(null) }

    LaunchedEffect(Unit) {
        viewModel.fetchMyAppointments()
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Moje Wizyty") },
                actions = {
                    TextButton(onClick = onLogout) {
                        Text("Wyloguj")
                    }
                }
            )
        }
    ) { padding ->
        if (viewModel.isLoading) {
            Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                CircularProgressIndicator()
            }
        } else {
            LazyColumn(modifier = Modifier.padding(padding).padding(horizontal = 16.dp)) {
                items(viewModel.myAppointments) { appointment ->
                    AppointmentItem(
                        appointment = appointment,
                        onReviewClick = { showReviewDialog = appointment.id },
                        summary = viewModel.myConsultations[appointment.id]
                    )
                }
            }
        }
    }

    if (showReviewDialog != null) {
        ReviewDialog(
            onDismiss = { showReviewDialog = null },
            onSubmit = { rating, comment ->
                viewModel.postReview(showReviewDialog!!, rating, comment)
                showReviewDialog = null
            }
        )
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AppointmentItem(
    appointment: AppointmentDto,
    onReviewClick: () -> Unit,
    summary: String? = null
) {
    val formatter = DateTimeFormatter.ofPattern("dd.MM.yyyy HH:mm")
    
    val date = try {
        java.time.OffsetDateTime.parse(appointment.startAt).format(formatter)
    } catch (e: Exception) {
        try {
            java.time.LocalDateTime.parse(appointment.startAt).format(formatter)
        } catch (e2: Exception) {
            appointment.startAt
        }
    }

    Card(
        modifier = Modifier.fillMaxWidth().padding(vertical = 8.dp),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(horizontalArrangement = Arrangement.SpaceBetween, modifier = Modifier.fillMaxWidth()) {
                Text(text = date, style = MaterialTheme.typography.titleMedium)
                Badge(containerColor = if(appointment.status == "COMPLETED") Color(0xFF4CAF50) else MaterialTheme.colorScheme.primary) {
                    Text(appointment.status, color = Color.White)
                }
            }
            Text(text = appointment.serviceName, style = MaterialTheme.typography.bodyLarge)
            Text(text = "Terapeuta: ${appointment.therapistName}", style = MaterialTheme.typography.bodyMedium)
            
            if (!summary.isNullOrBlank()) {
                Spacer(modifier = Modifier.height(12.dp))
                Surface(
                    color = MaterialTheme.colorScheme.secondaryContainer,
                    shape = MaterialTheme.shapes.small,
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Column(modifier = Modifier.padding(8.dp)) {
                        Text(
                            text = "Zalecenia terapeuty:",
                            style = MaterialTheme.typography.labelMedium,
                            color = MaterialTheme.colorScheme.onSecondaryContainer
                        )
                        Text(
                            text = summary,
                            style = MaterialTheme.typography.bodySmall
                        )
                    }
                }
            }

            if (appointment.status == "COMPLETED") {
                Button(
                    onClick = onReviewClick,
                    modifier = Modifier.align(Alignment.End).padding(top = 8.dp)
                ) {
                    Text("Oceń wizytę")
                }
            }
        }
    }
}

@Composable
fun ReviewDialog(onDismiss: () -> Unit, onSubmit: (Int, String) -> Unit) {
    var rating by remember { mutableStateOf(5) }
    var comment by remember { mutableStateOf("") }

    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("Dodaj opinię") },
        text = {
            Column {
                Text("Ocena (1-5):")
                Row {
                    (1..5).forEach { i ->
                        IconButton(onClick = { rating = i }) {
                            Icon(
                                Icons.Default.Star,
                                contentDescription = null,
                                tint = if (i <= rating) Color(0xFFFFB400) else Color.Gray
                            )
                        }
                    }
                }
                OutlinedTextField(
                    value = comment,
                    onValueChange = { comment = it },
                    label = { Text("Komentarz") },
                    modifier = Modifier.fillMaxWidth()
                )
            }
        },
        confirmButton = {
            Button(onClick = { onSubmit(rating, comment) }) {
                Text("Wyślij")
            }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) {
                Text("Anuluj")
            }
        }
    )
}

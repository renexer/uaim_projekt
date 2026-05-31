package com.uaim.projekt.ui.staff

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.uaim.projekt.api.StaffAppointmentDto
import java.time.ZonedDateTime
import java.time.format.DateTimeFormatter

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun StaffScheduleScreen(
    viewModel: StaffViewModel,
    onLogout: () -> Unit
) {
    var showSummaryDialog by remember { mutableStateOf<String?>(null) }
    
    LaunchedEffect(Unit) {
        viewModel.fetchAppointments()
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Mój Grafik") },
                actions = {
                    TextButton(onClick = onLogout) {
                        Text("Wyloguj", color = MaterialTheme.colorScheme.error)
                    }
                }
            )
        }
    ) { padding ->
        Column(modifier = Modifier.padding(padding)) {
            if (viewModel.isLoading) {
                Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                    CircularProgressIndicator()
                }
            } else if (viewModel.appointments.isEmpty()) {
                Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                    Text("Brak zaplanowanych wizyt")
                }
            } else {
                LazyColumn(modifier = Modifier.padding(horizontal = 16.dp)) {
                    items(viewModel.appointments) { appointment ->
                        AppointmentStaffItem(
                            appointment = appointment,
                            onStatusChange = { newStatus ->
                                viewModel.updateStatus(appointment.id, newStatus)
                            },
                            onAddSummary = { showSummaryDialog = appointment.id }
                        )
                    }
                }
            }
        }
    }

    if (showSummaryDialog != null) {
        SummaryDialog(
            onDismiss = { showSummaryDialog = null },
            onSubmit = { text ->
                viewModel.addSummary(showSummaryDialog!!, text)
                showSummaryDialog = null
            }
        )
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AppointmentStaffItem(
    appointment: StaffAppointmentDto,
    onStatusChange: (String) -> Unit,
    onAddSummary: () -> Unit
) {
    val formatter = DateTimeFormatter.ofPattern("HH:mm")
    val dateLabelFormatter = DateTimeFormatter.ofPattern("dd.MM")

    val (date, startTime, endTime) = try {
        val start = java.time.OffsetDateTime.parse(appointment.startAt)
        val end = java.time.OffsetDateTime.parse(appointment.endAt)
        Triple(start.format(dateLabelFormatter), start.format(formatter), end.format(formatter))
    } catch (e: Exception) {
        try {
            val start = java.time.LocalDateTime.parse(appointment.startAt)
            val end = java.time.LocalDateTime.parse(appointment.endAt)
            Triple(start.format(dateLabelFormatter), start.format(formatter), end.format(formatter))
        } catch (e2: Exception) {
            Triple("??", "??", "??")
        }
    }

    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 8.dp),
        colors = CardDefaults.cardColors(
            containerColor = when (appointment.status) {
                "COMPLETED" -> Color(0xFFE8F5E9)
                "CANCELLED_BY_PATIENT", "CANCELLED_BY_CLINIC" -> Color(0xFFFFEBEE)
                else -> MaterialTheme.colorScheme.surfaceVariant
            }
        )
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(horizontalArrangement = Arrangement.SpaceBetween, modifier = Modifier.fillMaxWidth()) {
                Text(text = "$date | $startTime - $endTime", fontWeight = FontWeight.Bold)
                Badge(
                    containerColor = when (appointment.status) {
                        "BOOKED" -> MaterialTheme.colorScheme.primary
                        "COMPLETED" -> Color(0xFF4CAF50)
                        else -> Color.Gray
                    }
                ) {
                    Text(appointment.status, color = Color.White)
                }
            }
            
            Spacer(modifier = Modifier.height(8.dp))
            Text(text = "Pacjent: ${appointment.patientEmail}", style = MaterialTheme.typography.bodyLarge)
            Text(text = "Usługa: ${appointment.serviceName}", style = MaterialTheme.typography.bodyMedium)
            
            if (appointment.status == "BOOKED") {
                Spacer(modifier = Modifier.height(12.dp))
                Row(horizontalArrangement = Arrangement.End, modifier = Modifier.fillMaxWidth()) {
                    TextButton(onClick = { onStatusChange("NO_SHOW") }) {
                        Text("Nieobecność", color = MaterialTheme.colorScheme.error)
                    }
                    Button(onClick = { onStatusChange("COMPLETED") }) {
                        Text("Zakończ")
                    }
                }
            } else if (appointment.status == "COMPLETED") {
                Button(
                    onClick = onAddSummary,
                    modifier = Modifier.align(Alignment.End).padding(top = 8.dp)
                ) {
                    Text("Dodaj zalecenia")
                }
            }
        }
    }
}

@Composable
fun SummaryDialog(onDismiss: () -> Unit, onSubmit: (String) -> Unit) {
    var text by remember { mutableStateOf("") }

    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("Dodaj podsumowanie wizyty") },
        text = {
            OutlinedTextField(
                value = text,
                onValueChange = { text = it },
                label = { Text("Zalecenia dla pacjenta") },
                modifier = Modifier.fillMaxWidth().height(150.dp)
            )
        },
        confirmButton = {
            Button(onClick = { onSubmit(text) }, enabled = text.length >= 5) {
                Text("Zapisz")
            }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) {
                Text("Anuluj")
            }
        }
    )
}

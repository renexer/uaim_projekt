package com.uaim.projekt.ui.client

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import com.uaim.projekt.api.AvailabilityResponse
import java.time.ZonedDateTime
import java.time.format.DateTimeFormatter

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun BookingScreen(
    viewModel: ClientViewModel,
    serviceId: String,
    therapistId: String,
    onBack: () -> Unit,
    onSuccess: () -> Unit
) {
    // Zakres na najbliższe 7 dni - wymuszamy format bez milisekund, który backend lubi najbardziej
    val formatterIso = DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm:ssXXX")
    val from = ZonedDateTime.now().format(formatterIso)
    val to = ZonedDateTime.now().plusDays(7).format(formatterIso)

    LaunchedEffect(serviceId, therapistId) {
        viewModel.fetchAvailability(serviceId, therapistId, from, to)
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Wybierz termin") },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "Wstecz")
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
            Column(modifier = Modifier.padding(padding).padding(16.dp)) {
                val item = viewModel.availability?.items?.firstOrNull { it.therapist.id == therapistId }
                
                if (item == null || item.slots.isEmpty()) {
                    Text("Brak dostępnych terminów w najbliższym czasie.")
                } else {
                    Text(
                        "Dostępne terminy dla: ${item.therapist.fullName}",
                        style = MaterialTheme.typography.titleMedium
                    )
                    Spacer(modifier = Modifier.height(16.dp))
                    
                    LazyVerticalGrid(
                        columns = GridCells.Fixed(3),
                        horizontalArrangement = Arrangement.spacedBy(8.dp),
                        verticalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        items(item.slots) { slot ->
                            SlotItem(slot.startAt) {
                                viewModel.bookAppointment(serviceId, therapistId, slot.startAt, onSuccess)
                            }
                        }
                    }
                }
                
                if (viewModel.errorMessage != null) {
                    Text(
                        text = viewModel.errorMessage!!,
                        color = MaterialTheme.colorScheme.error,
                        modifier = Modifier.padding(top = 16.dp)
                    )
                }
            }
        }
    }
}

@Composable
fun SlotItem(startAt: String, onClick: () -> Unit) {
    val formatter = DateTimeFormatter.ofPattern("dd.MM HH:mm")
    val time = try {
        java.time.OffsetDateTime.parse(startAt).format(formatter)
    } catch (e: Exception) {
        try {
            java.time.LocalDateTime.parse(startAt).format(formatter)
        } catch (e2: Exception) {
            startAt
        }
    }
    
    Surface(
        onClick = onClick,
        shape = MaterialTheme.shapes.medium,
        color = MaterialTheme.colorScheme.primaryContainer,
        modifier = Modifier.height(48.dp)
    ) {
        Box(contentAlignment = Alignment.Center) {
            Text(text = time, style = MaterialTheme.typography.bodySmall)
        }
    }
}

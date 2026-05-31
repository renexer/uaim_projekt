package com.uaim.projekt.ui.client

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.filled.List
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.uaim.projekt.api.ServiceDto

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ServicesScreen(
    viewModel: ClientViewModel,
    onServiceClick: (ServiceDto) -> Unit,
    onViewAppointments: () -> Unit
) {
    LaunchedEffect(Unit) {
        viewModel.fetchServices()
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Nasze Usługi") },
                actions = {
                    IconButton(onClick = onViewAppointments) {
                        Icon(androidx.compose.material.icons.Icons.Default.List, contentDescription = "Moje wizyty")
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
                items(viewModel.services) { service ->
                    ServiceItem(service) { onServiceClick(service) }
                }
            }
        }
    }
}

@Composable
fun ServiceItem(service: ServiceDto, onClick: () -> Unit) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 8.dp)
            .clickable { onClick() },
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(text = service.name, style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Bold)
            Text(text = service.description, style = MaterialTheme.typography.bodyMedium, maxLines = 2)
            Spacer(modifier = Modifier.height(8.dp))
            Row(horizontalArrangement = Arrangement.SpaceBetween, modifier = Modifier.fillMaxWidth()) {
                Text(text = "${service.durationMinutes} min", style = MaterialTheme.typography.labelLarge)
                Text(text = "${service.basePrice} ${service.currency}", style = MaterialTheme.typography.labelLarge, color = MaterialTheme.colorScheme.primary)
            }
        }
    }
}

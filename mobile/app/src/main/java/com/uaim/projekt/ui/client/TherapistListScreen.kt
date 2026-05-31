package com.uaim.projekt.ui.client

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Star
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import com.uaim.projekt.api.TherapistPublicDto

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun TherapistListScreen(
    viewModel: ClientViewModel,
    serviceId: String,
    serviceName: String,
    onBack: () -> Unit,
    onTherapistClick: (TherapistPublicDto) -> Unit
) {
    LaunchedEffect(serviceId) {
        viewModel.fetchTherapists(serviceId)
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text(serviceName) },
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
            LazyColumn(modifier = Modifier.padding(padding).padding(horizontal = 16.dp)) {
                items(viewModel.therapists) { therapist ->
                    TherapistItem(therapist, onClick = { onTherapistClick(therapist) })
                }
            }
        }
    }
}

@Composable
fun TherapistItem(therapist: TherapistPublicDto, onClick: () -> Unit) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 8.dp),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Row(
            modifier = Modifier.padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column(modifier = Modifier.weight(1f)) {
                Text(text = therapist.fullName, style = MaterialTheme.typography.titleMedium)
                Text(text = therapist.title, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.secondary)
                Spacer(modifier = Modifier.height(4.dp))
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(Icons.Default.Star, contentDescription = null, tint = Color(0xFFFFB400), modifier = Modifier.size(16.dp))
                    Text(text = " ${therapist.averageRating} (${therapist.reviewsCount})", style = MaterialTheme.typography.bodySmall)
                }
            }
            Button(onClick = onClick) {
                Text("Umów")
            }
        }
    }
}

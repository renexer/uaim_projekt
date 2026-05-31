# Aplikacja mobilna Android/Kotlin — dokumentacja części mobile

## Cel

Aplikacja mobilna jest natywnym klientem Android dla systemu gabinetu psychologiczno-terapeutycznego „Spokojna Przystań”. Aplikacja nie została przebudowana od zera. Zachowano istniejące działające funkcje, poprawiono konfigurację połączenia z backendem, dodano komentarze w kluczowych miejscach oraz uzupełniono obsługę anulowania wizyty pacjenta.

Aplikacja mobilna umożliwia pacjentowi:

- zalogowanie się,
- przeglądanie usług gabinetu,
- przejście do terapeutów obsługujących wybraną usługę,
- wybór dostępnego terminu,
- rezerwację wizyty,
- przegląd własnych wizyt,
- anulowanie wizyty zgodnie z regułami backendu,
- przegląd historii konsultacji,
- dodanie opinii po zakończonej wizycie.

W aplikacji mobilnej terapeuci są prezentowani w kontekście wybranej usługi. Nie ma osobnej globalnej zakładki „Terapeuci”. Użytkownik wybiera usługę, następnie widzi terapeutów przypisanych do tej usługi i przechodzi do wyboru terminu.

## Technologia i biblioteki

Aplikacja używa:

- Kotlin,
- Android Jetpack Compose,
- Navigation Compose,
- ViewModel,
- Kotlin coroutines,
- Retrofit,
- OkHttp,
- Gson converter,
- SharedPreferences do prostego przechowywania tokenów JWT.

## Konfiguracja backendu

Plik odpowiedzialny za konfigurację Retrofit i endpointów:

```text
mobile/app/src/main/java/com/uaim/projekt/api/AuthApi.kt
```

Dla emulatora Android Studio bazowy adres backendu powinien być ustawiony następująco:

```kotlin
private const val BASE_URL = "http://10.0.2.2:8080/"
```

Adres `10.0.2.2` jest specjalnym adresem emulatora Android, który wskazuje na komputer hosta. Oznacza to, że aplikacja mobilna uruchomiona w emulatorze łączy się z backendem działającym lokalnie na komputerze.

Dla telefonu fizycznego należy użyć adresu IP komputera w sieci lokalnej albo publicznego adresu serwera, np.:

```kotlin
private const val BASE_URL = "http://192.168.1.100:8080/"
```

Endpointy Retrofit korzystają z prefixu `api/v1`, np.:

```text
api/v1/auth/login
api/v1/services
api/v1/appointments
```

## Struktura katalogów mobile

```text
mobile/app/src/main/java/com/uaim/projekt/
├── MainActivity.kt
├── api/
│   ├── AuthApi.kt              # definicje endpointów Retrofit i DTO
│   └── AuthInterceptor.kt      # dodawanie nagłówka Authorization
├── auth/
│   └── TokenManager.kt         # zapis/odczyt tokenów JWT
└── ui/
    ├── Navigation.kt           # nawigacja Compose
    ├── login/
    │   ├── LoginScreen.kt
    │   └── LoginViewModel.kt
    ├── client/
    │   ├── ServicesScreen.kt
    │   ├── TherapistListScreen.kt
    │   ├── BookingScreen.kt
    │   ├── MyAppointmentsScreen.kt
    │   └── ClientViewModel.kt
    └── staff/
        ├── StaffScheduleScreen.kt
        └── StaffViewModel.kt
```

## Kluczowe klasy i odpowiedzialności

### `AuthApi.kt`

Plik zawiera:

- konfigurację bazowego adresu API,
- definicje endpointów Retrofit,
- klasy DTO dla zapytań i odpowiedzi,
- utworzenie klienta Retrofit i OkHttp.

### `AuthInterceptor.kt`

Interceptor OkHttp dodaje token JWT do zapytań wymagających autoryzacji:

```http
Authorization: Bearer <token>
```

Dzięki temu ViewModele i ekrany nie muszą ręcznie dopisywać nagłówka do każdego zapytania.

### `TokenManager.kt`

Klasa zarządza zapisem i odczytem tokenów JWT w `SharedPreferences`. Przechowuje token dostępowy, token odświeżający i podstawowe dane sesji.

### `LoginViewModel.kt`

ViewModel obsługuje proces logowania. Wysyła dane logowania do backendu, odbiera tokeny i zapisuje je przez `TokenManager`.

### `ClientViewModel.kt`

ViewModel dla części pacjenta. Odpowiada za pobieranie usług, terapeutów, dostępnych terminów, rezerwację wizyty, pobieranie wizyt pacjenta i anulowanie wizyty.

### `StaffViewModel.kt`

ViewModel dla terapeuty/staff. Odpowiada za pobieranie wizyt przypisanych do terapeuty/staff oraz operacje statusów i podsumowań konsultacji, jeżeli są dostępne w backendzie.

## Główne przepływy aplikacji

### Logowanie

Ekran logowania wysyła żądanie:

```text
POST api/v1/auth/login
```

Po poprawnym logowaniu tokeny JWT są zapisywane lokalnie, a użytkownik przechodzi do części pacjenta albo terapeuty/staff, zależnie od roli zwróconej przez backend.

Powiązane screeny:

```text
docs/screenshots/mobile/mobile-01-home.png
docs/screenshots/mobile/mobile-02-login.png
```

### Lista usług

Ekran usług pobiera dane z endpointu:

```text
GET api/v1/services
```

Widok pokazuje nazwę usługi, opis, czas trwania i cenę.

Powiązany screen:

```text
docs/screenshots/mobile/mobile-03-services.png
```

### Lista terapeutów dla usługi

Po wyborze usługi aplikacja przechodzi do listy terapeutów obsługujących tę usługę. Dane są pobierane z endpointu:

```text
GET api/v1/services/{service_id}/therapists
```

Widok pokazuje dane terapeuty, specjalizację, ocenę i przycisk przejścia do wyboru terminu.

Powiązany screen:

```text
docs/screenshots/mobile/mobile-05-therapists.png
```

### Wybór terminu i rezerwacja

Po wyborze terapeuty aplikacja pobiera dostępne terminy z endpointu:

```text
GET api/v1/availability?serviceId=...&therapistId=...&from=...&to=...
```

Użytkownik wybiera termin, a następnie aplikacja wysyła rezerwację:

```text
POST api/v1/appointments
```

Powiązany screen:

```text
docs/screenshots/mobile/mobile-06-booking.png
```

### Moje wizyty

Ekran wizyt pacjenta pobiera dane z endpointu:

```text
GET api/v1/appointments/me?scope=all
```

Widok pokazuje wizyty zaplanowane, zakończone i anulowane. Dla zakończonych wizyt aplikacja pokazuje podsumowanie konsultacji, jeżeli zostało dodane przez terapeutę.

Powiązany screen:

```text
docs/screenshots/mobile/mobile-04-my-appointments.png
```

### Anulowanie wizyty

Pacjent może anulować zaplanowaną wizytę. Operacja korzysta z endpointu:

```text
POST api/v1/appointments/{appointment_id}/cancel
```

Backend może odmówić anulowania, jeżeli narusza to reguły biznesowe, np. termin wizyty jest zbyt bliski. Dla terminu spełniającego warunki anulowanie działa poprawnie i wizyta zmienia status na anulowany.

Powiązany screen:

```text
docs/screenshots/mobile/mobile-07-cancelled-by-patient.png
```

### Historia konsultacji i opinie

Zakończone wizyty mogą zawierać podsumowanie konsultacji dodane przez terapeutę. Po zakończeniu wizyty pacjent może wystawić opinię, jeżeli backend pozwala na dodanie opinii dla danej wizyty.

### Widok terapeuty/staff

Jeżeli zalogowany użytkownik ma rolę terapeuty lub admina, aplikacja może prezentować widok grafiku/wizyt staff. Widok ten wykorzystuje endpointy staff backendu.

## Komentarze w kodzie

Komentarze dodano w miejscach istotnych dla zrozumienia działania aplikacji:

- przy konfiguracji Retrofit i adresu backendu,
- przy interceptorze dodającym token JWT,
- przy `TokenManager`, który zapisuje tokeny,
- przy ViewModelach odpowiedzialnych za logowanie i przepływy pacjenta,
- przy operacji anulowania wizyty.

Nie komentowano każdej linijki, aby kod pozostał czytelny.

## Weryfikacja działania

Aplikację mobilną zweryfikowano ręcznie na emulatorze Android. Sprawdzone przepływy:

- uruchomienie aplikacji,
- logowanie pacjenta,
- lista usług,
- lista terapeutów po wyborze usługi,
- wybór dostępnego terminu,
- rezerwacja wizyty,
- lista moich wizyt,
- anulowanie wizyty,
- historia konsultacji/opinie.

Backend podczas testów działał lokalnie pod adresem:

```text
http://127.0.0.1:8080/api/v1
```

Aplikacja mobilna w emulatorze używała adresu:

```text
http://10.0.2.2:8080/
```

## Uruchomienie lokalne

Aby uruchomić aplikację mobilną:

1. Uruchomić backend lokalnie.
2. Sprawdzić, czy endpoint zdrowia działa:

```text
http://127.0.0.1:8080/api/v1/health
```

3. Otworzyć projekt w Android Studio.
4. Uruchomić emulator Android.
5. Uruchomić konfigurację aplikacji.

Alternatywnie z terminala:

```bash
cd uaim_projekt
./gradlew :mobile:assembleDebug
```

Na Windows:

```powershell
cd uaim_projekt
.\gradlew.bat :mobile:assembleDebug
```

## Konta testowe

- Pacjent: `jan@example.com` / `Password123!`,
- Pacjent: `ola@example.com` / `Password123!`,
- Terapeuta: `anna@example.com` / `Password123!`,
- Terapeuta: `piotr@example.com` / `Password123!`,
- Administrator: `admin@example.com` / `Admin123!`.

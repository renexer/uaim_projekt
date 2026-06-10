# Frontend React — dokumentacja części webowej

## Cel

Frontend webowy jest aplikacją SPA dla systemu gabinetu psychologiczno-terapeutycznego „Spokojna Przystań”. Aplikacja realizuje interfejs pacjenta oraz podstawowy panel terapeuty/staff. W aktualnej wersji frontend nie jest już prostym healthcheckiem, lecz pełnym klientem webowym komunikującym się z backendem Flask przez API REST pod prefixem `/api/v1`.

Aplikacja webowa pozwala pacjentowi:

- założyć konto,
- zalogować się,
- przeglądać katalog usług,
- przeglądać terapeutów i ich oceny,
- sprawdzać dostępne terminy,
- rezerwować wizyty,
- przeglądać swoje wizyty,
- anulować wizyty zgodnie z regułami backendu,
- przeglądać historię konsultacji,
- dodawać opinie po zakończonych wizytach.

Terapeuta/staff może korzystać z panelu wizyt, zmieniać statusy wizyt oraz dodawać podsumowania konsultacji.

## Konfiguracja API

Plik odpowiedzialny za komunikację z backendem:

```text
frontend/src/api.js
```

Bazowy adres API jest ustawiany przez zmienną środowiskową:

```env
REACT_APP_API_URL=http://127.0.0.1:8080/api/v1
```

Przykład konfiguracji znajduje się w pliku:

```text
frontend/.env.example
```

Podczas lokalnej weryfikacji backend działał pod adresem:

```text
http://127.0.0.1:8080/api/v1
```

W przypadku wdrożenia przez Docker lub reverse proxy wartość `REACT_APP_API_URL` może zostać zmieniona, np. na ścieżkę względną `/api/v1` albo na adres publicznego serwera.

Klient API:

- obsługuje odpowiedzi backendu w formacie `{ data: ... }`,
- obsługuje błędy backendu w formacie `{ error: { message, code, details } }`,
- dodaje nagłówek `Authorization: Bearer <token>` dla zapytań wymagających logowania,
- udostępnia funkcje dla autoryzacji, usług, terapeutów, dostępności, wizyt, konsultacji i panelu staff,
- współpracuje z `AuthContext`, który przechowuje dane sesji użytkownika.

## Architektura aplikacji webowej

Aplikacja jest zbudowana w React i korzysta z `react-router-dom` do routingu. Stan autoryzacji użytkownika jest zarządzany przez `AuthContext`. Dane sesji są zapisywane w `localStorage`, aby odświeżenie strony nie powodowało natychmiastowego wylogowania.

Najważniejsze pliki:

```text
frontend/src/
├── api.js                         # klient HTTP, obsługa JWT i błędów API
├── AuthContext.js                 # globalny stan logowania użytkownika
├── App.js                         # definicja tras aplikacji
├── App.css                        # style aplikacji i responsywność
├── setupTests.js                  # konfiguracja testów React Testing Library
├── components/
│   ├── Layout.js                  # wspólny layout, menu, nazwa użytkownika i wylogowanie
│   ├── ProtectedRoute.js          # ochrona tras wymagających logowania/roli
│   └── StateBlocks.js             # komponenty loading/error/empty
└── pages/
    ├── HomePage.js                # strona startowa
    ├── RegisterPage.js            # rejestracja pacjenta
    ├── LoginPage.js               # logowanie
    ├── ServicesPage.js            # katalog usług
    ├── TherapistsPage.js          # lista terapeutów
    ├── TherapistDetailsPage.js    # profil terapeuty, opinie, terminy
    ├── BookingPage.js             # rezerwacja wizyty
    ├── AppointmentsPage.js        # moje wizyty i anulowanie
    ├── ConsultationsPage.js       # historia konsultacji i opinie
    ├── StaffPage.js               # panel terapeuty/staff
    ├── NotFoundPage.js            # strona 404
    └── pageUtils.js               # formatowanie dat/cen i funkcje pomocnicze
```

## Routing

| Ścieżka | Widok | Dostęp |
|---|---|---|
| `/` | Strona startowa | publiczny |
| `/register` | Rejestracja pacjenta | publiczny |
| `/login` | Logowanie | publiczny |
| `/services` | Lista usług | publiczny |
| `/services/:serviceId/therapists` | Terapeuci dla wybranej usługi | publiczny |
| `/therapists` | Lista terapeutów | publiczny |
| `/therapists/:therapistId` | Szczegóły terapeuty, opinie i terminy | publiczny, rezerwacja wymaga logowania |
| `/booking` | Rezerwacja wizyty | formularz widoczny publicznie, potwierdzenie wymaga logowania |
| `/appointments` | Moje wizyty | zalogowany pacjent |
| `/consultations` | Historia konsultacji i opinie | zalogowany pacjent |
| `/staff` | Panel terapeuty/staff | role `ADMIN` albo `THERAPIST` |
| `*` | Strona 404 | publiczny |

Trasy chronione są realizowane przez komponent `ProtectedRoute`. Użytkownik bez tokenu jest przekierowywany do logowania. Użytkownik bez wymaganej roli widzi komunikat o braku dostępu.

## Obsługa autoryzacji JWT

Za autoryzację odpowiadają:

```text
frontend/src/AuthContext.js
frontend/src/api.js
frontend/src/components/ProtectedRoute.js
```

Po poprawnym logowaniu frontend zapisuje w `localStorage`:

```text
uaim_access_token
uaim_refresh_token
uaim_user
```

Dla endpointów chronionych klient API dodaje nagłówek:

```http
Authorization: Bearer <token>
```

Wylogowanie usuwa dane sesji z `localStorage` i odświeża stan aplikacji.

## Obsługiwane endpointy backendu

Frontend korzysta z istniejącego kontraktu API backendu. Nie wymaga zmiany kontraktu API.

### Autoryzacja i profil użytkownika

| Funkcja | Endpoint | Metoda |
|---|---|---|
| Rejestracja pacjenta | `/api/v1/auth/register` | `POST` |
| Logowanie | `/api/v1/auth/login` | `POST` |
| Profil użytkownika | `/api/v1/users/me` | `GET` |
| Wylogowanie | `/api/v1/auth/logout` | `POST` |

### Katalog, terapeuci i rezerwacje

| Funkcja | Endpoint | Metoda |
|---|---|---|
| Lista usług | `/api/v1/services` | `GET` |
| Szczegóły usługi | `/api/v1/services/{id}` | `GET` |
| Terapeuci dla usługi | `/api/v1/services/{id}/therapists` | `GET` |
| Szczegóły terapeuty | `/api/v1/therapists/{id}` | `GET` |
| Opinie terapeuty | `/api/v1/therapists/{id}/reviews` | `GET` |
| Dostępność terminów | `/api/v1/availability?serviceId=&therapistId=&from=&to=` | `GET` |
| Rezerwacja wizyty | `/api/v1/appointments` | `POST` |
| Moje wizyty | `/api/v1/appointments/me?scope=...` | `GET` |
| Anulowanie wizyty | `/api/v1/appointments/{id}/cancel` | `POST` |
| Historia konsultacji | `/api/v1/consultations/me` | `GET` |
| Dodanie opinii | `/api/v1/appointments/{id}/review` | `POST` |

### Panel terapeuty/staff

| Funkcja | Endpoint | Metoda |
|---|---|---|
| Lista wizyt staff | `/api/v1/staff/appointments` | `GET` |
| Zmiana statusu wizyty | `/api/v1/staff/appointments/{id}/status` | `PATCH` |
| Podsumowanie konsultacji | `/api/v1/staff/appointments/{id}/consultation-summary` | `PUT` |

## Widoki i funkcje

### Strona startowa

Strona startowa zawiera krótki opis gabinetu oraz przyciski prowadzące do rejestracji, logowania i katalogu usług. Jest dostępna bez logowania.

Powiązany screen:

```text
docs/screenshots/web/web-01-home.png
```

### Rejestracja

Formularz rejestracji pacjenta zawiera pola: imię, nazwisko, e-mail, telefon, hasło i potwierdzenie hasła. Frontend waliduje podstawowe pola, format adresu e-mail, długość hasła i zgodność haseł. Błędy backendu są wyświetlane użytkownikowi.

### Logowanie

Formularz logowania wymaga e-maila i hasła. Po sukcesie zapisywany jest token JWT i dane użytkownika. Pacjent trafia do widoku „Moje wizyty”, a terapeuta/admin do panelu staff.

Powiązany screen:

```text
docs/screenshots/web/web-02-login.png
```

### Lista usług

Widok pobiera usługi z `/api/v1/services` i pokazuje nazwę, opis, czas trwania, cenę oraz walutę. Z poziomu karty usługi można przejść do terapeutów albo od razu do rezerwacji.

Powiązany screen:

```text
docs/screenshots/web/web-03-services.png
```

### Lista terapeutów

Widok `/therapists` prezentuje terapeutów oraz informacje o specjalizacji, doświadczeniu, opisie i ocenach. Frontend pobiera usługi i terapeutów przypisanych do usług, a następnie deduplikuje terapeutów po `id`.

Powiązany screen:

```text
docs/screenshots/web/web-04-therapists.png
```

### Szczegóły terapeuty

Widok szczegółów terapeuty pokazuje profil terapeuty, opis, ocenę, opinie oraz dostępne terminy dla wybranej usługi. Wybranie terminu prowadzi do rezerwacji wizyty.

### Rezerwacja wizyty

Widok umożliwia wybór usługi, terapeuty i terminu. Terminy pobierane są z `/api/v1/availability`. Potwierdzenie rezerwacji wysyła `POST /api/v1/appointments`. Po poprawnej rezerwacji użytkownik dostaje komunikat sukcesu, a zarezerwowana wizyta pojawia się w widoku „Moje wizyty”.

Powiązany screen:

```text
docs/screenshots/web/web-05-booking.png
```

### Moje wizyty

Widok pobiera listę zaplanowanych wizyt oraz wizyty historyczne/anulowane. Pacjent może anulować zaplanowaną wizytę, jeżeli pozwalają na to reguły backendu. Anulowanie jest realizowane przez `POST /api/v1/appointments/{id}/cancel`.

Powiązany screen:

```text
docs/screenshots/web/web-06-my-appointments.png
```

### Historia konsultacji i opinie

Widok pokazuje zakończone konsultacje, podsumowania dodane przez terapeutę oraz informację o opinii. Jeżeli backend zwraca, że opinia nie została jeszcze dodana, frontend pokazuje formularz dodania opinii.

Powiązany screen:

```text
docs/screenshots/web/web-07-cancelled-or-history.png
```

### Panel terapeuty/staff

Panel jest dostępny dla ról `ADMIN` i `THERAPIST`. Pokazuje wizyty obsługiwane przez terapeutę/staff oraz umożliwia zmianę statusu wizyty i dodanie podsumowania konsultacji.

Powiązany screen:

```text
docs/screenshots/web/web-08-staff-panel.png
```

## Obsługa stanów ładowania i błędów

Aplikacja używa komponentów ze `StateBlocks.js`:

- `LoadingBlock` — informacja o ładowaniu danych,
- `ErrorBlock` — informacja o błędzie API,
- `EmptyBlock` — informacja o pustej liście.

Dzięki temu widoki nie pozostają puste podczas oczekiwania na odpowiedź backendu.

## Responsywność i wygląd

Interfejs webowy został przygotowany jako lekki, responsywny layout. Karty usług, terapeutów i wizyt dopasowują się do szerokości ekranu. Aplikacja korzysta ze spójnych przycisków, sekcji, tabel i komunikatów.

## Testy frontendu

Plik testów:

```text
frontend/src/App.test.js
```

Dodano testy dla:

- renderowania strony startowej,
- logowania i zapisu tokenu JWT,
- chronionej trasy,
- pobierania i renderowania listy usług,
- obsługi błędu API,
- walidacji formularza rejestracji,
- listy terapeutów,
- formularza rezerwacji i dostępnych terminów,
- blokady panelu staff dla pacjenta,
- historii konsultacji,
- panelu terapeuty,
- szczegółów terapeuty,
- strony 404.

Uruchomienie testów:

```bash
cd frontend
npm test -- --coverage --watchAll=false
```

Wynik lokalnej weryfikacji:

```text
Test Suites: 1 passed, 1 total
Tests:       13 passed, 13 total
Snapshots:   0 total

Coverage:
All files: statements 66.6%, branches 52.76%, functions 66.21%, lines 68.39%
```

Build produkcyjny:

```bash
npm run build
```

Wynik:

```text
Compiled successfully.
```

## Uruchomienie lokalne

Backend powinien być uruchomiony pod adresem zgodnym z `REACT_APP_API_URL`, np. lokalnie:

```text
http://127.0.0.1:8080/api/v1
```

Uruchomienie frontendu:

```bash
cd frontend
npm install
cp .env.example .env
npm start
```

Na Windows PowerShell:

```powershell
cd frontend
Copy-Item .env.example .env -Force
npm install
npm start
```

Aplikacja webowa będzie dostępna pod adresem:

```text
http://localhost:3000
```

## Konta testowe

- Pacjent: `jan@example.com` / `Password123!`,
- Pacjent: `ola@example.com` / `Password123!`,
- Terapeuta: `anna@example.com` / `Password123!`,
- Terapeuta: `piotr@example.com` / `Password123!`,
- Administrator: `admin@example.com` / `Admin123!`.

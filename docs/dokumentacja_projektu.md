# Dokumentacja projektu UAIM — Gabinet psychologiczno-terapeutyczny

## 1. Opis ogólnej koncepcji rozwiązania

Projekt realizuje system dla gabinetu psychologiczno-terapeutycznego „Spokojna Przystań”. Aplikacja wspiera obsługę pacjentów, terapeutów oraz administratorów gabinetu. System umożliwia pacjentom rejestrację, logowanie, przeglądanie katalogu usług, przegląd terapeutów i ich ocen, wybór dostępnego terminu, rezerwację wizyty, anulowanie wizyty oraz przegląd historii konsultacji.

Po zakończonej konsultacji pacjent może zapoznać się z podsumowaniem przygotowanym przez terapeutę i dodać opinię. Terapeuta lub pracownik staff może korzystać z panelu wizyt, zmieniać statusy wizyt oraz dodawać podsumowania konsultacji. Administrator może zarządzać usługami, profilami terapeutów i grafikami dostępności.

Projekt ma charakter klient-serwer i składa się z aplikacji webowej React, natywnej aplikacji mobilnej Android/Kotlin, backendu Flask, relacyjnej bazy PostgreSQL oraz konfiguracji Docker umożliwiającej uruchomienie systemu w środowisku kontenerowym.

## 2. Ogólna architektura systemu

System składa się z następujących komponentów:

1. **Aplikacja webowa React SPA** — interfejs użytkownika działający w przeglądarce.
2. **Aplikacja mobilna Android/Kotlin** — natywny klient mobilny korzystający z tego samego API co aplikacja webowa.
3. **Backend Flask** — REST API pod prefiksem `/api/v1`, logika biznesowa, obsługa JWT, role użytkowników i komunikacja z bazą danych.
4. **Baza PostgreSQL** — relacyjna baza danych uruchamiana w Dockerze.
5. **NGINX / Docker** — serwowanie aplikacji webowej i przekazywanie zapytań API do backendu.

Ogólny schemat komunikacji:

```text
[React SPA]              \
                          -> [Flask API /api/v1] -> [PostgreSQL]
[Android/Kotlin mobile]  /
```

Aplikacja webowa i aplikacja mobilna nie komunikują się bezpośrednio z bazą danych. Wszystkie operacje biznesowe są wykonywane przez backend Flask. Backend odpowiada za autoryzację, walidację danych, logikę rezerwacji, wyliczanie dostępności terminów, obsługę ról użytkowników, konsultacje, opinie oraz powiadomienia.

W środowisku Docker frontend jest budowany jako aplikacja React i serwowany przez NGINX. Backend działa w kontenerze Python/Gunicorn, a baza danych działa w kontenerze PostgreSQL. Zapytania do `/api/` są przekazywane do backendu.

## 3. Lista wymaganych i zrealizowanych funkcji

| Funkcja / wymaganie | Status | Sposób realizacji |
|---|---|---|
| Zakładanie konta użytkownika | Zrealizowane | Formularz rejestracji pacjenta w aplikacji webowej, backend `POST /api/v1/auth/register`. |
| Uwierzytelnienie i logowanie | Zrealizowane | Logowanie web/mobile, tokeny JWT, backend `POST /api/v1/auth/login`. |
| Pobieranie profilu użytkownika | Zrealizowane | Endpoint `GET /api/v1/users/me`, używany do odtworzenia sesji i roli użytkownika. |
| Przeglądanie katalogu usług | Zrealizowane | Web/mobile: lista usług z `GET /api/v1/services`. |
| Przegląd terapeutów/terapeutek | Zrealizowane | Web: lista i szczegóły terapeutów; mobile: terapeuci po wyborze usługi. Endpointy `GET /api/v1/services/{id}/therapists`, `GET /api/v1/therapists/{id}`. |
| Oceny i opinie terapeutów | Zrealizowane | Lista opinii terapeuty przez `GET /api/v1/therapists/{id}/reviews`, dodanie opinii przez `POST /api/v1/appointments/{id}/review`. |
| Podgląd wolnych terminów | Zrealizowane | Web/mobile korzystają z `GET /api/v1/availability`. |
| Umawianie terminu wizyty | Zrealizowane | Wybór usługi, terapeuty i slotu, następnie `POST /api/v1/appointments`. |
| Zwalnianie/anulowanie terminu | Zrealizowane | Web/mobile: `POST /api/v1/appointments/{id}/cancel`; backend egzekwuje reguły anulowania, np. ograniczenia czasowe. |
| Przegląd zaplanowanych wizyt | Zrealizowane | Web/mobile: `GET /api/v1/appointments/me?scope=upcoming`. |
| Przegląd zrealizowanych wizyt | Zrealizowane | Web/mobile: `GET /api/v1/appointments/me?scope=all` oraz `GET /api/v1/consultations/me`. |
| Historia konsultacji | Zrealizowane | Pacjent widzi zakończone konsultacje i podsumowania terapeuty. |
| Przebieg/podsumowanie konsultacji | Zrealizowane | Staff dodaje opis przez `PUT /api/v1/staff/appointments/{id}/consultation-summary`. |
| Panel terapeuty/staff | Zrealizowane | Web: lista wizyt, zmiana statusu, podsumowanie konsultacji; mobile: podstawowy widok staff, jeżeli użytkownik ma odpowiednią rolę. |
| Powiadomienia email | Zrealizowane demonstracyjnie | Backend ma kolejkę `EmailNotification`, tryb konsolowy oraz możliwość konfiguracji SMTP przez `MAIL_BACKEND=smtp`. |
| Testy backendu | Zrealizowane | 14 testów, pokrycie 79%. |
| Testy frontendu | Zrealizowane | 13 testów, pokrycie powyżej 60% dla statements i lines. |
| Docker | Zrealizowane | `docker-compose.yml`, kontenery bazy, backendu i frontendu. |

## 4. Opis aplikacji webowej

Szczegółowa dokumentacja frontendu znajduje się w pliku:

```text
docs/frontend.md
```

### 4.1 Architektura aplikacji webowej

Aplikacja webowa została wykonana w React jako SPA. Wykorzystuje:

- `react-router-dom` do obsługi routingu,
- `AuthContext` do globalnego stanu autoryzacji,
- `localStorage` do zapisu danych sesji użytkownika,
- własnego klienta API w `frontend/src/api.js`,
- `ProtectedRoute` do blokowania tras wymagających logowania lub odpowiedniej roli,
- komponenty stanów asynchronicznych: ładowanie, błąd, pusty wynik,
- CSS w `frontend/src/App.css` do responsywnego i spójnego wyglądu aplikacji.

Frontend korzysta z backendu przez REST API `/api/v1`. W trybie lokalnym adres API jest ustawiany przez zmienną środowiskową `REACT_APP_API_URL`.

### 4.2 Struktura projektu webowego

```text
frontend/
├── public/
├── src/
│   ├── api.js
│   ├── AuthContext.js
│   ├── App.js
│   ├── App.css
│   ├── components/
│   │   ├── Layout.js
│   │   ├── ProtectedRoute.js
│   │   └── StateBlocks.js
│   └── pages/
│       ├── AppointmentsPage.js
│       ├── BookingPage.js
│       ├── ConsultationsPage.js
│       ├── HomePage.js
│       ├── LoginPage.js
│       ├── RegisterPage.js
│       ├── ServicesPage.js
│       ├── StaffPage.js
│       ├── TherapistDetailsPage.js
│       └── TherapistsPage.js
├── package.json
├── package-lock.json
├── .env.example
├── Dockerfile
└── nginx.conf
```

### 4.3 Widoki aplikacji webowej

Aplikacja webowa zawiera następujące widoki:

- **Strona startowa** — opis gabinetu, linki do logowania, rejestracji i katalogu usług.
- **Rejestracja** — formularz rejestracji pacjenta z podstawową walidacją.
- **Logowanie** — formularz logowania, zapis JWT i przekierowanie po zalogowaniu.
- **Lista usług** — pobieranie usług z backendu, nazwa, opis, czas trwania i cena.
- **Lista terapeutów** — prezentacja terapeutów, specjalizacji, opisu, doświadczenia i ocen.
- **Szczegóły terapeuty** — dane terapeuty, opinie, dostępne terminy.
- **Rezerwacja wizyty** — wybór usługi, terapeuty, terminu i potwierdzenie rezerwacji.
- **Moje wizyty** — lista zaplanowanych, zakończonych i anulowanych wizyt; możliwość anulowania zgodnie z regułami backendu.
- **Historia konsultacji i opinie** — podsumowania konsultacji i informacja o opiniach.
- **Panel terapeuty/staff** — lista wizyt terapeuty, zmiana statusu i dodawanie podsumowania konsultacji.
- **Strona 404** — informacja dla nieznanej ścieżki.

### 4.4 Routing i ochrona tras

Routing jest obsługiwany przez `react-router-dom`. Widoki wymagające logowania są zabezpieczone komponentem `ProtectedRoute`.

Przykłady zasad dostępu:

- niezalogowany użytkownik nie ma dostępu do „Moje wizyty” ani „Historia”,
- użytkownik bez roli `THERAPIST` albo `ADMIN` nie ma dostępu do panelu terapeuty/staff,
- po zalogowaniu interfejs dostosowuje menu do roli użytkownika.

### 4.5 Komunikacja z backendem

Wszystkie zapytania do backendu są wykonywane przez plik:

```text
frontend/src/api.js
```

Bazowy adres API jest ustawiany przez:

```env
REACT_APP_API_URL=http://127.0.0.1:8080/api/v1
```

W środowisku Docker frontend może korzystać z adresu względnego albo z konfiguracji NGINX przekazującej żądania `/api/` do backendu. Dzięki temu ten sam frontend może działać lokalnie i w kontenerach po zmianie konfiguracji środowiskowej.

### 4.6 Obsługa JWT

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

Wylogowanie usuwa dane sesji z `localStorage` i przywraca użytkownika do widoku publicznego.

### 4.7 Testy frontendu

Testy aplikacji webowej uruchomiono poleceniem:

```bash
cd frontend
npm test -- --coverage --watchAll=false
```

Wynik:

```text
Test Suites: 1 passed, 1 total
Tests:       13 passed, 13 total
Snapshots:   0 total

Coverage:
Statements: 66.6%
Branches:   52.76%
Functions:  66.21%
Lines:      68.39%
```

Build produkcyjny uruchomiono poleceniem:

```bash
npm run build
```

Wynik:

```text
Compiled successfully.
```

## 5. Opis backendu

Szczegółowa dokumentacja backendu znajduje się w pliku:

```text
docs/backend.md
```

Backend jest aplikacją Flask udostępniającą REST API pod prefiksem:

```text
/api/v1
```

Backend odpowiada za:

- rejestrację i logowanie,
- generowanie i walidację tokenów JWT,
- hashowanie haseł,
- obsługę ról użytkowników,
- katalog usług,
- profile terapeutów,
- grafiki dostępności,
- rezerwacje i anulowanie wizyt,
- konsultacje i podsumowania,
- opinie,
- funkcje staff/admin,
- kolejkę powiadomień email,
- komunikację z bazą PostgreSQL.

### 5.1 Technologie backendu

Backend wykorzystuje:

- Flask,
- Flask-SQLAlchemy,
- Flask-Migrate,
- SQLAlchemy,
- Marshmallow,
- Flask-JWT-Extended,
- PostgreSQL,
- Pytest,
- Gunicorn w środowisku Docker.

### 5.2 Najważniejsze modele danych

Backend zawiera modele danych obejmujące m.in.:

- użytkowników i role,
- profile pacjentów,
- profile terapeutów,
- usługi,
- grafiki dostępności,
- wizyty,
- konsultacje,
- opinie,
- powiadomienia email.

Modele są odwzorowane na tabele relacyjnej bazy danych przez SQLAlchemy.

### 5.3 Najważniejsze endpointy API

#### Autoryzacja i profil

```text
POST /api/v1/auth/register
POST /api/v1/auth/login
POST /api/v1/auth/refresh
POST /api/v1/auth/logout
GET  /api/v1/users/me
```

#### Usługi, terapeuci i opinie

```text
GET  /api/v1/services
GET  /api/v1/services/{service_id}
GET  /api/v1/services/{service_id}/therapists
GET  /api/v1/therapists/{therapist_id}
GET  /api/v1/therapists/{therapist_id}/reviews
```

#### Dostępność i wizyty

```text
GET  /api/v1/availability
POST /api/v1/appointments
GET  /api/v1/appointments/me
POST /api/v1/appointments/{appointment_id}/cancel
```

#### Konsultacje i opinie pacjenta

```text
GET  /api/v1/consultations/me
POST /api/v1/appointments/{appointment_id}/review
```

#### Staff/admin

```text
GET   /api/v1/staff/appointments
PATCH /api/v1/staff/appointments/{appointment_id}/status
PUT   /api/v1/staff/appointments/{appointment_id}/consultation-summary
```

### 5.4 Bezpieczeństwo backendu

- Hasła są hashowane po stronie backendu.
- Autoryzacja odbywa się przez token JWT.
- Role użytkowników obejmują `PATIENT`, `THERAPIST` i `ADMIN`.
- Endpointy staff/admin są chronione rolami.
- Frontend i mobile nie mają bezpośredniego dostępu do bazy danych.
- Sekrety i parametry połączenia powinny być przekazywane przez zmienne środowiskowe, szczególnie w Dockerze i na VPS.

### 5.5 Testy backendu

Testy backendu uruchomiono poleceniem:

```bash
cd backend
pytest --cov=app --cov-report=term-missing --cov-report=html
```

Wynik:

```text
14 passed
TOTAL coverage: 79%
```

Raport HTML po uruchomieniu testów znajduje się w:

```text
backend/htmlcov/index.html
```

## 6. Opis aplikacji mobilnej

Szczegółowa dokumentacja aplikacji mobilnej znajduje się w pliku:

```text
docs/mobile.md
```

### 6.1 Architektura mobile

Aplikacja mobilna została wykonana natywnie dla Androida w Kotlinie z użyciem Jetpack Compose. Komunikacja z backendem odbywa się przez Retrofit i OkHttp. Token JWT jest przechowywany przez `TokenManager`, a `AuthInterceptor` dodaje nagłówek autoryzacji do zapytań wymagających logowania.

### 6.2 Główne biblioteki mobile

Aplikacja mobilna wykorzystuje m.in.:

- Kotlin,
- Jetpack Compose,
- AndroidX Navigation,
- ViewModel,
- Retrofit,
- OkHttp,
- Gson lub konwerter JSON dla Retrofit,
- Material Design / Compose Material.

### 6.3 Główne widoki mobile

Aplikacja mobilna zawiera:

- ekran startowy/logowania,
- formularz logowania,
- listę usług,
- listę terapeutów dla wybranej usługi,
- ekran wyboru terminu,
- ekran moich wizyt,
- obsługę anulowania wizyty,
- historię konsultacji i opinie w ramach widoku wizyt,
- widok staff/terapeuty, jeżeli użytkownik ma odpowiednią rolę.

W aplikacji mobilnej terapeuci są prezentowani po wyborze usługi. Jest to świadomy układ procesu rezerwacji:

```text
usługa -> terapeuta -> termin -> rezerwacja
```

### 6.4 Konfiguracja API mobile

Dla emulatora Android Studio lokalny backend komputera jest dostępny pod adresem:

```kotlin
private const val BASE_URL = "http://10.0.2.2:8080/"
```

Adres `10.0.2.2` wskazuje z emulatora na komputer hosta. Przy wdrożeniu publicznym adres API powinien zostać zmieniony na publiczny adres backendu, np. domenę VPS.

### 6.5 Weryfikacja mobile

Aplikację mobilną zweryfikowano ręcznie na emulatorze Android. Sprawdzono:

- logowanie pacjenta,
- pobieranie listy usług,
- pobieranie terapeutów dla wybranej usługi,
- wybór dostępnego terminu,
- rezerwację wizyty,
- widok moich wizyt,
- anulowanie wizyty,
- historię konsultacji i opinie.

## 7. Opis konfiguracji Docker

Szczegółowa dokumentacja Docker znajduje się w pliku:

```text
docs/docker.md
```

Konfiguracja Docker obejmuje uruchomienie całego systemu w kontenerach:

- `db` — baza PostgreSQL,
- `backend` — aplikacja Flask uruchamiana w środowisku Python/Gunicorn,
- `frontend` — zbudowana aplikacja React serwowana przez NGINX.

Najważniejsze pliki:

```text
docker-compose.yml
.env.example
backend/Dockerfile
backend/docker-entrypoint.sh
frontend/Dockerfile
frontend/nginx.conf
```

### 7.1 Uruchomienie przez Docker Compose

Przykładowe uruchomienie:

```bash
cp .env.example .env
docker compose up --build
```

Na Windows PowerShell:

```powershell
Copy-Item .env.example .env -Force
docker compose up --build
```

Po uruchomieniu kontenerów aplikacja webowa jest dostępna w przeglądarce, a API backendu jest dostępne przez wystawiony port backendu albo przez proxy NGINX, zależnie od konfiguracji `docker-compose.yml`.

Przykładowe adresy w środowisku Docker:

```text
Frontend: http://localhost:3000
Backend healthcheck: http://localhost:8080/api/v1/health
API przez frontend/NGINX: http://localhost:3000/api/v1/health
```

### 7.2 Rola NGINX

NGINX pełni dwie funkcje:

1. Serwuje statyczne pliki aplikacji React po wykonaniu builda.
2. Przekazuje zapytania `/api/` do kontenera backendu.

Dzięki temu użytkownik korzysta z jednej aplikacji webowej, a komunikacja z backendem odbywa się przez wspólny prefiks `/api/v1`.

### 7.3 Zmienne środowiskowe

Konfiguracja powinna być przekazywana przez `.env`. Typowe zmienne:

- parametry bazy PostgreSQL,
- adres bazy dla backendu,
- sekret JWT,
- tryb pracy aplikacji,
- konfiguracja CORS,
- konfiguracja email,
- adres API dla frontendu.

Sekrety produkcyjne nie powinny być commitowane do repozytorium.

### 7.4 Zatrzymywanie środowiska

Zatrzymanie kontenerów:

```bash
docker compose down
```

Zatrzymanie wraz z usunięciem wolumenów bazy danych:

```bash
docker compose down -v
```

Usunięcie wolumenów usuwa dane z lokalnej bazy PostgreSQL, dlatego należy używać tej komendy ostrożnie.

## 8. Wyniki działania aplikacji i screeny

Screeny znajdują się w katalogu:

```text
docs/screenshots
```

### 8.1 Screeny aplikacji webowej

| Plik | Opis |
|---|---|
| `docs/screenshots/web/web-01-home.png` | Strona startowa aplikacji webowej |
| `docs/screenshots/web/web-02-login.png` | Logowanie w aplikacji webowej |
| `docs/screenshots/web/web-03-services.png` | Lista usług gabinetu |
| `docs/screenshots/web/web-04-therapists.png` | Lista terapeutów |
| `docs/screenshots/web/web-05-booking.png` | Rezerwacja wizyty i dostępne terminy |
| `docs/screenshots/web/web-06-my-appointments.png` | Moje wizyty pacjenta |
| `docs/screenshots/web/web-07-cancelled-or-history.png` | Historia konsultacji, opinie albo anulowana wizyta |
| `docs/screenshots/web/web-08-staff-panel.png` | Panel terapeuty/staff |

### 8.2 Screeny aplikacji mobilnej

| Plik | Opis |
|---|---|
| `docs/screenshots/mobile/mobile-01-home.png` | Ekran startowy/logowania aplikacji mobilnej |
| `docs/screenshots/mobile/mobile-02-login.png` | Formularz logowania z danymi pacjenta |
| `docs/screenshots/mobile/mobile-03-services.png` | Lista usług w aplikacji mobilnej |
| `docs/screenshots/mobile/mobile-04-my-appointments.png` | Moje wizyty pacjenta |
| `docs/screenshots/mobile/mobile-05-therapists.png` | Terapeuci dostępni dla wybranej usługi |
| `docs/screenshots/mobile/mobile-06-booking.png` | Wybór dostępnego terminu |
| `docs/screenshots/mobile/mobile-07-cancelled-by-patient.png` | Wizyta anulowana przez pacjenta |

### 8.3 Dodatkowe screeny techniczne

W dokumentacji technicznej można również umieścić:

- terminal lub Docker Desktop z uruchomionymi kontenerami,
- odpowiedź `/api/v1/health`,
- wynik testów backendu,
- wynik testów frontendu,
- potwierdzenie builda frontendu.

## 9. Wyniki testów

### 9.1 Backend

```text
14 passed
TOTAL coverage: 79%
```

Polecenie:

```bash
cd backend
pytest --cov=app --cov-report=term-missing --cov-report=html
```

Raport HTML:

```text
backend/htmlcov/index.html
```

### 9.2 Frontend

Polecenie:

```bash
cd frontend
npm test -- --coverage --watchAll=false
```

Wynik:

```text
Test Suites: 1 passed, 1 total
Tests:       13 passed, 13 total
Snapshots:   0 total

Coverage:
Statements: 66.6%
Branches:   52.76%
Functions:  66.21%
Lines:      68.39%
```

Build produkcyjny:

```bash
npm run build
```

Wynik:

```text
Compiled successfully.
```

## 10. Konta demonstracyjne

- Pacjent: `jan@example.com` / `Password123!`
- Pacjent: `ola@example.com` / `Password123!`
- Terapeuta: `anna@example.com` / `Password123!`
- Terapeuta: `piotr@example.com` / `Password123!`
- Administrator: `admin@example.com` / `Admin123!`

## 11. Instrukcja uruchomienia lokalnego

### 11.1 Backend lokalnie

Linux/macOS:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

Windows PowerShell:

```powershell
cd backend
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run.py
```

Podczas lokalnej weryfikacji backend działał pod adresem:

```text
http://127.0.0.1:8080/api/v1
```

Healthcheck:

```text
http://127.0.0.1:8080/api/v1/health
```

### 11.2 Frontend lokalnie

Linux/macOS:

```bash
cd frontend
npm install
cp .env.example .env
npm start
```

Windows PowerShell:

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

Przykładowa konfiguracja `frontend/.env`:

```env
REACT_APP_API_URL=http://127.0.0.1:8080/api/v1
```

### 11.3 Mobile lokalnie

1. Uruchomić backend.
2. Sprawdzić `http://127.0.0.1:8080/api/v1/health`.
3. Otworzyć projekt w Android Studio.
4. Uruchomić emulator Android.
5. Uruchomić aplikację.
6. Zalogować się kontem demonstracyjnym.

Dla emulatora Android Studio aplikacja mobilna używa adresu:

```text
http://10.0.2.2:8080/
```

## 12. Instrukcja uruchomienia przez Docker

1. Skopiować plik konfiguracyjny:

```bash
cp .env.example .env
```

Na Windows PowerShell:

```powershell
Copy-Item .env.example .env -Force
```

2. Uruchomić kontenery:

```bash
docker compose up --build
```

3. Sprawdzić działanie:

```text
Frontend: http://localhost:3000
Backend healthcheck: http://localhost:8080/api/v1/health
```

4. Zatrzymać kontenery:

```bash
docker compose down
```

5. W razie potrzeby usunąć również lokalne dane bazy:

```bash
docker compose down -v
```

## 13. Podsumowanie

Projekt został doprowadzony do postaci kompletnej aplikacji webowo-mobilnej z backendem i bazą danych. Frontend nie jest już prostym widokiem testowym, tylko pełną aplikacją obsługującą logowanie, rejestrację, katalog usług, terapeutów, szczegóły terapeuty, dostępność terminów, rezerwację, anulowanie wizyt, historię konsultacji, opinie oraz panel terapeuty/staff.

Backend udostępnia kompletne API `/api/v1`, obsługuje JWT, role, rezerwacje, konsultacje, opinie, powiadomienia email w trybie demonstracyjnym oraz testy backendu. Aplikacja mobilna korzysta z tego samego API, obsługuje główne przepływy pacjenta i została zweryfikowana na emulatorze Android.

Projekt posiada konfigurację Docker umożliwiającą uruchomienie bazy, backendu i frontendu w kontenerach. Testy backendu i frontendu przechodzą, a build produkcyjny frontendu kończy się powodzeniem.

## 14. Możliwość wdrożenia na VPS

Projekt może zostać wdrożony na VPS po skonfigurowaniu środowiska produkcyjnego. Zalecana architektura wdrożenia:

- Docker Compose do uruchomienia kontenerów,
- NGINX jako reverse proxy i serwer statyczny frontendu,
- backend Flask uruchamiany przez Gunicorn,
- PostgreSQL jako osobny kontener lub usługa zarządzana,
- HTTPS przez certyfikaty Let's Encrypt,
- produkcyjne zmienne środowiskowe,
- bezpieczny sekret JWT,
- ograniczone `CORS_ORIGINS`,
- prawdziwy SMTP do wysyłki maili,
- regularne backupy bazy danych,
- monitoring logów i stanu kontenerów.

Po wdrożeniu publicznym aplikacja webowa może być serwowana z domeny, a aplikacja mobilna powinna wskazywać na publiczny adres API zamiast adresu emulatora `10.0.2.2`.

# Dokumentacja projektu UAIM — gabinet psychologiczno-terapeutyczny

## 1. Opis ogólnej koncepcji rozwiązania

Projekt jest aplikacją do obsługi gabinetu psychologiczno-terapeutycznego. System umożliwia pacjentom przeglądanie usług i terapeutów, wyszukiwanie dostępnych terminów, rezerwację wizyt, anulowanie wizyt oraz przegląd historii konsultacji. Terapeuta lub administrator może obsługiwać wizyty, zmieniać ich status i dodawać podsumowania konsultacji. Administrator może zarządzać usługami, profilami terapeutów i grafikami dostępności.

## 2. Ogólna architektura systemu

System składa się z czterech głównych części:

1. **Aplikacja webowa React** — interfejs użytkownika działający w przeglądarce.
2. **Aplikacja mobilna Android/Kotlin** — natywny klient mobilny korzystający z tego samego API.
3. **Backend Flask** — REST API `/api/v1`, logika biznesowa, JWT, role, integracja z bazą.
4. **Baza PostgreSQL** — relacyjna baza danych uruchamiana w Dockerze.

W środowisku Docker frontend jest serwowany przez NGINX, backend działa w kontenerze Python/Gunicorn, a baza danych działa w kontenerze PostgreSQL. NGINX przekazuje zapytania `/api/` do backendu.

## 3. Lista wymaganych i zrealizowanych funkcji

| Funkcja | Status | Sposób realizacji |
|---|---|---|
| Zakładanie konta użytkownika | zrealizowane | `POST /api/v1/auth/register`, rola pacjenta. |
| Uwierzytelnienie/logowanie | zrealizowane | `POST /api/v1/auth/login`, tokeny JWT. |
| Przeglądanie katalogu usług | zrealizowane | `GET /api/v1/services`. |
| Przegląd terapeutów | zrealizowane | `GET /api/v1/services/<id>/therapists`, `GET /api/v1/therapists/<id>`. |
| Oceny terapeutów | zrealizowane częściowo | Opinie przez `/api/v1/therapists/<id>/reviews` i `/api/v1/appointments/<id>/review`. |
| Umawianie terminu wizyty | zrealizowane | Wyliczanie dostępności i `POST /api/v1/appointments`. |
| Zwalnianie terminu/rezygnacja | zrealizowane | `POST /api/v1/appointments/<id>/cancel`. |
| Przegląd zrealizowanych wizyt | zrealizowane | `/api/v1/consultations/me`. |
| Przebieg/podsumowanie konsultacji | zrealizowane | Staff dodaje opis przez `/api/v1/staff/appointments/<id>/consultation-summary`. |
| Powiadomienie email o umówieniu/anulowaniu wizyty | zrealizowane demonstracyjnie | Kolejka `EmailNotification`, tryb `console`; opcjonalnie SMTP przez `MAIL_BACKEND=smtp`. |
| Testy backendu | zrealizowane | 14 testów, pokrycie 79%. |
| Docker | zrealizowane | `docker-compose.yml`, kontenery db/backend/frontend. |

## 4. Opis aplikacji webowej

Aktualna aplikacja webowa React zawiera poprawiony healthcheck korzystający z aktywnego API `/api/v1/health`. Konfiguracja adresu backendu odbywa się przez `REACT_APP_API_URL`.

Pliki frontendu:

- `frontend/src/App.js` — ekran statusu połączenia z backendem,
- `frontend/src/App.css` — podstawowe style,
- `frontend/src/App.test.js` — test renderowania i odczytu statusu backendu,
- `frontend/.env.example` — przykładowa konfiguracja API,
- `frontend/Dockerfile` — build React i serwowanie przez NGINX,
- `frontend/nginx.conf` — konfiguracja SPA oraz proxy `/api/`.

Do pełnego oddania projektu aplikację webową należy jeszcze rozbudować o właściwe widoki: rejestrację, logowanie, listę usług, terapeutów, wybór terminów, rezerwacje i panel użytkownika. Backend jest już przygotowany pod te funkcje.

## 5. Opis aplikacji backend

Szczegółowy opis znajduje się w `docs/backend.md`.

Najważniejsze elementy:

- Flask + SQLAlchemy + Marshmallow,
- REST API `/api/v1`,
- JWT access/refresh,
- role `PATIENT`, `THERAPIST`, `ADMIN`,
- modele danych dla użytkowników, terapeutów, usług, grafików, wizyt, konsultacji, opinii i powiadomień,
- seed danych demonstracyjnych,
- testy integracyjne API.

## 6. Opis aplikacji mobilnej

Aplikacja mobilna znajduje się w katalogu `mobile`. Jest projektem Android/Kotlin. Powinna korzystać z tego samego API backendu co frontend webowy. Przy uruchamianiu na emulatorze Androida lokalny backend komputera powinien być adresowany jako `10.0.2.2`, a nie `localhost`.

Do dokumentacji końcowej należy uzupełnić szczegółowy opis klas i widoków mobilnych oraz listę bibliotek po wykonaniu pełnej weryfikacji aplikacji w Android Studio.

## 7. Opis pliku konfiguracyjnego Docker

Szczegółowy opis znajduje się w `docs/docker.md`.

Najważniejsze pliki:

- `docker-compose.yml`,
- `backend/Dockerfile`,
- `backend/docker-entrypoint.sh`,
- `frontend/Dockerfile`,
- `frontend/nginx.conf`,
- `.env.example`.

Uruchomienie:

```bash
cp .env.example .env
docker compose up --build
```

## 8. Wyniki działania aplikacji

Do finalnego oddania należy dodać zrzuty ekranu do katalogu `docs/screenshots`.

Lista wymaganych screenów:

1. Docker Desktop albo terminal z uruchomionymi kontenerami.
2. `http://localhost:5000/api/v1/health` z odpowiedzią `ok`.
3. Strona frontendu `http://localhost:3000` pokazująca status backendu.
4. Rejestracja użytkownika.
5. Logowanie użytkownika.
6. Lista usług.
7. Lista terapeutów.
8. Dostępne terminy terapeuty.
9. Rezerwacja wizyty.
10. Lista moich wizyt.
11. Anulowanie wizyty.
12. Historia konsultacji.
13. Widok terapeuty/staff z listą wizyt.
14. Dodanie podsumowania konsultacji.
15. Widoki aplikacji mobilnej odpowiadające głównym funkcjom.

## 9. Wyniki testów

Backend:

```text
14 passed
TOTAL coverage: 79%
```

Raport HTML znajduje się w `backend/htmlcov/index.html` po uruchomieniu:

```bash
cd backend
pytest --cov=app --cov-report=term-missing --cov-report=html
```

Frontend:

```bash
cd frontend
npm test -- --coverage --watchAll=false
npm run build
```

Podczas weryfikacji test frontendu przeszedł, a build produkcyjny zakończył się sukcesem.

## 10. Podsumowanie i możliwość wdrożenia na VPS

Projekt jest przygotowany do uruchomienia w środowisku kontenerowym. Dzięki `docker-compose.yml` można przenieść go na VPS, zainstalować Docker Compose, ustawić zmienne środowiskowe i uruchomić system jedną komendą.

Przed wdrożeniem komercyjnym należy:

- zmienić wszystkie sekrety i hasła,
- skonfigurować HTTPS,
- ustawić produkcyjne `CORS_ORIGINS`,
- podłączyć prawdziwy SMTP,
- dodać trwałe backupy bazy PostgreSQL,
- rozbudować aplikację webową o komplet widoków użytkownika.

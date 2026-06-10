# Backend Flask — dokumentacja techniczna

## Architektura

Backend jest aplikacją Flask z REST API pod prefiksem `/api/v1`. Warstwy aplikacji:

| Warstwa | Katalog | Odpowiedzialność |
|---|---|---|
| API | `app/api` | Blueprinty Flask, walidacja requestów, odpowiedzi JSON. |
| Schematy | `app/schemas` | Marshmallow: walidacja danych wejściowych i serializacja. |
| Serwisy | `app/services` | Logika biznesowa: rezerwacje, dostępność, opinie, admin, powiadomienia. |
| Repozytoria | `app/repositories` | Odczyt i zapis danych przez SQLAlchemy. |
| Modele | `app/models` | Modele SQLAlchemy. |
| Utils | `app/utils` | JWT, role, błędy, enumy, paginacja, daty. |
| CLI | `app/cli` | Komendy Flask: seed i wysyłka zaległych powiadomień. |

Aplikacja używa factory `create_app()` w `app/__init__.py`, dzięki czemu testy, uruchomienie lokalne i Docker korzystają z tej samej konfiguracji.

## Konfiguracja

Konfiguracja jest odczytywana ze zmiennych środowiskowych w `app/config.py`.

| Zmienna | Znaczenie |
|---|---|
| `FLASK_ENV` | `development`, `testing` albo `production`. |
| `SECRET_KEY` | Sekret Flask. Wdrożeniowo musi być zmieniony. |
| `JWT_SECRET_KEY` | Sekret podpisu tokenów JWT. Wdrożeniowo musi być zmieniony. |
| `DATABASE_URL` | Adres bazy danych, np. PostgreSQL w Dockerze. |
| `TEST_DATABASE_URL` | Baza używana w testach. Domyślnie SQLite in-memory. |
| `CORS_ORIGINS` | Dozwolone originy frontendu, rozdzielane przecinkami. |
| `APP_TIMEZONE` | Strefa czasowa grafiku, domyślnie `Europe/Warsaw`. |
| `INIT_DB` | Czy przy starcie Dockerem tworzyć tabele i seedować dane. |
| `MAIL_BACKEND` | `console` albo `smtp`. |
| `MAIL_SENDER` | Nadawca wiadomości e-mail. |
| `MAIL_SMTP_HOST` | Host SMTP, wymagany dla `MAIL_BACKEND=smtp`. |
| `MAIL_SMTP_PORT` | Port SMTP. |
| `MAIL_SMTP_USERNAME` | Login SMTP. |
| `MAIL_SMTP_PASSWORD` | Hasło SMTP. Nie wolno commitować prawdziwego hasła. |
| `MAIL_SMTP_USE_TLS` | Czy używać STARTTLS. |

Przykładowe pliki: `.env.example` oraz `backend/.env.example`.

## Modele danych

Najważniejsze modele:

| Model | Znaczenie |
|---|---|
| `User` | Konto użytkownika z hashem hasła, danymi osobowymi i rolami. |
| `Role`, `UserRole` | Role `PATIENT`, `THERAPIST`, `ADMIN`. |
| `TherapistProfile` | Profil terapeuty, opis, doświadczenie, ocena. |
| `Service` | Usługa gabinetu, czas trwania, cena bazowa. |
| `TherapistService` | Przypisanie terapeuty do usługi z opcjonalną ceną/czasem. |
| `AvailabilityRule` | Regularny grafik terapeuty. |
| `AvailabilityException` | Wyjątki w grafiku, np. niedostępność. |
| `Appointment` | Wizyta pacjenta z migawką ceny, terapeuty i usługi. |
| `ConsultationSummary` | Podsumowanie konsultacji dodawane przez terapeutę/staff. |
| `Review` | Opinia pacjenta po zakończonej wizycie. |
| `EmailNotification` | Kolejka powiadomień e-mail. |

## Endpointy API

### Publiczne

| Metoda | Endpoint | Opis |
|---|---|---|
| `GET` | `/api/v1/health` | Healthcheck backendu. |
| `POST` | `/api/v1/auth/register` | Rejestracja pacjenta. |
| `POST` | `/api/v1/auth/login` | Logowanie i zwrot tokenów JWT. |
| `POST` | `/api/v1/auth/refresh` | Odświeżenie access tokenu. |
| `GET` | `/api/v1/services` | Lista aktywnych usług. |
| `GET` | `/api/v1/services/<service_id>` | Szczegóły usługi. |
| `GET` | `/api/v1/services/<service_id>/therapists` | Terapeuci wykonujący usługę. |
| `GET` | `/api/v1/therapists/<therapist_id>` | Publiczne dane terapeuty. |
| `GET` | `/api/v1/availability` | Wyliczenie dostępnych terminów. |
| `GET` | `/api/v1/therapists/<therapist_id>/reviews` | Opinie terapeuty. |

### Pacjent zalogowany

| Metoda | Endpoint | Opis |
|---|---|---|
| `GET` | `/api/v1/users/me` | Dane aktualnego użytkownika. |
| `POST` | `/api/v1/auth/logout` | Wylogowanie logiczne. |
| `POST` | `/api/v1/appointments` | Rezerwacja wizyty. |
| `GET` | `/api/v1/appointments/me` | Lista wizyt pacjenta. |
| `GET` | `/api/v1/appointments/<appointment_id>` | Szczegóły wizyty pacjenta. |
| `POST` | `/api/v1/appointments/<appointment_id>/cancel` | Anulowanie wizyty. |
| `GET` | `/api/v1/consultations/me` | Historia konsultacji pacjenta. |
| `POST` | `/api/v1/appointments/<appointment_id>/review` | Dodanie opinii po zakończonej wizycie. |

### Staff/admin

| Metoda | Endpoint | Rola | Opis |
|---|---|---|---|
| `GET` | `/api/v1/staff/appointments` | `ADMIN`, `THERAPIST` | Lista wizyt dla staffu. |
| `PATCH` | `/api/v1/staff/appointments/<appointment_id>/status` | `ADMIN`, `THERAPIST` | Zmiana statusu wizyty. |
| `PUT` | `/api/v1/staff/appointments/<appointment_id>/consultation-summary` | `ADMIN`, `THERAPIST` | Dodanie/aktualizacja opisu konsultacji. |
| `GET` | `/api/v1/admin/services` | `ADMIN` | Lista usług dla admina. |
| `POST` | `/api/v1/admin/services` | `ADMIN` | Utworzenie usługi. |
| `PATCH` | `/api/v1/admin/services/<service_id>` | `ADMIN` | Aktualizacja usługi. |
| `GET` | `/api/v1/admin/therapists` | `ADMIN` | Lista terapeutów. |
| `POST` | `/api/v1/admin/therapists` | `ADMIN` | Utworzenie profilu terapeuty. |
| `PATCH` | `/api/v1/admin/therapists/<therapist_id>` | `ADMIN` | Aktualizacja profilu terapeuty. |
| `POST` | `/api/v1/admin/therapists/<therapist_id>/services` | `ADMIN` | Przypisanie usługi do terapeuty. |
| `DELETE` | `/api/v1/admin/therapists/<therapist_id>/services/<service_id>` | `ADMIN` | Usunięcie przypisania usługi. |
| `GET` | `/api/v1/admin/therapists/<therapist_id>/availability-rules` | `ADMIN` | Lista reguł grafiku. |
| `POST` | `/api/v1/admin/therapists/<therapist_id>/availability-rules` | `ADMIN` | Dodanie reguły grafiku. |
| `PATCH` | `/api/v1/admin/availability-rules/<rule_id>` | `ADMIN` | Aktualizacja reguły grafiku. |
| `DELETE` | `/api/v1/admin/availability-rules/<rule_id>` | `ADMIN` | Usunięcie reguły grafiku. |
| `GET` | `/api/v1/admin/therapists/<therapist_id>/availability-exceptions` | `ADMIN` | Lista wyjątków grafiku. |
| `POST` | `/api/v1/admin/therapists/<therapist_id>/availability-exceptions` | `ADMIN` | Dodanie wyjątku grafiku. |

## Zabezpieczenia

- Hasła są przechowywane jako hash generowany przez Werkzeug (`generate_password_hash`, `check_password_hash`).
- Uwierzytelnienie działa przez JWT (`Flask-JWT-Extended`).
- Endpointy chronione używają `@jwt_required()`.
- Endpointy administracyjne i staffowe dodatkowo używają dekoratora `roles_required(...)`.
- Sekrety nie są wpisane jako wartości produkcyjne w kodzie. Wdrożeniowo trzeba je przekazać przez `.env`.
- CORS jest ograniczany przez `CORS_ORIGINS`.

## Powiadomienia e-mail

`NotificationService` zapisuje wiadomości do tabeli `email_notifications`.

Obsługiwane zdarzenia:

- potwierdzenie rezerwacji,
- przypomnienie 24h przed wizytą,
- anulowanie wizyty.

Tryby:

- `MAIL_BACKEND=console` — demonstracyjnie wypisuje wiadomości w logach,
- `MAIL_BACKEND=smtp` — wysyła przez SMTP skonfigurowane zmiennymi `MAIL_SMTP_*`.

Wysyłka zaległych powiadomień:

```bash
flask --app app reminders send-due
```

## Testy backendu

Komenda:

```bash
cd backend
pytest --cov=app --cov-report=term-missing --cov-report=html
```

Weryfikacja wykonana podczas prac:

- liczba testów: 14,
- wynik: 14 passed,
- pokrycie: 79%,
- raport HTML: `backend/htmlcov/index.html`.

Podczas testów pojawiają się ostrzeżenia SQLAlchemy `Query.get()` jako legacy API. Nie blokują one działania testów, ale warto je poprawić w kolejnym etapie.

## Uruchomienie lokalne bez Dockera

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python run.py
```

Backend będzie dostępny pod:

```text
http://localhost:8080/api/v1/health
```

## Uruchomienie z Dockerem

Szczegóły są w `docs/docker.md`.

```bash
cp .env.example .env
docker compose up --build
```

# UAIM — gabinet psychologiczno-terapeutyczny

Projekt składa się z backendu Flask, frontendu React, natywnej aplikacji mobilnej Android/Kotlin oraz bazy PostgreSQL uruchamianej w Dockerze.

## Szybkie uruchomienie przez Docker

```bash
cp .env.example .env
# opcjonalnie edytuj .env i zmień SECRET_KEY/JWT_SECRET_KEY

docker compose up --build
```

Po uruchomieniu:

| Usługa | Adres |
|---|---|
| Frontend React przez NGINX | http://localhost:3000 |
| Backend Flask API | http://localhost:5000/api/v1 |
| Healthcheck backendu | http://localhost:5000/api/v1/health |
| PostgreSQL | localhost:5432 |
| pgAdmin, opcjonalnie | `docker compose --profile tools up pgadmin` i http://localhost:5050 |

Zatrzymanie systemu:

```bash
docker compose down
```

Usunięcie danych PostgreSQL z wolumenu:

```bash
docker compose down -v
```

## Konta demonstracyjne

| Rola | Email | Hasło |
|---|---|---|
| Admin | `admin@example.com` | `Admin123!` |
| Terapeuta | `anna@example.com` | `Password123!` |
| Terapeuta | `piotr@example.com` | `Password123!` |
| Pacjent | `jan@example.com` | `Password123!` |
| Pacjent | `ola@example.com` | `Password123!` |

## Testy

Backend:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pytest --cov=app --cov-report=term-missing --cov-report=html
```

W wykonanej weryfikacji backendu: **14 testów przeszło, pokrycie 79%**.

Frontend:

```bash
cd frontend
npm install
npm test -- --coverage --watchAll=false
npm run build
```

## Dokumentacja

Najważniejsze pliki:

- `docs/backend.md` — backend, modele, endpointy, bezpieczeństwo, testy.
- `docs/docker.md` — uruchomienie przez Docker i opis kontenerów.
- `docs/dokumentacja_projektu.md` — szkic dokumentacji końcowej projektu.
- `docs/README.md` — wcześniejsza szczegółowa dokumentacja backendowa.

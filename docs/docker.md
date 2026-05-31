# Docker — opis konfiguracji

## Cel

Konfiguracja Docker uruchamia kompletny system demonstracyjny bez ręcznego startowania backendu i bazy danych. Aplikacja mobilna nie jest konteneryzowana, bo zgodnie z założeniem projektu działa jako natywna aplikacja Android.

## Pliki

| Plik | Znaczenie |
|---|---|
| `docker-compose.yml` | Definicja usług: PostgreSQL, backend Flask, frontend React/NGINX, opcjonalny pgAdmin. |
| `backend/Dockerfile` | Buduje obraz backendu na Pythonie 3.12. |
| `backend/docker-entrypoint.sh` | Tworzy tabele, seeduje dane demonstracyjne i uruchamia Gunicorn. |
| `backend/.dockerignore` | Pomija pliki lokalne i tymczasowe w obrazie backendu. |
| `frontend/Dockerfile` | Buduje aplikację React i serwuje ją przez NGINX. |
| `frontend/nginx.conf` | Serwuje SPA oraz przekazuje `/api/` do backendu. |
| `.env.example` | Przykładowe zmienne środowiskowe dla uruchomienia Dockerem. |

## Usługi w `docker-compose.yml`

### `db`

- obraz: `postgres:16-alpine`,
- baza: `uaim`,
- użytkownik: `uaim`,
- port hosta: `5432`,
- dane trzymane w wolumenie `postgres_data`,
- healthcheck: `pg_isready`.

### `backend`

- budowany z `backend/Dockerfile`,
- port hosta: `5000`,
- korzysta z `DATABASE_URL=postgresql://uaim:uaim_password@db:5432/uaim`,
- po starcie wykonuje `db.create_all()` i `seed_database()`, jeśli `INIT_DB=true`,
- uruchamia aplikację przez Gunicorn,
- healthcheck sprawdza `/api/v1/health`.

### `frontend`

- budowany z `frontend/Dockerfile`,
- port hosta: `3000`,
- React jest budowany statycznie i serwowany przez NGINX,
- NGINX przekazuje zapytania `/api/` do `backend:5000`.

### `pgadmin`

- opcjonalny profil `tools`,
- start:

```bash
docker compose --profile tools up pgadmin
```

- adres: `http://localhost:5050`,
- login demo: `admin@example.com`, hasło: `admin`.

## Uruchomienie

```bash
cp .env.example .env
docker compose up --build
```

Adresy po starcie:

- frontend: `http://localhost:3000`,
- backend: `http://localhost:5000/api/v1`,
- healthcheck: `http://localhost:5000/api/v1/health`.

## Zatrzymanie

```bash
docker compose down
```

Pełne czyszczenie bazy demonstracyjnej:

```bash
docker compose down -v
```

## Uwagi wdrożeniowe

Przed wdrożeniem na VPS należy:

1. skopiować `.env.example` do `.env`,
2. zmienić `SECRET_KEY` i `JWT_SECRET_KEY`,
3. zmienić hasło PostgreSQL,
4. ustawić właściwe `CORS_ORIGINS`,
5. skonfigurować SMTP albo pozostawić `MAIL_BACKEND=console` tylko w środowisku demonstracyjnym,
6. wystawić frontend przez HTTPS, np. reverse proxy NGINX/Caddy/Traefik.

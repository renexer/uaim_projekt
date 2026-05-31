# UAIM — gabinet psychologiczno-terapeutyczny

Projekt składa się z:

* backendu Flask,
* frontendu React uruchamianego przez NGINX,
* natywnej aplikacji mobilnej Android/Kotlin,
* bazy danych PostgreSQL,
* konfiguracji Docker Compose uruchamiającej backend, frontend i bazę danych.

Aplikacja realizuje system obsługi gabinetu psychologiczno-terapeutycznego: logowanie, katalog usług, terapeutów, dostępne terminy, rezerwacje wizyt, anulowanie wizyt oraz obsługę ról użytkowników.

---

## Szybkie uruchomienie przez Docker

Wymagania:

* uruchomiony Docker Desktop,
* dostępny terminal PowerShell lub Bash,
* sklonowane repozytorium.

### Windows PowerShell

W katalogu głównym projektu:

```powershell
Copy-Item .env.example .env
docker compose up --build -d
docker compose ps
```

### Linux / macOS / Git Bash

```bash
cp .env.example .env
docker compose up --build -d
docker compose ps
```

Po uruchomieniu powinny działać trzy kontenery:

| Usługa          | Oczekiwany status |
| --------------- | ----------------- |
| `uaim_db`       | `healthy`         |
| `uaim_backend`  | `healthy`         |
| `uaim_frontend` | `Up`              |

---

## Adresy usług

| Usługa                                    | Adres                               |
| ----------------------------------------- | ----------------------------------- |
| Frontend React przez NGINX                | http://localhost:3000               |
| Backend Flask API                         | http://localhost:8080/api/v1        |
| Healthcheck backendu bezpośrednio         | http://localhost:8080/api/v1/health |
| Healthcheck backendu przez frontend/NGINX | http://localhost:3000/api/v1/health |
| PostgreSQL                                | localhost:5432                      |

Uwaga: backend **wewnątrz sieci Dockera** działa na porcie `5000`, ale z komputera użytkownika jest dostępny przez port `8080`.

---

## Sprawdzenie działania

### Windows PowerShell

```powershell
Invoke-RestMethod http://localhost:8080/api/v1/health
Invoke-RestMethod http://localhost:3000/api/v1/health
```

Oczekiwany wynik:

```text
status=ok
```

### Linux / macOS / Git Bash

```bash
curl http://localhost:8080/api/v1/health
curl http://localhost:3000/api/v1/health
```

Następnie otwórz aplikację w przeglądarce:

```text
http://localhost:3000
```

---

## Zatrzymanie systemu

Zatrzymanie kontenerów bez usuwania danych bazy:

```bash
docker compose down
```

Zatrzymanie kontenerów razem z usunięciem wolumenu PostgreSQL, czyli danych demonstracyjnych:

```bash
docker compose down -v --remove-orphans
```

Po użyciu `docker compose down -v` baza zostanie utworzona od nowa przy kolejnym uruchomieniu.

---

## Ponowne uruchomienie po świeżym klonie repozytorium

```bash
cp .env.example .env
docker compose up --build -d
docker compose ps
```

Na Windows PowerShell:

```powershell
Copy-Item .env.example .env
docker compose up --build -d
docker compose ps
```

Nie należy commitować pliku `.env`. Do repozytorium powinien trafić tylko `.env.example`.

---

## Konta demonstracyjne

| Rola      | Email               | Hasło          |
| --------- | ------------------- | -------------- |
| Admin     | `admin@example.com` | `Admin123!`    |
| Terapeuta | `anna@example.com`  | `Password123!` |
| Terapeuta | `piotr@example.com` | `Password123!` |
| Pacjent   | `jan@example.com`   | `Password123!` |
| Pacjent   | `ola@example.com`   | `Password123!` |

---

## Typowa ścieżka testowa aplikacji

Po uruchomieniu Dockera można sprawdzić aplikację ręcznie:

1. Otwórz `http://localhost:3000`.
2. Zaloguj się jako pacjent, np. `jan@example.com` / `Password123!`.
3. Przejdź do katalogu usług.
4. Wybierz terapeutę i dostępny termin.
5. Zarezerwuj wizytę.
6. Przejdź do widoku swoich wizyt.
7. Sprawdź możliwość anulowania wizyty.

---

## Testy backendu lokalnie

Zalecany Python: `3.12`.

### Windows PowerShell

```powershell
cd backend
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest --cov=app --cov-report=term-missing --cov-report=html
```

### Linux / macOS / Git Bash

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pytest --cov=app --cov-report=term-missing --cov-report=html
```

W wykonanej weryfikacji backendu: **14 testów przeszło, pokrycie kodu wyniosło 79%**.

---

## Testy frontendu lokalnie

```bash
cd frontend
npm install
npm test -- --coverage --watchAll=false
npm run build
```

---

## Najczęstsze problemy

### Docker nie działa

Jeżeli pojawia się komunikat o braku połączenia z Docker API, uruchom Docker Desktop i poczekaj, aż silnik Docker będzie gotowy.

### Brak pliku `.env`

Jeżeli pojawia się błąd:

```text
env file .env not found
```

utwórz plik `.env` z przykładu:

```powershell
Copy-Item .env.example .env
```

albo:

```bash
cp .env.example .env
```

### Backend nie startuje przez `docker-entrypoint.sh`

Jeżeli w logach backendu pojawia się:

```text
exec ./docker-entrypoint.sh: no such file or directory
```

oznacza to zwykle problem z końcami linii CRLF/LF. W projekcie zabezpiecza to `.gitattributes` oraz Dockerfile, dlatego po świeżym klonie należy przebudować obraz:

```bash
docker compose build --no-cache backend
docker compose up -d
```

### Sprawdzenie logów

```bash
docker compose logs --no-color backend --tail=100
docker compose logs --no-color db --tail=100
docker compose logs --no-color frontend --tail=100
```

---

## Dokumentacja

Najważniejsze pliki:

* `docs/dokumentacja_projektu.md` — główna dokumentacja końcowa projektu,
* `docs/backend.md` — opis backendu, modeli, endpointów, zabezpieczeń i testów,
* `docs/frontend.md` — opis aplikacji webowej,
* `docs/mobile.md` — opis aplikacji mobilnej Android,
* `docs/docker.md` — opis uruchomienia i konfiguracji Docker,
* `docs/README.md` — dodatkowa / wcześniejsza dokumentacja techniczna backendu.

---

## Przydatne komendy

Status kontenerów:

```bash
docker compose ps
```

Pełne przebudowanie i uruchomienie:

```bash
docker compose down -v --remove-orphans
docker compose up --build -d
```

Logi backendu:

```bash
docker compose logs --no-color backend --tail=100
```

Zatrzymanie aplikacji:

```bash
docker compose down
```

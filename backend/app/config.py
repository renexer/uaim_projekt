import os
from datetime import timedelta


# Bazowa konfiguracja aplikacji Flask, wspólna dla wszystkich środowisk uruchomieniowych.
class BaseConfig:
    """Wspólna konfiguracja aplikacji odczytywana ze zmiennych środowiskowych.

    W repozytorium zostają tylko bezpieczne wartości demonstracyjne. Wdrożenie
    lokalne, Docker i VPS powinny przekazywać sekrety przez `.env` albo panel
    zmiennych środowiskowych, a nie przez kod źródłowy.
    """

    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "dev-secret-change-me-32-characters-minimum",
    )
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv(
        "JWT_SECRET_KEY",
        "dev-jwt-secret-change-me-32-characters-minimum",
    )
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=int(os.getenv("JWT_ACCESS_MINUTES", "30")))
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=int(os.getenv("JWT_REFRESH_DAYS", "7")))
    CORS_ORIGINS = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:3000,http://127.0.0.1:3000",
        ).split(",")
        if origin.strip()
    ]
    APP_TIMEZONE = os.getenv("APP_TIMEZONE", "Europe/Warsaw")

    # Konfiguracja powiadomień: `console` zapisuje wiadomości w logach, a `smtp`
    # wysyła je przez serwer skonfigurowany zmiennymi MAIL_SMTP_*.
    MAIL_BACKEND = os.getenv("MAIL_BACKEND", "console")
    MAIL_SENDER = os.getenv("MAIL_SENDER", "noreply@example.com")
    MAIL_SMTP_HOST = os.getenv("MAIL_SMTP_HOST", "")
    MAIL_SMTP_PORT = int(os.getenv("MAIL_SMTP_PORT", "587"))
    MAIL_SMTP_USERNAME = os.getenv("MAIL_SMTP_USERNAME", "")
    MAIL_SMTP_PASSWORD = os.getenv("MAIL_SMTP_PASSWORD", "")
    MAIL_SMTP_USE_TLS = os.getenv("MAIL_SMTP_USE_TLS", "true").lower() in {"1", "true", "yes"}

    JSON_SORT_KEYS = False


# Konfiguracja środowiska developerskiego z włączonym trybem debugowania.
class DevelopmentConfig(BaseConfig):
    DEBUG = True


# Konfiguracja środowiska testowego używana przez testy automatyczne.
class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv("TEST_DATABASE_URL", "sqlite:///:memory:")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=5)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(minutes=30)


# Konfiguracja środowiska produkcyjnego z wyłączonym debugowaniem.
class ProductionConfig(BaseConfig):
    DEBUG = False

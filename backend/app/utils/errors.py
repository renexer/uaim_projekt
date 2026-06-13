from __future__ import annotations


# Bazowy wyjątek aplikacyjny przenoszący kod błędu, status HTTP i dodatkowe szczegóły.
class AppError(Exception):
    status_code = 400
    code = "APP_ERROR"

    # Konstruktor inicjalizuje zależności potrzebne do działania klasy.
    def __init__(self, message: str, code: str | None = None, status_code: int | None = None, details=None):
        super().__init__(message)
        self.message = message
        self.details = details
        if code:
            self.code = code
        if status_code:
            self.status_code = status_code


# Wyjątek zgłaszany przy błędnych danych wejściowych.
class ValidationError(AppError):
    status_code = 400
    code = "VALIDATION_ERROR"


# Wyjątek zgłaszany, gdy użytkownik nie jest uwierzytelniony.
class UnauthorizedError(AppError):
    status_code = 401
    code = "UNAUTHORIZED"


# Wyjątek zgłaszany, gdy użytkownik nie ma uprawnień do operacji.
class ForbiddenError(AppError):
    status_code = 403
    code = "FORBIDDEN"


# Wyjątek zgłaszany, gdy wymagany zasób nie istnieje.
class NotFoundError(AppError):
    status_code = 404
    code = "NOT_FOUND"


# Wyjątek zgłaszany, gdy operacja powoduje konflikt stanu danych.
class ConflictError(AppError):
    status_code = 409
    code = "CONFLICT"

from marshmallow import ValidationError as MarshmallowValidationError

from app.utils.errors import ValidationError


# Funkcja pomocnicza waliduje dane wejściowe Marshmallow i zamienia błędy na jednolity AppError.
def load_or_400(schema, payload):
    try:
        return schema.load(payload)
    except MarshmallowValidationError as exc:
        raise ValidationError("Nieprawidłowe dane wejściowe.", details=exc.messages)


# Funkcja pomocnicza buduje spójny format poprawnej odpowiedzi API.
def success(data, meta=None, status=200):
    body = {"data": data}
    if meta is not None:
        body["meta"] = meta
    return body, status
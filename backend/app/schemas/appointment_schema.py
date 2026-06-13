from marshmallow import Schema, fields


# Schemat Marshmallow walidujący dane potrzebne do rezerwacji wizyty.
class AppointmentCreateSchema(Schema):
    serviceId = fields.String(required=True)
    therapistId = fields.String(required=True)
    startAt = fields.DateTime(required=True)


# Schemat Marshmallow walidujący opcjonalny powód anulowania wizyty.
class AppointmentCancelSchema(Schema):
    reason = fields.String(load_default=None)

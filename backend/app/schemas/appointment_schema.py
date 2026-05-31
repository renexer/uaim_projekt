from marshmallow import Schema, fields


class AppointmentCreateSchema(Schema):
    serviceId = fields.String(required=True)
    therapistId = fields.String(required=True)
    startAt = fields.DateTime(required=True)


class AppointmentCancelSchema(Schema):
    reason = fields.String(load_default=None)
from marshmallow import Schema, fields


class AvailabilityQuerySchema(Schema):
    serviceId = fields.String(required=True)
    therapistId = fields.String(load_default=None)
    from_ = fields.DateTime(required=True, data_key="from")
    to = fields.DateTime(required=True)


class SlotSchema(Schema):
    startAt = fields.DateTime(attribute="start_at")
    endAt = fields.DateTime(attribute="end_at")

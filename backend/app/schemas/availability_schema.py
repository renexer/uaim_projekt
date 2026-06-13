from marshmallow import Schema, fields


# Schemat Marshmallow walidujący parametry zapytania o dostępne terminy.
class AvailabilityQuerySchema(Schema):
    serviceId = fields.String(required=True)
    therapistId = fields.String(load_default=None)
    from_ = fields.DateTime(required=True, data_key="from")
    to = fields.DateTime(required=True)


# Schemat Marshmallow opisujący format pojedynczego dostępnego slotu czasowego.
class SlotSchema(Schema):
    startAt = fields.DateTime(attribute="start_at")
    endAt = fields.DateTime(attribute="end_at")

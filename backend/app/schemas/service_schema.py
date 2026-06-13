from marshmallow import Schema, fields


# Schemat Marshmallow serializujący dane usługi do odpowiedzi API.
class ServiceSchema(Schema):
    id = fields.String(dump_only=True)
    code = fields.String()
    name = fields.String()
    description = fields.String()
    durationMinutes = fields.Integer(attribute="duration_minutes")
    basePrice = fields.Decimal(attribute="base_price", as_string=True)
    currency = fields.String()
    isActive = fields.Boolean(attribute="is_active")

from marshmallow import Schema, fields, validate


class ServiceCreateSchema(Schema):
    code = fields.String(required=True, validate=validate.Length(min=3, max=100))
    name = fields.String(required=True, validate=validate.Length(min=3, max=255))
    description = fields.String(required=True, validate=validate.Length(min=5))
    durationMinutes = fields.Integer(required=True, validate=validate.Range(min=15, max=240))
    basePrice = fields.Decimal(required=True, as_string=True)
    currency = fields.String(load_default="PLN", validate=validate.Length(equal=3))
    isActive = fields.Boolean(load_default=True)


class ServiceUpdateSchema(Schema):
    code = fields.String(validate=validate.Length(min=3, max=100))
    name = fields.String(validate=validate.Length(min=3, max=255))
    description = fields.String(validate=validate.Length(min=5))
    durationMinutes = fields.Integer(validate=validate.Range(min=15, max=240))
    basePrice = fields.Decimal(as_string=True)
    currency = fields.String(validate=validate.Length(equal=3))
    isActive = fields.Boolean()


class TherapistProfileCreateSchema(Schema):
    userId = fields.String(required=True)
    title = fields.String(required=True, validate=validate.Length(min=2, max=120))
    bio = fields.String(required=True, validate=validate.Length(min=5))
    experienceYears = fields.Integer(load_default=None)
    photoUrl = fields.String(load_default=None)
    isActive = fields.Boolean(load_default=True)


class TherapistProfileUpdateSchema(Schema):
    title = fields.String(validate=validate.Length(min=2, max=120))
    bio = fields.String(validate=validate.Length(min=5))
    experienceYears = fields.Integer(load_default=None)
    photoUrl = fields.String(load_default=None)
    isActive = fields.Boolean()


class TherapistServiceAssignSchema(Schema):
    serviceId = fields.String(required=True)
    priceOverride = fields.Decimal(load_default=None, as_string=True)
    durationOverrideMinutes = fields.Integer(load_default=None)
    isActive = fields.Boolean(load_default=True)


class AvailabilityRuleCreateSchema(Schema):
    weekday = fields.Integer(required=True, validate=validate.Range(min=1, max=7))
    startTime = fields.Time(required=True)
    endTime = fields.Time(required=True)
    validFrom = fields.Date(required=True)
    validTo = fields.Date(load_default=None)
    isActive = fields.Boolean(load_default=True)


class AvailabilityRuleUpdateSchema(Schema):
    weekday = fields.Integer(validate=validate.Range(min=1, max=7))
    startTime = fields.Time()
    endTime = fields.Time()
    validFrom = fields.Date()
    validTo = fields.Date(load_default=None)
    isActive = fields.Boolean()


class AvailabilityExceptionCreateSchema(Schema):
    type = fields.String(required=True, validate=validate.OneOf(["UNAVAILABLE", "EXTRA_AVAILABLE"]))
    startAt = fields.DateTime(required=True)
    endAt = fields.DateTime(required=True)
    reason = fields.String(load_default=None)


class AppointmentStatusUpdateSchema(Schema):
    status = fields.String(required=True, validate=validate.OneOf(["COMPLETED", "NO_SHOW", "CANCELLED_BY_CLINIC"]))
    cancellationReason = fields.String(load_default=None)

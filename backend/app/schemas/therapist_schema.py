from marshmallow import Schema, fields


class TherapistPublicSchema(Schema):
    id = fields.String(dump_only=True)
    fullName = fields.Method("get_full_name")
    title = fields.String()
    bio = fields.String()
    experienceYears = fields.Integer(attribute="experience_years")
    photoUrl = fields.String(attribute="photo_url", allow_none=True)
    averageRating = fields.Decimal(attribute="average_rating", as_string=True)
    reviewsCount = fields.Integer(attribute="reviews_count")
    isActive = fields.Boolean(attribute="is_active")

    def get_full_name(self, obj):
        return obj.user.full_name()

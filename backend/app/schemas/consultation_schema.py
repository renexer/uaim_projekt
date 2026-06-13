from marshmallow import Schema, fields, validate


# Schemat Marshmallow walidujący treść podsumowania konsultacji.
class ConsultationSummaryUpsertSchema(Schema):
    summaryText = fields.String(required=True, validate=validate.Length(min=5))

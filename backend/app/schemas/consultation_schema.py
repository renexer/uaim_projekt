from marshmallow import Schema, fields, validate


class ConsultationSummaryUpsertSchema(Schema):
    summaryText = fields.String(required=True, validate=validate.Length(min=5))

from marshmallow import Schema, fields, validate


class ReviewCreateSchema(Schema):
    rating = fields.Integer(required=True, validate=validate.Range(min=1, max=5))
    comment = fields.String(load_default=None, validate=validate.Length(max=2000))

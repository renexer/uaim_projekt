from marshmallow import Schema, fields, validate


class RegisterSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=8, max=128))
    firstName = fields.String(required=True, validate=validate.Length(min=2, max=100))
    lastName = fields.String(required=True, validate=validate.Length(min=2, max=100))
    phone = fields.String(load_default=None)


class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True)

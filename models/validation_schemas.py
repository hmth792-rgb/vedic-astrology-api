"""
Input validation schemas using Marshmallow
"""
from marshmallow import Schema, fields, validate, ValidationError
import re


class UserDetailsSchema(Schema):
    """Schema for validating user birth details"""
    
    name = fields.Str(
        required=True, 
        validate=validate.Length(min=1, max=100),
        error_messages={"required": "Name is required"}
    )
    
    datetime = fields.Str(
        required=True,
        validate=validate.Regexp(
            r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$',
            error="Invalid datetime format. Use YYYY-MM-DDTHH:MM:SS"
        ),
        error_messages={"required": "Birth datetime is required"}
    )
    
    latitude = fields.Float(
        required=True,
        validate=validate.Range(min=-90, max=90),
        error_messages={"required": "Latitude is required"}
    )
    
    longitude = fields.Float(
        required=True,
        validate=validate.Range(min=-180, max=180),
        error_messages={"required": "Longitude is required"}
    )
    
    timezone = fields.Float(
        required=True,
        validate=validate.Range(min=-12, max=14),
        error_messages={"required": "Timezone offset is required (e.g., 5.5 for IST)"}
    )
    
    place = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=200),
        error_messages={"required": "Place is required"}
    )
    
    religion = fields.Str(
        required=False,
        validate=validate.Length(max=50),
        allow_none=True
    )
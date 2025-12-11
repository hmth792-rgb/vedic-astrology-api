"""
Transit Routes
API endpoints for planetary transit calculations
"""
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from datetime import datetime, timezone
from models.astrology_models import UserDetails
from models.validation_schemas import UserDetailsSchema
from calculators.transit_calculator import TransitCalculator
import os

# Create blueprint
transit_bp = Blueprint('transit', __name__, url_prefix='/api/v1')

# Initialize calculator and schema
ephe_path = os.getenv('EPHE_PATH', './ephe')
transit_calculator = TransitCalculator(ephe_path=ephe_path)
user_schema = UserDetailsSchema()


@transit_bp.route('/transits', methods=['POST'])
def get_all_transits():
    """
    Get current transits for all major planets
    
    Request body:
    {
        "name": "string",
        "datetime": "YYYY-MM-DDTHH:MM:SS",  // Birth datetime
        "latitude": float,
        "longitude": float,
        "timezone": float,
        "place": "string",
        "transit_date": "YYYY-MM-DDTHH:MM:SS"  // Optional: date to calculate transits for (default: now)
    }
    
    Returns:
    {
        "status": "success",
        "user": { ... },
        "natal_ascendant": { ... },
        "transit_date": "...",
        "ayanamsa": float,
        "transits": {
            "SATURN": { ... },
            "JUPITER": { ... },
            "MERCURY": { ... },
            "MARS": { ... },
            "VENUS": { ... },
            "SUN": { ... },
            "MOON": { ... }
        }
    }
    """
    try:
        user_data = request.get_json()
        
        if not user_data:
            return jsonify({
                "status": "error",
                "message": "Request body is required"
            }), 400
        
        # Extract transit_date if provided
        transit_date_str = user_data.pop('transit_date', None)
        transit_date = None
        
        if transit_date_str:
            try:
                # Parse the transit date string to datetime object
                transit_date = datetime.strptime(transit_date_str.replace('T', ' '), '%Y-%m-%d %H:%M:%S')
                transit_date = transit_date.replace(tzinfo=timezone.utc)
            except ValueError:
                return jsonify({
                    "status": "error",
                    "message": "Invalid transit_date format. Use YYYY-MM-DDTHH:MM:SS"
                }), 400
        
        # Validate user data
        try:
            validated_data = user_schema.load(user_data)
        except ValidationError as err:
            return jsonify({
                "status": "error",
                "message": "Validation failed",
                "errors": err.messages
            }), 400
        
        # Create UserDetails object
        user_details = UserDetails(**validated_data)
        
        # Calculate transits
        transit_data = transit_calculator.calculate_transits(user_details, transit_date)
        
        return jsonify({
            "status": "success",
            "user": {
                "name": user_details.name,
                "birth_datetime": user_details.datetime,
                "latitude": user_details.latitude,
                "longitude": user_details.longitude,
                "place": user_details.place,
                "timezone": user_details.timezone
            },
            "natal_ascendant": transit_data["natal_ascendant"],
            "transit_date": transit_data["transit_date"],
            "ayanamsa": transit_data["ayanamsa"],
            "transits": transit_data["transits"]
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@transit_bp.route('/transits/major', methods=['POST'])
def get_major_transits():
    """
    Get transits for major slow-moving planets only (Saturn, Jupiter, Mercury)
    
    Request body:
    {
        "name": "string",
        "datetime": "YYYY-MM-DDTHH:MM:SS",  // Birth datetime
        "latitude": float,
        "longitude": float,
        "timezone": float,
        "place": "string",
        "transit_date": "YYYY-MM-DDTHH:MM:SS"  // Optional: date to calculate transits for (default: now)
    }
    
    Returns:
    {
        "status": "success",
        "user": { ... },
        "natal_ascendant": { ... },
        "transit_date": "...",
        "ayanamsa": float,
        "major_transits": {
            "SATURN": { 
                "planet": "SATURN",
                "longitude": float,
                "sign": "Aquarius",
                "sign_sanskrit": "Kumbha",
                "sign_number": 11,
                "degrees_in_sign": float,
                "house": 5,
                "is_retrograde": false
            },
            "JUPITER": { ... },
            "MERCURY": { ... }
        }
    }
    """
    try:
        user_data = request.get_json()
        
        if not user_data:
            return jsonify({
                "status": "error",
                "message": "Request body is required"
            }), 400
        
        # Extract transit_date if provided
        transit_date_str = user_data.pop('transit_date', None)
        transit_date = None
        
        if transit_date_str:
            try:
                # Parse the transit date string to datetime object
                transit_date = datetime.strptime(transit_date_str.replace('T', ' '), '%Y-%m-%d %H:%M:%S')
                transit_date = transit_date.replace(tzinfo=timezone.utc)
            except ValueError:
                return jsonify({
                    "status": "error",
                    "message": "Invalid transit_date format. Use YYYY-MM-DDTHH:MM:SS"
                }), 400
        
        # Validate user data
        try:
            validated_data = user_schema.load(user_data)
        except ValidationError as err:
            return jsonify({
                "status": "error",
                "message": "Validation failed",
                "errors": err.messages
            }), 400
        
        # Create UserDetails object
        user_details = UserDetails(**validated_data)
        
        # Calculate major transits
        transit_data = transit_calculator.get_major_transits(user_details, transit_date)
        
        return jsonify({
            "status": "success",
            "user": {
                "name": user_details.name,
                "birth_datetime": user_details.datetime,
                "latitude": user_details.latitude,
                "longitude": user_details.longitude,
                "place": user_details.place,
                "timezone": user_details.timezone
            },
            "natal_ascendant": transit_data["natal_ascendant"],
            "transit_date": transit_data["transit_date"],
            "ayanamsa": transit_data["ayanamsa"],
            "major_transits": transit_data["major_transits"]
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

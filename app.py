"""
Astrology API - D1 Chart Calculator
Professional API for generating D1 Rashi charts using Swiss Ephemeris
"""
from flask import Flask, request, jsonify, Response
from marshmallow import ValidationError
import traceback
import os
import sys
import json

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.astrology_models import UserDetails
from models.validation_schemas import UserDetailsSchema
from calculators.d1_chart_calculator import D1ChartCalculator

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Initialize calculator
calculator = D1ChartCalculator(ephe_path="./ephe")

# Initialize validation schema
user_schema = UserDetailsSchema()


@app.route('/')
def home():
    """API welcome endpoint"""
    return jsonify({
        "message": "Welcome to Astrology D1 Chart API",
        "version": "1.0.0",
        "description": "Calculate complete D1 Rashi charts using Swiss Ephemeris",
        "endpoints": {
            "calculate_d1_chart_full": "/api/v1/d1-chart",
            "calculate_d1_chart_refined": "/api/v1/d1-chart-refined",
            "health_check": "/health",
            "documentation": "/docs"
        }
    })


@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Astrology D1 Chart API",
        "ephemeris": "Swiss Ephemeris"
    })


@app.route('/api/v1/d1-chart', methods=['POST'])
def calculate_d1_chart():
    """
    Calculate complete D1 Rashi chart
    
    Expected JSON input:
    {
        "name": "John Doe",
        "datetime": "1990-01-15T14:30:00",
        "latitude": 28.6139,
        "longitude": 77.2090,
        "timezone": 5.5,
        "place": "New Delhi, India",
        "religion": "Hindu"
    }
    """
    try:
        # Validate input
        json_data = request.get_json()
        if not json_data:
            return jsonify({
                "error": "No JSON data provided",
                "status": "error"
            }), 400
        
        # Validate using schema
        try:
            validated_data = user_schema.load(json_data)
        except ValidationError as err:
            return jsonify({
                "error": "Validation failed",
                "details": err.messages,
                "status": "error"
            }), 400
        
        # Create UserDetails object
        user_details = UserDetails(**validated_data)
        
        # Calculate D1 chart
        d1_chart = calculator.calculate_d1_chart(user_details)
        
        # Convert to response format
        response = _format_chart_response(d1_chart)
        
        return jsonify({
            "status": "success",
            "data": response
        })
        
    except Exception as e:
        app.logger.error(f"Error calculating D1 chart: {str(e)}")
        app.logger.error(f"Traceback: {traceback.format_exc()}")
        
        return jsonify({
            "error": "Internal server error during chart calculation",
            "message": str(e),
            "status": "error"
        }), 500


@app.route('/api/v1/d1-chart-refined', methods=['POST'])
def calculate_d1_chart_refined():
    """
    Calculate REFINED D1 Rashi chart with simplified output
    Returns only essential columns: Graha, Longitude, Nakshatra, Lord/Sub Lord, 
    Ruler of, Is In, B. Owner, Relationship, Dignities
    
    Expected JSON input (same as d1-chart):
    {
        "name": "John Doe",
        "datetime": "1990-01-15T14:30:00",
        "latitude": 28.6139,
        "longitude": 77.2090,
        "timezone": 5.5,
        "place": "New Delhi, India",
        "religion": "Hindu"
    }
    """
    try:
        # Validate input
        json_data = request.get_json()
        if not json_data:
            return jsonify({
                "error": "No JSON data provided",
                "status": "error"
            }), 400
        
        # Validate using schema
        try:
            validated_data = user_schema.load(json_data)
        except ValidationError as err:
            return jsonify({
                "error": "Validation failed",
                "details": err.messages,
                "status": "error"
            }), 400
        
        # Create UserDetails object
        user_details = UserDetails(**validated_data)
        
        # Calculate D1 chart
        d1_chart = calculator.calculate_d1_chart(user_details)
        
        # Convert to refined response format
        response = _format_refined_chart_response(d1_chart)
        
        # Return with Response to preserve dictionary order
        result = {
            "status": "success",
            "data": response
        }
        return Response(
            json.dumps(result, ensure_ascii=False),
            mimetype='application/json'
        )
        
    except Exception as e:
        app.logger.error(f"Error calculating refined D1 chart: {str(e)}")
        app.logger.error(f"Traceback: {traceback.format_exc()}")
        
        return jsonify({
            "error": "Internal server error during chart calculation",
            "message": str(e),
            "status": "error"
        }), 500


@app.route('/docs')
def api_documentation():
    """API documentation endpoint"""
    return jsonify({
        "title": "Astrology D1 Chart API Documentation",
        "version": "1.0.0",
        "description": "Complete API for calculating D1 Rashi charts using Swiss Ephemeris",
        "endpoints": [
            {
                "path": "/",
                "method": "GET",
                "description": "API welcome and overview"
            },
            {
                "path": "/health",
                "method": "GET", 
                "description": "Health check endpoint"
            },
            {
                "path": "/api/v1/d1-chart",
                "method": "POST",
                "description": "Calculate complete D1 Rashi chart (all details)",
                "parameters": {
                    "name": "string (required) - Full name",
                    "datetime": "string (required) - Birth date and time in ISO format (YYYY-MM-DDTHH:MM:SS)",
                    "latitude": "float (required) - Birth latitude (-90 to 90)",
                    "longitude": "float (required) - Birth longitude (-180 to 180)",
                    "timezone": "float (required) - Timezone offset in hours (e.g., 5.5 for IST, -5 for EST)",
                    "place": "string (required) - Birth place name",
                    "religion": "string (optional) - Religion"
                },
                "response": {
                    "user_details": "Input user details",
                    "lagna": "Ascendant position and details",
                    "planets": "All planetary positions with signs, nakshatras, etc.",
                    "houses": "12 houses with cusps and planetary occupants",
                    "nakshatra_details": "Complete nakshatra information",
                    "sun_moon_shine": "Sunrise, sunset, moon phase, tithi",
                    "ayanamsa": "Ayanamsa value used",
                    "calculation_time": "UTC timestamp of calculation"
                }
            },
            {
                "path": "/api/v1/d1-chart-refined",
                "method": "POST",
                "description": "Calculate REFINED D1 Rashi chart (simplified essential columns only)",
                "parameters": "Same as /api/v1/d1-chart",
                "response": {
                    "graha_table": "Simplified planetary table with essential columns",
                    "bhava_table": "Simplified house table with essential columns"
                }
            }
        ],
        "example_request": {
            "name": "John Doe",
            "datetime": "1990-01-15T14:30:00",
            "latitude": 28.6139,
            "longitude": 77.2090,
            "timezone": 5.5,
            "place": "New Delhi, India",
            "religion": "Hindu"
        }
    })


def _format_refined_chart_response(d1_chart):
    """Format D1Chart object for REFINED JSON response (graha details only, correct sequence)"""

    from utils.vedic_helper import VedicAstrologyHelper
    from models.astrology_models import Planet
    helper = VedicAstrologyHelper()
    from services.swiss_ephemeris_service import SwissEphemerisService
    ephe_service = SwissEphemerisService()

    def format_longitude_dms(longitude, sign):
        """Format longitude in DMS format"""
        degree_in_sign = longitude % 30
        degrees = int(degree_in_sign)
        minutes = int((degree_in_sign - degrees) * 60)
        seconds = int(((degree_in_sign - degrees) * 60 - minutes) * 60)
        sign_short = helper.get_sign_short_name(sign)
        return f"{degrees:02d}° {sign_short} {minutes:02d}′ {seconds:02d}″"

    # Graha Table - Simplified columns
    graha_table = []

    # Add Lagna first
    lagna_nak_entry = next((n for n in ephe_service.nakshatras if n["name"] == d1_chart.lagna.nakshatra), None)
    lagna_nak_lord = lagna_nak_entry["ruler"] if lagna_nak_entry else d1_chart.houses[0].ruler_planet
    lagna_sub_lord = helper.get_sub_lord(d1_chart.lagna.longitude, lagna_nak_lord)
    lagna_lord_field = f"{helper.get_sanskrit_planet_name(lagna_nak_lord)}, {helper.get_sanskrit_planet_name(lagna_sub_lord)}"

    graha_table.append({
        "Graha": "Lagna",
        "Longitude": format_longitude_dms(d1_chart.lagna.longitude, d1_chart.lagna.sign),
        "Nakshatra": f"{d1_chart.lagna.nakshatra.name.replace('_', ' ').title()} {d1_chart.lagna.nakshatra_pada}",
        "Lord/Sub Lord": lagna_lord_field,
        "Ruler of": "-",
        "Is In": 1,
        "B. Owner": d1_chart.houses[0].ruler_planet.name,
        "Relationship": "-",
        "Dignities": "-"
    })
    planet_order = [
        Planet.SUN, Planet.MOON, Planet.MARS, Planet.MERCURY,
        Planet.JUPITER, Planet.VENUS, Planet.SATURN, Planet.RAHU, Planet.KETU
    ]
    
    for planet_enum in planet_order:
        planet_pos = next((p for p in d1_chart.planets if p.planet == planet_enum), None)
        if not planet_pos:
            continue
            
        symbol = helper.get_planet_symbol(planet_pos.planet)
        retrograde_symbol = "↺" if planet_pos.retrograde else ""

        # Lord/Sub Lord formatting
        nak_lord_name = helper.get_sanskrit_planet_name(planet_pos.nakshatra_lord) if planet_pos.nakshatra_lord else ""
        sub_lord_name = helper.get_sanskrit_planet_name(planet_pos.sub_lord) if planet_pos.sub_lord else ""
        lord_sub_lord = f"{nak_lord_name}, {sub_lord_name}" if nak_lord_name and sub_lord_name else "-"

        # Ruler of formatting (short)
        ruler_of = ", ".join([str(h) for h in planet_pos.ruler_of_houses]) if planet_pos.ruler_of_houses else "-"

        # Relationship wording
        if not planet_pos.relationship:
            rel_word = "-"
        elif planet_pos.relationship == "Own House":
            rel_word = "Own House"
        elif planet_pos.relationship == "Friend":
            rel_word = "Friend's House"
        elif planet_pos.relationship == "Enemy":
            rel_word = "Enemy's House"
        else:
            rel_word = planet_pos.relationship

        # Create ordered dict with exact field sequence
        graha_dict = {}
        graha_dict["Graha"] = f"{symbol}{planet_pos.planet.name.title()}{retrograde_symbol}"
        graha_dict["Longitude"] = format_longitude_dms(planet_pos.longitude, planet_pos.sign)
        graha_dict["Nakshatra"] = f"{planet_pos.nakshatra.name.replace('_', ' ').title()} {planet_pos.nakshatra_pada}"
        graha_dict["Lord/Sub Lord"] = lord_sub_lord
        graha_dict["Ruler of"] = ruler_of
        graha_dict["Is In"] = planet_pos.is_in_house if planet_pos.is_in_house else "-"
        graha_dict["B. Owner"] = planet_pos.house_owner.name if planet_pos.house_owner else "-"
        graha_dict["Relationship"] = rel_word
        graha_dict["Dignities"] = planet_pos.dignity if planet_pos.dignity else "-"
        graha_table.append(graha_dict)

    return {
        "Ascendant (Lagna)": graha_table[0] if graha_table else {},
        "Sun": graha_table[1] if len(graha_table) > 1 else {},
        "Moon": graha_table[2] if len(graha_table) > 2 else {},
        "Mars": graha_table[3] if len(graha_table) > 3 else {},
        "Mercury": graha_table[4] if len(graha_table) > 4 else {},
        "Jupiter": graha_table[5] if len(graha_table) > 5 else {},
        "Venus": graha_table[6] if len(graha_table) > 6 else {},
        "Saturn": graha_table[7] if len(graha_table) > 7 else {},
        "Rahu": graha_table[8] if len(graha_table) > 8 else {},
        "Ketu": graha_table[9] if len(graha_table) > 9 else {},
        "ayanamsa": round(d1_chart.ayanamsa, 6)
    }


def _format_chart_response(d1_chart):
    """Format D1Chart object for JSON response"""
    
    from utils.vedic_helper import VedicAstrologyHelper
    helper = VedicAstrologyHelper()
    
    def format_longitude_dms(longitude, sign):
        """Format longitude in DMS format"""
        degree_in_sign = longitude % 30
        degrees = int(degree_in_sign)
        minutes = int((degree_in_sign - degrees) * 60)
        seconds = int(((degree_in_sign - degrees) * 60 - minutes) * 60)
        sign_short = helper.get_sign_short_name(sign)
        return f"{degrees:02d}° {sign_short} {minutes:02d}′ {seconds:02d}″"
    
    def format_planet(planet_pos):
        """Format planet with all Vedic details"""
        symbol = helper.get_planet_symbol(planet_pos.planet)
        retrograde_symbol = " ↺" if planet_pos.retrograde else ""
        
        # Format nakshatra with lord
        nak_lord_name = planet_pos.nakshatra_lord.name if planet_pos.nakshatra_lord else ""
        sub_lord_name = planet_pos.sub_lord.name if planet_pos.sub_lord else ""
        
        return {
            "graha": f"{symbol}{planet_pos.planet.name.title()}{retrograde_symbol}",
            "long": format_longitude_dms(planet_pos.longitude, planet_pos.sign),
            "long_dec": round(planet_pos.longitude, 6),
            "nak": planet_pos.nakshatra.name.replace("_", " ").title(),
            "nak_pada": planet_pos.nakshatra_pada,
            "nak_lord": nak_lord_name,
            "sub_lord": sub_lord_name,
            "rules": planet_pos.ruler_of_houses if planet_pos.ruler_of_houses else [],
            "in": planet_pos.is_in_house if planet_pos.is_in_house else 0,
            "house_owner": planet_pos.house_owner.name if planet_pos.house_owner else "-",
            "rel": planet_pos.relationship if planet_pos.relationship else "-",
            "dig": planet_pos.dignity if planet_pos.dignity else "-",
            "sign": planet_pos.sign.name,
            "deg": round(planet_pos.degree, 6),
            "retro": planet_pos.retrograde
        }
    
    def format_house(house_data):
        """Format house (Bhava) with all details"""
        return {
            "no": house_data.house_number,
            "res": [p.name for p in house_data.planets_in_house],
            "own": house_data.ruler_planet.name,
            "rashi": house_data.sign_short_name if house_data.sign_short_name else house_data.sign.name,
            "sign": house_data.sign.name,
            "qual": house_data.qualities if house_data.qualities else [],
            "asp": [p.name for p in house_data.aspected_by] if house_data.aspected_by else [],
            "cusp": round(house_data.cusp_longitude, 6)
        }
    
    def format_nakshatra(nak_details):
        return {
            "name": nak_details.name.name.replace("_", " ").title(),
            "ruler": nak_details.ruler.name,
            "degree_start": round(nak_details.degree_start, 6),
            "degree_end": round(nak_details.degree_end, 6),
            "symbol": nak_details.symbol,
            "deity": nak_details.deity,
            "quality": nak_details.quality
        }
    
    # Format Lagna separately
    lagna_data = {
        "graha": "Lagna",
        "long": format_longitude_dms(d1_chart.lagna.longitude, d1_chart.lagna.sign),
        "long_dec": round(d1_chart.lagna.longitude, 6),
        "nak": d1_chart.lagna.nakshatra.name.replace("_", " ").title(),
        "nak_pada": d1_chart.lagna.nakshatra_pada,
        "sign": d1_chart.lagna.sign.name,
        "deg": round(d1_chart.lagna.degree, 6)
    }
    
    return {
        "lagna": lagna_data,
        "grahas": [format_planet(p) for p in d1_chart.planets],
        "bhavas": [format_house(h) for h in d1_chart.houses],
        "ayanamsa": round(d1_chart.ayanamsa, 6)
    }


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

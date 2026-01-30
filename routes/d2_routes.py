"""
D2 Chart (Hora) Routes
Divisional chart for wealth, fortune, and material prosperity analysis
Only refined endpoint with essential graha data
"""
import os
from flask import Blueprint, request, jsonify, Response
from marshmallow import ValidationError
import json

from models.astrology_models import UserDetails, Planet
from models.validation_schemas import UserDetailsSchema
from calculators.d1_chart_calculator import D1ChartCalculator
from calculators.d2_chart_calculator import D2ChartCalculator
from utils.vedic_helper import VedicAstrologyHelper
from services.swiss_ephemeris_service import SwissEphemerisService

# Create blueprint
d2_bp = Blueprint('d2', __name__, url_prefix='/api/v1')

# Initialize schema
user_schema = UserDetailsSchema()


@d2_bp.route('/d2-chart-refined', methods=['POST'])
def calculate_d2_chart_refined():
    """
    Calculate D2 (Hora) chart - simplified response with essential graha data only
    
    Returns: Graha, Longitude, Nakshatra, Lord/Sub Lord, Ruler of, Is In, B. Owner, 
             Relationship, Dignities
    
    Request body:
    {
        "name": "string (required)",
        "datetime": "string (required) ISO format YYYY-MM-DDTHH:MM:SS",
        "latitude": "float (required)",
        "longitude": "float (required)",
        "timezone": "float (required)",
        "place": "string (required)",
        "religion": "string (optional)",
        "sidereal_mode": "string (optional) - LAHIRI, RAMAN, KRISHNAMURTI, etc"
    }
    """
    try:
        json_data = request.get_json()
        if not json_data:
            return jsonify({
                "error": "No JSON data provided",
                "status": "error"
            }), 400
        
        # Extract optional sidereal_mode before validation
        sidereal_mode = json_data.pop('sidereal_mode', None)

        try:
            validated_data = user_schema.load(json_data)
        except ValidationError as err:
            return jsonify({
                "error": "Validation failed",
                "details": err.messages,
                "status": "error"
            }), 400

        user_details = UserDetails(**validated_data)

        # Get config from environment or use defaults
        ephe_path = os.getenv('EPHEMERIS_PATH', './ephe')
        node_rulership = os.getenv('NODE_RULERSHIP_STRATEGY', 'nak_lord_rules')
        nakshatra_eps = float(os.getenv('NAKSHATRA_EPSILON', 1e-6))
        
        # Use provided sidereal_mode or default from env
        if sidereal_mode is None:
            sidereal_mode = os.getenv('SIDEREAL_MODE', None)

        # Instantiate calculators
        d1_calculator = D1ChartCalculator(
            ephe_path=ephe_path,
            node_rulership_strategy=node_rulership,
            nakshatra_epsilon=nakshatra_eps,
            sidereal_mode=sidereal_mode
        )
        d2_calculator = D2ChartCalculator(
            ephe_path=ephe_path,
            node_rulership_strategy=node_rulership,
            nakshatra_epsilon=nakshatra_eps,
            sidereal_mode=sidereal_mode
        )

        # Calculate D1 then D2
        d1_chart = d1_calculator.calculate_d1_chart(user_details)
        d2_data = d2_calculator.calculate_d2_chart(user_details, d1_chart)

        response = _format_refined_d2_response(d2_data, ephe_path)
        
        return Response(
            json.dumps(response, ensure_ascii=False),
            mimetype='application/json'
        )
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500


def _format_refined_d2_response(d2_data: dict, ephe_path: str) -> dict:
    """
    Format D2 data into refined response with essential graha information only
    
    Returns simplified table: Graha, Longitude, Nakshatra, Lord/Sub Lord, 
    Ruler of, Is In, B. Owner, Relationship, Dignities
    """
    vedic_helper = VedicAstrologyHelper()
    planets_data = d2_data['planets']
    houses_data = d2_data['houses']
    
    # Build graha table
    graha_table = []
    
    for planet in planets_data:
        # Get sign name (English and Sanskrit)
        sign_name_english = vedic_helper.get_sign_name(planet.sign)
        sign_name_sanskrit = vedic_helper.get_sign_short_name(planet.sign)
        sign_display = f"{sign_name_english} ({sign_name_sanskrit})"
        
        # Nakshatra display
        nak_name = planet.nakshatra.name if planet.nakshatra else "N/A"
        pada = planet.nakshatra_pada if hasattr(planet, 'nakshatra_pada') else 0
        nakshatra_display = f"{nak_name} - {pada}"
        
        # Lord/Sub Lord
        nak_lord = planet.nakshatra_lord.name if planet.nakshatra_lord else "N/A"
        sub_lord = planet.sub_lord.name if planet.sub_lord else "N/A"
        lord_display = f"{nak_lord}/{sub_lord}"
        
        # Ruler of (houses ruled by this planet)
        ruled_houses = planet.ruler_of_houses if hasattr(planet, 'ruler_of_houses') else []
        ruler_of = ", ".join([str(h) for h in ruled_houses]) if ruled_houses else "-"
        
        # Is In (current house position)
        is_in = str(planet.is_in_house) if hasattr(planet, 'is_in_house') and planet.is_in_house else "-"
        
        # B. Owner (Bhava/Sign owner)
        sign_lord_name = planet.house_owner.name if hasattr(planet, 'house_owner') and planet.house_owner else "N/A"
        
        # Relationship with sign lord
        relationship = planet.relationship if hasattr(planet, 'relationship') else "Neutral"
        
        # Dignities
        dignities = planet.dignity if hasattr(planet, 'dignity') else "-"
        
        graha_row = {
            "Graha": planet.planet.name,
            "Longitude": f"{planet.longitude:.6f}",
            "Sign": sign_display,
            "Degree in Sign": f"{planet.degree:.6f}",
            "Nakshatra": nakshatra_display,
            "Lord/Sub Lord": lord_display,
            "Ruler of": ruler_of,
            "Is In": is_in,
            "B. Owner": sign_lord_name,
            "Relationship": relationship,
            "Dignities": dignities
        }
        
        graha_table.append(graha_row)
    
    # Get Lagna info
    lagna = d2_data['lagna']
    lagna_sign_english = vedic_helper.get_sign_name(lagna.sign)
    lagna_sign_sanskrit = vedic_helper.get_sign_short_name(lagna.sign)
    
    return {
        "status": "success",
        "chart_type": "D2 (Hora)",
        "description": "Divisional chart for wealth, fortune, and material prosperity",
        "lagna": {
            "longitude": lagna.longitude,
            "sign": f"{lagna_sign_english} ({lagna_sign_sanskrit})",
            "degree_in_sign": lagna.degree
        },
        "ayanamsa": d2_data['ayanamsa'],
        "graha_table": graha_table
    }

"""
D12 Chart (Dwadash Amsha) Routes
Divisional chart for parents and ancestors
Refined endpoint with essential graha data only
"""
import os
from flask import Blueprint, request, jsonify, Response
from marshmallow import ValidationError
import json

from models.astrology_models import UserDetails, Planet
from models.validation_schemas import UserDetailsSchema
from calculators.d1_chart_calculator import D1ChartCalculator
from calculators.d12_chart_calculator import D12ChartCalculator
from utils.vedic_helper import VedicAstrologyHelper
from services.swiss_ephemeris_service import SwissEphemerisService

# Create blueprint
d12_bp = Blueprint('d12', __name__, url_prefix='/api/v1')

# Initialize schema
user_schema = UserDetailsSchema()


@d12_bp.route('/d12-chart-refined', methods=['POST'])
def calculate_d12_chart_refined():
    """
    Calculate D12 (Dwadash Amsha) chart - simplified response with essential graha data only
    
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
        ayanamsa_offset = float(os.getenv('AYANAMSA_OFFSET', '-0.245877'))  # Drik Panchang compatibility
        
        # Use provided sidereal_mode or default from env
        if sidereal_mode is None:
            sidereal_mode = os.getenv('SIDEREAL_MODE', None)

        # Instantiate calculator
        d12_calculator = D12ChartCalculator(
            ephe_path=ephe_path,
            node_rulership_strategy=node_rulership,
            nakshatra_epsilon=nakshatra_eps,
            sidereal_mode=sidereal_mode,
            ayanamsa_offset=ayanamsa_offset
        )

        # Calculate D12 chart
        d12_data = d12_calculator.calculate_d12_chart(user_details)

        response = _format_refined_d12_response(d12_data, ephe_path)
        
        return Response(
            json.dumps(response, ensure_ascii=False),
            mimetype='application/json'
        )
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500


def _format_refined_d12_response(d12_data: dict, ephe_path: str) -> dict:
    """
    Format D12 data into refined response matching D9 format with named dict structure
    """
    helper = VedicAstrologyHelper()
    ephe_service = SwissEphemerisService(ephe_path=ephe_path)
    planets_data = d12_data['planets']
    
    def format_longitude_dms(longitude, sign):
        """Format longitude in DMS format with sign name"""
        degree_in_sign = longitude % 30
        degrees = int(degree_in_sign)
        minutes = int((degree_in_sign - degrees) * 60)
        seconds = int(((degree_in_sign - degrees) * 60 - minutes) * 60)
        sign_short = helper.get_sign_short_name(sign)
        return f"{degrees:02d}° {sign_short} {minutes:02d}′ {seconds:02d}″"
    
    # Build graha table
    graha_table = []
    
    # Add D12 Lagna (Ascendant)
    d12_lagna = d12_data['lagna']
    lagna_nak_lord = d12_lagna.nakshatra_lord  # Use enriched value from calculator
    lagna_sub_lord = d12_lagna.sub_lord  # Use enriched value from calculator
    
    lagna_lord_field = f"{helper.get_sanskrit_planet_name(lagna_nak_lord)}, {helper.get_sanskrit_planet_name(lagna_sub_lord)}" if lagna_nak_lord and lagna_sub_lord else "-"
    
    lagna_ruler_of = ", ".join([str(h) for h in d12_lagna.ruler_of_houses]) if d12_lagna.ruler_of_houses else "-"
    
    lagna_dict = {
        "Graha": "Lagna",
        "Longitude": format_longitude_dms(d12_lagna.longitude, d12_lagna.sign),
        "Nakshatra": f"{d12_lagna.nakshatra.name.replace('_', ' ').title()} {d12_lagna.nakshatra_pada}",
        "Lord/Sub Lord": lagna_lord_field,
        "Ruler of": lagna_ruler_of,
        "Is In": 1,
        "B. Owner": helper.get_sanskrit_planet_name(d12_data['houses'][0].ruler_planet),
        "Relationship": "-",
        "Dignities": "-"
    }
    graha_table.append(lagna_dict)
    
    # Add all planets in proper order
    planet_order = [
        Planet.SUN, Planet.MOON, Planet.MARS, Planet.MERCURY,
        Planet.JUPITER, Planet.VENUS, Planet.SATURN, Planet.RAHU, Planet.KETU
    ]
    
    for planet_enum in planet_order:
        planet_pos = next((p for p in planets_data if p.planet == planet_enum), None)
        if not planet_pos:
            continue
        
        symbol = helper.get_planet_symbol(planet_pos.planet)
        retrograde_symbol = "↺" if planet_pos.retrograde else ""
        
        nak_lord_name = helper.get_sanskrit_planet_name(planet_pos.nakshatra_lord) if planet_pos.nakshatra_lord else ""
        sub_lord_name = helper.get_sanskrit_planet_name(planet_pos.sub_lord) if planet_pos.sub_lord else ""
        lord_sub_lord = f"{nak_lord_name}, {sub_lord_name}" if nak_lord_name and sub_lord_name else "-"
        
        ruler_of = ", ".join([str(h) for h in planet_pos.ruler_of_houses]) if planet_pos.ruler_of_houses else "-"
        
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
        
        graha_dict = {
            "Graha": f"{symbol}{planet_pos.planet.name.title()}{retrograde_symbol}",
            "Longitude": format_longitude_dms(planet_pos.longitude, planet_pos.sign),
            "Nakshatra": f"{planet_pos.nakshatra.name.replace('_', ' ').title()} {planet_pos.nakshatra_pada}",
            "Lord/Sub Lord": lord_sub_lord,
            "Ruler of": ruler_of,
            "Is In": planet_pos.is_in_house if planet_pos.is_in_house else "-",
            "B. Owner": helper.get_sanskrit_planet_name(planet_pos.house_owner) if planet_pos.house_owner else "-",
            "Relationship": rel_word,
            "Dignities": planet_pos.dignity if planet_pos.dignity else "-"
        }
        graha_table.append(graha_dict)
    
    # Create named dictionary for each graha (matching D9/D1 format)
    data_dict = {
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
        "ayanamsa": round(d12_data['ayanamsa'], 6)
    }
    
    return {
        "status": "success",
        "chart_type": "D12 (Dwadash Amsha) - Divisional Chart for Parents & Ancestors",
        "data": data_dict
    }

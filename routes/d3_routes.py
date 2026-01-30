"""
D3 Chart (Drekkana) Routes
Divisional chart for siblings, courage, and communication analysis
Only refined endpoint with essential graha data
"""
import os
from flask import Blueprint, request, jsonify, Response
from marshmallow import ValidationError
import json

from models.astrology_models import UserDetails, Planet
from models.validation_schemas import UserDetailsSchema
from calculators.d1_chart_calculator import D1ChartCalculator
from calculators.d3_chart_calculator import D3ChartCalculator
from utils.vedic_helper import VedicAstrologyHelper
from services.swiss_ephemeris_service import SwissEphemerisService

# Create blueprint
d3_bp = Blueprint('d3', __name__, url_prefix='/api/v1')

# Initialize schema
user_schema = UserDetailsSchema()


@d3_bp.route('/d3-chart-refined', methods=['POST'])
def calculate_d3_chart_refined():
    """
    Calculate D3 (Drekkana) chart - simplified response with essential graha data only
    
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
        d3_calculator = D3ChartCalculator(
            ephe_path=ephe_path,
            node_rulership_strategy=node_rulership,
            nakshatra_epsilon=nakshatra_eps,
            sidereal_mode=sidereal_mode
        )

        # Calculate D1 then D3
        d1_chart = d1_calculator.calculate_d1_chart(user_details)
        d3_data = d3_calculator.calculate_d3_chart(user_details, d1_chart)

        response = _format_refined_d3_response(d3_data, ephe_path)
        
        return Response(
            json.dumps(response, ensure_ascii=False),
            mimetype='application/json'
        )
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500


def _format_refined_d3_response(d3_data: dict, ephe_path: str) -> dict:
    """
    Format D3 data into refined response with essential graha information only
    
    Returns table: Graha, Longitude, Nakshatra (Pada), Lord/Sub-Lord, 
    Ruler of, Is In (Bhava), B. Owner, Relationship, Dignities
    """
    vedic_helper = VedicAstrologyHelper()
    ephe_service = SwissEphemerisService(ephe_path)
    planets_data = d3_data['planets']
    houses_data = d3_data['houses']
    lagna = d3_data['lagna']
    
    # Helper function to format longitude as degrees, minutes, seconds
    def format_longitude(longitude, sign):
        degree_in_sign = longitude % 30
        degrees = int(degree_in_sign)
        minutes = int((degree_in_sign - degrees) * 60)
        seconds = int(((degree_in_sign - degrees) * 60 - minutes) * 60)
        sign_short = vedic_helper.get_sign_short_name(sign)
        return f"{degrees:02d}° {sign_short} {minutes:02d}′ {seconds:02d}″"
    
    # Build graha table
    graha_table = []
    
    # Add Lagna first
    lagna_nak_entry = next((n for n in ephe_service.nakshatras if n["name"] == lagna.nakshatra), None)
    lagna_nak_lord = lagna_nak_entry["ruler"].name if lagna_nak_entry else "N/A"
    lagna_sub_lord = "N/A"
    if lagna_nak_entry:
        lagna_sub_lord_planet = vedic_helper.get_sub_lord(
            lagna.longitude, lagna_nak_entry["ruler"],
            ephe_service=ephe_service,
            epsilon=1e-6
        )
        lagna_sub_lord = lagna_sub_lord_planet.name if lagna_sub_lord_planet else "N/A"
    
    lagna_row = {
        "Graha": "Lagna (Q)",
        "Longitude": format_longitude(lagna.longitude, lagna.sign),
        "Nakshatra (Pada)": f"{lagna.nakshatra.name} (Pada {lagna.nakshatra_pada})" if lagna.nakshatra else "N/A",
        "Lord / Sub-Lord": f"{lagna_nak_lord}, {lagna_sub_lord}",
        "Ruler of": "1 Bhava",
        "Is In (Bhava)": "1 Bhava",
        "B. Owner": VedicAstrologyHelper.SIGN_LORDS[lagna.sign].name if lagna.sign in VedicAstrologyHelper.SIGN_LORDS else "N/A",
        "Relationship": "–",
        "Dignities": "–"
    }
    graha_table.append(lagna_row)
    
    # Add planets
    for planet in planets_data:
        # Nakshatra (Pada) display
        nak_name = planet.nakshatra.name if planet.nakshatra else "N/A"
        pada = planet.nakshatra_pada if hasattr(planet, 'nakshatra_pada') else 0
        nakshatra_display = f"{nak_name} (Pada {pada})"
        
        # Lord / Sub-Lord
        nak_lord = planet.nakshatra_lord.name if planet.nakshatra_lord else "N/A"
        sub_lord = planet.sub_lord.name if planet.sub_lord else "N/A"
        lord_display = f"{nak_lord}, {sub_lord}"
        
        # Ruler of (houses ruled by this planet)
        ruled_houses = planet.ruler_of_houses if hasattr(planet, 'ruler_of_houses') else []
        if ruled_houses:
            ruler_of = ", ".join([f"{h} Bhava" for h in ruled_houses]) if len(ruled_houses) == 1 else ", ".join([str(h) for h in ruled_houses]) + " Bhava"
        else:
            ruler_of = "–"
        
        # Is In (Bhava) - current house position
        is_in = f"{planet.is_in_house} Bhava" if hasattr(planet, 'is_in_house') and planet.is_in_house else "–"
        
        # B. Owner (Bhava/Sign owner)
        sign_lord_name = planet.house_owner.name if hasattr(planet, 'house_owner') and planet.house_owner else "N/A"
        
        # Relationship with sign lord
        relationship = planet.relationship if hasattr(planet, 'relationship') else "Neutral"
        if relationship == "Friend":
            relationship = "Friend's House"
        elif relationship == "Enemy":
            relationship = "Enemy's House"
        elif relationship == "Own":
            relationship = "Own House"
        elif relationship == "Neutral":
            relationship = "Neutral"
        
        # Dignities
        dignities = planet.dignity if hasattr(planet, 'dignity') else "–"
        if dignities == "-" or not dignities:
            dignities = "–"
        
        # Add retrograde symbol if applicable
        planet_name = planet.planet.name
        if hasattr(planet, 'retrograde') and planet.retrograde:
            planet_name += " ↺"
        
        graha_row = {
            "Graha": planet_name,
            "Longitude": format_longitude(planet.longitude, planet.sign),
            "Nakshatra (Pada)": nakshatra_display,
            "Lord / Sub-Lord": lord_display,
            "Ruler of": ruler_of,
            "Is In (Bhava)": is_in,
            "B. Owner": sign_lord_name,
            "Relationship": relationship,
            "Dignities": dignities
        }
        
        graha_table.append(graha_row)
    
    # Get Lagna info for response metadata
    lagna_sign_english = vedic_helper.get_sign_name(lagna.sign)
    lagna_sign_sanskrit = vedic_helper.get_sign_short_name(lagna.sign)
    
    return {
        "status": "success",
        "chart_type": "D3 (Drekkana)",
        "description": "Divisional chart for siblings, courage, and communication",
        "lagna": {
            "longitude": lagna.longitude,
            "sign": f"{lagna_sign_english} ({lagna_sign_sanskrit})",
            "degree_in_sign": lagna.degree
        },
        "ayanamsa": d3_data['ayanamsa'],
        "graha_table": graha_table
    }

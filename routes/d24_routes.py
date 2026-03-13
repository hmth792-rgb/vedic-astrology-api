"""
D24 Chart API Routes (Chaturvimshamsha)
"""
import json
import os
from flask import request, jsonify, Response, Blueprint
from marshmallow import ValidationError

from models.astrology_models import UserDetails, Planet
from models.validation_schemas import UserDetailsSchema
from calculators.d24_chart_calculator import D24ChartCalculator
from utils.vedic_helper import VedicAstrologyHelper
from services.swiss_ephemeris_service import SwissEphemerisService

d24_routes = Blueprint('d24', __name__, url_prefix='/api')

user_schema = UserDetailsSchema()

def _format_refined_response(chart_data: dict, ephe_path: str) -> dict:
    """
    Format divisional chart data into refined response format
    """
    helper = VedicAstrologyHelper()
    ephe_service = SwissEphemerisService(ephe_path=ephe_path)
    planets_data = chart_data['planets']
    
    def format_longitude_dms(longitude, sign):
        """Format longitude in DMS format with sign name"""
        degree_in_sign = longitude % 30
        degrees = int(degree_in_sign)
        minutes = int((degree_in_sign - degrees) * 60)
        seconds = int(((degree_in_sign - degrees) * 60 - minutes) * 60)
        sign_short = helper.get_sign_short_name(sign)
        return f"{degrees:02d}° {sign_short} {minutes:02d}′ {seconds:02d}″"

    def format_bhava_list(values):
        if not values:
            return "-"
        return ", ".join([f"{v} Bhava" for v in values])

    def format_bhava_value(value):
        if not value or value == "-":
            return "-"
        return f"{value} Bhava"
    
    # Build graha table
    graha_table = []
    
    # Add Lagna
    lagna = chart_data['lagna']
    lagna_nak_lord = lagna.nakshatra_lord
    lagna_sub_lord = lagna.sub_lord
    
    lagna_lord_field = f"{helper.get_sanskrit_planet_name(lagna_nak_lord)}, {helper.get_sanskrit_planet_name(lagna_sub_lord)}" if lagna_nak_lord and lagna_sub_lord else "-"
    lagna_ruler_of = format_bhava_list(lagna.ruler_of_houses) if lagna.ruler_of_houses else "-"
    
    lagna_dict = {
        "Graha": "Lagna",
        "Longitude": format_longitude_dms(lagna.longitude, lagna.sign),
        "Nakshatra": f"{lagna.nakshatra.name.replace('_', ' ').title()} {lagna.nakshatra_pada}",
        "Lord/Sub Lord": lagna_lord_field,
        "Ruler of": "1 Bhava",
        "Is In": helper.get_sanskrit_planet_name(chart_data['houses'][0].ruler_planet),
        "B. Owner": "-",
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
        
        ruler_of = format_bhava_list(planet_pos.ruler_of_houses) if planet_pos.ruler_of_houses else "-"
        
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
            "Is In": format_bhava_value(planet_pos.is_in_house) if planet_pos.is_in_house else "-",
            "B. Owner": helper.get_sanskrit_planet_name(planet_pos.house_owner) if planet_pos.house_owner else "-",
            "Relationship": rel_word,
            "Dignities": planet_pos.dignity if planet_pos.dignity else "-"
        }
        graha_table.append(graha_dict)
    
    return {
        "chart_type": chart_data['chart_type'],
        "description": chart_data['description'],
        "data": graha_table,
        "ayanamsa": chart_data['ayanamsa']
    }


@d24_routes.route('/v1/d24-chart-refined', methods=['POST'])
def calculate_d24_chart_refined():
    """
    Calculate D24 (Chaturvimshamsha) chart - Education & Learning
    
    Request body:
    {
        "name": "string (required)",
        "datetime": "string (required) ISO format YYYY-MM-DDTHH:MM:SS",
        "latitude": "float (required)",
        "longitude": "float (required)",
        "timezone": "float (required)",
        "place": "string (required)",
        "religion": "string (optional)",
        "sidereal_mode": "string (optional)"
    }
    """
    try:
        json_data = request.get_json()
        if not json_data:
            return jsonify({
                "error": "No JSON data provided",
                "status": "error"
            }), 400
        
        sidereal_mode = json_data.pop('sidereal_mode', None)
        d24_longitude_offset = json_data.pop('d24_longitude_offset', None)
        d24_lagna_offset = json_data.pop('d24_lagna_offset', None)

        try:
            validated_data = user_schema.load(json_data)
        except ValidationError as err:
            return jsonify({
                "error": "Validation failed",
                "details": err.messages,
                "status": "error"
            }), 400

        user_details = UserDetails(**validated_data)

        ephe_path = os.getenv('EPHEMERIS_PATH', './ephe')
        node_rulership = os.getenv('NODE_RULERSHIP_STRATEGY', 'co_signs')
        nakshatra_eps = float(os.getenv('NAKSHATRA_EPSILON', 1e-6))
        ayanamsa_offset = float(os.getenv('AYANAMSA_OFFSET', '-0.245877'))
        default_d24_longitude_offset = float(os.getenv('D24_LONGITUDE_OFFSET', '-0.162'))
        default_d24_lagna_offset = float(os.getenv('D24_LAGNA_OFFSET', '-0.5333394196895132'))
        
        # D27 defaults (if requested via same endpoint)
        default_d27_longitude_offset = float(os.getenv('D27_LONGITUDE_OFFSET', '-0.182'))
        default_d27_lagna_offset = float(os.getenv('D27_LAGNA_OFFSET', '6.0387'))
        
        if sidereal_mode is None:
            sidereal_mode = os.getenv('SIDEREAL_MODE', None)

        d24_calculator = D24ChartCalculator(
            ephe_path=ephe_path,
            node_rulership_strategy=node_rulership,
            nakshatra_epsilon=nakshatra_eps,
            sidereal_mode=sidereal_mode,
            ayanamsa_offset=ayanamsa_offset,
            d24_longitude_offset=float(d24_longitude_offset) if d24_longitude_offset is not None else default_d24_longitude_offset,
            d24_lagna_offset=float(d24_lagna_offset) if d24_lagna_offset is not None else default_d24_lagna_offset
        )

        d24_data = d24_calculator.calculate_d24_chart(user_details)
        response = _format_refined_response(d24_data, ephe_path)
        
        return Response(
            json.dumps(response, ensure_ascii=False),
            mimetype='application/json'
        )
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500

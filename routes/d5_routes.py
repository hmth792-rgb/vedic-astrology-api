"""
D5 Chart (Quinamsha) Routes
Divisional chart for learning, intellect, education, and skills
Refined endpoint with essential graha data only
"""
import os
import json
from flask import Blueprint, request, jsonify, Response
from marshmallow import ValidationError

from models.astrology_models import UserDetails, Planet
from models.validation_schemas import UserDetailsSchema
from calculators.d1_chart_calculator import D1ChartCalculator
from calculators.d5_chart_calculator import D5ChartCalculator
from utils.vedic_helper import VedicAstrologyHelper

# Create blueprint
d5_bp = Blueprint('d5', __name__, url_prefix='/api/v1')

# Initialize schema
user_schema = UserDetailsSchema()


@d5_bp.route('/d5-chart-refined', methods=['POST'])
def calculate_d5_chart_refined():
    """
    Calculate D5 (Quinamsha) chart - refined response

    Returns: Graha, Longitude, Nakshatra, Lord/Sub Lord, Ruler of, Is In, B. Owner,
             Relationship, Dignities
    """
    try:
        json_data = request.get_json()
        if not json_data:
            return jsonify({"error": "No JSON data provided", "status": "error"}), 400

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

        ephe_path = os.getenv('EPHEMERIS_PATH', './ephe')
        node_rulership = os.getenv('NODE_RULERSHIP_STRATEGY', 'nak_lord_rules')
        nakshatra_eps = float(os.getenv('NAKSHATRA_EPSILON', 1e-6))

        if sidereal_mode is None:
            sidereal_mode = os.getenv('SIDEREAL_MODE', None)

        d1_calculator = D1ChartCalculator(
            ephe_path=ephe_path,
            node_rulership_strategy=node_rulership,
            nakshatra_epsilon=nakshatra_eps,
            sidereal_mode=sidereal_mode
        )
        d5_calculator = D5ChartCalculator(
            ephe_path=ephe_path,
            node_rulership_strategy=node_rulership,
            nakshatra_epsilon=nakshatra_eps,
            sidereal_mode=sidereal_mode
        )

        d1_chart = d1_calculator.calculate_d1_chart(user_details)
        d5_data = d5_calculator.calculate_d5_chart(user_details, d1_chart)

        response = _format_refined_d5_response(d5_data)

        return Response(json.dumps(response, ensure_ascii=False), mimetype='application/json')

    except Exception as e:
        return jsonify({"error": str(e), "status": "error"}), 500


def _format_refined_d5_response(d5_data: dict) -> dict:
    """Format D5 data into refined response matching D9 format with named dict structure"""
    helper = VedicAstrologyHelper()
    from services.swiss_ephemeris_service import SwissEphemerisService
    ephe_service = SwissEphemerisService("./ephe")
    
    planets_data = d5_data['planets']
    lagna = d5_data['lagna']

    def format_longitude_dms(longitude, sign):
        """Format longitude in DMS format with sign name"""
        degree_in_sign = longitude % 30
        degrees = int(degree_in_sign)
        minutes = int((degree_in_sign - degrees) * 60)
        seconds = int(((degree_in_sign - degrees) * 60 - minutes) * 60)
        sign_short = helper.get_sign_short_name(sign)
        return f"{degrees:02d}° {sign_short} {minutes:02d}′ {seconds:02d}″"

    graha_table = []
    
    # Add D5 Lagna
    d5_lagna = lagna
    lagna_nak_entry = next((n for n in ephe_service.nakshatras if n["name"] == d5_lagna.nakshatra), None)
    lagna_nak_lord = lagna_nak_entry["ruler"] if lagna_nak_entry else None
    lagna_sub_lord = helper.get_sub_lord(
        d5_lagna.longitude,
        lagna_nak_lord,
        ephe_service=ephe_service,
        epsilon=1e-6
    ) if lagna_nak_lord else None
    
    lagna_lord_field = f"{helper.get_sanskrit_planet_name(lagna_nak_lord)}, {helper.get_sanskrit_planet_name(lagna_sub_lord)}" if lagna_nak_lord and lagna_sub_lord else "-"
    
    lagna_dict = {
        "Graha": "Lagna",
        "Longitude": format_longitude_dms(d5_lagna.longitude, d5_lagna.sign),
        "Nakshatra": f"{d5_lagna.nakshatra.name.replace('_', ' ').title()} {d5_lagna.nakshatra_pada}",
        "Lord/Sub Lord": lagna_lord_field,
        "Ruler of": "-",
        "Is In": 1,
        "B. Owner": helper.get_sanskrit_planet_name(d5_data['houses'][0].ruler_planet),
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
        "ayanamsa": round(d5_data['ayanamsa'], 6)
    }

    return {
        "status": "success",
        "chart_type": "D5 (Quinamsha) - Divisional Chart for Education & Intellect",
        "data": data_dict
    }

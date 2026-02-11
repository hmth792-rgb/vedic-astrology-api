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
    """Format D5 data into refined response with essential graha information only."""
    vedic_helper = VedicAstrologyHelper()
    from services.swiss_ephemeris_service import SwissEphemerisService
    ephe_service = SwissEphemerisService("./ephe")
    
    planets_data = d5_data['planets']
    houses_data = d5_data['houses']
    lagna = d5_data['lagna']

    # Helper function to format longitude as degrees, minutes, seconds
    def format_longitude(longitude, sign):
        degree_in_sign = longitude % 30
        degrees = int(degree_in_sign)
        minutes = int((degree_in_sign - degrees) * 60)
        seconds = int(((degree_in_sign - degrees) * 60 - minutes) * 60)
        sign_short = vedic_helper.get_sign_short_name(sign)
        return f"{degrees:02d}° {sign_short} {minutes:02d}′ {seconds:02d}″"

    # Helper to compute house number from lagna sign and target sign
    def house_from_sign(lagna_sign, target_sign):
        return ((target_sign.value - lagna_sign.value) % 12) + 1

    graha_table = []
    
    # Add Lagna first
    lagna_nak_entry = next((n for n in ephe_service.nakshatras if n["name"] == lagna.nakshatra), None)
    lagna_nak_lord = vedic_helper.get_sanskrit_planet_name(lagna_nak_entry["ruler"]) if lagna_nak_entry else "N/A"
    lagna_sub_lord = "N/A"
    if lagna_nak_entry:
        lagna_sub_lord_planet = vedic_helper.get_sub_lord(
            lagna.longitude, lagna_nak_entry["ruler"],
            ephe_service=ephe_service,
            epsilon=1e-6
        )
        lagna_sub_lord = vedic_helper.get_sanskrit_planet_name(lagna_sub_lord_planet) if lagna_sub_lord_planet else "N/A"
    
    lagna_nak_name = lagna.nakshatra.name.replace('_', ' ').title() if lagna.nakshatra else "N/A"
    lagna_pada = lagna.nakshatra_pada if hasattr(lagna, 'nakshatra_pada') else 0
    
    lagna_row = {
        "Graha": "Lagna (Q)",
        "Longitude": format_longitude(lagna.longitude, lagna.sign),
        "Nakshatra (Pada)": f"{lagna_nak_name} {lagna_pada}",
        "Lord / Sub-Lord": f"{lagna_nak_lord}, {lagna_sub_lord}",
        "Ruler of": "1 Bhava",
        "Is In (Bhava)": "1 Bhava",
        "B. Owner": vedic_helper.get_sanskrit_planet_name(VedicAstrologyHelper.SIGN_LORDS[lagna.sign]) if lagna.sign in VedicAstrologyHelper.SIGN_LORDS else "N/A",
        "Relationship": "–",
        "Dignities": "–"
    }
    graha_table.append(lagna_row)

    # Add planets
    for planet in planets_data:
        # Get planet symbol and Sanskrit name
        symbol = vedic_helper.get_planet_symbol(planet.planet)
        sanskrit_name = vedic_helper.get_sanskrit_planet_name(planet.planet)
        
        # Add retrograde symbol if applicable
        retrograde_symbol = " ↺" if hasattr(planet, 'retrograde') and planet.retrograde else ""
        planet_display = f"{symbol} {sanskrit_name}{retrograde_symbol}"

        # Nakshatra (Pada) display
        nak_name = planet.nakshatra.name.replace('_', ' ').title() if planet.nakshatra else "N/A"
        pada = planet.nakshatra_pada if hasattr(planet, 'nakshatra_pada') else 0
        nakshatra_display = f"{nak_name} {pada}"
        
        # Lord / Sub-Lord (use Sanskrit names)
        nak_lord = vedic_helper.get_sanskrit_planet_name(planet.nakshatra_lord) if planet.nakshatra_lord else "N/A"
        sub_lord = vedic_helper.get_sanskrit_planet_name(planet.sub_lord) if planet.sub_lord else "N/A"
        lord_display = f"{nak_lord}, {sub_lord}"
        
        # Ruler of (houses ruled by this planet)
        ruled_houses = planet.ruler_of_houses if hasattr(planet, 'ruler_of_houses') else []

        # Special handling for Rahu/Ketu - use co-lord sign rulership (Aquarius/Scorpio)
        from models.astrology_models import Planet as PlanetEnum, Zodiac as ZodiacEnum
        if planet.planet in (PlanetEnum.RAHU, PlanetEnum.KETU):
            if planet.planet == PlanetEnum.RAHU:
                target_sign = ZodiacEnum.AQUARIUS
            else:
                target_sign = ZodiacEnum.SCORPIO

            ruled_houses = [house_from_sign(lagna.sign, target_sign)]
        
        if ruled_houses:
            ruler_of = ", ".join([f"{h}" for h in ruled_houses]) + " Bhava"
        else:
            ruler_of = "–"
        
        # Is In (Bhava)
        is_in = f"{planet.is_in_house} Bhava" if hasattr(planet, 'is_in_house') and planet.is_in_house else "–"
        
        # B. Owner (use Sanskrit name)
        sign_lord_name = vedic_helper.get_sanskrit_planet_name(planet.house_owner) if hasattr(planet, 'house_owner') and planet.house_owner else "N/A"
        
        # Relationship
        relationship = planet.relationship if hasattr(planet, 'relationship') else "Neutral"
        if planet.planet == PlanetEnum.RAHU:
            relationship = "Friend"
        elif planet.planet == PlanetEnum.KETU:
            relationship = "Neutral"
        if relationship == "Friend":
            relationship = "Friend's House"
        elif relationship == "Enemy":
            relationship = "Enemy's House"
        elif relationship == "Own House":
            relationship = "Own House"
        
        # Dignities
        dignities = planet.dignity if hasattr(planet, 'dignity') else "–"
        if dignities == "-" or not dignities:
            dignities = "–"

        graha_row = {
            "Graha": planet_display,
            "Longitude": format_longitude(planet.longitude, planet.sign),
            "Nakshatra (Pada)": nakshatra_display,
            "Lord / Sub-Lord": lord_display,
            "Ruler of": ruler_of,
            "Is In (Bhava)": is_in,
            "B. Owner": sign_lord_name,
            "Relationship": relationship,
            "Dignities": dignities,
        }
        graha_table.append(graha_row)

    lagna_sign_eng = vedic_helper.get_sign_name(lagna.sign)
    lagna_sign_sans = vedic_helper.get_sign_short_name(lagna.sign)

    return {
        "status": "success",
        "chart_type": "D5 (Quinamsha)",
        "description": d5_data.get("description", "Divisional chart for learning, intellect, education, and skills"),
        "lagna": {
            "longitude": format_longitude(lagna.longitude, lagna.sign),
            "sign": f"{lagna_sign_eng} ({lagna_sign_sans})",
            "degree_in_sign": lagna.degree,
        },
        "ayanamsa": d5_data['ayanamsa'],
        "graha_table": graha_table,
    }

"""
D40 Chart API Routes (Khavedamsha)
"""
import json
import os
from flask import request, jsonify, Response, Blueprint
from marshmallow import ValidationError

from models.astrology_models import UserDetails, Planet
from models.validation_schemas import UserDetailsSchema
from calculators.d40_chart_calculator import D40ChartCalculator
from utils.vedic_helper import VedicAstrologyHelper
from services.swiss_ephemeris_service import SwissEphemerisService

d40_routes = Blueprint('d40', __name__, url_prefix='/api')
user_schema = UserDetailsSchema()


def _format_refined_response(chart_data: dict, ephe_path: str) -> dict:
    helper = VedicAstrologyHelper()
    SwissEphemerisService(ephe_path=ephe_path)
    planets_data = chart_data['planets']

    def format_longitude_dms(longitude, sign):
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

    graha_table = []
    lagna = chart_data['lagna']
    lagna_lord_field = f"{helper.get_sanskrit_planet_name(lagna.nakshatra_lord)}, {helper.get_sanskrit_planet_name(lagna.sub_lord)}" if lagna.nakshatra_lord and lagna.sub_lord else "-"
    graha_table.append({
        "Graha": "Lagna",
        "Longitude": format_longitude_dms(lagna.longitude, lagna.sign),
        "Nakshatra": f"{lagna.nakshatra.name.replace('_', ' ').title()} {lagna.nakshatra_pada}",
        "Lord/Sub Lord": lagna_lord_field,
        "Ruler of": "1 Bhava",
        "Is In": helper.get_sanskrit_planet_name(chart_data['houses'][0].ruler_planet),
        "B. Owner": "-",
        "Relationship": "-",
        "Dignities": "-"
    })

    planet_order = [Planet.SUN, Planet.MOON, Planet.MARS, Planet.MERCURY, Planet.JUPITER, Planet.VENUS, Planet.SATURN, Planet.RAHU, Planet.KETU]
    for planet_enum in planet_order:
        planet_pos = next((p for p in planets_data if p.planet == planet_enum), None)
        if not planet_pos:
            continue
        symbol = helper.get_planet_symbol(planet_pos.planet)
        retrograde_symbol = "↺" if planet_pos.retrograde else ""
        nak_lord_name = helper.get_sanskrit_planet_name(planet_pos.nakshatra_lord) if planet_pos.nakshatra_lord else ""
        sub_lord_name = helper.get_sanskrit_planet_name(planet_pos.sub_lord) if planet_pos.sub_lord else ""
        lord_sub_lord = f"{nak_lord_name}, {sub_lord_name}" if nak_lord_name and sub_lord_name else "-"
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
        graha_table.append({
            "Graha": f"{symbol}{planet_pos.planet.name.title()}{retrograde_symbol}",
            "Longitude": format_longitude_dms(planet_pos.longitude, planet_pos.sign),
            "Nakshatra": f"{planet_pos.nakshatra.name.replace('_', ' ').title()} {planet_pos.nakshatra_pada}",
            "Lord/Sub Lord": lord_sub_lord,
            "Ruler of": format_bhava_list(planet_pos.ruler_of_houses) if planet_pos.ruler_of_houses else "-",
            "Is In": format_bhava_value(planet_pos.is_in_house) if planet_pos.is_in_house else "-",
            "B. Owner": helper.get_sanskrit_planet_name(planet_pos.house_owner) if planet_pos.house_owner else "-",
            "Relationship": rel_word,
            "Dignities": planet_pos.dignity if planet_pos.dignity else "-"
        })

    return {
        "chart_type": chart_data['chart_type'],
        "description": chart_data['description'],
        "data": graha_table,
        "ayanamsa": chart_data['ayanamsa']
    }


@d40_routes.route('/v1/d40-chart-refined', methods=['POST'])
def calculate_d40_chart_refined():
    try:
        json_data = request.get_json()
        if not json_data:
            return jsonify({"error": "No JSON data provided", "status": "error"}), 400

        sidereal_mode = json_data.pop('sidereal_mode', None)
        d40_longitude_offset = json_data.pop('d40_longitude_offset', None)
        d40_lagna_offset = json_data.pop('d40_lagna_offset', None)

        try:
            validated_data = user_schema.load(json_data)
        except ValidationError as err:
            return jsonify({"error": "Validation failed", "details": err.messages, "status": "error"}), 400

        user_details = UserDetails(**validated_data)
        ephe_path = os.getenv('EPHEMERIS_PATH', './ephe')
        node_rulership = os.getenv('NODE_RULERSHIP_STRATEGY', 'co_signs')
        nakshatra_eps = float(os.getenv('NAKSHATRA_EPSILON', 1e-6))
        ayanamsa_offset = float(os.getenv('AYANAMSA_OFFSET', '-0.245877'))
        default_d40_longitude_offset = float(os.getenv('D40_LONGITUDE_OFFSET', '-0.269'))
        default_d40_lagna_offset = float(os.getenv('D40_LAGNA_OFFSET', '-0.889'))
        if sidereal_mode is None:
            sidereal_mode = os.getenv('SIDEREAL_MODE', None)

        d40_calculator = D40ChartCalculator(
            ephe_path=ephe_path,
            node_rulership_strategy=node_rulership,
            nakshatra_epsilon=nakshatra_eps,
            sidereal_mode=sidereal_mode,
            ayanamsa_offset=ayanamsa_offset,
            d40_longitude_offset=float(d40_longitude_offset) if d40_longitude_offset is not None else default_d40_longitude_offset,
            d40_lagna_offset=float(d40_lagna_offset) if d40_lagna_offset is not None else default_d40_lagna_offset
        )
        d40_data = d40_calculator.calculate_d40_chart(user_details)
        response = _format_refined_response(d40_data, ephe_path)
        return Response(json.dumps(response, ensure_ascii=False), mimetype='application/json')
    except Exception as e:
        return jsonify({"error": str(e), "status": "error"}), 500

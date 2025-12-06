"""
D1 Chart Routes
All D1 (Rashi/Birth chart) related endpoints
"""
from flask import Blueprint, request, jsonify, Response
from marshmallow import ValidationError
import traceback
import json

from models.astrology_models import UserDetails, Planet
from models.validation_schemas import UserDetailsSchema
from calculators.d1_chart_calculator import D1ChartCalculator
from utils.vedic_helper import VedicAstrologyHelper

# Create blueprint
d1_bp = Blueprint('d1', __name__, url_prefix='/api/v1')

# Initialize
user_schema = UserDetailsSchema()
calculator = D1ChartCalculator(ephe_path="./ephe")


@d1_bp.route('/d1-chart', methods=['POST'])
def calculate_d1_chart():
    """
    Calculate complete D1 chart with all details
    
    Request body:
    {
        "name": "string (required)",
        "datetime": "string (required) ISO format YYYY-MM-DDTHH:MM:SS",
        "latitude": "float (required) -90 to 90",
        "longitude": "float (required) -180 to 180",
        "timezone": "float (required) hours offset",
        "place": "string (required)",
        "religion": "string (optional)"
    }
    """
    try:
        json_data = request.get_json()
        if not json_data:
            return jsonify({
                "error": "No JSON data provided",
                "status": "error"
            }), 400
        
        try:
            validated_data = user_schema.load(json_data)
        except ValidationError as err:
            return jsonify({
                "error": "Validation failed",
                "details": err.messages,
                "status": "error"
            }), 400
        
        user_details = UserDetails(**validated_data)
        d1_chart = calculator.calculate_d1_chart(user_details)
        response = _format_full_chart_response(d1_chart)
        
        return Response(
            json.dumps(response, ensure_ascii=False),
            mimetype='application/json'
        )
        
    except Exception as e:
        return jsonify({
            "error": "Internal server error during chart calculation",
            "message": str(e),
            "status": "error"
        }), 500


@d1_bp.route('/d1-chart-refined', methods=['POST'])
def calculate_d1_chart_refined():
    """
    Calculate D1 chart - simplified response with grahas only
    
    Returns only essential graha data: Graha, Longitude, Nakshatra, Lord/Sub Lord,
    Ruler of, Is In, B. Owner, Relationship, Dignities
    """
    try:
        json_data = request.get_json()
        if not json_data:
            return jsonify({
                "error": "No JSON data provided",
                "status": "error"
            }), 400
        
        try:
            validated_data = user_schema.load(json_data)
        except ValidationError as err:
            return jsonify({
                "error": "Validation failed",
                "details": err.messages,
                "status": "error"
            }), 400
        
        user_details = UserDetails(**validated_data)
        d1_chart = calculator.calculate_d1_chart(user_details)
        response = _format_refined_chart_response(d1_chart)
        
        return Response(
            json.dumps(response, ensure_ascii=False),
            mimetype='application/json'
        )
        
    except Exception as e:
        return jsonify({
            "error": "Internal server error during chart calculation",
            "message": str(e),
            "status": "error"
        }), 500


def _format_refined_chart_response(d1_chart):
    """Format D1 chart for refined endpoint"""
    from services.swiss_ephemeris_service import SwissEphemerisService
    helper = VedicAstrologyHelper()
    ephe_service = SwissEphemerisService(ephe_path="./ephe")
    
    def format_longitude_dms(longitude, sign):
        degree_in_sign = longitude % 30
        degrees = int(degree_in_sign)
        minutes = int((degree_in_sign - degrees) * 60)
        seconds = int(((degree_in_sign - degrees) * 60 - minutes) * 60)
        sign_short = helper.get_sign_short_name(sign)
        return f"{degrees:02d}° {sign_short} {minutes:02d}′ {seconds:02d}″"

    graha_table = []

    # Add Lagna first
    lagna_nak_entry = next((n for n in ephe_service.nakshatras if n["name"] == d1_chart.lagna.nakshatra), None)
    lagna_nak_lord = lagna_nak_entry["ruler"] if lagna_nak_entry else d1_chart.houses[0].ruler_planet
    lagna_sub_lord = helper.get_sub_lord(d1_chart.lagna.longitude, lagna_nak_lord)
    lagna_lord_field = f"{helper.get_sanskrit_planet_name(lagna_nak_lord)}, {helper.get_sanskrit_planet_name(lagna_sub_lord)}"

    graha_dict = {}
    graha_dict["Graha"] = "Lagna"
    graha_dict["Longitude"] = format_longitude_dms(d1_chart.lagna.longitude, d1_chart.lagna.sign)
    graha_dict["Nakshatra"] = f"{d1_chart.lagna.nakshatra.name.replace('_', ' ').title()} {d1_chart.lagna.nakshatra_pada}"
    graha_dict["Lord/Sub Lord"] = lagna_lord_field
    graha_dict["Ruler of"] = "-"
    graha_dict["Is In"] = 1
    graha_dict["B. Owner"] = d1_chart.houses[0].ruler_planet.name
    graha_dict["Relationship"] = "-"
    graha_dict["Dignities"] = "-"
    graha_table.append(graha_dict)

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
        "status": "success",
        "data": {
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
            "Sunshine and Moonshine": {
                "Sun Sign": f"{d1_chart.sun_moon_shine.sun_sign} ({d1_chart.sun_moon_shine.sun_sign_sanskrit} Rashi)",
                "Moon Sign": f"{d1_chart.sun_moon_shine.moon_sign} ({d1_chart.sun_moon_shine.moon_sign_sanskrit} Rashi)",
                "Sunrise": d1_chart.sun_moon_shine.sunrise_time,
                "Sunset": d1_chart.sun_moon_shine.sunset_time,
                "Moonrise": d1_chart.sun_moon_shine.moonrise_time,
                "Moonset": d1_chart.sun_moon_shine.moonset_time,
                "Sun Strength": f"{d1_chart.sun_moon_shine.sun_strength:.2f}%",
                "Moon Strength": f"{d1_chart.sun_moon_shine.moon_strength:.2f}%",
                "Moon Phase": d1_chart.sun_moon_shine.moon_phase,
                "Tithi": d1_chart.sun_moon_shine.tithi
            },
            "ayanamsa": round(d1_chart.ayanamsa, 6)
        }
    }


def _format_full_chart_response(d1_chart):
    """Format D1 chart for full endpoint"""
    from services.swiss_ephemeris_service import SwissEphemerisService
    helper = VedicAstrologyHelper()
    
    def format_longitude_dms(longitude, sign):
        degree_in_sign = longitude % 30
        degrees = int(degree_in_sign)
        minutes = int((degree_in_sign - degrees) * 60)
        seconds = int(((degree_in_sign - degrees) * 60 - minutes) * 60)
        sign_short = helper.get_sign_short_name(sign)
        return f"{degrees:02d}° {sign_short} {minutes:02d}′ {seconds:02d}″"
    
    def format_planet(planet_pos):
        symbol = helper.get_planet_symbol(planet_pos.planet)
        retrograde_symbol = " ↺" if planet_pos.retrograde else ""
        
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
    
    # Format Lagna
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
        "status": "success",
        "data": {
            "lagna": lagna_data,
            "grahas": [format_planet(p) for p in d1_chart.planets],
            "bhavas": [format_house(h) for h in d1_chart.houses],
            "ayanamsa": round(d1_chart.ayanamsa, 6)
        }
    }

"""
Dasha Routes
Mahadasha and Antardasha period calculations using Vimshottari dasha system
"""
import os
from datetime import datetime
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from models.astrology_models import UserDetails, Planet
from models.validation_schemas import UserDetailsSchema
from calculators.dasha_calculator import DashaCalculator
from calculators.d1_chart_calculator import D1ChartCalculator
from utils.dasha_helper import NumerologyHelper, DashaAnalysisHelper

# Create blueprint
dasha_bp = Blueprint('dasha', __name__, url_prefix='/api/v1')

# Initialize schema
user_schema = UserDetailsSchema()


@dasha_bp.route('/dasha', methods=['POST'])
def get_dasha():
    """
    Unified Dasha endpoint - Get Mahadasha and Antardasha periods
    
    Flexible request supporting multiple time formats:
    
    Option 1 - Single Year:
    {
        "name": "string",
        "datetime": "YYYY-MM-DDTHH:MM:SS",
        "latitude": float,
        "longitude": float,
        "timezone": float,
        "place": "string",
        "year": 2024
    }
    
    Option 2 - Date Range:
    {
        "name": "string",
        "datetime": "YYYY-MM-DDTHH:MM:SS",
        "latitude": float,
        "longitude": float,
        "timezone": float,
        "place": "string",
        "start_date": "2024-01-01",
        "end_date": "2024-12-31"
    }
    
    Option 3 - Specific Month:
    {
        "name": "string",
        "datetime": "YYYY-MM-DDTHH:MM:SS",
        "latitude": float,
        "longitude": float,
        "timezone": float,
        "place": "string",
        "year": 2024,
        "month": 3
    }
    
    Option 4 - Specific Day:
    {
        "name": "string",
        "datetime": "YYYY-MM-DDTHH:MM:SS",
        "latitude": float,
        "longitude": float,
        "timezone": float,
        "place": "string",
        "date": "2024-03-15"
    }
    
    Returns:
    {
        "status": "success",
        "user": { ... },
        "query_type": "year|month|day|range",
        "range": { "start": "...", "end": "..." },
        "active_mahadasha": "Planet Name",
        "active_antardasha": "Planet Name",
        "dasha_periods": [ ... ]
    }
    """
    try:
        # Get raw data
        user_data = request.get_json()
        
        if not user_data:
            return jsonify({
                "status": "error",
                "message": "Request body is required"
            }), 400
        
        # Determine query type and calculate dates
        query_type = None
        start_date = None
        end_date = None
        
        # Option 1: Single year (full year)
        if 'year' in user_data and 'month' not in user_data and 'date' not in user_data and 'start_date' not in user_data:
            try:
                year = int(user_data['year'])
                start_date = f"{year}-01-01"
                end_date = f"{year}-12-31"
                query_type = "year"
            except (ValueError, TypeError):
                return jsonify({
                    "status": "error",
                    "message": "Invalid year format. Must be integer (e.g., 2024)"
                }), 400
        
        # Option 2: Year + Month
        elif 'year' in user_data and 'month' in user_data and 'date' not in user_data and 'start_date' not in user_data:
            try:
                year = int(user_data['year'])
                month = int(user_data['month'])
                if month < 1 or month > 12:
                    raise ValueError("Month must be 1-12")
                
                # Calculate start and end of month
                start_date = f"{year}-{month:02d}-01"
                if month == 12:
                    end_date = f"{year}-12-31"
                else:
                    from datetime import datetime, timedelta
                    first_of_next = datetime(year, month + 1, 1)
                    last_of_month = first_of_next - timedelta(days=1)
                    end_date = last_of_month.strftime("%Y-%m-%d")
                
                query_type = "month"
            except (ValueError, TypeError) as e:
                return jsonify({
                    "status": "error",
                    "message": f"Invalid year/month format: {str(e)}"
                }), 400
        
        # Option 3: Single date (full day)
        elif 'date' in user_data and 'year' not in user_data and 'start_date' not in user_data:
            date_str = user_data['date']
            start_date = date_str
            end_date = date_str
            query_type = "day"
        
        # Option 4: Date range
        elif 'start_date' in user_data and 'end_date' in user_data:
            start_date = user_data['start_date']
            end_date = user_data['end_date']
            query_type = "range"
        
        else:
            return jsonify({
                "status": "error",
                "message": "Provide one of: 'year', 'year+month', 'date', or 'start_date+end_date'"
            }), 400
        
        # Remove time-related fields before schema validation
        user_data_copy = {
            k: v for k, v in user_data.items() 
            if k not in ['year', 'month', 'date', 'start_date', 'end_date']
        }
        
        # Validate input with schema
        validated_data = user_schema.load(user_data_copy)
        
        # Convert dict to UserDetails object
        user_details = UserDetails(**validated_data)
        
        # Initialize calculator
        ephe_path = os.getenv('EPHEMERIS_PATH', './ephe')
        sidereal_mode = user_data.get('sidereal_mode')
        if sidereal_mode is None:
            sidereal_mode = os.getenv('SIDEREAL_MODE', None)
        
        calculator = DashaCalculator(
            ephe_path=ephe_path,
            sidereal_mode=sidereal_mode
        )
        
        # Get Moon info using D1 chart
        d1_calculator = D1ChartCalculator(ephe_path=ephe_path, sidereal_mode=sidereal_mode)
        d1_chart = d1_calculator.calculate_d1_chart(user_details)
        moon_planet = next((p for p in d1_chart.planets if p.planet == Planet.MOON), None)
        moon_nakshatra = moon_planet.nakshatra.name.replace("_", " ").title() if moon_planet else "-"
        moon_pada = moon_planet.nakshatra_pada if moon_planet else "-"
        
        # Calculate dasha for date range
        dasha_data = calculator.get_dasha_for_date_range(user_details, start_date, end_date)
        
        # Format dasha periods - convert Planet enums to strings
        formatted_periods = []
        for period in dasha_data["dasha_periods"]:
            formatted_period = {
                "level": period.get("level", "-"),
                "planet": period.get("planet_name", "-"),
                "start_date": period.get("start_date", "-"),
                "end_date": period.get("end_date", "-"),
                "duration_years": period.get("duration_years", 0),
                "duration_days": period.get("duration_days", 0)
            }
            # Add mahadasha_planet if it's an Antardasha
            if period.get("level") == "Antardasha":
                formatted_period["mahadasha_planet"] = period.get("mahadasha_planet_name", "-")
            formatted_periods.append(formatted_period)
        
        # Calculate numerology
        try:
            birth_date_only = user_details.datetime.split("T")[0]  # YYYY-MM-DD
            day_of_birth = int(birth_date_only.split("-")[2])
            
            name_number = NumerologyHelper.calculate_number(user_details.name)
            destiny_number = NumerologyHelper.calculate_destiny_number(birth_date_only)
            basic_number = NumerologyHelper.calculate_basic_number(day_of_birth)
        except Exception:
            name_number = destiny_number = basic_number = None
        
        # Get detailed current dasha analysis
        dasha_analysis = DashaAnalysisHelper.get_current_dasha_details(
            user_details.datetime,
            formatted_periods
        )
        
        # Find active mahadasha and antardasha at range start
        def _parse_date(dt_str: str):
            if not dt_str:
                return None
            # Normalize 'Z' suffix and missing time parts
            cleaned = dt_str.replace("Z", "")
            try:
                return datetime.fromisoformat(cleaned)
            except Exception:
                try:
                    return datetime.fromisoformat(cleaned + "T00:00:00")
                except Exception:
                    return None

        query_start_dt = _parse_date(start_date)
        active_maha = None
        active_antar = None

        for period in formatted_periods:
            p_start = _parse_date(period.get("start_date", ""))
            p_end = _parse_date(period.get("end_date", ""))
            if not p_start or not p_end or not query_start_dt:
                continue

            if period["level"] == "Mahadasha" and p_start <= query_start_dt <= p_end:
                active_maha = period["planet"]
            elif period["level"] == "Antardasha" and p_start <= query_start_dt <= p_end:
                active_antar = period["planet"]

        # Fallback to current analysis if nothing matched (e.g., parsing issues)
        if active_maha is None and dasha_analysis.get("current_mahadasha"):
            active_maha = dasha_analysis["current_mahadasha"].get("planet")
        if active_antar is None and dasha_analysis.get("current_antardasha"):
            active_antar = dasha_analysis["current_antardasha"].get("planet")
        
        # Build detailed analysis section
        analysis = {
            "numerology": {
                "name_number": name_number,
                "destiny_number": destiny_number,
                "basic_number": basic_number
            }
        }
        
        # Add current period details if available
        if dasha_analysis["current_mahadasha_progress"]:
            maha_prog = dasha_analysis["current_mahadasha_progress"]
            maha_planet = dasha_analysis["current_mahadasha"]["planet"]
            analysis["current_mahadasha"] = {
                "lord": maha_planet,
                "number": dasha_analysis["current_mahadasha"].get("duration_years", 0),
                "period": f"{maha_prog['start_date']} – {maha_prog['end_date']}",
                "progress": f"{int(maha_prog['elapsed_years'])}/{int(maha_prog['total_years'])} years",
                "percentage": maha_prog['percentage']
            }
        
        if dasha_analysis["current_antardasha_progress"]:
            antar_prog = dasha_analysis["current_antardasha_progress"]
            antar_planet = dasha_analysis["current_antardasha"]["planet"]
            analysis["current_antardasha"] = {
                "lord": antar_planet,
                "number": dasha_analysis["current_antardasha"].get("duration_years", 0),
                "period": f"{antar_prog['start_date']} – {antar_prog['end_date']}",
                "duration_days": antar_prog['duration_days'],
                "progress": f"{antar_prog['elapsed_days']}/{antar_prog['duration_days']} days",
                "percentage": antar_prog['percentage']
            }
        
        if dasha_analysis["pratantardasha"]:
            prat = dasha_analysis["pratantardasha"]
            analysis["pratantardasha"] = {
                "starting_lord": prat["starting_lord"],
                "current_lord": prat["current_lord"],
                "started": prat["started"],
                "expected_end": prat["expected_end"],
                "duration_days": prat["duration_days"]
            }
        
        # Format response
        return jsonify({
            "status": "success",
            "query_type": query_type,
            "range": {
                "start": start_date,
                "end": end_date
            },
            "user": {
                "name": user_details.name,
                "birth_date": user_details.datetime,
                "moon_nakshatra": moon_nakshatra,
                "moon_pada": moon_pada
            },
            "analysis": analysis,
            "active_mahadasha": active_maha,
            "active_antardasha": active_antar,
            "dasha_periods": formatted_periods
        }), 200
        
    except ValidationError as e:
        return jsonify({
            "status": "error",
            "message": "Validation failed",
            "errors": e.messages
        }), 400
    except ValueError as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Server error: {str(e)}"
        }), 500

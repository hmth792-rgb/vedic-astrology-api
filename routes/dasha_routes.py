"""
Dasha Routes
Mahadasha and Antardasha period calculations using Vimshottari dasha system
"""
import os
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from models.astrology_models import UserDetails, Planet
from models.validation_schemas import UserDetailsSchema
from calculators.dasha_calculator import DashaCalculator
from calculators.d1_chart_calculator import D1ChartCalculator

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
        
        # Find active mahadasha and antardasha for the period
        active_maha = None
        active_antar = None
        
        for period in formatted_periods:
            if period["level"] == "Mahadasha":
                active_maha = period["planet"]
            elif period["level"] == "Antardasha" and active_antar is None:
                active_antar = period["planet"]
        
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

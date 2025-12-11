"""
Vedic Astrology Chart API - Application Entry Point

Main Flask application with D9 (Navamsha) chart calculation
using Swiss Ephemeris and Vedic astrology principles
"""
import os
from pathlib import Path
from flask import Flask, jsonify

# Load environment variables from .env file
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(env_path)
    except ImportError:
        # dotenv not available, continue without it
        pass

# Add project root to Python path
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import route blueprints
from routes import d1_bp, d9_bp, dasha_bp, transit_bp

# Initialize Flask app
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Register blueprints
app.register_blueprint(d1_bp)
app.register_blueprint(d9_bp)
app.register_blueprint(dasha_bp)
app.register_blueprint(transit_bp)


@app.route('/')
def home():
    """API welcome endpoint"""
    return jsonify({
        "message": "Welcome to Vedic Astrology Chart API",
        "version": "3.0.0",
        "description": "Calculate D1 and D9 divisional charts, Mahadasha/Antardasha periods, and Planetary Transits using Swiss Ephemeris and Vedic astrology",
        "charts_available": ["D1 (Rashi) - Birth Chart", "D9 (Navamsha) - Marriage & Relationships", "Dasha Periods - Mahadasha & Antardasha", "Planetary Transits - Current positions through houses"],
        "endpoints": {
            "D1 Refined": "/api/v1/d1-chart-refined (POST)",
            "D9 Refined": "/api/v1/d9-chart-refined (POST)",
            "Dasha (Unified)": "/api/v1/dasha (POST) - year, month, day, or date range",
            "All Transits": "/api/v1/transits (POST) - Current positions of all major planets",
            "Major Transits": "/api/v1/transits/major (POST) - Saturn, Jupiter, Mercury only",
            "Health": "/health (GET)",
            "Documentation": "/docs (GET)"
        }
    })


@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Vedic Astrology Chart API",
        "ephemeris": "Swiss Ephemeris",
        "version": "3.0.0"
    })


@app.route('/docs')
def api_documentation():
    """API documentation endpoint"""
    return jsonify({
        "title": "Vedic Astrology Chart API Documentation",
        "version": "3.0.0",
        "description": "API for calculating D1 (Rashi) and D9 (Navamsha) divisional charts using Swiss Ephemeris",
        "request_format": {
            "name": "string (required) - Full name",
            "datetime": "string (required) - Birth date and time in ISO format (YYYY-MM-DDTHH:MM:SS)",
            "latitude": "float (required) - Birth latitude (-90 to 90)",
            "longitude": "float (required) - Birth longitude (-180 to 180)",
            "timezone": "float (required) - Timezone offset in hours (e.g., 5.5 for IST, -5 for EST)",
            "place": "string (required) - Birth place name",
            "religion": "string (optional) - Religion",
            "sidereal_mode": "string (optional) - Ayanamsa mode (LAHIRI, RAMAN, KRISHNAMURTI)"
        },
        "endpoints": {
            "D1 Chart Refined": {
                "path": "/api/v1/d1-chart-refined",
                "method": "POST",
                "description": "Calculate D1 (Rashi) birth chart with essential graha data only",
                "response": "Simplified format: Graha, Longitude, Nakshatra, Lord/Sub Lord, Ruler of, Is In, B. Owner, Relationship, Dignities"
            },
            "D9 Chart Refined": {
                "path": "/api/v1/d9-chart-refined",
                "method": "POST",
                "description": "Calculate D9 (Navamsha) chart with essential graha data only",
                "response": "Simplified format: Graha, Longitude, Nakshatra, Lord/Sub Lord, Ruler of, Is In, B. Owner, Relationship, Dignities"
            }
        },
        "example_request": {
            "name": "John Doe",
            "datetime": "1990-01-15T10:30:00",
            "latitude": 28.7041,
            "longitude": 77.1025,
            "timezone": 5.5,
            "place": "New Delhi"
        }
    })


if __name__ == '__main__':
    # Load config from environment
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    host = os.getenv('FLASK_HOST', '127.0.0.1')
    port = int(os.getenv('FLASK_PORT', 5000))
    
    app.run(debug=debug, host=host, port=port)

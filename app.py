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
from routes import d1_bp, d2_bp, d3_bp, d4_bp, d5_bp, d6_bp, d7_bp, d8_bp, d9_bp, d10_bp, d11_bp, d12_bp, d16_bp, dasha_bp, transit_bp
from routes.d20_routes import d20_routes
from routes.d24_routes import d24_routes
from routes.d27_routes import d27_routes
from routes.d30_routes import d30_routes
from routes.d40_routes import d40_routes
from routes.d45_routes import d45_routes
from routes.d60_routes import d60_routes

# Initialize Flask app
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Register blueprints
app.register_blueprint(d1_bp)
app.register_blueprint(d2_bp)
app.register_blueprint(d3_bp)
app.register_blueprint(d4_bp)
app.register_blueprint(d5_bp)
app.register_blueprint(d6_bp)
app.register_blueprint(d7_bp)
app.register_blueprint(d8_bp)
app.register_blueprint(d9_bp)
app.register_blueprint(d10_bp)
app.register_blueprint(d11_bp)
app.register_blueprint(d12_bp)
app.register_blueprint(d16_bp)
app.register_blueprint(d20_routes)
app.register_blueprint(d24_routes)
app.register_blueprint(d27_routes)
app.register_blueprint(d30_routes)
app.register_blueprint(d40_routes)
app.register_blueprint(d45_routes)
app.register_blueprint(d60_routes)
app.register_blueprint(dasha_bp)
app.register_blueprint(transit_bp)


@app.route('/')
def home():
    """API welcome endpoint"""
    return jsonify({
        "message": "Welcome to Vedic Astrology Chart API",
        "version": "3.0.0",
        "description": "Calculate D1, D2, D3, D4, D5, D6, D7, D8, D9, and D10 divisional charts, Mahadasha/Antardasha periods, and Planetary Transits using Swiss Ephemeris and Vedic astrology",
        "charts_available": [
            "D1 (Rashi) - Birth Chart",
            "D2 (Hora) - Wealth & Fortune",
            "D3 (Drekkana) - Siblings & Courage",
            "D4 (Chaturthamsa) - Property & Fixed Assets",
            "D5 (Quinamsha) - Intellect & Skills",
            "D6 (Shashtamsha) - Health & Enemies",
            "D7 (Saptamsha) - Children & Creativity",
            "D8 (Ashtamsa) - Longevity & Obstacles",
            "D9 (Navamsha) - Marriage & Relationships",
            "D10 (Dasamsa) - Career & Profession",
            "D20 (Vimshamsha) - Spiritual Progress",
            "D24 (Chaturvimshamsha) - Education & Learning",
            "D27 (Bhamsa) - Strengths & Weaknesses",
            "D30 (Trimsamsha) - Misfortune & Suffering",
            "D40 (Khavedamsha) - Maternal Lineage & Subtle Fortune",
            "D45 (Akshavedamsha) - Character & Spiritual Merit",
            "D60 (Shashtiamsha) - Past-Life Karma",
            "Dasha Periods - Mahadasha & Antardasha",
            "Planetary Transits - Current positions through houses"
        ],
        "endpoints": {
            "D1 Refined": "/api/v1/d1-chart-refined (POST)",
            "D2 Refined": "/api/v1/d2-chart-refined (POST)",
            "D3 Refined": "/api/v1/d3-chart-refined (POST)",
            "D4 Refined": "/api/v1/d4-chart-refined (POST)",
            "D5 Refined": "/api/v1/d5-chart-refined (POST)",
            "D6 Refined": "/api/v1/d6-chart-refined (POST)",
            "D7 Refined": "/api/v1/d7-chart-refined (POST)",
            "D8 Refined": "/api/v1/d8-chart-refined (POST)",
            "D9 Refined": "/api/v1/d9-chart-refined (POST)",
            "D10 Refined": "/api/v1/d10-chart-refined (POST)",
            "D20 Refined": "/api/v1/d20-chart-refined (POST)",
            "D24 Refined": "/api/v1/d24-chart-refined (POST)",
            "D27 Refined": "/api/v1/d27-chart-refined (POST)",
            "D30 Refined": "/api/v1/d30-chart-refined (POST)",
            "D40 Refined": "/api/v1/d40-chart-refined (POST)",
            "D45 Refined": "/api/v1/d45-chart-refined (POST)",
            "D60 Refined": "/api/v1/d60-chart-refined (POST)",
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
        "description": "API for calculating D1 through D60 selected divisional charts using Swiss Ephemeris",
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
            "D2 Chart Refined": {
                "path": "/api/v1/d2-chart-refined",
                "method": "POST",
                "description": "Calculate D2 (Hora) chart for wealth, fortune, and material prosperity with essential graha data only",
                "response": "Simplified format: Graha, Longitude, Nakshatra, Lord/Sub Lord, Ruler of, Is In, B. Owner, Relationship, Dignities"
            },
            "D3 Chart Refined": {
                "path": "/api/v1/d3-chart-refined",
                "method": "POST",
                "description": "Calculate D3 (Drekkana) chart for siblings, courage, and communication with essential graha data only",
                "response": "Simplified format: Graha, Longitude, Nakshatra, Lord/Sub Lord, Ruler of, Is In, B. Owner, Relationship, Dignities"
            },
            "D9 Chart Refined": {
                "path": "/api/v1/d9-chart-refined",
                "method": "POST",
                "description": "Calculate D9 (Navamsha) chart with essential graha data only",
                "response": "Simplified format: Graha, Longitude, Nakshatra, Lord/Sub Lord, Ruler of, Is In, B. Owner, Relationship, Dignities"
            },
            "D8 Chart Refined": {
                "path": "/api/v1/d8-chart-refined",
                "method": "POST",
                "description": "Calculate D8 (Ashtamsa) chart for longevity, obstacles, and misfortunes",
                "response": "Simplified format: Graha, Longitude, Nakshatra, Lord/Sub Lord, Ruler of, Is In, B. Owner, Relationship, Dignities"
            },
            "D10 Chart Refined": {
                "path": "/api/v1/d10-chart-refined",
                "method": "POST",
                "description": "Calculate D10 (Dasamsa) chart for career, profession, and status",
                "response": "Simplified format: Graha, Longitude, Nakshatra, Lord/Sub Lord, Ruler of, Is In, B. Owner, Relationship, Dignities"
            },
            "D4 Chart Refined": {
                "path": "/api/v1/d4-chart-refined",
                "method": "POST",
                "description": "Calculate D4 (Chaturthamsa) chart for property, fixed assets, and material foundations",
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

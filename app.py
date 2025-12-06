"""
Astrology API - Main Application
Professional API for generating divisional charts using Swiss Ephemeris
Supports D1 (Rashi), D9 (Navamsha), and more charts
"""
from flask import Flask, jsonify
import os
import sys

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import route blueprints
from routes import d1_bp, d9_bp

# Initialize Flask app
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Register blueprints
app.register_blueprint(d1_bp)
app.register_blueprint(d9_bp)


@app.route('/')
def home():
    """API welcome endpoint"""
    return jsonify({
        "message": "Welcome to Vedic Astrology Chart API",
        "version": "2.0.0",
        "description": "Calculate divisional charts using Swiss Ephemeris and Vedic astrology",
        "charts_available": {
            "D1": "Rashi Chart (Birth Chart)",
            "D9": "Navamsha Chart (Marriage & Relationships)"
        },
        "endpoints": {
            "D1": {
                "full": "/api/v1/d1-chart (POST)",
                "refined": "/api/v1/d1-chart-refined (POST)"
            },
            "D9": {
                "full": "/api/v1/d9-chart (POST)",
                "refined": "/api/v1/d9-chart-refined (POST)"
            },
            "health": "/health (GET)",
            "docs": "/docs (GET)"
        }
    })


@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Vedic Astrology Chart API",
        "ephemeris": "Swiss Ephemeris",
        "version": "2.0.0"
    })


@app.route('/docs')
def api_documentation():
    """API documentation endpoint"""
    return jsonify({
        "title": "Vedic Astrology Chart API Documentation",
        "version": "2.0.0",
        "description": "Complete API for calculating divisional charts using Swiss Ephemeris",
        "request_format": {
            "name": "string (required) - Full name",
            "datetime": "string (required) - Birth date and time in ISO format (YYYY-MM-DDTHH:MM:SS)",
            "latitude": "float (required) - Birth latitude (-90 to 90)",
            "longitude": "float (required) - Birth longitude (-180 to 180)",
            "timezone": "float (required) - Timezone offset in hours (e.g., 5.5 for IST, -5 for EST)",
            "place": "string (required) - Birth place name",
            "religion": "string (optional) - Religion"
        },
        "endpoints": {
            "D1 Chart (Rashi)": {
                "path": "/api/v1/d1-chart",
                "method": "POST",
                "description": "Calculate complete D1 chart with all astronomical and Vedic data",
                "response": "Full chart with lagna, planets, houses, nakshatras"
            },
            "D1 Chart Refined": {
                "path": "/api/v1/d1-chart-refined",
                "method": "POST",
                "description": "Calculate D1 chart with essential graha data only",
                "response": "Simplified format: Graha, Longitude, Nakshatra, Lord/Sub Lord, Ruler of, Is In, B. Owner, Relationship, Dignities"
            },
            "D9 Chart (Navamsha)": {
                "path": "/api/v1/d9-chart",
                "method": "POST",
                "description": "Calculate complete D9 chart (divisional chart for marriage & relationships)",
                "response": "Full D9 chart with converted planetary positions"
            },
            "D9 Chart Refined": {
                "path": "/api/v1/d9-chart-refined",
                "method": "POST",
                "description": "Calculate D9 chart with essential graha data only",
                "response": "Simplified D9 format with same fields as D1 refined"
            }
        }
    })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

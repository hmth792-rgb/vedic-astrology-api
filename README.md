# Astrology D1 Chart API

A professional Python Flask API for generating complete D1 (Rashi) charts using Swiss Ephemeris. This API calculates accurate astronomical data including planetary positions, houses, nakshatras, and sun/moon shine values.

## ✨ Features

- **Complete D1 Chart Calculation**: Full Rashi chart with all planetary positions
- **Swiss Ephemeris Integration**: High-precision astronomical calculations
- **Comprehensive Data**: Planetary positions, houses, nakshatras, lagna
- **Sun/Moon Shine**: Sunrise, sunset, moon phases, and tithi calculations
- **Professional API**: RESTful endpoints with proper validation
- **Modular Architecture**: Clean, reusable, and extensible code structure
- **Input Validation**: Robust validation using Marshmallow schemas
- **Error Handling**: Comprehensive error handling and logging

## 🏗️ Project Structure

```
Python/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── README.md                      # This file
├── .deployment                    # Azure deployment config
│
├── models/                        # Data models and schemas
│   ├── __init__.py
│   ├── astrology_models.py        # Core astrology data models
│   └── validation_schemas.py      # Input validation schemas
│
├── services/                      # Business logic layer
│   ├── __init__.py
│   └── swiss_ephemeris_service.py # Swiss Ephemeris integration
│
├── calculators/                   # Chart calculation engines
│   ├── __init__.py
│   └── d1_chart_calculator.py     # Main D1 chart calculator
│
└── ephe/                          # Swiss Ephemeris data files
    └── README.md                  # Instructions for ephemeris files
```

## 🚀 Installation & Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set up Swiss Ephemeris Data

The API requires Swiss Ephemeris data files for accurate calculations:

1. Download ephemeris files from: https://www.astro.com/ftp/swisseph/ephe/
2. Place files in the `ephe/` directory
3. Minimum required: `semo_18.se1` (covers 1800-2399)

**Quick setup option:**
```python
import swisseph as swe
swe.set_ephe_path('./ephe')  # Auto-downloads needed files
```

### 3. Run the API

```bash
python app.py
```

The API will be available at `http://localhost:5000`

## 📡 API Endpoints

### 🏠 Home - `GET /`
Welcome message and API overview

### 💊 Health Check - `GET /health`
Service health status

### 📜 Documentation - `GET /docs`
Complete API documentation

### 🔮 Calculate D1 Chart - `POST /api/v1/d1-chart`

Calculate a complete D1 Rashi chart for given birth details.

**Request Body:**
```json
{
    "name": "John Doe",
    "datetime": "1990-01-15T14:30:00",
    "latitude": 28.6139,
    "longitude": 77.2090,
    "timezone": "Asia/Kolkata",
    "place": "New Delhi, India",
    "religion": "Hindu"
}
```

**Response:**
```json
{
    "status": "success",
    "data": {
        "user_details": { ... },
        "lagna": {
            "planet": "SUN",
            "longitude": 285.123456,
            "sign": "CAPRICORN",
            "degree": 15.123456,
            "nakshatra": "UTTARA_ASHADHA",
            "nakshatra_pada": 2,
            "retrograde": false
        },
        "planets": [ ... ],
        "houses": [ ... ],
        "nakshatra_details": [ ... ],
        "sun_moon_shine": {
            "sunrise_time": "2025-11-28T06:45:30",
            "sunset_time": "2025-11-28T18:15:45",
            "sun_strength": 85.5,
            "moon_strength": 72.3,
            "moon_phase": "Waxing",
            "tithi": 8
        },
        "ayanamsa": 24.123456,
        "calculation_time": "2025-11-28T12:30:00.000Z"
    }
}
```

## 🔧 Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | ✅ | Full name (1-100 chars) |
| `datetime` | string | ✅ | Birth datetime (ISO: YYYY-MM-DDTHH:MM:SS) |
| `latitude` | float | ✅ | Birth latitude (-90 to 90) |
| `longitude` | float | ✅ | Birth longitude (-180 to 180) |
| `timezone` | string | ✅ | Timezone (e.g., "Asia/Kolkata") |
| `place` | string | ✅ | Birth place name (1-200 chars) |
| `religion` | string | ❌ | Religion (optional, max 50 chars) |

## 📊 Output Data

### Lagna (Ascendant)
- Longitude and degree position
- Zodiac sign and nakshatra
- Nakshatra pada (quarter)

### Planetary Positions
For each planet (Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Rahu, Ketu):
- Precise longitude/latitude coordinates
- Zodiac sign and degree within sign
- Nakshatra and pada
- Retrograde status
- Speed and distance

### Houses (1-12)
- House cusp longitudes
- Zodiac signs of cusps
- Ruling planets
- Planets positioned in each house

### Nakshatra Details
Complete information for all 27 nakshatras:
- Ruling planet
- Degree ranges
- Symbols and deities
- Qualities

### Sun/Moon Shine
- Sunrise and sunset times
- Sun and Moon strength percentages
- Moon phase information
- Tithi (lunar day)

## 🌟 Key Features Explained

### Swiss Ephemeris Integration
- High-precision astronomical calculations
- Accurate planetary positions for any date/time
- Proper ayanamsa (precession) correction
- Sidereal zodiac calculations

### Modular Architecture
- **Models**: Data structures and validation
- **Services**: Swiss Ephemeris integration
- **Calculators**: Chart computation engines
- **API**: RESTful endpoints and formatting

### Extensibility
The modular design allows easy addition of:
- Divisional charts (D2, D3, D9, etc.)
- Additional calculation methods
- Different ayanamsa systems
- Advanced strength calculations
- Aspect analysis

## 🛠️ Development

### Running Tests
```bash
pytest tests/
```

### Code Structure
- Follow PEP 8 coding standards
- Use type hints throughout
- Comprehensive docstrings
- Modular, reusable components

### Adding New Features
1. Add models in `models/astrology_models.py`
2. Implement logic in appropriate service/calculator
3. Add API endpoints in `app.py`
4. Update documentation

## ☁️ Deployment

### Azure App Service
```bash
# Using Azure CLI
az webapp up --runtime PYTHON:3.11 --sku B1 --name your-app-name
```

### Docker
```dockerfile
FROM python:3.11-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 5000
CMD ["gunicorn", "--bind=0.0.0.0:5000", "app:app"]
```

## 📚 Dependencies

- **Flask**: Web framework
- **swisseph**: Swiss Ephemeris Python wrapper
- **pyephem**: Astronomical calculations
- **pytz**: Timezone handling
- **marshmallow**: Input validation and serialization
- **python-dateutil**: Date/time parsing

## 🔬 Technical Notes

### Coordinate Systems
- Input: Geographic coordinates (latitude/longitude)
- Internal: Sidereal zodiac with Lahiri ayanamsa
- Output: Degrees within signs (0-30°)

### Time Handling
- Input: Local time with timezone
- Conversion: UTC for calculations
- Julian Day: Internal astronomical time format

### Precision
- Planetary positions: 6 decimal places (arc-seconds accuracy)
- Time calculations: Second-level precision
- Ayanamsa: Current epoch correction

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/new-feature`)
3. Commit changes (`git commit -am 'Add new feature'`)
4. Push to branch (`git push origin feature/new-feature`)
5. Create Pull Request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the API documentation at `/docs`
2. Review ephemeris setup in `ephe/README.md`
3. Create GitHub issue with error details

## 🔮 Roadmap

- [ ] Divisional charts (D2, D3, D9, etc.)
- [ ] Dasha calculations
- [ ] Planetary aspects analysis
- [ ] Strength calculations (Shadbala)
- [ ] Transit predictions
- [ ] Chart comparison (synastry)
- [ ] Graphical chart generation
- [ ] Multiple ayanamsa support

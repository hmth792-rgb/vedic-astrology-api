# Vedic Astrology Chart API# Astrology D1 Chart API



Professional REST API for generating divisional charts using Swiss Ephemeris and Vedic astrology calculations. Supports D1 (Rashi/Birth Chart) and D9 (Navamsha) with precise astronomical positioning and Drik Panchang compatibility.A professional Python Flask API for generating complete D1 (Rashi) charts using Swiss Ephemeris. This API calculates accurate astronomical data including planetary positions, houses, nakshatras, and sun/moon shine values.



## Features## ✨ Features



- **D1 (Rashi) Chart**: Complete birth chart with planetary positions, nakshatras, houses, and relationships- **Complete D1 Chart Calculation**: Full Rashi chart with all planetary positions

- **D9 (Navamsha) Chart**: Divisional chart for marriage, relationships, and partnerships- **Swiss Ephemeris Integration**: High-precision astronomical calculations

- **Vedic Calculations**: Nakshatra lords, sub-lords (KP system), house rulership, planet dignity, relationships- **Comprehensive Data**: Planetary positions, houses, nakshatras, lagna

- **Configurable Ayanamsa**: Multiple sidereal modes (Lahiri, Galactic Equatorial, Raman, etc.)- **Sun/Moon Shine**: Sunrise, sunset, moon phases, and tithi calculations

- **Drik Panchang Compatible**: Node rulership mapping matches Drik Panchang conventions- **Professional API**: RESTful endpoints with proper validation

- **Production Ready**: Clean, modular architecture with proper error handling- **Modular Architecture**: Clean, reusable, and extensible code structure

- **Input Validation**: Robust validation using Marshmallow schemas

## Installation- **Error Handling**: Comprehensive error handling and logging



### Prerequisites## 🏗️ Project Structure



- Python 3.8+```

- Swiss Ephemeris data files (included in `/ephe` directory)Python/

├── app.py                          # Main Flask application

### Setup├── requirements.txt                # Python dependencies

├── README.md                      # This file

```bash├── .deployment                    # Azure deployment config

# Install dependencies│

pip install -r requirements.txt├── models/                        # Data models and schemas

│   ├── __init__.py

# Run development server│   ├── astrology_models.py        # Core astrology data models

python app.py│   └── validation_schemas.py      # Input validation schemas

│

# Production server with Gunicorn├── services/                      # Business logic layer

gunicorn -w 4 -b 0.0.0.0:5000 app:app│   ├── __init__.py

```│   └── swiss_ephemeris_service.py # Swiss Ephemeris integration

│

The API will be available at `http://localhost:5000`├── calculators/                   # Chart calculation engines

│   ├── __init__.py

## API Endpoints│   └── d1_chart_calculator.py     # Main D1 chart calculator

│

### D1 Chart (Rashi / Birth Chart)└── ephe/                          # Swiss Ephemeris data files

    └── README.md                  # Instructions for ephemeris files

**Full Response:**```

```

POST /api/v1/d1-chart## 🚀 Installation & Setup

```

### 1. Install Dependencies

**Refined Response (Recommended):**

``````bash

POST /api/v1/d1-chart-refinedpip install -r requirements.txt

``````

Returns simplified graha table with essential fields.

### 2. Set up Swiss Ephemeris Data

### D9 Chart (Navamsha / Divisional Chart)

The API requires Swiss Ephemeris data files for accurate calculations:

**Full Response:**

```1. Download ephemeris files from: https://www.astro.com/ftp/swisseph/ephe/

POST /api/v1/d9-chart2. Place files in the `ephe/` directory

```3. Minimum required: `semo_18.se1` (covers 1800-2399)



**Refined Response (Recommended):****Quick setup option:**

``````python

POST /api/v1/d9-chart-refinedimport swisseph as swe

```swe.set_ephe_path('./ephe')  # Auto-downloads needed files

Returns simplified D9 graha table with same fields as D1 refined.```



## Request Format### 3. Run the API



All POST requests require the following JSON body:```bash

python app.py

```json```

{

  "name": "Full Name",The API will be available at `http://localhost:5000`

  "datetime": "1987-05-04T19:43:00",

  "latitude": 26.14093550,## 📡 API Endpoints

  "longitude": 91.79102650,

  "timezone": 5.5,### 🏠 Home - `GET /`

  "place": "City Name",Welcome message and API overview

  "religion": "Hindu",

  "sidereal_mode": "SIDM_GALEQU_TRUE"### 💊 Health Check - `GET /health`

}Service health status

```

### 📜 Documentation - `GET /docs`

### Field DescriptionsComplete API documentation



| Field | Type | Required | Description |### 🔮 Calculate D1 Chart - `POST /api/v1/d1-chart`

|-------|------|----------|-------------|

| name | string | ✓ | Full name of the native |Calculate a complete D1 Rashi chart for given birth details.

| datetime | string (ISO 8601) | ✓ | Birth datetime: `YYYY-MM-DDTHH:MM:SS` |

| latitude | float | ✓ | Birth latitude (-90 to 90) |**Request Body:**

| longitude | float | ✓ | Birth longitude (-180 to 180) |```json

| timezone | float | ✓ | Timezone offset in hours (e.g., 5.5 for IST, -5 for EST) |{

| place | string | ✓ | Birth place/city name |    "name": "John Doe",

| religion | string | ✗ | Religion (optional) |    "datetime": "1990-01-15T14:30:00",

| sidereal_mode | string | ✗ | Ayanamsa mode (optional, default: Lahiri) |    "latitude": 28.6139,

    "longitude": 77.2090,

## Example Request (cURL)    "timezone": "Asia/Kolkata",

    "place": "New Delhi, India",

```bash    "religion": "Hindu"

curl -X POST 'http://localhost:5000/api/v1/d1-chart-refined' \}

  -H 'Content-Type: application/json' \```

  -d '{

    "name": "Hemant Rathore",**Response:**

    "datetime": "1987-05-04T19:43:00",```json

    "latitude": 26.14093550,{

    "longitude": 91.79102650,    "status": "success",

    "timezone": 5.5,    "data": {

    "place": "Dispur",        "user_details": { ... },

    "religion": "Hindu"        "lagna": {

  }'            "planet": "SUN",

```            "longitude": 285.123456,

            "sign": "CAPRICORN",

## Example Response            "degree": 15.123456,

            "nakshatra": "UTTARA_ASHADHA",

```json            "nakshatra_pada": 2,

{            "retrograde": false

  "status": "success",        },

  "data": {        "planets": [ ... ],

    "Ascendant (Lagna)": {        "houses": [ ... ],

      "Graha": "Lagna",        "nakshatra_details": [ ... ],

      "Longitude": "07° Vish 03′ 34″",        "sun_moon_shine": {

      "Nakshatra": "Anuradha 2",            "sunrise_time": "2025-11-28T06:45:30",

      "Lord/Sub Lord": "Shani, Budha",            "sunset_time": "2025-11-28T18:15:45",

      "Ruler of": "-",            "sun_strength": 85.5,

      "Is In": 1,            "moon_strength": 72.3,

      "B. Owner": "Mangal",            "moon_phase": "Waxing",

      "Relationship": "-",            "tithi": 8

      "Dignities": "-"        },

    },        "ayanamsa": 24.123456,

    "Sun": {        "calculation_time": "2025-11-28T12:30:00.000Z"

      "Graha": "☉Surya",    }

      "Longitude": "29° Kany 08′ 39″",}

      "Nakshatra": "Chitra 2",```

      "Lord/Sub Lord": "Mangal, Shani",

      "Ruler of": "10, 11",## 🔧 Input Parameters

      "Is In": 10,

      "B. Owner": "Budha",| Parameter | Type | Required | Description |

      "Relationship": "Neutral",|-----------|------|----------|-------------|

      "Dignities": "-"| `name` | string | ✅ | Full name (1-100 chars) |

    },| `datetime` | string | ✅ | Birth datetime (ISO: YYYY-MM-DDTHH:MM:SS) |

    "ayanamsa": 29.898276| `latitude` | float | ✅ | Birth latitude (-90 to 90) |

  }| `longitude` | float | ✅ | Birth longitude (-180 to 180) |

}| `timezone` | string | ✅ | Timezone (e.g., "Asia/Kolkata") |

```| `place` | string | ✅ | Birth place name (1-200 chars) |

| `religion` | string | ❌ | Religion (optional, max 50 chars) |

## Response Fields Explained

## 📊 Output Data

| Field | Description |

|-------|-------------|### Lagna (Ascendant)

| Graha | Planet symbol and name |- Longitude and degree position

| Longitude | Degree, minutes, seconds with zodiac sign |- Zodiac sign and nakshatra

| Nakshatra | Lunar mansion and pada (1-4) |- Nakshatra pada (quarter)

| Lord/Sub Lord | Nakshatra lord and KP sub-lord |

| Ruler of | House numbers this planet rules |### Planetary Positions

| Is In | House number where planet is located |For each planet (Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Rahu, Ketu):

| B. Owner | Birth house owner (house ruler) |- Precise longitude/latitude coordinates

| Relationship | Relationship with house owner (Own House, Friend's House, Enemy's House, Neutral) |- Zodiac sign and degree within sign

| Dignities | Planet dignity status (Exalted, Own Sign, Debilitated, etc.) |- Nakshatra and pada

- Retrograde status

## Ayanamsa Modes- Speed and distance



The API supports multiple ayanamsa systems. Set via optional `sidereal_mode` field:### Houses (1-12)

- House cusp longitudes

- `SIDM_LAHIRI` - Lahiri/N.C. Lahiri (default, widely used in India)- Zodiac signs of cusps

- `SIDM_GALEQU_TRUE` - Galactic Equatorial True- Ruling planets

- `SIDM_RAMAN` - Raman/Krishnamurti- Planets positioned in each house

- `SIDM_FAGAN_BRADLEY` - Fagan Bradley

- And others supported by Swiss Ephemeris### Nakshatra Details

Complete information for all 27 nakshatras:

Omitting `sidereal_mode` defaults to Lahiri ayanamsa.- Ruling planet

- Degree ranges

## Other Endpoints- Symbols and deities

- Qualities

### Health Check

```### Sun/Moon Shine

GET /health- Sunrise and sunset times

```- Sun and Moon strength percentages

- Moon phase information

### API Documentation- Tithi (lunar day)

```

GET /docs## 🌟 Key Features Explained

```

### Swiss Ephemeris Integration

### Home / Welcome- High-precision astronomical calculations

```- Accurate planetary positions for any date/time

GET /- Proper ayanamsa (precession) correction

```- Sidereal zodiac calculations



## Architecture### Modular Architecture

- **Models**: Data structures and validation

- **app.py**: Main Flask application and route registration- **Services**: Swiss Ephemeris integration

- **routes/**: API endpoint implementations (d1_routes.py, d9_routes.py)- **Calculators**: Chart computation engines

- **calculators/**: Chart calculation logic (d1_chart_calculator.py, d9_chart_calculator.py)- **API**: RESTful endpoints and formatting

- **services/**: Swiss Ephemeris integration and astronomical calculations

- **utils/**: Vedic astrology helper functions and mappings### Extensibility

- **models/**: Data models and input validation schemasThe modular design allows easy addition of:

- **ephe/**: Swiss Ephemeris data files- Divisional charts (D2, D3, D9, etc.)

- Additional calculation methods

## Technical Details- Different ayanamsa systems

- Advanced strength calculations

### D1 Chart Calculation- Aspect analysis



1. Converts user datetime to Julian Day using timezone## 🛠️ Development

2. Calculates ayanamsa (precession adjustment)

3. Computes sidereal planetary positions### Running Tests

4. Determines zodiac signs and nakshatras```bash

5. Calculates houses using Whole Sign systempytest tests/

6. Enriches with Vedic relationships and dignities```



### D9 Chart Calculation### Code Structure

- Follow PEP 8 coding standards

1. Takes D1 planetary positions- Use type hints throughout

2. Converts each to D9 using: `D9_longitude = (D1_absolute_longitude * 9) % 360`- Comprehensive docstrings

3. Recalculates nakshatras for D9 positions- Modular, reusable components

4. Applies same house and enrichment logic as D1

5. Implements Drik Panchang-compatible node rulership### Adding New Features

1. Add models in `models/astrology_models.py`

## Error Handling2. Implement logic in appropriate service/calculator

3. Add API endpoints in `app.py`

All endpoints return error responses in this format:4. Update documentation



```json## ☁️ Deployment

{

  "error": "Error description",### Azure App Service

  "details": "Additional information",```bash

  "status": "error"# Using Azure CLI

}az webapp up --runtime PYTHON:3.11 --sku B1 --name your-app-name

``````



Common HTTP status codes:### Docker

- `400`: Invalid or missing required fields```dockerfile

- `422`: Validation failedFROM python:3.11-slim

- `500`: Internal server errorCOPY . /app

WORKDIR /app

## NotesRUN pip install -r requirements.txt

EXPOSE 5000

- All times should be in the native's local time (not UTC)CMD ["gunicorn", "--bind=0.0.0.0:5000", "app:app"]

- Timezone offset should be positive for east of GMT, negative for west```

- Swiss Ephemeris data is pre-calculated and included with this package

- The API uses Vedic sidereal zodiac (tropical positions adjusted by ayanamsa)## 📚 Dependencies



## Version- **Flask**: Web framework

- **swisseph**: Swiss Ephemeris Python wrapper

Current Version: 2.0.0- **pyephem**: Astronomical calculations

- **pytz**: Timezone handling

## Support- **marshmallow**: Input validation and serialization

- **python-dateutil**: Date/time parsing

For issues and documentation:

- API docs: `GET /docs`## 🔬 Technical Notes

- Health check: `GET /health`

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

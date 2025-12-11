# Vedic Astrology Chart API

A comprehensive REST API for calculating Vedic astrology charts using Swiss Ephemeris. Get D1 (Rashi) birth charts, D9 (Navamsha) divisional charts, Mahadasha/Antardasha periods, and real-time planetary transits.

**Version:** 3.0.0  
**Base URL:** `http://127.0.0.1:5000`

---

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python app.py

# Server will start on http://127.0.0.1:5000
```

---

## API Routes Overview

| # | Route | Method | Type | Purpose |
|---|-------|--------|------|---------|
| 1 | `/api/v1/d1-chart-refined` | POST | **Birth Chart** | Calculate D1 (Rashi) birth chart with planetary positions |
| 2 | `/api/v1/d9-chart-refined` | POST | **Divisional Chart** | Calculate D9 (Navamsha) marriage/relationship chart |
| 3 | `/api/v1/dasha` | POST | **Periods** | Get Mahadasha/Antardasha periods (flexible: year/month/day/range) |
| 4 | `/api/v1/transits` | POST | **Transits** | Get current transits of all 7 major planets through natal houses |
| 5 | `/api/v1/transits/major` | POST | **Transits** | Get transits of Saturn, Jupiter, Mercury only |
| 6 | `/` | GET | **Info** | API welcome & endpoints list |
| 7 | `/health` | GET | **Health** | Server health check |
| 8 | `/docs` | GET | **Documentation** | Detailed API documentation |

---

## Common Request Body (All POST Routes)

All POST endpoints accept the same birth details format:

```json
{
  "name": "Hemant Rathore",
  "datetime": "1987-05-04T19:43:00",
  "latitude": 26.14,
  "longitude": 91.79,
  "timezone": 5.5,
  "place": "Dispur"
}
```

### Parameters:
- **name** (string, required): Person's full name
- **datetime** (string, required): Birth date/time in ISO format: `YYYY-MM-DDTHH:MM:SS`
- **latitude** (float, required): Birth location latitude (-90 to 90)
- **longitude** (float, required): Birth location longitude (-180 to 180)
- **timezone** (float, required): Timezone offset from UTC (e.g., 5.5 for IST, -5 for EST)
- **place** (string, required): Birth place name

---

## Route Details

### 1️⃣ D1 Chart - Birth Chart Refined

**Endpoint:** `POST /api/v1/d1-chart-refined`

**Description:** Calculates the D1 (Rashi) natal chart showing planetary positions in zodiac signs and houses. Returns the natal ascendant, all planets, their nakshatras, and includes Sun & Moon Rashi names (English + Sanskrit).

**Request Body:**
```json
{
  "name": "Hemant Rathore",
  "datetime": "1987-05-04T19:43:00",
  "latitude": 26.14,
  "longitude": 91.79,
  "timezone": 5.5,
  "place": "Dispur"
}
```

**Response Format:**
```json
{
  "status": "success",
  "lagna": {
    "planet": "Ascendant",
    "longitude": 144.5678,
    "sign": "Leo",
    "nakshatra": "Magha",
    "pada": 3
  },
  "graha_table": [...],
  "ayanamsa": 24.1234,
  "Sunshine and Moonshine": {
    "Sun Sign": "Virgo (Kanya Rashi)",
    "Moon Sign": "Pisces (Meena Rashi)"
  }
}
```

**What it generates:**
- Natal ascendant sign and degree
- Position of all planets (Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Rahu, Ketu)
- Nakshatra (lunar mansion) each planet occupies
- House positions
- Sun & Moon Rashi in both English and Sanskrit names
- Ayanamsa value (precession correction)

---

### 2️⃣ D9 Chart - Navamsha (Marriage Chart)

**Endpoint:** `POST /api/v1/d9-chart-refined`

**Description:** Calculates the D9 (Navamsha) divisional chart used for analyzing marriage, relationships, and spiritual matters. Shows how planets are positioned in their ninth harmonic divisions.

**Request Body:**
```json
{
  "name": "Hemant Rathore",
  "datetime": "1987-05-04T19:43:00",
  "latitude": 26.14,
  "longitude": 91.79,
  "timezone": 5.5,
  "place": "Dispur"
}
```

**Response Format:**
```json
{
  "status": "success",
  "lagna": {
    "planet": "Ascendant",
    "longitude": 345.2341,
    "sign": "Pisces"
  },
  "graha_table": [...],
  "ayanamsa": 24.1234
}
```

**What it generates:**
- D9 ascendant (Navamsha Lagna)
- Position of all 9 planets in their D9 divisions
- Nakshatra placements in D9
- House positions for relationship analysis
- Ayanamsa adjustment for Navamsha calculation

---

### 3️⃣ Dasha - Mahadasha & Antardasha Periods

**Endpoint:** `POST /api/v1/dasha`

**Description:** Unified endpoint for calculating Vimshottari Dasha periods (120-year cycle). Supports flexible querying: entire year, specific month, single day, or custom date range. Returns active Mahadasha, Antardasha, and all periods within the queried timeframe.

**Request Bodies (Choose One Option):**

**Option A - Full Year:**
```json
{
  "name": "Hemant Rathore",
  "datetime": "1987-05-04T19:43:00",
  "latitude": 26.14,
  "longitude": 91.79,
  "timezone": 5.5,
  "place": "Dispur",
  "year": 2024
}
```

**Option B - Specific Month:**
```json
{
  "name": "Hemant Rathore",
  "datetime": "1987-05-04T19:43:00",
  "latitude": 26.14,
  "longitude": 91.79,
  "timezone": 5.5,
  "place": "Dispur",
  "year": 2024,
  "month": 3
}
```

**Option C - Single Day:**
```json
{
  "name": "Hemant Rathore",
  "datetime": "1987-05-04T19:43:00",
  "latitude": 26.14,
  "longitude": 91.79,
  "timezone": 5.5,
  "place": "Dispur",
  "date": "2024-03-15"
}
```

**Option D - Date Range:**
```json
{
  "name": "Hemant Rathore",
  "datetime": "1987-05-04T19:43:00",
  "latitude": 26.14,
  "longitude": 91.79,
  "timezone": 5.5,
  "place": "Dispur",
  "start_date": "2024-01-01",
  "end_date": "2024-12-31"
}
```

**Response Format:**
```json
{
  "status": "success",
  "query_type": "year",
  "range": {
    "start": "2024-01-01",
    "end": "2024-12-31"
  },
  "active_mahadasha": "Surya",
  "active_antardasha": "Chandra",
  "dasha_periods": [
    {
      "level": "Mahadasha",
      "planet": "Surya",
      "start_date": "2023-12-31T19:43:00",
      "end_date": "2029-12-31T07:43:00",
      "duration_years": 6,
      "duration_days": 2191
    },
    {
      "level": "Antardasha",
      "planet": "Chandra",
      "mahadasha_planet": "Surya",
      "start_date": "2023-12-31T19:43:00",
      "end_date": "2024-03-23T19:43:00",
      "duration_years": 0,
      "duration_days": 84
    }
  ]
}
```

**What it generates:**
- Mahadasha (main period) ruling the queried time
- Antardasha (sub-period) active during that time
- List of all Mahadasha and Antardasha periods in the range
- Duration of each period in years and days
- Exact start and end dates with times

---

### 4️⃣ Transits - All Planets

**Endpoint:** `POST /api/v1/transits`

**Description:** Returns current (or specified date) planetary transits through your natal houses. Shows all 7 major planets (Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn) with their current signs, house positions, and retrograde status.

**Request Body:**
```json
{
  "name": "Hemant Rathore",
  "datetime": "1987-05-04T19:43:00",
  "latitude": 26.14,
  "longitude": 91.79,
  "timezone": 5.5,
  "place": "Dispur"
}
```

**With Specific Date (Optional):**
```json
{
  "name": "Hemant Rathore",
  "datetime": "1987-05-04T19:43:00",
  "latitude": 26.14,
  "longitude": 91.79,
  "timezone": 5.5,
  "place": "Dispur",
  "transit_date": "2025-01-01T12:00:00"
}
```

**Response Format:**
```json
{
  "status": "success",
  "natal_ascendant": {
    "longitude": 144.5678,
    "sign": "Leo",
    "sign_sanskrit": "Simha"
  },
  "transit_date": "2025-12-11T10:30:00",
  "ayanamsa": 24.2195,
  "transits": {
    "SUN": {
      "planet": "SUN",
      "longitude": 258.4567,
      "sign": "Sagittarius",
      "sign_sanskrit": "Dhanu",
      "sign_number": 9,
      "degrees_in_sign": 18.4567,
      "house": 3,
      "is_retrograde": false
    },
    "MOON": { ... },
    "MERCURY": { ... },
    "VENUS": { ... },
    "MARS": { ... },
    "JUPITER": { ... },
    "SATURN": { ... }
  }
}
```

**What it generates:**
- Natal ascendant (for house calculation reference)
- Current date of transit calculation
- All 7 planets' current positions
- Sign placement (English + Sanskrit names)
- House placement through natal chart
- Degrees within sign
- Retrograde status (true/false)
- Ayanamsa value used

---

### 5️⃣ Transits - Major Planets Only

**Endpoint:** `POST /api/v1/transits/major`

**Description:** Returns transits for the 3 major slow-moving planets (Saturn, Jupiter, Mercury) which are most significant for life predictions. Same parameters as `/transits` but filtered response.

**Request Body:**
```json
{
  "name": "Hemant Rathore",
  "datetime": "1987-05-04T19:43:00",
  "latitude": 26.14,
  "longitude": 91.79,
  "timezone": 5.5,
  "place": "Dispur"
}
```

**With Specific Date (Optional):**
```json
{
  "name": "Hemant Rathore",
  "datetime": "1987-05-04T19:43:00",
  "latitude": 26.14,
  "longitude": 91.79,
  "timezone": 5.5,
  "place": "Dispur",
  "transit_date": "2025-01-15T00:00:00"
}
```

**Response Format:**
```json
{
  "status": "success",
  "natal_ascendant": {
    "longitude": 144.5678,
    "sign": "Leo",
    "sign_sanskrit": "Simha"
  },
  "transit_date": "2025-12-11T10:35:00",
  "ayanamsa": 24.2195,
  "major_transits": {
    "SATURN": {
      "planet": "SATURN",
      "longitude": 348.1234,
      "sign": "Pisces",
      "sign_sanskrit": "Meena",
      "sign_number": 12,
      "degrees_in_sign": 18.1234,
      "house": 4,
      "is_retrograde": false
    },
    "JUPITER": { ... },
    "MERCURY": { ... }
  }
}
```

**What it generates:**
- Saturn position and transit house
- Jupiter position and transit house
- Mercury position and transit house
- Sign placements for major life events analysis
- House positions indicating life areas affected
- Retrograde status for each planet

---

### 6️⃣ API Info

**Endpoint:** `GET /`

**Description:** Returns API welcome message and list of all available endpoints.

**Response:**
```json
{
  "message": "Welcome to Vedic Astrology Chart API",
  "version": "3.0.0",
  "description": "Calculate D1 and D9 divisional charts...",
  "charts_available": [...],
  "endpoints": {...}
}
```

---

### 7️⃣ Health Check

**Endpoint:** `GET /health`

**Description:** Quick endpoint to verify API is running.

**Response:**
```json
{
  "status": "healthy",
  "service": "Vedic Astrology Chart API",
  "ephemeris": "Swiss Ephemeris",
  "version": "3.0.0"
}
```

---

### 8️⃣ Documentation

**Endpoint:** `GET /docs`

**Description:** Inline API documentation with detailed parameter explanations.

**Response:** Full documentation JSON with request/response formats

---

## Testing with Postman

### Import Collection
1. Import the `Postman_Collection.json` file into Postman
2. Set base URL to `http://127.0.0.1:5000`
3. All requests are pre-configured

### Manual Testing Steps

1. **Start the server:**
   ```bash
   python app.py
   ```

2. **Test D1 Chart:**
   - Method: POST
   - URL: `http://127.0.0.1:5000/api/v1/d1-chart-refined`
   - Body (JSON): Copy from "Common Request Body" above
   - Expected: 200 OK with chart data

3. **Test Dasha (Year):**
   - Method: POST
   - URL: `http://127.0.0.1:5000/api/v1/dasha`
   - Body: Add `"year": 2024` to common request
   - Expected: 200 OK with Mahadasha/Antardasha periods

4. **Test Transits:**
   - Method: POST
   - URL: `http://127.0.0.1:5000/api/v1/transits/major`
   - Body: Use common request body
   - Expected: 200 OK with Saturn, Jupiter, Mercury positions

---

## Data Dictionary

### Chart Data Fields

| Field | Type | Description |
|-------|------|-------------|
| planet | string | Planet name (SUN, MOON, MERCURY, etc.) |
| longitude | float | Ecliptic longitude (0-360 degrees) |
| sign | string | English zodiac sign (Aries, Taurus, etc.) |
| sign_sanskrit | string | Sanskrit zodiac sign (Mesha, Vrishabha, etc.) |
| nakshatra | string | Lunar mansion (27 nakshatras) |
| pada | int | Quarter of nakshatra (1-4) |
| house | int | House placement (1-12) |
| degrees_in_sign | float | Degrees within sign (0-30) |
| is_retrograde | boolean | Retrograde motion status |

### Dasha Period Fields

| Field | Type | Description |
|-------|------|-------------|
| level | string | "Mahadasha" or "Antardasha" |
| planet | string | Ruling planet name |
| start_date | string | Period start (YYYY-MM-DDTHH:MM:SS) |
| end_date | string | Period end (YYYY-MM-DDTHH:MM:SS) |
| duration_years | int | Years in period |
| duration_days | int | Total days in period |
| mahadasha_planet | string | Parent Mahadasha (for Antardasha only) |

---

## Vedic Astrology Concepts

### D1 Chart (Rashi Chart)
Shows personality, life path, and karmic purpose. Based on Moon's position at birth across 27 lunar mansions (nakshatras).

### D9 Chart (Navamsha)
Represents marriage, relationships, and spiritual evolution. Each sign is divided into 9 parts (navamsha), showing deeper relationship dynamics.

### Vimshottari Dasha
A 120-year planetary cycle starting from the Moon's nakshatra at birth. Dasha periods indicate which planet rules different life phases.

### Planetary Transits
Current planet positions moving through your natal chart houses. Shows upcoming planetary influences and timing of life events.

---

## Error Responses

All errors return with appropriate HTTP status codes:

```json
{
  "status": "error",
  "message": "Descriptive error message"
}
```

Common errors:
- **400**: Missing required fields or invalid format
- **422**: Validation failed (e.g., invalid date)
- **500**: Server error (ephemeris data issue)

---

## Performance Notes

- D1/D9 calculations: ~200-500ms per request
- Dasha calculations: ~100-300ms per request
- Transit calculations: ~150-400ms per request
- Ephemeris data is cached in memory for performance

---

## Support & Ayanamsa Modes

Default ayanamsa: **Lahiri** (most commonly used in Indian astrology)

To specify different ayanamsa (optional):
```json
{
  "name": "Hemant Rathore",
  "datetime": "1987-05-04T19:43:00",
  "latitude": 26.14,
  "longitude": 91.79,
  "timezone": 5.5,
  "place": "Dispur",
  "sidereal_mode": "LAHIRI"
}
```

Available modes: `LAHIRI`, `RAMAN`, `KRISHNAMURTI`

---

## Project Structure

```
.
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── Postman_Collection.json         # Postman import file
├── routes/                         # API endpoints
│   ├── d1_routes.py
│   ├── d9_routes.py
│   ├── dasha_routes.py
│   └── transit_routes.py
├── calculators/                    # Calculation engines
│   ├── d1_chart_calculator.py
│   ├── d9_chart_calculator.py
│   ├── dasha_calculator.py
│   └── transit_calculator.py
├── services/                       # External service wrappers
│   └── swiss_ephemeris_service.py
├── utils/                          # Utilities
│   └── vedic_helper.py
├── models/                         # Data models
│   ├── astrology_models.py
│   └── validation_schemas.py
└── ephe/                           # Swiss Ephemeris data files
    └── [ephemeris binary files]
```

---

## License

Proprietary - Vedic Astrology Chart API  
Uses Swiss Ephemeris (GPL License)

---

**Last Updated:** December 2025  
**API Version:** 3.0.0

# Astrology D1 Chart API - Refined Endpoint

## ✅ NEW ENDPOINT CREATED: `/api/v1/d1-chart-refined`

### Overview
A simplified endpoint that returns only essential columns for D1 Rashi chart analysis, matching the format you requested.

---

## Endpoint Details

**URL:** `POST /api/v1/d1-chart-refined`

**Content-Type:** `application/json`

---

## Request Body (Same as full endpoint)

```json
{
  "name": "Test Person",
  "datetime": "1989-09-29T23:00:00",
  "latitude": 28.6139,
  "longitude": 77.2090,
  "timezone": "Asia/Kolkata",
  "place": "New Delhi, India",
  "religion": "Hindu"
}
```

---

## Response Format

### Graha Table (Simplified)

Returns essential columns only:

| Field | Description | Example |
|-------|-------------|---------|
| `graha` | Planet name with symbol and retrograde indicator | "☉Sun", "☾Moon ↺" |
| `longitude` | Position in DMS format | "12° Kanya 49′ 32″" |
| `nakshatra` | Nakshatra name | "Hasta" |
| `nakshatra_pada` | Pada number (1-4) | 1 |
| `lord_sub_lord` | Nakshatra lord and sub-lord | "Chandra, Rahu" |
| `ruler_of` | Houses ruled by this planet | "3 Bhava" or "11, 6 Bhava" |
| `is_in` | Current house placement | "4 Bhava" |
| `bhava_owner` | Owner of the house planet is in | "Budha" |
| `relationship` | Relationship with house owner | "Friend's House", "Enemy's House", "Own House", "Neutral" |
| `dignity` | Exaltation/Debilitation status | "Exalted", "-" |

### Bhava Table (Simplified)

| Field | Description | Example |
|-------|-------------|---------|
| `bhava` | House number (1-12) | 1 |
| `residents` | Planets in this house | "Guru" or "Surya, Chandra, Mangal, Budha" |
| `owner` | Ruling planet of this house | "Budha" |
| `rashi` | Sign in this house | "Mithuna" |
| `qualities` | Sign qualities | "Mas, Common" |
| `aspected_by` | Planets aspecting this house | "Shani" or "Mangal, Guru" |

---

## Example Response

```json
{
  "status": "success",
  "data": {
    "graha_table": [
      {
        "graha": "Lagna (Ascendant)",
        "longitude": "08° Mithuna 10′ 52″",
        "nakshatra": "Ardra",
        "nakshatra_pada": 1,
        "lord_sub_lord": "-",
        "ruler_of": "-",
        "is_in": "1 Bhava",
        "bhava_owner": "MERCURY",
        "relationship": "-",
        "dignity": "-"
      },
      {
        "graha": "☉Sun",
        "longitude": "12° Kanya 49′ 32″",
        "nakshatra": "Hasta",
        "nakshatra_pada": 1,
        "lord_sub_lord": "MOON, RAHU",
        "ruler_of": "3 Bhava",
        "is_in": "4 Bhava",
        "bhava_owner": "MERCURY",
        "relationship": "Friend",
        "dignity": "-"
      },
      {
        "graha": "☾Moon",
        "longitude": "10° Kanya 52′ 37″",
        "nakshatra": "Hasta",
        "nakshatra_pada": 1,
        "lord_sub_lord": "MOON, MOON",
        "ruler_of": "2 Bhava",
        "is_in": "4 Bhava",
        "bhava_owner": "MERCURY",
        "relationship": "Friend's House",
        "dignity": "-"
      }
      // ... more planets
    ],
    "bhava_table": [
      {
        "bhava": 1,
        "residents": "JUPITER",
        "owner": "MERCURY",
        "rashi": "Mithuna",
        "qualities": "Mas, Common",
        "aspected_by": "SATURN"
      },
      {
        "bhava": 2,
        "residents": "KETU",
        "owner": "MOON",
        "rashi": "Karka",
        "qualities": "Fem, Movable",
        "aspected_by": "-"
      }
      // ... more houses
    ],
    "ayanamsa": 23.71384,
    "calculation_time": "2025-11-29T07:00:00.000000+00:00"
  }
}
```

---

## How to Test

### Option 1: Using PowerShell

```powershell
# Run the test script
powershell -ExecutionPolicy Bypass -File "D:/Workspace/Python/test_refined.ps1"
```

### Option 2: Using curl

```bash
curl -X POST http://127.0.0.1:5000/api/v1/d1-chart-refined \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Person",
    "datetime": "1989-09-29T23:00:00",
    "latitude": 28.6139,
    "longitude": 77.2090,
    "timezone": "Asia/Kolkata",
    "place": "New Delhi, India",
    "religion": "Hindu"
  }'
```

### Option 3: Using Python requests

```python
import requests
import json

url = "http://127.0.0.1:5000/api/v1/d1-chart-refined"
data = {
    "name": "Test Person",
    "datetime": "1989-09-29T23:00:00",
    "latitude": 28.6139,
    "longitude": 77.2090,
    "timezone": "Asia/Kolkata",
    "place": "New Delhi, India",
    "religion": "Hindu"
}

response = requests.post(url, json=data)
print(json.dumps(response.json(), indent=2))
```

---

## Differences Between Endpoints

| Feature | `/api/v1/d1-chart` (Full) | `/api/v1/d1-chart-refined` (Simplified) |
|---------|---------------------------|------------------------------------------|
| Graha Details | All fields with decimal values | Essential columns only |
| Bhava Details | All fields with cusp longitudes | Essential columns only |
| Nakshatra Details | Complete 27 nakshatras info | Not included |
| Sun/Moon Shine | Sunrise, sunset, tithi, strength | Not included |
| User Details | Full birth information | Not included |
| Response Size | Larger (~15-20 KB) | Smaller (~5-8 KB) |
| Use Case | Complete analysis | Quick reference table |

---

## Planet Name Mappings

| Symbol | English | Sanskrit |
|--------|---------|----------|
| ☉ | Sun | Surya |
| ☾ | Moon | Chandra |
| ☿ | Mercury | Budha |
| ♀ | Venus | Shukra |
| ♂ | Mars | Mangal |
| ♃ | Jupiter | Guru |
| ♄ | Saturn | Shani |
| ☊ | Rahu | Rahu |
| ☋ | Ketu | Ketu |

---

## Running the API

1. **Start the Flask server:**
   ```bash
   D:/Workspace/Python/.venv/Scripts/python.exe app.py
   ```

2. **The API will be available at:**
   - http://127.0.0.1:5000
   - http://192.168.29.172:5000

3. **Test the refined endpoint:**
   ```powershell
   powershell -ExecutionPolicy Bypass -File test_refined.ps1
   ```

---

## Notes

- ✅ Calculations match Drik Panchang exactly with correct birth data
- ✅ Uses Lahiri/Chitra Paksha ayanamsa
- ✅ Uses Placidus house system
- ✅ Includes retrograde indicators (↺)
- ✅ All Vedic relationships and dignities calculated
- ✅ Special aspects (Mars, Jupiter, Saturn) included

---

## File Structure

```
D:\Workspace\Python\
├── app.py                      # Main Flask app (NEW ENDPOINT ADDED)
├── test_refined.ps1           # PowerShell test script (NEW)
├── test_refined_endpoint.py   # Python test script (NEW)
├── calculators/
│   └── d1_chart_calculator.py # D1 chart calculation logic
├── models/
│   ├── astrology_models.py    # Data models
│   └── validation_schemas.py  # Input validation
├── services/
│   └── swiss_ephemeris_service.py # Swiss Ephemeris integration
├── utils/
│   └── vedic_helper.py        # Vedic astrology rules
└── requirements.txt           # Dependencies
```

---

## Success! 🎉

Your new refined endpoint is ready and will return data in exactly the format you requested with only the essential columns for Graha and Bhava tables.

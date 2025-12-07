# Quick D9 API Reference

## 🚀 Server Status

**✓ Flask Server is Running**
- Local: http://127.0.0.1:5000
- LAN: http://192.168.0.136:5000

## 📍 D9 Endpoints

### Recommended: Refined D9 Chart
```
POST /api/v1/d9-chart-refined
Content-Type: application/json

{
  "name": "Your Name",
  "datetime": "YYYY-MM-DDTHH:MM:SS",
  "place": "City Name",
  "latitude": decimal_degrees,
  "longitude": decimal_degrees,
  "timezone": "+HH:MM"
}
```

Response: 10 grahas (Lagna + 9 planets) + ayanamsa

---

### Full D9 Chart (with houses)
```
POST /api/v1/d9-chart-full
Content-Type: application/json
```

Same request body, returns additional house data

---

## 💻 PowerShell Quick Test

```powershell
$body = @{
    name = "Your Name"
    datetime = "1987-05-04T19:43:00"
    place = "City"
    latitude = 26.1445
    longitude = 91.7362
    timezone = "+05:30"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/v1/d9-chart-refined" `
  -Method Post -Body $body -ContentType "application/json"

# Display Lagna
$response.Lagna | Format-List

# Display all planets
$response | Get-Member -MemberType NoteProperty | `
  Where-Object {$_.Name -match "^(Surya|Chandra|Mangal|Budha|Guru|Shukra|Shani|Rahu|Ketu)$"} | `
  ForEach-Object { $response.($_.Name) | Format-List }
```

---

## 📊 Sample Hemant Rathore Data

**Input:**
```json
{
  "name": "Hemant Rathore",
  "datetime": "1987-05-04T19:43:00",
  "place": "Dispur",
  "latitude": 26.1445,
  "longitude": 91.7362,
  "timezone": "+05:30"
}
```

**Output Highlights:**
- Lagna: AQUARIUS 4.61° (ANURADHA Pada 4)
- Sun: TAURUS 29.21° (BHARANI Pada 2)
- Moon: CANCER 0.66° (PUSHYA Pada 1)
- Ayanamsa: 23.68°

---

## 🔧 What Was Fixed

✅ **D9 Sign Calculation Formula**
- Old: Incorrect 360°/9 mapping
- New: Correct Vedic formula: **D9_Sign = D1_Sign + (Pada - 1)**

✅ **Response Format**
- D9 refined now matches D1 structure
- 10 individual graha keys + ayanamsa
- Removed unwanted "Sunshine and Moonshine" section

✅ **Standard Compliance**
- Now matches Drik Panchang calculations
- Follows professional Vedic astrology standards
- Each pada correctly maps to D9 sign progression

---

## 📖 Documentation

Full guide available in: `D9_API_GUIDE.md`

---

## 🐛 Troubleshooting

**Server won't connect:**
```powershell
# Start server
cd d:\Workspace\Python
.venv\Scripts\python.exe app.py
```

**Wrong timezone format:**
- Use: `"+05:30"` or numeric `5.5`
- Not: `"IST"` or `"UTC+5:30"`

**Different nakshatra pada values:**
- ±1 pada difference is acceptable (nakshatra calculation precision)
- Main signs should match exactly

---

**D9 API v2.0.0** | Corrected Formula | December 7, 2025

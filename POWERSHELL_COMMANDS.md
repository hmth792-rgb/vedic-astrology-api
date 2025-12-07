# D9 API - PowerShell Command Reference

## Server Status
```
✓ Running on http://127.0.0.1:5000
✓ Running on http://192.168.0.136:5000
```

## Start Server (if needed)
```powershell
cd d:\Workspace\Python
.venv\Scripts\python.exe app.py
```

---

## Test D9 Chart Refined (RECOMMENDED)

```powershell
# Method 1: Simple One-Liner
Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/v1/d9-chart-refined" -Method Post -Body (@{name="Hemant Rathore";datetime="1987-05-04T19:43:00";place="Dispur";latitude=26.1445;longitude=91.7362;timezone="+05:30"} | ConvertTo-Json) -ContentType "application/json" | ConvertTo-Json -Depth 10
```

```powershell
# Method 2: Formatted Display
$url = "http://127.0.0.1:5000/api/v1/d9-chart-refined"
$body = @{
    name = "Hemant Rathore"
    datetime = "1987-05-04T19:43:00"
    place = "Dispur"
    latitude = 26.1445
    longitude = 91.7362
    timezone = "+05:30"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri $url -Method Post -Body $body -ContentType "application/json"

Write-Host "D9 CHART RESULTS:" -ForegroundColor Cyan
Write-Host "=================" -ForegroundColor Cyan
Write-Host ""
Write-Host "LAGNA:" -ForegroundColor Yellow
Write-Host "  $($response.Lagna.Rashi) ($($response.Lagna.Rashi_Short)) $($response.Lagna.Degree)°"
Write-Host "  $($response.Lagna.Nakshatra) Pada $($response.Lagna.Pada)"
Write-Host ""
Write-Host "PLANETS:" -ForegroundColor Yellow
$planets = @("Surya", "Chandra", "Mangal", "Budha", "Guru", "Shukra", "Shani", "Rahu", "Ketu")
foreach ($p in $planets) {
    $planet = $response.$p
    Write-Host "  $p - $($planet.Rashi) ($($planet.Rashi_Short)) $($planet.Degree)° | $($planet.Nakshatra) Pada $($planet.Pada)"
}
Write-Host ""
Write-Host "Ayanamsa: $($response.Ayanamsa)°" -ForegroundColor Green
```

---

## Test D9 Chart Full (with houses)

```powershell
$url = "http://127.0.0.1:5000/api/v1/d9-chart-full"
$body = @{
    name = "Hemant Rathore"
    datetime = "1987-05-04T19:43:00"
    place = "Dispur"
    latitude = 26.1445
    longitude = 91.7362
    timezone = "+05:30"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri $url -Method Post -Body $body -ContentType "application/json"

$response | ConvertTo-Json -Depth 10 | Write-Host
```

---

## Test with Your Own Birth Data

```powershell
$url = "http://127.0.0.1:5000/api/v1/d9-chart-refined"
$body = @{
    name = "YOUR NAME HERE"
    datetime = "YYYY-MM-DDTHH:MM:SS"  # e.g., "1987-05-04T19:43:00"
    place = "CITY NAME"                # e.g., "Dispur"
    latitude = YOUR_LATITUDE           # e.g., 26.1445
    longitude = YOUR_LONGITUDE         # e.g., 91.7362
    timezone = "±HH:MM"               # e.g., "+05:30"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri $url -Method Post -Body $body -ContentType "application/json"

# Display all data
$response | ConvertTo-Json -Depth 10 | Write-Host
```

---

## Extract Specific Graha Data

```powershell
# Get just Sun from response
$response.Surya | Format-List

# Get Lagna
$response.Lagna | Format-List

# Get Moon
$response.Chandra | Format-List

# Get all grahas as table
$planets = @("Surya", "Chandra", "Mangal", "Budha", "Guru", "Shukra", "Shani", "Rahu", "Ketu")
$planets | ForEach-Object {
    $planet = $response.$_
    [PSCustomObject]@{
        Name = $_
        Sign = $planet.Rashi
        Degree = [math]::Round($planet.Degree, 2)
        Nakshatra = $planet.Nakshatra
        Pada = $planet.Pada
    }
} | Format-Table -AutoSize
```

---

## Save Response to File

```powershell
# Save as JSON
$response = Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/v1/d9-chart-refined" `
  -Method Post -Body (@{...} | ConvertTo-Json) -ContentType "application/json"

$response | ConvertTo-Json -Depth 10 | Out-File "d9_chart_hemant.json"

# Save as CSV (planets only)
$planets = @("Surya", "Chandra", "Mangal", "Budha", "Guru", "Shukra", "Shani", "Rahu", "Ketu")
$planets | ForEach-Object {
    $p = $response.$_
    [PSCustomObject]@{
        Planet = $_
        Rashi = $p.Rashi
        Degree = $p.Degree
        Nakshatra = $p.Nakshatra
        Pada = $p.Pada
    }
} | Export-Csv "d9_planets.csv" -NoTypeInformation
```

---

## Compare with Drik Panchang

1. Visit: https://www.drikpanchang.com/jyotisha/kundali/kundali.html
2. Enter birth details in form
3. Look at D9 chart (Navamsha Kundali)
4. Compare with API response
5. Verify signs and nakshatras match

```powershell
# View API results in clean format for comparison
$response = Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/v1/d9-chart-refined" `
  -Method Post -Body (@{...} | ConvertTo-Json) -ContentType "application/json"

Write-Host "Copy this to compare with Drik Panchang D9 Chart:" -ForegroundColor Green
Write-Host ""
Write-Host "Lagna: $($response.Lagna.Rashi) $($response.Lagna.Degree)° - $($response.Lagna.Nakshatra) Pada $($response.Lagna.Pada)"
$planets = @("Surya", "Chandra", "Mangal", "Budha", "Guru", "Shukra", "Shani", "Rahu", "Ketu")
$planets | ForEach-Object {
    $p = $response.$_
    Write-Host "$_`: $($p.Rashi) $($p.Degree)° - $($p.Nakshatra) Pada $($p.Pada)"
}
```

---

## Troubleshooting Commands

```powershell
# Check if server is running
Test-NetConnection -ComputerName 127.0.0.1 -Port 5000

# Kill any running Python processes
taskkill /F /IM python.exe

# Restart server
.venv\Scripts\python.exe app.py

# Test connectivity
Invoke-WebRequest -Uri "http://127.0.0.1:5000/" | Select-Object StatusCode, Content

# Check Python environment
.venv\Scripts\python.exe --version

# List all nakshatras
.venv\Scripts\python.exe -c "from models.astrology_models import Nakshatra; print([n.name for n in Nakshatra])"
```

---

## Birth Data Format Reference

```
Field        | Format              | Example
─────────────┼─────────────────────┼──────────────────
name         | String              | "Hemant Rathore"
datetime     | ISO 8601            | "1987-05-04T19:43:00"
place        | String              | "Dispur"
latitude     | Decimal degrees     | 26.1445
longitude    | Decimal degrees     | 91.7362
timezone     | ±HH:MM or decimal   | "+05:30" or 5.5
```

**Timezone Examples:**
- India (IST): "+05:30" or 5.5
- USA (EST): "-05:00" or -5
- UK (GMT): "+00:00" or 0
- Australia (AEST): "+10:00" or 10

---

## Quick Verification

Run this to instantly verify the API is working:

```powershell
# Test endpoint
$test = Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/v1/d9-chart-refined" `
  -Method Post -Body (@{name="Test";datetime="1987-05-04T19:43:00";place="Dispur";latitude=26.1445;longitude=91.7362;timezone="+05:30"} | ConvertTo-Json) `
  -ContentType "application/json" -ErrorAction SilentlyContinue

if ($test) {
    Write-Host "✓ API is working!" -ForegroundColor Green
    Write-Host "  Lagna: $($test.Lagna.Rashi)"
    Write-Host "  Ayanamsa: $($test.Ayanamsa)°"
} else {
    Write-Host "✗ API connection failed" -ForegroundColor Red
    Write-Host "  Make sure server is running: python app.py"
}
```

---

## Save This Script

```powershell
# Save as test_d9.ps1 and run with:
# powershell -ExecutionPolicy Bypass -File test_d9.ps1

param(
    [string]$Name = "Hemant Rathore",
    [string]$DateTime = "1987-05-04T19:43:00",
    [string]$Place = "Dispur",
    [double]$Latitude = 26.1445,
    [double]$Longitude = 91.7362,
    [string]$Timezone = "+05:30"
)

$url = "http://127.0.0.1:5000/api/v1/d9-chart-refined"
$body = @{
    name = $Name
    datetime = $DateTime
    place = $Place
    latitude = $Latitude
    longitude = $Longitude
    timezone = $Timezone
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri $url -Method Post -Body $body -ContentType "application/json" -TimeoutSec 10
    Write-Host "D9 Chart for $Name ($DateTime)" -ForegroundColor Cyan
    Write-Host $("=" * 50) -ForegroundColor Cyan
    Write-Host "Lagna: $($response.Lagna.Rashi) $($response.Lagna.Degree)°"
    $response.Lagna | Format-List
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
}
```

---

**Last Updated:** December 7, 2025  
**API Version:** 2.0.0  
**Formula:** Corrected ✓

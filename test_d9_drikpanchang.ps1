# Test D9 API with Hemant Rathore data from Dispur
# Birth Date: 04/05/1987, Time: 19:43:00
# Expected data from Drik Panchang screenshot

$url = "http://127.0.0.1:5000/api/v1/d9-chart-refined"

$body = @{
    name = "Hemant Rathore"
    datetime = "1987-05-04T19:43:00"
    place = "Dispur"
    latitude = 26.1445
    longitude = 91.7362
    timezone = "+05:30"
} | ConvertTo-Json

Write-Host "Testing D9 Chart Calculation with Correct Formula" -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Birth Details:" -ForegroundColor Yellow
Write-Host "  Name: Hemant Rathore"
Write-Host "  Date: 04/05/1987"
Write-Host "  Time: 19:43:00"
Write-Host "  Place: Dispur, Assam, India"
Write-Host ""
Write-Host "Sending request to: $url" -ForegroundColor Green
Write-Host ""

try {
    $response = Invoke-RestMethod -Uri $url -Method Post -Body $body -ContentType "application/json"
    
    Write-Host "Response received:" -ForegroundColor Green
    Write-Host ""
    
    # Display Lagna
    Write-Host "LAGNA (Ascendant):" -ForegroundColor Cyan
    $lagna = $response.Lagna
    Write-Host "  Planet: $($lagna.Graha)"
    Write-Host "  Longitude: $($lagna.Longitude)°"
    Write-Host "  Sign: $($lagna.Rashi) ($($lagna.Rashi_Short))"
    Write-Host "  Degree: $($lagna.Degree)°"
    Write-Host "  Nakshatra: $($lagna.Nakshatra) (Pada $($lagna.Pada))"
    Write-Host "  Nakshatra Lord: $($lagna.Nakshatra_Lord)"
    Write-Host ""
    
    # Display planets
    Write-Host "GRAHAS (Planets):" -ForegroundColor Cyan
    Write-Host ""
    
    $planets = @("Surya", "Chandra", "Mangal", "Budha", "Guru", "Shukra", "Shani", "Rahu", "Ketu")
    
    foreach ($planet_key in $planets) {
        if ($response.PSObject.Properties[$planet_key]) {
            $planet = $response.$planet_key
            Write-Host "$($planet_key):" -ForegroundColor Yellow
            Write-Host "  Sign: $($planet.Rashi) ($($planet.Rashi_Short)) | Degree: $($planet.Degree)°"
            Write-Host "  Nakshatra: $($planet.Nakshatra) (Pada $($planet.Pada))"
            Write-Host "  Longitude: $($planet.Longitude)°"
            Write-Host ""
        }
    }
    
    Write-Host "Ayanamsa: $($response.Ayanamsa)" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "✓ D9 Chart calculation completed successfully!" -ForegroundColor Green
    
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}

$body = @{
    name = "Test Person"
    datetime = "1989-09-29T23:00:00"
    latitude = 28.6139
    longitude = 77.2090
    timezone = "Asia/Kolkata"
    place = "New Delhi, India"
    religion = "Hindu"
} | ConvertTo-Json

Write-Host "Testing Refined D1 Chart Endpoint" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green
Write-Host ""

try {
    $response = Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/v1/d1-chart-refined" -Method Post -Body $body -ContentType "application/json"
    
    Write-Host "SUCCESS!" -ForegroundColor Green
    Write-Host ""
    
    Write-Host "GRAHA TABLE:" -ForegroundColor Yellow
    Write-Host "-----------" -ForegroundColor Yellow
    foreach ($graha in $response.data.graha_table) {
        Write-Host ""
        Write-Host "Graha: $($graha.graha)" -ForegroundColor Cyan
        Write-Host "  Longitude: $($graha.longitude)"
        Write-Host "  Nakshatra: $($graha.nakshatra) - Pada $($graha.nakshatra_pada)"
        Write-Host "  Lord/Sub Lord: $($graha.lord_sub_lord)"
        Write-Host "  Ruler of: $($graha.ruler_of)"
        Write-Host "  Is In: $($graha.is_in)"
        Write-Host "  Bhava Owner: $($graha.bhava_owner)"
        Write-Host "  Relationship: $($graha.relationship)"
        Write-Host "  Dignity: $($graha.dignity)"
    }
    
    Write-Host ""
    Write-Host "=================================" -ForegroundColor Green
    Write-Host "BHAVA TABLE:" -ForegroundColor Yellow
    Write-Host "-----------" -ForegroundColor Yellow
    foreach ($bhava in $response.data.bhava_table) {
        Write-Host ""
        Write-Host "Bhava $($bhava.bhava) ($($bhava.rashi)):" -ForegroundColor Cyan
        Write-Host "  Residents: $($bhava.residents)"
        Write-Host "  Owner: $($bhava.owner)"
        Write-Host "  Qualities: $($bhava.qualities)"
        Write-Host "  Aspected By: $($bhava.aspected_by)"
    }
    
    Write-Host ""
    Write-Host "=================================" -ForegroundColor Green
    Write-Host "Ayanamsa: $($response.data.ayanamsa)" -ForegroundColor Magenta
    Write-Host "Calculation Time: $($response.data.calculation_time)" -ForegroundColor Magenta
    
} catch {
    Write-Host "ERROR!" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}

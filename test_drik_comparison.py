"""
Test script to verify calculations match Drik Panchang exactly
Using Lahiri/Chitra Paksha Ayanamsa and Placidus House System
"""

import swisseph as swe
from datetime import datetime
import pytz
import json

def calculate_d1_chart(name, date_str, time_str, place, lat, lon, timezone_str):
    """
    Calculate D1 chart exactly as Drik Panchang does
    
    Args:
        name: Person's name
        date_str: Date in YYYY-MM-DD format
        time_str: Time in HH:MM:SS format
        place: Place name
        lat: Latitude
        lon: Longitude
        timezone_str: Timezone (e.g., 'Asia/Kolkata')
    """
    
    # Parse date and time
    dt_parts = date_str.split('-')
    time_parts = time_str.split(':')
    
    year = int(dt_parts[0])
    month = int(dt_parts[1])
    day = int(dt_parts[2])
    hour = int(time_parts[0])
    minute = int(time_parts[1])
    second = int(time_parts[2])
    
    # Create datetime with timezone
    tz = pytz.timezone(timezone_str)
    birth_dt = datetime(year, month, day, hour, minute, second)
    birth_dt_local = tz.localize(birth_dt)
    birth_dt_utc = birth_dt_local.astimezone(pytz.UTC)
    
    # Calculate Julian Day
    jd = swe.julday(birth_dt_utc.year, birth_dt_utc.month, birth_dt_utc.day,
                    birth_dt_utc.hour + birth_dt_utc.minute/60.0 + birth_dt_utc.second/3600.0)
    
    # Set sidereal mode with Lahiri ayanamsa (Chitra Paksha)
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    ayanamsa = swe.get_ayanamsa_ut(jd)
    
    # Calculate houses using Placidus system
    houses, ascmc = swe.houses(jd, lat, lon, b'P')
    asc_tropical = ascmc[0]
    asc_sidereal = (asc_tropical - ayanamsa) % 360
    
    # Calculate all planets
    planets_data = []
    
    # Signs reference
    signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", 
             "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
    signs_sanskrit = ["Mesha", "Vrishabha", "Mithuna", "Karka", "Simha", "Kanya",
                      "Tula", "Vrishchika", "Dhanu", "Makara", "Kumbha", "Meena"]
    
    planet_ids = [
        (swe.SUN, "Sun", "Surya", "☉"),
        (swe.MOON, "Moon", "Chandra", "☾"),
        (swe.MERCURY, "Mercury", "Budha", "☿"),
        (swe.VENUS, "Venus", "Shukra", "♀"),
        (swe.MARS, "Mars", "Mangal", "♂"),
        (swe.JUPITER, "Jupiter", "Guru", "♃"),
        (swe.SATURN, "Saturn", "Shani", "♄"),
        (swe.MEAN_NODE, "Rahu", "Rahu", "☊"),
    ]
    
    for planet_id, eng_name, sanskrit_name, symbol in planet_ids:
        pos, ret = swe.calc_ut(jd, planet_id)
        trop_long = pos[0]
        sid_long = (trop_long - ayanamsa) % 360
        
        sign_num = int(sid_long / 30)
        deg_in_sign = sid_long % 30
        
        # Calculate DMS
        degrees = int(deg_in_sign)
        minutes = int((deg_in_sign - degrees) * 60)
        seconds = int(((deg_in_sign - degrees) * 60 - minutes) * 60)
        
        is_retro = pos[3] < 0
        
        planets_data.append({
            'name': eng_name,
            'sanskrit': sanskrit_name,
            'symbol': symbol,
            'longitude_decimal': sid_long,
            'degree_in_sign': deg_in_sign,
            'sign': signs[sign_num],
            'sign_sanskrit': signs_sanskrit[sign_num],
            'dms': f"{degrees:02d}° {signs_sanskrit[sign_num]} {minutes:02d}′ {seconds:02d}″",
            'retrograde': is_retro
        })
    
    # Calculate Ketu (opposite of Rahu)
    rahu_long = planets_data[-1]['longitude_decimal']
    ketu_long = (rahu_long + 180) % 360
    ketu_sign_num = int(ketu_long / 30)
    ketu_deg_in_sign = ketu_long % 30
    ketu_degrees = int(ketu_deg_in_sign)
    ketu_minutes = int((ketu_deg_in_sign - ketu_degrees) * 60)
    ketu_seconds = int(((ketu_deg_in_sign - ketu_degrees) * 60 - ketu_minutes) * 60)
    
    planets_data.append({
        'name': 'Ketu',
        'sanskrit': 'Ketu',
        'symbol': '☋',
        'longitude_decimal': ketu_long,
        'degree_in_sign': ketu_deg_in_sign,
        'sign': signs[ketu_sign_num],
        'sign_sanskrit': signs_sanskrit[ketu_sign_num],
        'dms': f"{ketu_degrees:02d}° {signs_sanskrit[ketu_sign_num]} {ketu_minutes:02d}′ {ketu_seconds:02d}″",
        'retrograde': True  # Ketu is always retrograde
    })
    
    # Lagna
    lagna_sign_num = int(asc_sidereal / 30)
    lagna_deg_in_sign = asc_sidereal % 30
    lagna_degrees = int(lagna_deg_in_sign)
    lagna_minutes = int((lagna_deg_in_sign - lagna_degrees) * 60)
    lagna_seconds = int(((lagna_deg_in_sign - lagna_degrees) * 60 - lagna_minutes) * 60)
    
    result = {
        'name': name,
        'date': date_str,
        'time': time_str,
        'place': place,
        'timezone': timezone_str,
        'ayanamsa': round(ayanamsa, 6),
        'lagna': {
            'longitude_decimal': asc_sidereal,
            'degree_in_sign': lagna_deg_in_sign,
            'sign': signs[lagna_sign_num],
            'sign_sanskrit': signs_sanskrit[lagna_sign_num],
            'dms': f"{lagna_degrees:02d}° {signs_sanskrit[lagna_sign_num]} {lagna_minutes:02d}′ {lagna_seconds:02d}″"
        },
        'planets': planets_data
    }
    
    return result


# Test with the birth data from your manual chart
print("="*80)
print("DRIK PANCHANG COMPARISON TEST")
print("="*80)
print()

# Calculate for the same birth data
result = calculate_d1_chart(
    name="Namrata Dixit",
    date_str="1989-09-16",  # Sept 16, 1989
    time_str="23:00:00",    # 11:00 PM IST
    place="Hardoi, Uttar Pradesh",
    lat=27.33699775,
    lon=80.09982319183257,
    timezone_str="Asia/Kolkata"
)

print(f"Name: {result['name']}")
print(f"Date: {result['date']}")
print(f"Time: {result['time']} ({result['timezone']})")
print(f"Place: {result['place']}")
print(f"Ayanamsa (Lahiri): {result['ayanamsa']}°")
print()

print("LAGNA (ASCENDANT):")
print(f"  {result['lagna']['dms']}")
print(f"  Decimal: {result['lagna']['longitude_decimal']:.6f}°")
print()

print("PLANETARY POSITIONS:")
print("-" * 80)
print(f"{'Planet':<15} {'Longitude':<25} {'Sign':<15} {'Retro':<5}")
print("-" * 80)

for planet in result['planets']:
    retro_mark = "↺" if planet['retrograde'] else ""
    print(f"{planet['sanskrit']:<15} {planet['dms']:<25} {planet['sign']:<15} {retro_mark:<5}")

print()
print("="*80)
print("COMPARE THESE VALUES WITH YOUR MANUAL DATA")
print("="*80)
print()
print("Expected from your manual data:")
print("  Lagna: 10° Mithun")
print("  Sun: 12° Kanya")
print("  Moon: 10° Kanya")
print("  Mercury: 03° Kanya")
print("  Venus: 26° Tula")
print("  Mars: 12° Kanya")
print("  Jupiter: 15° Mithuna")
print("  Saturn: 13° Dhanu")
print("  Rahu: 29° Makara")
print("  Ketu: 29° Karka")

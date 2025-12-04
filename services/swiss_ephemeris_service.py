"""
Swiss Ephemeris Service
Handles all interactions with the Swiss Ephemeris library
"""
import swisseph as swe
import math
from datetime import datetime, timezone
from typing import Tuple, List, Dict
import pytz
from models.astrology_models import Planet, Zodiac, Nakshatra, PlanetPosition


class SwissEphemerisService:
    """Service class for Swiss Ephemeris calculations"""
    
    def __init__(self, ephe_path: str = "./ephe"):
        """
        Initialize Swiss Ephemeris with ephemeris files path
        
        Args:
            ephe_path: Path to Swiss Ephemeris data files
        """
        self.ephe_path = ephe_path
        swe.set_ephe_path(ephe_path)
        
        # Planet mapping for Swiss Ephemeris
        self.planet_map = {
            Planet.SUN: swe.SUN,
            Planet.MOON: swe.MOON,
            Planet.MERCURY: swe.MERCURY,
            Planet.VENUS: swe.VENUS,
            Planet.MARS: swe.MARS,
            Planet.JUPITER: swe.JUPITER,
            Planet.SATURN: swe.SATURN,
            Planet.URANUS: swe.URANUS,
            Planet.NEPTUNE: swe.NEPTUNE,
            Planet.PLUTO: swe.PLUTO,
            Planet.RAHU: swe.MEAN_NODE,  # Mean North Node
        }
        
        # Nakshatra data with degrees and rulers
        self.nakshatras = self._initialize_nakshatras()
    
    def _initialize_nakshatras(self) -> List[Dict]:
        """Initialize nakshatra data with degrees and rulers"""
        nakshatras = [
            {"name": Nakshatra.ASHWINI, "start": 0, "end": 13.333333, "ruler": Planet.KETU, "symbol": "Horse Head", "deity": "Ashwin Kumaras"},
            {"name": Nakshatra.BHARANI, "start": 13.333333, "end": 26.666667, "ruler": Planet.VENUS, "symbol": "Yoni", "deity": "Yama"},
            {"name": Nakshatra.KRITTIKA, "start": 26.666667, "end": 40, "ruler": Planet.SUN, "symbol": "Knife", "deity": "Agni"},
            {"name": Nakshatra.ROHINI, "start": 40, "end": 53.333333, "ruler": Planet.MOON, "symbol": "Cart", "deity": "Brahma"},
            {"name": Nakshatra.MRIGASHIRA, "start": 53.333333, "end": 66.666667, "ruler": Planet.MARS, "symbol": "Deer Head", "deity": "Soma"},
            {"name": Nakshatra.ARDRA, "start": 66.666667, "end": 80, "ruler": Planet.RAHU, "symbol": "Teardrop", "deity": "Rudra"},
            {"name": Nakshatra.PUNARVASU, "start": 80, "end": 93.333333, "ruler": Planet.JUPITER, "symbol": "Bow and Quiver", "deity": "Aditi"},
            {"name": Nakshatra.PUSHYA, "start": 93.333333, "end": 106.666667, "ruler": Planet.SATURN, "symbol": "Cow's Udder", "deity": "Brihaspati"},
            {"name": Nakshatra.ASHLESHA, "start": 106.666667, "end": 120, "ruler": Planet.MERCURY, "symbol": "Serpent", "deity": "Sarpa"},
            {"name": Nakshatra.MAGHA, "start": 120, "end": 133.333333, "ruler": Planet.KETU, "symbol": "Throne", "deity": "Pitru"},
            {"name": Nakshatra.PURVA_PHALGUNI, "start": 133.333333, "end": 146.666667, "ruler": Planet.VENUS, "symbol": "Hammock", "deity": "Bhaga"},
            {"name": Nakshatra.UTTARA_PHALGUNI, "start": 146.666667, "end": 160, "ruler": Planet.SUN, "symbol": "Bed", "deity": "Aryaman"},
            {"name": Nakshatra.HASTA, "start": 160, "end": 173.333333, "ruler": Planet.MOON, "symbol": "Hand", "deity": "Savitar"},
            {"name": Nakshatra.CHITRA, "start": 173.333333, "end": 186.666667, "ruler": Planet.MARS, "symbol": "Pearl", "deity": "Vishvakarma"},
            {"name": Nakshatra.SWATI, "start": 186.666667, "end": 200, "ruler": Planet.RAHU, "symbol": "Blade of Grass", "deity": "Vayu"},
            {"name": Nakshatra.VISHAKHA, "start": 200, "end": 213.333333, "ruler": Planet.JUPITER, "symbol": "Archway", "deity": "Indra-Agni"},
            {"name": Nakshatra.ANURADHA, "start": 213.333333, "end": 226.666667, "ruler": Planet.SATURN, "symbol": "Lotus", "deity": "Mitra"},
            {"name": Nakshatra.JYESHTHA, "start": 226.666667, "end": 240, "ruler": Planet.MERCURY, "symbol": "Earring", "deity": "Indra"},
            {"name": Nakshatra.MULA, "start": 240, "end": 253.333333, "ruler": Planet.KETU, "symbol": "Root", "deity": "Nirrti"},
            {"name": Nakshatra.PURVA_ASHADHA, "start": 253.333333, "end": 266.666667, "ruler": Planet.VENUS, "symbol": "Fan", "deity": "Apas"},
            {"name": Nakshatra.UTTARA_ASHADHA, "start": 266.666667, "end": 280, "ruler": Planet.SUN, "symbol": "Elephant Tusk", "deity": "Vishve Devas"},
            {"name": Nakshatra.SHRAVANA, "start": 280, "end": 293.333333, "ruler": Planet.MOON, "symbol": "Ear", "deity": "Vishnu"},
            {"name": Nakshatra.DHANISHTA, "start": 293.333333, "end": 306.666667, "ruler": Planet.MARS, "symbol": "Drum", "deity": "Vasu"},
            {"name": Nakshatra.SHATABHISHA, "start": 306.666667, "end": 320, "ruler": Planet.RAHU, "symbol": "Circle", "deity": "Varuna"},
            {"name": Nakshatra.PURVA_BHADRAPADA, "start": 320, "end": 333.333333, "ruler": Planet.JUPITER, "symbol": "Sword", "deity": "Aja Ekapada"},
            {"name": Nakshatra.UTTARA_BHADRAPADA, "start": 333.333333, "end": 346.666667, "ruler": Planet.SATURN, "symbol": "Snake", "deity": "Ahir Budhnya"},
            {"name": Nakshatra.REVATI, "start": 346.666667, "end": 360, "ruler": Planet.MERCURY, "symbol": "Fish", "deity": "Pushan"}
        ]
        return nakshatras
    
    def convert_to_julian_day(self, birth_datetime: str, timezone_offset: float) -> float:
        """
        Convert birth datetime to Julian Day Number
        
        Args:
            birth_datetime: Birth datetime in ISO format (YYYY-MM-DDTHH:MM:SS)
            timezone_offset: Timezone offset in hours (e.g., 5.5 for IST, -5 for EST)
            
        Returns:
            Julian Day Number
        """
        # Parse datetime
        dt = datetime.fromisoformat(birth_datetime)
        
        # Calculate UTC time by subtracting timezone offset
        utc_hour = dt.hour - timezone_offset
        utc_minute = dt.minute
        utc_second = dt.second
        
        # Handle day overflow/underflow
        utc_day = dt.day
        utc_month = dt.month
        utc_year = dt.year
        
        # Adjust for hour overflow
        if utc_hour >= 24:
            utc_hour -= 24
            utc_day += 1
        elif utc_hour < 0:
            utc_hour += 24
            utc_day -= 1
        
        # Simple day adjustment (Swiss Ephemeris handles complex cases)
        # Calculate Julian Day
        julian_day = swe.julday(
            utc_year, utc_month, utc_day,
            utc_hour + utc_minute/60.0 + utc_second/3600.0
        )
        
        return julian_day
    
    def calculate_ayanamsa(self, julian_day: float) -> float:
        """
        Calculate Ayanamsa (precession correction)
        
        Args:
            julian_day: Julian Day Number
            
        Returns:
            Ayanamsa value in degrees
        """
        # Use Lahiri Ayanamsa (most commonly used in India)
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        return swe.get_ayanamsa(julian_day)
    
    def get_planet_position(self, planet: Planet, julian_day: float) -> Tuple[float, float, float, float]:
        """
        Get planet position using Swiss Ephemeris
        
        Args:
            planet: Planet enum
            julian_day: Julian Day Number
            
        Returns:
            Tuple of (longitude, latitude, distance, speed)
        """
        if planet == Planet.KETU:
            # Ketu is 180 degrees opposite to Rahu
            rahu_pos = swe.calc_ut(julian_day, swe.MEAN_NODE)[0]
            longitude = (rahu_pos[0] + 180) % 360
            return (longitude, 0, 0, rahu_pos[3])
        
        swe_planet = self.planet_map.get(planet)
        if swe_planet is None:
            raise ValueError(f"Unknown planet: {planet}")
        
        result = swe.calc_ut(julian_day, swe_planet)
        return result[0][:4]  # longitude, latitude, distance, speed
    
    def calculate_houses(self, julian_day: float, latitude: float, longitude: float) -> List[float]:
        """
        Calculate house cusps using Placidus system
        
        Args:
            julian_day: Julian Day Number
            latitude: Birth latitude
            longitude: Birth longitude
            
        Returns:
            List of 12 house cusp longitudes
        """
        houses_result = swe.houses(julian_day, latitude, longitude, b'P')  # Placidus system
        return houses_result[0]  # House cusps
    
    def calculate_ascendant(self, julian_day: float, latitude: float, longitude: float) -> float:
        """
        Calculate ascendant (Lagna)
        
        Args:
            julian_day: Julian Day Number
            latitude: Birth latitude
            longitude: Birth longitude
            
        Returns:
            Ascendant longitude in degrees
        """
        houses_result = swe.houses(julian_day, latitude, longitude, b'P')
        return houses_result[1][0]  # Ascendant is the first value in cusps
    
    def longitude_to_zodiac_sign(self, longitude: float) -> Zodiac:
        """Convert longitude to zodiac sign"""
        sign_number = int(longitude / 30) + 1
        return Zodiac(sign_number)
    
    def longitude_to_nakshatra(self, longitude: float) -> Tuple[Nakshatra, int]:
        """
        Convert longitude to nakshatra and pada
        
        Args:
            longitude: Longitude in degrees
            
        Returns:
            Tuple of (Nakshatra, pada)
        """
        for nak_data in self.nakshatras:
            if nak_data["start"] <= longitude < nak_data["end"]:
                # Calculate pada (1-4)
                pada_size = (nak_data["end"] - nak_data["start"]) / 4
                pada = int((longitude - nak_data["start"]) / pada_size) + 1
                return (nak_data["name"], pada)
        
        # Handle edge case for last nakshatra (Revati)
        return (Nakshatra.REVATI, 4)
    
    def is_planet_retrograde(self, speed: float) -> bool:
        """Check if planet is retrograde based on speed"""
        return speed < 0
    
    def calculate_sunrise_sunset(self, julian_day: float, latitude: float, longitude: float) -> Dict[str, str]:
        """
        Calculate sunrise and sunset times
        
        Args:
            julian_day: Julian Day Number
            latitude: Birth latitude  
            longitude: Birth longitude
            
        Returns:
            Dictionary with sunrise and sunset times
        """
        try:
            # Set geographic location
            geopos = [longitude, latitude, 0]
            
            # Calculate sunrise
            # rise_trans(jd_start, body, geopos, atpress, attemp, rsmi)
            sunrise_result = swe.rise_trans(
                julian_day - 1, swe.SUN, geopos, 1013.25, 15, 1 | swe.CALC_RISE
            )
            
            # Calculate sunset
            sunset_result = swe.rise_trans(
                julian_day - 1, swe.SUN, geopos, 1013.25, 15, 1 | swe.CALC_SET
            )
            
            # Convert Julian Day back to datetime if successful
            if sunrise_result[0] >= 0:
                sunrise_dt = swe.jdut1_to_utc(sunrise_result[1], 1)  # 1 for Gregorian calendar
                sunrise_str = f"{sunrise_dt[0]:04d}-{sunrise_dt[1]:02d}-{sunrise_dt[2]:02d}T{sunrise_dt[3]:02d}:{sunrise_dt[4]:02d}:{int(sunrise_dt[5]):02d}"
            else:
                sunrise_str = "N/A"
                
            if sunset_result[0] >= 0:
                sunset_dt = swe.jdut1_to_utc(sunset_result[1], 1)
                sunset_str = f"{sunset_dt[0]:04d}-{sunset_dt[1]:02d}-{sunset_dt[2]:02d}T{sunset_dt[3]:02d}:{sunset_dt[4]:02d}:{int(sunset_dt[5]):02d}"
            else:
                sunset_str = "N/A"
            
            return {
                "sunrise": sunrise_str,
                "sunset": sunset_str
            }
        except Exception as e:
            # If rise_trans fails, return estimated times
            return {
                "sunrise": "06:00:00",
                "sunset": "18:00:00"
            }
    
    def __del__(self):
        """Cleanup Swiss Ephemeris resources"""
        swe.close()
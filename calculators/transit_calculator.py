"""
Transit Calculator
Calculates current planetary transits through houses for major planets
"""
from datetime import datetime, timezone
from typing import Dict, List
import math

from models.astrology_models import UserDetails, Planet, Zodiac
from services.swiss_ephemeris_service import SwissEphemerisService
from utils.vedic_helper import VedicAstrologyHelper


class TransitCalculator:
    """Calculate planetary transits through natal chart houses"""
    
    # Major planets for transit analysis
    TRANSIT_PLANETS = [
        Planet.SATURN,
        Planet.JUPITER,
        Planet.MERCURY,
        Planet.MARS,
        Planet.VENUS,
        Planet.SUN,
        Planet.MOON
    ]
    
    def __init__(self, ephe_path: str = "./ephe"):
        self.ephemeris_service = SwissEphemerisService(ephe_path)
        self.vedic_helper = VedicAstrologyHelper()
    
    def calculate_transits(self, user_details: UserDetails, transit_date: datetime = None) -> Dict:
        """
        Calculate planetary transits for a specific date
        
        Args:
            user_details: Birth details for natal chart reference
            transit_date: Date to calculate transits for (default: current date/time)
        
        Returns:
            Dictionary with transit information
        """
        if transit_date is None:
            transit_date = datetime.now(timezone.utc)
        
        # Convert transit_date to ISO string format for ephemeris service
        transit_date_str = transit_date.strftime('%Y-%m-%dT%H:%M:%S')
        
        # Calculate natal chart basics
        natal_jd = self.ephemeris_service.convert_to_julian_day(
            user_details.datetime, user_details.timezone
        )
        natal_ayanamsa = self.ephemeris_service.calculate_ayanamsa(natal_jd)
        
        natal_ascendant = self.ephemeris_service.calculate_ascendant(
            natal_jd, user_details.latitude, user_details.longitude
        )
        natal_ascendant_sidereal = (natal_ascendant - natal_ayanamsa) % 360
        
        # Calculate transit positions
        transit_jd = self.ephemeris_service.convert_to_julian_day(
            transit_date_str, 0  # UTC
        )
        transit_ayanamsa = self.ephemeris_service.calculate_ayanamsa(transit_jd)
        
        # Get current planetary positions
        transit_positions = {}
        for planet in self.TRANSIT_PLANETS:
            # Get planet position (returns longitude, latitude, distance, speed)
            tropical_long, _, _, speed = self.ephemeris_service.get_planet_position(
                planet, transit_jd
            )
            sidereal_long = (tropical_long - transit_ayanamsa) % 360
            
            # Calculate house position (from natal ascendant)
            house_number = self._calculate_house_from_ascendant(
                sidereal_long, natal_ascendant_sidereal
            )
            
            # Get sign information
            sign_num = int(sidereal_long / 30)
            sign_zodiac = Zodiac(sign_num + 1)  # Zodiac enum is 1-12, not 0-11
            sign_name = self.vedic_helper.get_sign_name(sign_zodiac)
            sign_short = self.vedic_helper.get_sign_short_name(sign_zodiac)
            
            # Degrees within sign
            degrees_in_sign = sidereal_long % 30
            
            # Check if retrograde based on speed
            is_retrograde = self.ephemeris_service.is_planet_retrograde(speed)
            
            transit_positions[planet.name] = {
                "planet": planet.name,
                "longitude": round(sidereal_long, 4),
                "sign": sign_name,
                "sign_sanskrit": sign_short,
                "sign_number": sign_num + 1,
                "degrees_in_sign": round(degrees_in_sign, 4),
                "house": house_number,
                "is_retrograde": is_retrograde
            }
        
        # Format transit_date for response (YYYY-MM-DDTHH:MM:SS format)
        if isinstance(transit_date, str):
            transit_date_response = transit_date
        else:
            # Format without timezone info for clean response
            transit_date_response = transit_date.strftime('%Y-%m-%dT%H:%M:%S')
        
        return {
            "natal_ascendant": {
                "longitude": round(natal_ascendant_sidereal, 4),
                "sign": self.vedic_helper.get_sign_name(Zodiac(int(natal_ascendant_sidereal / 30) + 1)),
                "sign_sanskrit": self.vedic_helper.get_sign_short_name(Zodiac(int(natal_ascendant_sidereal / 30) + 1))
            },
            "transit_date": transit_date_response,
            "ayanamsa": round(transit_ayanamsa, 4),
            "transits": transit_positions
        }
    
    def _calculate_house_from_ascendant(self, planet_longitude: float, ascendant_longitude: float) -> int:
        """
        Calculate which house a planet is in based on natal ascendant
        Uses equal house system: each house is 30 degrees from ascendant
        """
        # Calculate angular distance from ascendant
        distance = (planet_longitude - ascendant_longitude) % 360
        
        # Each house is 30 degrees
        house = int(distance / 30) + 1
        
        return house
    
    def _check_retrograde(self, julian_day: float, planet: Planet) -> bool:
        """Check if planet is retrograde by comparing speed"""
        try:
            # Get position slightly before and after
            pos_before = self.ephemeris_service.calculate_planet_position(
                julian_day - 0.1, planet
            )
            pos_after = self.ephemeris_service.calculate_planet_position(
                julian_day + 0.1, planet
            )
            
            # Calculate angular difference considering 360-degree wraparound
            diff = pos_after - pos_before
            if diff > 180:
                diff -= 360
            elif diff < -180:
                diff += 360
            
            # Negative difference means retrograde
            return diff < 0
        except:
            return False
    
    def get_major_transits(self, user_details: UserDetails, transit_date: datetime = None) -> Dict:
        """
        Get transits for major slow-moving planets only (Saturn, Jupiter, Mercury)
        
        Args:
            user_details: Birth details
            transit_date: Date to calculate transits for
        
        Returns:
            Dictionary with Saturn, Jupiter, and Mercury transits
        """
        all_transits = self.calculate_transits(user_details, transit_date)
        
        # Filter for major planets
        major_planets = ["SATURN", "JUPITER", "MERCURY"]
        major_transits = {
            planet: data 
            for planet, data in all_transits["transits"].items() 
            if planet in major_planets
        }
        
        return {
            "natal_ascendant": all_transits["natal_ascendant"],
            "transit_date": all_transits["transit_date"],
            "ayanamsa": all_transits["ayanamsa"],
            "major_transits": major_transits
        }

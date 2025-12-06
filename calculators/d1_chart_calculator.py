"""
D1 Chart Calculator
Main engine for calculating Rashi (D1) chart with all astronomical data
"""
from datetime import datetime, timezone
from typing import List, Dict
import math

from models.astrology_models import (
    UserDetails, D1Chart, PlanetPosition, HouseData, NakshatraDetails,
    SunMoonShine, Planet, Zodiac, Nakshatra
)
from services.swiss_ephemeris_service import SwissEphemerisService
from utils.vedic_helper import VedicAstrologyHelper


class D1ChartCalculator:
    """Main calculator for D1 Rashi chart"""
    
    def __init__(self, ephe_path: str = "./ephe"):
        """
        Initialize D1 Chart Calculator
        
        Args:
            ephe_path: Path to Swiss Ephemeris data files
        """
        self.ephemeris_service = SwissEphemerisService(ephe_path)
        self.vedic_helper = VedicAstrologyHelper()
        
        # Zodiac sign rulers
        self.sign_rulers = VedicAstrologyHelper.SIGN_LORDS
    
    def calculate_d1_chart(self, user_details: UserDetails) -> D1Chart:
        """
        Calculate complete D1 chart
        
        Args:
            user_details: User birth details
            
        Returns:
            Complete D1Chart object with all calculations
        """
        # Convert to Julian Day
        julian_day = self.ephemeris_service.convert_to_julian_day(
            user_details.datetime, user_details.timezone
        )
        
        # Calculate Ayanamsa
        ayanamsa = self.ephemeris_service.calculate_ayanamsa(julian_day)
        
        # Calculate Ascendant
        ascendant_longitude = self.ephemeris_service.calculate_ascendant(
            julian_day, user_details.latitude, user_details.longitude
        )
        
        # Apply Ayanamsa for sidereal calculation
        sidereal_ascendant = (ascendant_longitude - ayanamsa) % 360
        
        # Create Lagna position
        lagna = self._create_lagna_position(sidereal_ascendant)
        
        # Calculate all planet positions
        planets = self._calculate_planet_positions(julian_day, ayanamsa)
        
        # Calculate houses
        houses = self._calculate_houses(julian_day, user_details, ayanamsa, planets)
        
        # Enrich planets with Vedic details
        planets = self._enrich_planet_details(planets, houses)
        
        # Enrich houses with aspects and qualities
        houses = self._enrich_house_details(houses, planets)
        
        # Get nakshatra details
        nakshatra_details = self._get_nakshatra_details()
        
        # Calculate sun/moon shine
        sun_moon_shine = self._calculate_sun_moon_shine(
            julian_day, user_details.latitude, user_details.longitude, planets
        )
        
        return D1Chart(
            user_details=user_details,
            lagna=lagna,
            planets=planets,
            houses=houses,
            nakshatra_details=nakshatra_details,
            sun_moon_shine=sun_moon_shine,
            ayanamsa=ayanamsa,
            calculation_time=datetime.now(timezone.utc).isoformat()
        )
    
    def _create_lagna_position(self, longitude: float) -> PlanetPosition:
        """Create PlanetPosition object for Lagna"""
        sign = self.ephemeris_service.longitude_to_zodiac_sign(longitude)
        degree = longitude % 30
        nakshatra, pada = self.ephemeris_service.longitude_to_nakshatra(longitude)
        
        # Lagna is not a planet, but we use the same structure for consistency
        return PlanetPosition(
            planet=Planet.SUN,  # Placeholder - Lagna is not a planet
            longitude=longitude,
            latitude=0.0,
            distance=0.0,
            speed=0.0,
            sign=sign,
            degree=degree,
            nakshatra=nakshatra,
            nakshatra_pada=pada,
            retrograde=False
        )
    
    def _calculate_planet_positions(self, julian_day: float, ayanamsa: float) -> List[PlanetPosition]:
        """Calculate positions for all planets"""
        planets = []
        
        for planet in [Planet.SUN, Planet.MOON, Planet.MERCURY, Planet.VENUS,
                      Planet.MARS, Planet.JUPITER, Planet.SATURN, Planet.RAHU, Planet.KETU]:
            
            # Get tropical position
            longitude, latitude, distance, speed = self.ephemeris_service.get_planet_position(
                planet, julian_day
            )
            
            # Convert to sidereal
            sidereal_longitude = (longitude - ayanamsa) % 360
            
            # Calculate derived values
            sign = self.ephemeris_service.longitude_to_zodiac_sign(sidereal_longitude)
            degree = sidereal_longitude % 30
            nakshatra, pada = self.ephemeris_service.longitude_to_nakshatra(sidereal_longitude)
            retrograde = self.ephemeris_service.is_planet_retrograde(speed)
            
            planet_pos = PlanetPosition(
                planet=planet,
                longitude=sidereal_longitude,
                latitude=latitude,
                distance=distance,
                speed=speed,
                sign=sign,
                degree=degree,
                nakshatra=nakshatra,
                nakshatra_pada=pada,
                retrograde=retrograde
            )
            
            planets.append(planet_pos)
        
        return planets
    
    def _calculate_houses(self, julian_day: float, user_details: UserDetails, 
                         ayanamsa: float, planets: List[PlanetPosition]) -> List[HouseData]:
        """Calculate house cusps and determine planets in each house using Whole Sign houses"""
        
        # Get ascendant to determine house 1 sign (Whole Sign system)
        ascendant_longitude = self.ephemeris_service.calculate_ascendant(
            julian_day, user_details.latitude, user_details.longitude
        )
        sidereal_ascendant = (ascendant_longitude - ayanamsa) % 360
        
        # In Whole Sign system, house 1 starts at 0° of the ascendant's sign
        ascendant_sign_num = int(sidereal_ascendant / 30)
        
        houses = []
        
        for i in range(12):
            house_number = i + 1
            # Each house occupies one complete sign in Whole Sign system
            house_sign_num = (ascendant_sign_num + i) % 12
            cusp_longitude = house_sign_num * 30  # Start of sign
            sign = self.ephemeris_service.longitude_to_zodiac_sign(cusp_longitude)
            ruler_planet = self.sign_rulers[sign]
            
            # Find planets in this house (Whole Sign method)
            planets_in_house = self._find_planets_in_house_whole_sign(
                house_sign_num, planets
            )
            
            house_data = HouseData(
                house_number=house_number,
                cusp_longitude=cusp_longitude,
                sign=sign,
                ruler_planet=ruler_planet,
                planets_in_house=planets_in_house
            )
            
            houses.append(house_data)
        
        return houses
    
    def _find_planets_in_house_whole_sign(self, house_sign_num: int,
                                          planets: List[PlanetPosition]) -> List[Planet]:
        """Find which planets are in a house using Whole Sign system"""
        
        planets_in_house = []
        
        # In Whole Sign, a house occupies one complete sign (30 degrees)
        house_start = house_sign_num * 30
        house_end = (house_sign_num + 1) * 30
        
        for planet_pos in planets:
            planet_longitude = planet_pos.longitude
            
            # Check if planet is in this sign/house
            if house_start <= planet_longitude < house_end:
                planets_in_house.append(planet_pos.planet)
        
        return planets_in_house
    
    def _find_planets_in_house(self, house_number: int, house_cusps: List[float],
                              ayanamsa: float, planets: List[PlanetPosition]) -> List[Planet]:
        """Find which planets are positioned in a specific house (DEPRECATED - kept for compatibility)"""
        
        planets_in_house = []
        
        # Get current and next house cusp longitudes
        current_cusp = (house_cusps[house_number - 1] - ayanamsa) % 360
        next_cusp = (house_cusps[house_number % 12] - ayanamsa) % 360
        
        for planet_pos in planets:
            planet_longitude = planet_pos.longitude
            
            # Handle the case where house spans across 0 degrees
            if current_cusp > next_cusp:
                if planet_longitude >= current_cusp or planet_longitude < next_cusp:
                    planets_in_house.append(planet_pos.planet)
            else:
                if current_cusp <= planet_longitude < next_cusp:
                    planets_in_house.append(planet_pos.planet)
        
        return planets_in_house
    
    def _get_nakshatra_details(self) -> List[NakshatraDetails]:
        """Get detailed information for all 27 nakshatras"""
        
        nakshatra_details = []
        
        for nak_data in self.ephemeris_service.nakshatras:
            details = NakshatraDetails(
                name=nak_data["name"],
                ruler=nak_data["ruler"],
                degree_start=nak_data["start"],
                degree_end=nak_data["end"],
                symbol=nak_data["symbol"],
                deity=nak_data["deity"],
                quality="Sattva"  # Simplified - in real implementation, this varies
            )
            nakshatra_details.append(details)
        
        return nakshatra_details
    
    def _calculate_sun_moon_shine(self, julian_day: float, latitude: float,
                                 longitude: float, planets: List[PlanetPosition]) -> SunMoonShine:
        """Calculate sun and moon shine data"""
        
        # Get sunrise/sunset times
        sun_times = self.ephemeris_service.calculate_sunrise_sunset(
            julian_day, latitude, longitude
        )
        
        # Find Sun and Moon positions
        sun_pos = next(p for p in planets if p.planet == Planet.SUN)
        moon_pos = next(p for p in planets if p.planet == Planet.MOON)
        
        # Get sign names
        sun_sign_name = sun_pos.sign.name.title()
        sun_sign_sanskrit = self.vedic_helper.get_sign_sanskrit_name(sun_pos.sign)
        moon_sign_name = moon_pos.sign.name.title()
        moon_sign_sanskrit = self.vedic_helper.get_sign_sanskrit_name(moon_pos.sign)
        
        # Calculate moon phase (simplified)
        moon_sun_angle = abs(moon_pos.longitude - sun_pos.longitude)
        if moon_sun_angle > 180:
            moon_sun_angle = 360 - moon_sun_angle
        
        # Determine moon phase
        if moon_sun_angle < 45:
            moon_phase = "New"
        elif moon_sun_angle < 135:
            moon_phase = "Waxing" if moon_pos.longitude > sun_pos.longitude else "Waning"
        elif moon_sun_angle < 225:
            moon_phase = "Full"
        else:
            moon_phase = "Waning" if moon_pos.longitude > sun_pos.longitude else "Waxing"
        
        # Calculate strengths (simplified - based on nakshatra position)
        sun_strength = self._calculate_planet_strength(sun_pos)
        moon_strength = self._calculate_planet_strength(moon_pos)
        
        # Calculate Tithi (lunar day)
        tithi = int((moon_pos.longitude - sun_pos.longitude) % 360 / 12) + 1
        
        return SunMoonShine(
            sunrise_time=sun_times["sunrise"],
            sunset_time=sun_times["sunset"],
            moonrise_time="",  # Would need additional calculation
            moonset_time="",   # Would need additional calculation
            sun_strength=sun_strength,
            moon_strength=moon_strength,
            moon_phase=moon_phase,
            tithi=tithi,
            sun_sign=sun_sign_name,
            sun_sign_sanskrit=sun_sign_sanskrit,
            moon_sign=moon_sign_name,
            moon_sign_sanskrit=moon_sign_sanskrit
        )
    
    def _calculate_planet_strength(self, planet_pos: PlanetPosition) -> float:
        """
        Calculate basic planet strength (simplified)
        In real implementation, this would include:
        - Shadbala (six-fold strength)
        - Dignity (exaltation, own sign, debilitation)
        - Aspects
        - House position strength
        """
        
        # Basic strength based on degree position in sign
        degree = planet_pos.degree
        
        # Planets are strongest at middle of sign (15 degrees)
        strength = 100 - abs(15 - degree) * 2
        
        # Adjust for retrograde motion
        if planet_pos.retrograde:
            strength *= 0.8
        
        return max(0, min(100, strength))
    
    def _enrich_planet_details(self, planets: List[PlanetPosition], houses: List[HouseData]) -> List[PlanetPosition]:
        """Add Vedic astrology details to planet positions"""
        
        enriched_planets = []
        
        for planet_pos in planets:
            # Find which house the planet is in
            planet_house = None
            for house in houses:
                if planet_pos.planet in house.planets_in_house:
                    planet_house = house.house_number
                    break
            
            # Get nakshatra lord from ephemeris service
            nak_data = next((n for n in self.ephemeris_service.nakshatras if n["name"] == planet_pos.nakshatra), None)
            nakshatra_lord = nak_data["ruler"] if nak_data else None
            # Compute KP sub-lord based on absolute longitude
            sub_lord = None
            if nak_data:
                sub_lord = self.vedic_helper.get_sub_lord(planet_pos.longitude, nakshatra_lord)
            
            # Find which houses this planet rules (based on sign rulership)
            ruler_of_houses = []
            for house in houses:
                if house.ruler_planet == planet_pos.planet:
                    ruler_of_houses.append(house.house_number)
            
            # Get house owner (sign lord of the house planet is in)
            house_owner = None
            if planet_house:
                house_data = houses[planet_house - 1]
                house_owner = house_data.ruler_planet
            
            # Calculate relationship with house owner
            relationship = self.vedic_helper.get_planet_relationship(planet_pos.planet, house_owner) if house_owner else "-"
            
            # Calculate dignity
            dignity = self.vedic_helper.get_planet_dignity(planet_pos.planet, planet_pos.sign, planet_pos.degree)
            
            # Update planet position with enriched data
            planet_pos.nakshatra_lord = nakshatra_lord
            planet_pos.sub_lord = sub_lord if sub_lord else nakshatra_lord
            planet_pos.ruler_of_houses = ruler_of_houses
            planet_pos.is_in_house = planet_house
            planet_pos.house_owner = house_owner
            planet_pos.relationship = relationship
            planet_pos.dignity = dignity
            
            enriched_planets.append(planet_pos)
        
        return enriched_planets
    
    def _enrich_house_details(self, houses: List[HouseData], planets: List[PlanetPosition]) -> List[HouseData]:
        """Add aspects and qualities to house data"""
        
        enriched_houses = []
        
        # Create planet-house mapping for aspect calculation
        planet_houses = [(p.planet, p.is_in_house) for p in planets if p.is_in_house]
        
        for house in houses:
            # Get Sanskrit name
            house.sign_short_name = self.vedic_helper.get_sign_short_name(house.sign)
            
            # Get qualities
            gender = self.vedic_helper.SIGN_GENDER.get(house.sign, "")
            modality = self.vedic_helper.SIGN_MODALITY.get(house.sign, "")
            house.qualities = [gender[:3], modality]  # "Mas/Fem", "Movable/Fixed/Common"
            
            # Calculate aspects
            aspecting_planets = []
            for planet_pos in planets:
                if planet_pos.is_in_house and planet_pos.is_in_house != house.house_number:
                    # Calculate house difference
                    diff = (house.house_number - planet_pos.is_in_house) % 12
                    if diff == 0:
                        diff = 12
                    
                    # All planets aspect 7th house
                    if diff == 7:
                        aspecting_planets.append(planet_pos.planet)
                    # Mars special aspects (4th, 7th, 8th)
                    elif planet_pos.planet == Planet.MARS and diff in [4, 8]:
                        aspecting_planets.append(planet_pos.planet)
                    # Jupiter special aspects (5th, 7th, 9th)
                    elif planet_pos.planet == Planet.JUPITER and diff in [5, 9]:
                        aspecting_planets.append(planet_pos.planet)
                    # Saturn special aspects (3rd, 7th, 10th)
                    elif planet_pos.planet == Planet.SATURN and diff in [3, 10]:
                        aspecting_planets.append(planet_pos.planet)
            
            house.aspected_by = aspecting_planets
            enriched_houses.append(house)
        
        return enriched_houses
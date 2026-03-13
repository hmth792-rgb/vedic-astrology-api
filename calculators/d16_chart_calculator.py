"""
D16 Chart (Shodash Amsha) Calculator
Divisional chart for vehicles and conveyances
D16 divides each zodiac sign into 16 equal parts (1.875 degrees each)
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
from calculators.d1_chart_calculator import D1ChartCalculator


class D16ChartCalculator:
    """Calculator for D16 Shodash Amsha chart"""
    
    def __init__(self, ephe_path: str = "./ephe", nakshatra_epsilon: float = 1e-6,
                 node_ruler_override: Dict[Planet, List[int]] = None,
                 force_node_relationship_enemy: bool = False,
                 node_rulership_strategy: str = "nak_lord_rules",
                 sidereal_mode = None, ayanamsa_offset: float = -0.245877):
        """
        Initialize D16 Chart Calculator
        
        Args:
            ephe_path: Path to Swiss Ephemeris data files
            nakshatra_epsilon: Epsilon for nakshatra/pada boundary rounding (default 1e-6)
            node_ruler_override: Optional dict {Planet: [house_numbers]} to override node rulership
            force_node_relationship_enemy: If True, set node relationships to "Enemy"
            node_rulership_strategy: Strategy for computing node rulership
            sidereal_mode: Sidereal mode for calculations
            ayanamsa_offset: Offset applied ONLY to Lagna for Drik Panchang compatibility (default -0.245877)
        """
        self.ephemeris_service = SwissEphemerisService(ephe_path)
        if sidereal_mode is not None:
            try:
                self.ephemeris_service.set_sidereal_mode(sidereal_mode)
            except Exception:
                pass
        self.vedic_helper = VedicAstrologyHelper()

        self.sign_rulers = VedicAstrologyHelper.SIGN_LORDS
        self.nakshatra_epsilon = nakshatra_epsilon
        self.ayanamsa_offset = ayanamsa_offset

        self.node_ruler_override = node_ruler_override
        self.force_node_relationship_enemy = force_node_relationship_enemy
        self.node_rulership_strategy = node_rulership_strategy

        # Create D1 calculator using standard Swiss Ephemeris (no offset for planets)
        self.d1_calculator = D1ChartCalculator(
            ephe_path,
            node_rulership_strategy=self.node_rulership_strategy,
            nakshatra_epsilon=self.nakshatra_epsilon,
            sidereal_mode=self.ephemeris_service.sidereal_mode_name
        )
    
    def calculate_d16_chart(self, user_details: UserDetails, d1_chart: D1Chart = None) -> Dict:
        """
        Calculate D16 (Shodash Amsha) chart
        
        Args:
            user_details: User birth details
            d1_chart: Optional pre-calculated D1 chart
            
        Returns:
            Dictionary containing D16 chart data with planets in D16 divisions
        """
        if d1_chart is None:
            d1_chart = self.d1_calculator.calculate_d1_chart(user_details)
        
        # Convert all planets to D16 positions (standard ephemeris, no offset)
        d16_planets = []
        for planet in d1_chart.planets:
            d16_planet = self._convert_to_d16(planet)
            d16_planets.append(d16_planet)
        
        # Convert Lagna to D16 with special ayanamsa_offset handling
        d16_lagna = self._convert_to_d16_with_offset(d1_chart.lagna)
        
        # Calculate D16 houses
        d16_houses = self._calculate_d16_houses(d16_lagna, d16_planets)
        
        # Enrich Lagna with Vedic details
        d16_lagna = self._enrich_planet_with_vedic_details(d16_lagna, d16_houses, d16_planets)
        
        # Enrich planets with Vedic details
        enriched_planets = []
        for planet in d16_planets:
            enriched_planet = self._enrich_planet_with_vedic_details(planet, d16_houses, d16_planets)
            enriched_planets.append(enriched_planet)
        
        return {
            "chart_type": "D16 (Shodash Amsha)",
            "description": "Divisional chart for vehicles and conveyances",
            "lagna": d16_lagna,
            "planets": enriched_planets,
            "houses": d16_houses,
            "ayanamsa": d1_chart.ayanamsa
        }
    
    def _convert_to_d16(self, planet_position: PlanetPosition) -> PlanetPosition:
        """
        Convert D1 planet position to D16 (Shodash Amsha) position
        
        D16 Formula: Multiply absolute D1 longitude by 16 and mod 360
        This is the standard mathematical divisional chart formula.
        
        D16_Longitude = (D1_Longitude * 16) mod 360
        
        Args:
            planet_position: Planet position in D1 chart
            
        Returns:
            PlanetPosition with D16 longitude
        """
        # Standard mathematical Shodash Amsha: multiply absolute D1 longitude by 16 and mod 360
        abs_d1_long = planet_position.longitude  # absolute longitude 0-360 from D1
        d16_longitude = (abs_d1_long * 16.0) % 360.0

        # Derive sign and degree from absolute D16 longitude
        d16_sign_num = int(d16_longitude // 30) + 1
        d16_degree = d16_longitude % 30.0

        # Recalculate nakshatra and pada for the D16 longitude
        # Add a small epsilon to avoid boundary rounding differences with reference software
        nakshatra, pada = self.ephemeris_service.longitude_to_nakshatra(d16_longitude + self.nakshatra_epsilon)

        # Create new planet position with D16 longitude
        return PlanetPosition(
            planet=planet_position.planet,
            longitude=d16_longitude,
            latitude=planet_position.latitude,
            distance=planet_position.distance,
            speed=planet_position.speed,
            sign=Zodiac(d16_sign_num),  # Zodiac enum is 1-12
            degree=d16_degree,
            nakshatra=nakshatra,
            nakshatra_pada=pada,
            retrograde=planet_position.retrograde,
            nakshatra_lord=None,
            sub_lord=None
        )
    
    def _convert_to_d16_with_offset(self, lagna_position: PlanetPosition) -> PlanetPosition:
        """
        Convert D1 Lagna to D16 with special ayanamsa_offset handling
        
        The ayanamsa_offset is applied ONLY to Lagna (not to planets) to match Drik Panchang.
        This is done BEFORE the D16 conversion to avoid amplification.
        
        Args:
            lagna_position: Lagna position in D1 chart
            
        Returns:
            PlanetPosition with D16 Lagna longitude (offset-corrected)
        """
        # Apply ayanamsa offset to D1 Lagna BEFORE converting to D16
        # This corrects the Lagna for Drik Panchang compatibility
        offset_d1_long = lagna_position.longitude - self.ayanamsa_offset  # Subtract offset to correct
        offset_d1_long = offset_d1_long % 360.0  # Normalize
        
        # Now convert offset-corrected D1 Lagna to D16
        d16_longitude = (offset_d1_long * 16.0) % 360.0

        # Derive sign and degree from absolute D16 longitude
        d16_sign_num = int(d16_longitude // 30) + 1
        d16_degree = d16_longitude % 30.0

        # Recalculate nakshatra and pada for the offset-corrected D16 longitude
        nakshatra, pada = self.ephemeris_service.longitude_to_nakshatra(d16_longitude + self.nakshatra_epsilon)

        # Create new Lagna position with offset-corrected D16 longitude
        return PlanetPosition(
            planet=lagna_position.planet,
            longitude=d16_longitude,
            latitude=lagna_position.latitude,
            distance=lagna_position.distance,
            speed=lagna_position.speed,
            sign=Zodiac(d16_sign_num),  # Zodiac enum is 1-12
            degree=d16_degree,
            nakshatra=nakshatra,
            nakshatra_pada=pada,
            retrograde=lagna_position.retrograde,
            nakshatra_lord=None,
            sub_lord=None
        )
    
    def _calculate_d16_houses(self, d16_lagna: PlanetPosition, d16_planets: List[PlanetPosition]) -> List[HouseData]:
        """
        Calculate D16 houses based on D16 Lagna
        
        Args:
            d16_lagna: D16 Lagna position
            d16_planets: List of planets in D16 positions
            
        Returns:
            List of 12 HouseData objects
        """
        houses = []
        lagna_sign = d16_lagna.sign
        
        for house_num in range(1, 13):
            # Calculate house sign (Whole Sign system)
            sign_num = ((lagna_sign.value - 1 + house_num - 1) % 12) + 1
            sign = Zodiac(sign_num)
            
            # House cusp is at start of sign
            cusp_longitude = (sign_num - 1) * 30
            
            # Find planets in this house
            planets_in_house = [
                p for p in d16_planets 
                if p.sign == sign
            ]
            
            # Get sign lord
            sign_lord = self.sign_rulers[sign]
            
            house_data = HouseData(
                house_number=house_num,
                cusp_longitude=cusp_longitude,
                sign=sign,
                ruler_planet=sign_lord,
                planets_in_house=[p.planet for p in planets_in_house],
                sign_short_name=self.vedic_helper.get_sign_short_name(sign)
            )
            houses.append(house_data)
        
        return houses
    
    def _enrich_planet_with_vedic_details(self, planet: PlanetPosition, 
                                         houses: List[HouseData],
                                         all_planets: List[PlanetPosition]) -> PlanetPosition:
        """
        Enrich planet with Vedic astrology details
        
        Args:
            planet: Planet position to enrich
            houses: List of houses
            all_planets: All planets in chart
            
        Returns:
            Enriched PlanetPosition
        """
        # Nakshatra and pada already calculated in _convert_to_d16
        nak_entry = next((n for n in self.ephemeris_service.nakshatras if n["name"] == planet.nakshatra), None)
        if nak_entry:
            planet.nakshatra_lord = nak_entry["ruler"]
        
        # Calculate KP sub-lord
        if planet.nakshatra_lord:
            planet.sub_lord = self.vedic_helper.get_sub_lord(
                planet.longitude, planet.nakshatra_lord,
                ephe_service=self.ephemeris_service,
                epsilon=self.nakshatra_epsilon
            )
        
        # Find which house this planet is in
        planet_house = next((h for h in houses if planet.sign == h.sign), None)
        
        # Get sign lord
        sign_lord = self.sign_rulers[planet.sign]
        
        # Determine relationship with sign lord
        relationship = self.vedic_helper.get_planet_relationship(planet.planet, sign_lord)
        
        # Get dignities
        dignity = self.vedic_helper.get_planet_dignity(planet.planet, planet.sign, planet.degree)
        
        # Find houses ruled by this planet
        ruled_houses = [h.house_number for h in houses if h.ruler_planet == planet.planet]
        
        # Special case: Lagna (with planet = SUN marker) always rules house 1
        if planet.planet == Planet.SUN and planet_house and planet_house.house_number == 1:
            ruled_houses = [1]
        # Special handling for Rahu and Ketu node rulership
        # In Vedic astrology, Rahu and Ketu are shadow planets (nodes) without sign rulership
        # They do not rule any zodiac signs or houses
        elif planet.planet == Planet.RAHU or planet.planet == Planet.KETU:
            # Nodes don't rule any houses - show as empty
            ruled_houses = []
        
        # Update planet with enriched data
        planet.is_in_house = planet_house.house_number if planet_house else None
        planet.house_owner = sign_lord
        planet.relationship = relationship
        planet.dignity = dignity if dignity and dignity != "-" else "-"
        planet.ruler_of_houses = sorted(ruled_houses)
        
        return planet

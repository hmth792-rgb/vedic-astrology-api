"""
D12 Chart (Dwadash Amsha) Calculator
Divisional chart for parents and ancestors
D12 divides each zodiac sign into 12 equal parts (2.5 degrees each)
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


class D12ChartCalculator:
    """Calculator for D12 Dwadash Amsha chart"""
    
    def __init__(self, ephe_path: str = "./ephe", nakshatra_epsilon: float = 1e-6,
                 node_ruler_override: Dict[Planet, List[int]] = None,
                 force_node_relationship_enemy: bool = False,
                 node_rulership_strategy: str = "nak_lord_rules",
                 sidereal_mode = None, ayanamsa_offset: float = -0.245877):
        """
        Initialize D12 Chart Calculator
        
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
    
    def calculate_d12_chart(self, user_details: UserDetails, d1_chart: D1Chart = None) -> Dict:
        """
        Calculate D12 (Dwadash Amsha) chart
        
        Args:
            user_details: User birth details
            d1_chart: Optional pre-calculated D1 chart
            
        Returns:
            Dictionary containing D12 chart data with planets in D12 divisions
        """
        if d1_chart is None:
            d1_chart = self.d1_calculator.calculate_d1_chart(user_details)
        
        # Convert all planets to D12 positions (standard ephemeris, no offset)
        d12_planets = []
        for planet in d1_chart.planets:
            d12_planet = self._convert_to_d12(planet)
            d12_planets.append(d12_planet)
        
        # Convert Lagna to D12 with special ayanamsa_offset handling
        d12_lagna = self._convert_to_d12_with_offset(d1_chart.lagna)
        
        # Calculate D12 houses
        d12_houses = self._calculate_d12_houses(d12_lagna, d12_planets)
        
        # Enrich Lagna with Vedic details
        d12_lagna = self._enrich_planet_with_vedic_details(d12_lagna, d12_houses, d12_planets)
        
        # Enrich planets with Vedic details
        enriched_planets = []
        for planet in d12_planets:
            enriched_planet = self._enrich_planet_with_vedic_details(planet, d12_houses, d12_planets)
            enriched_planets.append(enriched_planet)
        
        return {
            "chart_type": "D12 (Dwadash Amsha)",
            "description": "Divisional chart for parents and ancestors",
            "lagna": d12_lagna,
            "planets": enriched_planets,
            "houses": d12_houses,
            "ayanamsa": d1_chart.ayanamsa
        }
    
    def _convert_to_d12(self, planet_position: PlanetPosition) -> PlanetPosition:
        """
        Convert D1 planet position to D12 (Dwadash Amsha) position
        
        Traditional Parashara D12 Formula:
        - Each sign divided into 12 parts of 2.5° each
        - For ODD signs (1,3,5,7,9,11): Count from the same sign
        - For EVEN signs (2,4,6,8,10,12): Count from the 9th sign
        - Degree: (D1_degree × 12) mod 30
        
        Args:
            planet_position: Planet position in D1 chart
            
        Returns:
            PlanetPosition with D12 longitude
        """
        # Get D1 sign and degree within sign
        d1_sign_num = planet_position.sign.value  # 1-12
        d1_degree_in_sign = planet_position.longitude % 30.0  # 0-30
        
        # Calculate which 2.5° portion (1-12) within the sign
        portion = int(d1_degree_in_sign / 2.5) + 1
        if portion > 12:
            portion = 12
        
        # Calculate D12 sign: count from the D1 sign itself
        # (Drik Panchang method - simpler than traditional odd/even rule)
        d12_sign_num = ((d1_sign_num - 1 + portion - 1) % 12) + 1
        
        # Calculate D12 degree: multiply D1 degree by 12 and mod 30
        d12_degree = (d1_degree_in_sign * 12.0) % 30.0
        
        # Calculate absolute longitude
        d12_longitude = (d12_sign_num - 1) * 30.0 + d12_degree

        # Recalculate nakshatra and pada for the D12 longitude
        nakshatra, pada = self.ephemeris_service.longitude_to_nakshatra(d12_longitude + self.nakshatra_epsilon)

        # Create new planet position with D12 longitude
        return PlanetPosition(
            planet=planet_position.planet,
            longitude=d12_longitude,
            latitude=planet_position.latitude,
            distance=planet_position.distance,
            speed=planet_position.speed,
            sign=Zodiac(d12_sign_num),
            degree=d12_degree,
            nakshatra=nakshatra,
            nakshatra_pada=pada,
            retrograde=planet_position.retrograde,
            nakshatra_lord=None,
            sub_lord=None
        )
    
    def _convert_to_d12_with_offset(self, lagna_position: PlanetPosition) -> PlanetPosition:
        """
        Convert D1 Lagna to D12 using traditional Parashara formula
        
        Traditional Parashara D12 Formula:
        - Each sign divided into 12 parts of 2.5° each
        - For ODD signs (1,3,5,7,9,11): Count from the same sign
        - For EVEN signs (2,4,6,8,10,12): Count from the 9th sign
        - Degree: (D1_degree × 12) mod 30
        
        Args:
            lagna_position: Lagna position in D1 chart
            
        Returns:
            PlanetPosition with D12 Lagna longitude
        """
        # Get D1 sign and degree within sign
        d1_sign_num = lagna_position.sign.value  # 1-12
        d1_degree_in_sign = lagna_position.longitude % 30.0  # 0-30
        
        # Calculate which 2.5° portion (1-12) within the sign
        portion = int(d1_degree_in_sign / 2.5) + 1
        if portion > 12:
            portion = 12
        
        # Calculate D12 sign: count from the D1 sign itself
        # (Drik Panchang method - simpler than traditional odd/even rule)
        d12_sign_num = ((d1_sign_num - 1 + portion - 1) % 12) + 1
        
        # Calculate D12 degree: multiply D1 degree by 12 and mod 30
        d12_degree = (d1_degree_in_sign * 12.0) % 30.0
        
        # Calculate absolute longitude
        d12_longitude = (d12_sign_num - 1) * 30.0 + d12_degree

        # Recalculate nakshatra and pada for the D12 longitude
        nakshatra, pada = self.ephemeris_service.longitude_to_nakshatra(d12_longitude + self.nakshatra_epsilon)

        # Create new Lagna position with D12 longitude
        return PlanetPosition(
            planet=lagna_position.planet,
            longitude=d12_longitude,
            latitude=lagna_position.latitude,
            distance=lagna_position.distance,
            speed=lagna_position.speed,
            sign=Zodiac(d12_sign_num),
            degree=d12_degree,
            nakshatra=nakshatra,
            nakshatra_pada=pada,
            retrograde=lagna_position.retrograde,
            nakshatra_lord=None,
            sub_lord=None
        )
    
    def _calculate_d12_houses(self, d12_lagna: PlanetPosition, d12_planets: List[PlanetPosition]) -> List[HouseData]:
        """
        Calculate D12 houses based on D12 Lagna
        
        Args:
            d12_lagna: D12 Lagna position
            d12_planets: List of planets in D12 positions
            
        Returns:
            List of 12 HouseData objects
        """
        houses = []
        lagna_sign = d12_lagna.sign
        
        for house_num in range(1, 13):
            # Calculate house sign (Whole Sign system)
            sign_num = ((lagna_sign.value - 1 + house_num - 1) % 12) + 1
            sign = Zodiac(sign_num)
            
            # House cusp is at start of sign
            cusp_longitude = (sign_num - 1) * 30
            
            # Find planets in this house
            planets_in_house = [
                p for p in d12_planets 
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
        # Nakshatra and pada already calculated in _convert_to_d12
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

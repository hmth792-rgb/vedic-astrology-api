"""
D2 Chart (Hora) Calculator
Divisional chart for wealth, fortune, and material prosperity
D2 divides each zodiac sign into 2 equal parts (15 degrees each)
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


class D2ChartCalculator:
    """Calculator for D2 Hora chart"""
    
    def __init__(self, ephe_path: str = "./ephe", nakshatra_epsilon: float = 1e-6,
                 node_ruler_override: Dict[Planet, List[int]] = None,
                 force_node_relationship_enemy: bool = False,
                 node_rulership_strategy: str = "nak_lord_rules",
                 sidereal_mode = None):
        """
        Initialize D2 Chart Calculator
        
        Args:
            ephe_path: Path to Swiss Ephemeris data files
            nakshatra_epsilon: Epsilon for nakshatra/pada boundary rounding (default 1e-6)
            node_ruler_override: Optional dict {Planet: [house_numbers]} to override node rulership
            force_node_relationship_enemy: If True, set node relationships to "Enemy"
            node_rulership_strategy: Strategy for computing node rulership:
                - "nak_lord_rules": node rules houses of its nakshatra-lord (default)
                - "drik_compat": Drik Panchang compatible (uses nakshatra-lord position with offset)
        """
        self.ephemeris_service = SwissEphemerisService(ephe_path)
        if sidereal_mode is not None:
            try:
                self.ephemeris_service.set_sidereal_mode(sidereal_mode)
            except Exception:
                pass
        self.vedic_helper = VedicAstrologyHelper()

        # small epsilon used when mapping longitudes to nakshatras/padas to
        # reduce boundary mismatches with reference software (tweakable)
        self.sign_rulers = VedicAstrologyHelper.SIGN_LORDS
        self.nakshatra_epsilon = nakshatra_epsilon

        # Optional hard-coded node rulership override to match reference conventions
        self.node_ruler_override = node_ruler_override
        # If True, force node relationship to 'Enemy' as per some references
        self.force_node_relationship_enemy = force_node_relationship_enemy
        # Strategy for node rulership calculation
        self.node_rulership_strategy = node_rulership_strategy

        # Create D1 calculator
        self.d1_calculator = D1ChartCalculator(
            ephe_path,
            node_rulership_strategy=self.node_rulership_strategy,
            nakshatra_epsilon=self.nakshatra_epsilon,
            sidereal_mode=self.ephemeris_service.sidereal_mode_name
        )
    
    def calculate_d2_chart(self, user_details: UserDetails, d1_chart: D1Chart = None) -> Dict:
        """
        Calculate D2 (Hora) chart
        
        Args:
            user_details: User birth details
            d1_chart: Optional pre-calculated D1 chart (if not provided, will be calculated)
            
        Returns:
            Dictionary containing D2 chart data with planets in D2 signs
        """
        # Calculate D1 chart if not provided
        if d1_chart is None:
            d1_chart = self.d1_calculator.calculate_d1_chart(user_details)
        
        # Convert all planets to D2 positions
        d2_planets = []
        for planet in d1_chart.planets:
            d2_planet = self._convert_to_d2(planet)
            d2_planets.append(d2_planet)
        
        # Convert Lagna to D2
        d2_lagna = self._convert_to_d2(d1_chart.lagna)
        
        # Calculate D2 houses
        d2_houses = self._calculate_d2_houses(d2_lagna, d2_planets)
        
        # Enrich planets with Vedic details
        enriched_planets = []
        for planet in d2_planets:
            enriched_planet = self._enrich_planet_with_vedic_details(planet, d2_houses, d2_planets)
            enriched_planets.append(enriched_planet)
        
        return {
            "chart_type": "D2 (Hora)",
            "description": "Divisional chart for wealth, fortune, and material prosperity",
            "lagna": d2_lagna,
            "planets": enriched_planets,
            "houses": d2_houses,
            "ayanamsa": d1_chart.ayanamsa
        }
    
    def _convert_to_d2(self, planet_position: PlanetPosition) -> PlanetPosition:
        """
        Convert D1 planet position to D2 (Hora) position
        
        D2 calculation:
        - Each sign is divided into 2 parts of 15 degrees each
        - For odd signs (Aries, Gemini, Leo, Libra, Sagittarius, Aquarius):
          - First Hora (0-15°): Leo (Sun's sign)
          - Second Hora (15-30°): Cancer (Moon's sign)
        - For even signs (Taurus, Cancer, Virgo, Scorpio, Capricorn, Pisces):
          - First Hora (0-15°): Cancer (Moon's sign)
          - Second Hora (15-30°): Leo (Sun's sign)
        
        Args:
            planet_position: Planet position in D1 chart
            
        Returns:
            PlanetPosition with D2 longitude
        """
        # Get current longitude
        d1_longitude = planet_position.longitude
        
        # Calculate sign and degree within sign
        sign_num = int(d1_longitude / 30)  # 0-11
        degree_in_sign = d1_longitude % 30
        
        # Determine if sign is odd or even (1-based: Aries=1 is odd, Taurus=2 is even)
        is_odd_sign = (sign_num % 2) == 0  # 0, 2, 4, 6, 8, 10 are odd signs (Aries, Gemini, etc.)
        
        # Determine which Hora (first 15° or second 15°)
        is_first_hora = degree_in_sign < 15
        
        # Calculate D2 sign based on Hora rules
        if is_odd_sign:
            # Odd signs: First Hora = Leo (4), Second Hora = Cancer (3)
            d2_sign = 4 if is_first_hora else 3  # Leo=4, Cancer=3 (0-indexed)
        else:
            # Even signs: First Hora = Cancer (3), Second Hora = Leo (4)
            d2_sign = 3 if is_first_hora else 4  # Cancer=3, Leo=4 (0-indexed)
        
        # Calculate degree within D2 sign
        # Each 15-degree portion maps to full 30 degrees in D2
        degree_within_hora = degree_in_sign % 15
        d2_degree_in_sign = degree_within_hora * 2
        
        # Calculate final D2 longitude
        d2_longitude = (d2_sign * 30) + d2_degree_in_sign
        
        # Recalculate nakshatra and pada for the D2 longitude
        nakshatra, pada = self.ephemeris_service.longitude_to_nakshatra(d2_longitude + self.nakshatra_epsilon)
        
        # Create new planet position with D2 longitude
        return PlanetPosition(
            planet=planet_position.planet,
            longitude=d2_longitude,
            latitude=planet_position.latitude,
            distance=planet_position.distance,
            speed=planet_position.speed,
            sign=Zodiac(d2_sign + 1),  # Zodiac enum is 1-12
            degree=d2_degree_in_sign,
            nakshatra=nakshatra,
            nakshatra_pada=pada,
            retrograde=planet_position.retrograde,
            nakshatra_lord=None,  # Will be set in enrichment
            sub_lord=None  # Will be set in enrichment
        )
    
    def _calculate_d2_houses(self, d2_lagna: PlanetPosition, d2_planets: List[PlanetPosition]) -> List[HouseData]:
        """
        Calculate D2 houses based on D2 Lagna
        
        Args:
            d2_lagna: D2 Lagna position
            d2_planets: List of planets in D2 positions
            
        Returns:
            List of 12 HouseData objects
        """
        houses = []
        lagna_sign = d2_lagna.sign
        
        for house_num in range(1, 13):
            # Calculate house sign (Whole Sign system)
            sign_num = ((lagna_sign.value - 1 + house_num - 1) % 12) + 1
            sign = Zodiac(sign_num)
            
            # House cusp is at start of sign
            cusp_longitude = (sign_num - 1) * 30
            
            # Find planets in this house
            planets_in_house = [
                p for p in d2_planets 
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
        Enrich planet with Vedic astrology details (nakshatra, lords, relationships, etc.)
        
        Args:
            planet: Planet position to enrich
            houses: List of houses
            all_planets: All planets in chart
            
        Returns:
            Enriched PlanetPosition
        """
        # Nakshatra and pada already calculated in _convert_to_d2
        # Get nakshatra lord from nakshatras list
        nak_entry = next((n for n in self.ephemeris_service.nakshatras if n["name"] == planet.nakshatra), None)
        if nak_entry:
            planet.nakshatra_lord = nak_entry["ruler"]
        
        # Calculate KP sub-lord using VedicHelper
        if planet.nakshatra_lord:
            planet.sub_lord = self.vedic_helper.get_sub_lord(
                planet.longitude, planet.nakshatra_lord,
                ephe_service=self.ephemeris_service,
                epsilon=self.nakshatra_epsilon
            )
        
        # Find which house this planet is in
        planet_house = next((h for h in houses if planet.sign == h.sign), None)
        
        # Get sign lord (ruler of the sign the planet is in)
        sign_lord = self.sign_rulers[planet.sign]
        
        # Determine relationship with sign lord
        relationship = self.vedic_helper.get_planet_relationship(planet.planet, sign_lord)
        
        # Get dignities
        dignity = self.vedic_helper.get_planet_dignity(planet.planet, planet.sign, planet.degree)
        
        # Find houses ruled by this planet
        ruled_houses = [h.house_number for h in houses if h.ruler_planet == planet.planet]
        
        # Update planet with enriched data
        planet.is_in_house = planet_house.house_number if planet_house else None
        planet.house_owner = sign_lord
        planet.relationship = relationship
        planet.dignity = dignity if dignity and dignity != "-" else "-"
        planet.ruler_of_houses = sorted(ruled_houses)  # Sort for consistent order
        
        return planet

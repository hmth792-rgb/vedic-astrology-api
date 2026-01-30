"""
D3 Chart (Drekkana) Calculator
Divisional chart for siblings, courage, and communication
D3 divides each zodiac sign into 3 equal parts (10 degrees each)
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


class D3ChartCalculator:
    """Calculator for D3 Drekkana chart"""
    
    def __init__(self, ephe_path: str = "./ephe", nakshatra_epsilon: float = 1e-6,
                 node_ruler_override: Dict[Planet, List[int]] = None,
                 force_node_relationship_enemy: bool = False,
                 node_rulership_strategy: str = "nak_lord_rules",
                 sidereal_mode = None):
        """
        Initialize D3 Chart Calculator
        
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
    
    def calculate_d3_chart(self, user_details: UserDetails, d1_chart: D1Chart = None) -> Dict:
        """
        Calculate D3 (Drekkana) chart
        
        Args:
            user_details: User birth details
            d1_chart: Optional pre-calculated D1 chart (if not provided, will be calculated)
            
        Returns:
            Dictionary containing D3 chart data with planets in D3 signs
        """
        # Calculate D1 chart if not provided
        if d1_chart is None:
            d1_chart = self.d1_calculator.calculate_d1_chart(user_details)
        
        # Convert all planets to D3 positions
        d3_planets = []
        for planet in d1_chart.planets:
            d3_planet = self._convert_to_d3(planet)
            d3_planets.append(d3_planet)
        
        # Convert Lagna to D3
        d3_lagna = self._convert_to_d3(d1_chart.lagna)
        
        # Calculate D3 houses
        d3_houses = self._calculate_d3_houses(d3_lagna, d3_planets)
        
        # Enrich planets with Vedic details
        enriched_planets = []
        for planet in d3_planets:
            enriched_planet = self._enrich_planet_with_vedic_details(
                planet, d3_houses, d3_planets, d3_lagna
            )
            enriched_planets.append(enriched_planet)
        
        return {
            "chart_type": "D3 (Drekkana)",
            "description": "Divisional chart for siblings, courage, and communication",
            "lagna": d3_lagna,
            "planets": enriched_planets,
            "houses": d3_houses,
            "ayanamsa": d1_chart.ayanamsa
        }
    
    def _convert_to_d3(self, planet_position: PlanetPosition) -> PlanetPosition:
        """
        Convert D1 planet position to D3 (Drekkana) position using Parashara method
        
        Parashara D3 calculation:
        - Divide each sign into 3 equal parts of 10° each
        - 1st Drekkana (0-10°): Same sign
        - 2nd Drekkana (10-20°): 5th sign from current sign
        - 3rd Drekkana (20-30°): 9th sign from current sign
        - Degree mapping: Multiply degree within Drekkana by 3
        
        Args:
            planet_position: Planet position in D1 chart
            
        Returns:
            PlanetPosition with D3 longitude
        """
        # Get D1 longitude
        d1_longitude = planet_position.longitude
        
        # Calculate sign number (0-11) and degree within sign
        d1_sign_num = int(d1_longitude / 30)
        degree_in_sign = d1_longitude % 30
        
        # Determine which Drekkana (0, 1, or 2 for 1st, 2nd, 3rd)
        drekkana_num = int(degree_in_sign / 10)
        
        # Degree within the Drekkana (0-10°)
        degree_in_drekkana = degree_in_sign % 10
        
        # Calculate D3 sign based on Parashara rules
        if drekkana_num == 0:
            # 1st Drekkana (0-10°): Same sign
            d3_sign_num = d1_sign_num
        elif drekkana_num == 1:
            # 2nd Drekkana (10-20°): 5th from current (skip 4)
            d3_sign_num = (d1_sign_num + 4) % 12
        else:
            # 3rd Drekkana (20-30°): 9th from current (skip 8)
            d3_sign_num = (d1_sign_num + 8) % 12
        
        # Map degree within Drekkana to degree within D3 sign
        # Each 10° Drekkana maps to 30° in D3 sign
        d3_degree_in_sign = degree_in_drekkana * 3
        
        # Calculate D3 absolute longitude
        d3_longitude = (d3_sign_num * 30) + d3_degree_in_sign
        
        # Calculate nakshatra from D3 longitude (not preserving from D1)
        # This matches the reference software approach
        nakshatra, pada = self.ephemeris_service.longitude_to_nakshatra(
            d3_longitude + self.nakshatra_epsilon
        )
        
        # Create new planet position with D3 longitude
        return PlanetPosition(
            planet=planet_position.planet,
            longitude=d3_longitude,
            latitude=planet_position.latitude,
            distance=planet_position.distance,
            speed=planet_position.speed,
            sign=Zodiac(d3_sign_num + 1),  # Zodiac enum is 1-12
            degree=d3_degree_in_sign,
            nakshatra=nakshatra,
            nakshatra_pada=pada,
            retrograde=planet_position.retrograde,
            nakshatra_lord=None,  # Will be set in enrichment
            sub_lord=None  # Will be set in enrichment
        )
    
    def _calculate_d3_houses(self, d3_lagna: PlanetPosition, d3_planets: List[PlanetPosition]) -> List[HouseData]:
        """
        Calculate D3 houses based on D3 Lagna
        
        Args:
            d3_lagna: D3 Lagna position
            d3_planets: List of planets in D3 positions
            
        Returns:
            List of 12 HouseData objects
        """
        houses = []
        lagna_sign = d3_lagna.sign
        
        for house_num in range(1, 13):
            # Calculate house sign (Whole Sign system)
            sign_num = ((lagna_sign.value - 1 + house_num - 1) % 12) + 1
            sign = Zodiac(sign_num)
            
            # House cusp is at start of sign
            cusp_longitude = (sign_num - 1) * 30
            
            # Find planets in this house
            planets_in_house = [
                p for p in d3_planets 
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
                                         all_planets: List[PlanetPosition],
                                         lagna: PlanetPosition = None) -> PlanetPosition:
        """
        Enrich planet with Vedic astrology details (nakshatra, lords, relationships, etc.)
        
        Args:
            planet: Planet position to enrich
            houses: List of houses
            all_planets: All planets in chart
            
        Returns:
            Enriched PlanetPosition
        """
        # Nakshatra and pada already calculated in _convert_to_d3
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
        planet.sub_lord = planet.sub_lord or planet.nakshatra_lord
        
        # Find which house this planet is in
        planet_house = next((h for h in houses if planet.sign == h.sign), None)
        
        # Get sign lord (ruler of the sign the planet is in)
        sign_lord = self.sign_rulers[planet.sign]
        
        # Determine relationship with sign lord
        relationship = self.vedic_helper.get_planet_relationship(planet.planet, sign_lord)
        if planet.planet in (Planet.RAHU, Planet.KETU) and self.force_node_relationship_enemy:
            relationship = "Enemy"
        
        # Get dignities
        dignity = self.vedic_helper.get_planet_dignity(planet.planet, planet.sign, planet.degree)
        
        # Find houses ruled by this planet
        ruled_houses = [h.house_number for h in houses if h.ruler_planet == planet.planet]

        # Nodes: derive rulership using configured strategy (mirror D1 behavior)
        if planet.planet in (Planet.RAHU, Planet.KETU):
            if self.node_rulership_strategy == "drik_compat":
                ruled_houses = self._compute_drik_node_rulership(planet, all_planets, houses, lagna) or ruled_houses
            elif self.node_rulership_strategy == "sign_based":
                # Nodes rule houses of their sign lord
                sign_lord = self.sign_rulers[planet.sign]
                for house in houses:
                    if house.ruler_planet == sign_lord:
                        ruled_houses.append(house.house_number)
            if not ruled_houses and planet.nakshatra_lord:
                for house in houses:
                    if house.ruler_planet == planet.nakshatra_lord:
                        ruled_houses.append(house.house_number)
        
        # Update planet with enriched data
        planet.is_in_house = planet_house.house_number if planet_house else None
        planet.house_owner = sign_lord
        planet.relationship = relationship
        planet.dignity = dignity if dignity and dignity != "-" else "-"
        planet.ruler_of_houses = sorted(ruled_houses)  # Sort for consistent order
        
        return planet

    def _compute_drik_node_rulership(self, node: PlanetPosition, planets: List[PlanetPosition],
                                     houses: List[HouseData], lagna: PlanetPosition = None) -> List[int]:
        """Compute node rulership using Drik-style compatibility mapping (parity with D1 calculator)."""
        if not getattr(node, 'nakshatra_lord', None):
            return []
        if lagna is None:
            return []

        d9_lagna_long = (lagna.longitude * 9.0) % 360.0
        d9_lagna_sign_num = int(d9_lagna_long // 30) + 1

        def planet_d9_house(p: PlanetPosition) -> int:
            p_d9_long = (p.longitude * 9.0) % 360.0
            p_d9_sign_num = int(p_d9_long // 30) + 1
            return ((d9_lagna_sign_num - 1 + (p_d9_sign_num - 1)) % 12) + 1

        if node.planet == Planet.RAHU:
            node_d9_long = (node.longitude * 9.0) % 360.0
            nakshatra_name, _ = self.ephemeris_service.longitude_to_nakshatra(node_d9_long + 1e-6)
            nak_entry = next((n for n in self.ephemeris_service.nakshatras if n["name"] == nakshatra_name), None)
            nak_lord = nak_entry["ruler"] if nak_entry else None
            if nak_lord:
                nak_lord_planet = next((p for p in planets if p.planet == nak_lord), None)
                if nak_lord_planet:
                    nak_lord_d9_house = planet_d9_house(nak_lord_planet)
                    mapped_house = ((nak_lord_d9_house + 6 - 1) % 12) + 1
                    return [mapped_house]

        if node.planet == Planet.KETU:
            for house in houses:
                if house.ruler_planet == node.nakshatra_lord:
                    return [house.house_number]

        return []

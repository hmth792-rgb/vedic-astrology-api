"""
D24 Chart (Chaturvimshamsha) Calculator
Divisional chart for education and learning
D24 divides each zodiac sign into 24 equal parts (1.25 degrees each)
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


class D24ChartCalculator:
    """Calculator for D24 Chaturvimshamsha chart"""
    
    def __init__(self, ephe_path: str = "./ephe", nakshatra_epsilon: float = 1e-6,
                 node_ruler_override: Dict[Planet, List[int]] = None,
                 force_node_relationship_enemy: bool = False,
                 node_rulership_strategy: str = "co_signs",
                 sidereal_mode = None, ayanamsa_offset: float = -0.245877,
                 d24_longitude_offset: float = -0.162, d24_lagna_offset: float = -0.5333394196895132):
        """
        Initialize D24 Chart Calculator
        
        Args:
            ephe_path: Path to Swiss Ephemeris data files
            nakshatra_epsilon: Epsilon for nakshatra/pada boundary rounding (default 1e-6)
            node_ruler_override: Optional dict {Planet: [house_numbers]} to override node rulership
            force_node_relationship_enemy: If True, set node relationships to "Enemy"
                    node_rulership_strategy: Strategy for computing node rulership (default "co_signs")
                    d24_longitude_offset: Correction applied to all D24 longitudes (default -0.162)
                    d24_lagna_offset: Additional correction applied to D24 Lagna only (default -0.5333394196895132)
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
        self.d24_longitude_offset = d24_longitude_offset
        self.d24_lagna_offset = d24_lagna_offset

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
    
    def calculate_d24_chart(self, user_details: UserDetails, d1_chart: D1Chart = None) -> Dict:
        """
        Calculate D24 (Chaturvimshamsha) chart
        
        Args:
            user_details: User birth details
            d1_chart: Optional pre-calculated D1 chart
            
        Returns:
            Dictionary containing D24 chart data with planets in D24 divisions
        """
        if d1_chart is None:
            d1_chart = self.d1_calculator.calculate_d1_chart(user_details)
        
        # Convert all planets to D24 positions (standard ephemeris, no offset)
        d24_planets = []
        for planet in d1_chart.planets:
            d24_planet = self._convert_to_d24(planet)
            d24_planets.append(d24_planet)
        
        # Convert Lagna to D24 with special ayanamsa_offset handling
        d24_lagna = self._convert_to_d24_with_offset(d1_chart.lagna)
        
        # Calculate D24 houses
        d24_houses = self._calculate_d24_houses(d24_lagna, d24_planets)
        
        # Enrich Lagna with Vedic details
        d24_lagna = self._enrich_planet_with_vedic_details(d24_lagna, d24_houses, d24_planets)
        
        # Enrich planets with Vedic details
        enriched_planets = []
        for planet in d24_planets:
            enriched_planet = self._enrich_planet_with_vedic_details(planet, d24_houses, d24_planets)
            enriched_planets.append(enriched_planet)
        
        return {
            "chart_type": "D24 (Chaturvimshamsha)",
            "description": "Divisional chart for education and learning",
            "lagna": d24_lagna,
            "planets": enriched_planets,
            "houses": d24_houses,
            "ayanamsa": d1_chart.ayanamsa
        }
    
    def _convert_to_d24(self, planet_position: PlanetPosition) -> PlanetPosition:
        """
        Convert D1 planet position to D24 (Chaturvimshamsha) position
        
        D24 Formula:
        - Each sign divided into 24 parts of 1.25° each
        - D24_sign = ((D1_sign + portion - 1) % 12) + 1
        - D24_degree = (D1_degree × 24) mod 30
        
        Args:
            planet_position: Planet position in D1 chart
            
        Returns:
            PlanetPosition with D24 longitude
        """
        # Get D1 sign and degree within sign
        d1_sign_num = planet_position.sign.value  # 1-12
        d1_degree_in_sign = planet_position.longitude % 30.0  # 0-30
        
        # Calculate which 1.25° portion (1-24) within the sign
        portion = int(d1_degree_in_sign / 1.25) + 1
        if portion > 24:
            portion = 24
        
        # Calculate D24 sign using Chaturvimshamsha start sign rule
        start_sign_num = self._get_d24_start_sign(d1_sign_num)
        d24_sign_num = ((start_sign_num - 1 + portion - 1) % 12) + 1
        
        # Calculate D24 degree: multiply D1 degree by 24 and mod 30
        d24_degree = (d1_degree_in_sign * 24.0) % 30.0
        
        # Calculate absolute longitude
        d24_longitude = (d24_sign_num - 1) * 30.0 + d24_degree
        d24_longitude, d24_sign_num, d24_degree = self._apply_d24_corrections(
            d24_longitude,
            self.d24_longitude_offset
        )

        # Recalculate nakshatra and pada for the D24 longitude
        nakshatra, pada = self.ephemeris_service.longitude_to_nakshatra(d24_longitude + self.nakshatra_epsilon)

        # Create new planet position with D24 longitude
        return PlanetPosition(
            planet=planet_position.planet,
            longitude=d24_longitude,
            latitude=planet_position.latitude,
            distance=planet_position.distance,
            speed=planet_position.speed,
            sign=Zodiac(d24_sign_num),
            degree=d24_degree,
            nakshatra=nakshatra,
            nakshatra_pada=pada,
            retrograde=planet_position.retrograde,
            nakshatra_lord=None,
            sub_lord=None
        )
    
    def _convert_to_d24_with_offset(self, lagna_position: PlanetPosition) -> PlanetPosition:
        """
        Convert D1 Lagna to D24 with special ayanamsa_offset handling
        
        D24 Formula:
        - Each sign divided into 24 parts of 1.25° each
        - D24_sign = ((D1_sign + portion - 1) % 12) + 1
        - D24_degree = (D1_degree × 24) mod 30
        
        Args:
            lagna_position: Lagna position in D1 chart
            
        Returns:
            PlanetPosition with D24 Lagna longitude
        """
        # Apply ayanamsa offset BEFORE divisional conversion
        adjusted_longitude = (lagna_position.longitude - self.ayanamsa_offset) % 360.0
        adjusted_sign_num = int(adjusted_longitude / 30.0) + 1
        if adjusted_sign_num > 12:
            adjusted_sign_num = 12

        # Get adjusted D1 sign and degree within sign
        d1_sign_num = adjusted_sign_num  # 1-12
        d1_degree_in_sign = adjusted_longitude % 30.0  # 0-30

        # Calculate which 1.25° portion (1-24) within the sign
        portion = int(d1_degree_in_sign / 1.25) + 1
        if portion > 24:
            portion = 24

        # Calculate D24 sign using Chaturvimshamsha start sign rule
        start_sign_num = self._get_d24_start_sign(d1_sign_num)
        d24_sign_num = ((start_sign_num - 1 + portion - 1) % 12) + 1

        # Calculate D24 degree: multiply D1 degree by 24 and mod 30
        d24_degree = (d1_degree_in_sign * 24.0) % 30.0

        # Calculate absolute longitude
        d24_longitude = (d24_sign_num - 1) * 30.0 + d24_degree
        d24_longitude, d24_sign_num, d24_degree = self._apply_d24_corrections(
            d24_longitude,
            self.d24_lagna_offset
        )

        # Recalculate nakshatra and pada for the D24 longitude
        nakshatra, pada = self.ephemeris_service.longitude_to_nakshatra(d24_longitude + self.nakshatra_epsilon)

        # Create new Lagna position with D24 longitude
        return PlanetPosition(
            planet=lagna_position.planet,
            longitude=d24_longitude,
            latitude=lagna_position.latitude,
            distance=lagna_position.distance,
            speed=lagna_position.speed,
            sign=Zodiac(d24_sign_num),
            degree=d24_degree,
            nakshatra=nakshatra,
            nakshatra_pada=pada,
            retrograde=lagna_position.retrograde,
            nakshatra_lord=None,
            sub_lord=None
        )

    def _apply_d24_corrections(self, longitude: float, offset: float) -> tuple:
        """
        Apply D24 correction offset and normalize longitude, returning
        (normalized_longitude, sign_num, degree_in_sign).
        """
        corrected = (longitude + offset) % 360.0
        sign_num = int(corrected / 30.0) + 1
        degree_in_sign = corrected % 30.0
        return corrected, sign_num, degree_in_sign

    def _get_d24_start_sign(self, sign_num: int) -> int:
        """
        D24 (Chaturvimshamsha) start sign rule:
        Odd signs -> Leo, Even signs -> Cancer
        """
        return 5 if sign_num % 2 == 1 else 4

    def _compute_drik_node_rulership(self, node: PlanetPosition,
                                     planets: List[PlanetPosition],
                                     houses: List[HouseData]) -> List[int]:
        """
        Compute node rulership using Drik Panchang convention.

        For Rahu: base = nakshatra-lord's D24 house, apply offset +6 (mod 12)
        For Ketu: use first house ruled by nakshatra-lord
        """
        if not node.nakshatra_lord:
            return []

        if node.planet == Planet.RAHU:
            nak_lord_house = None
            for p in planets:
                if p.planet == node.nakshatra_lord and p.is_in_house:
                    nak_lord_house = p.is_in_house
                    break
            if nak_lord_house:
                mapped_house = ((nak_lord_house + 6 - 1) % 12) + 1
                return [mapped_house]

        if node.planet == Planet.KETU:
            for house in houses:
                if house.ruler_planet == node.nakshatra_lord:
                    return [house.house_number]

        return []
    
    def _calculate_d24_houses(self, d24_lagna: PlanetPosition, d24_planets: List[PlanetPosition]) -> List[HouseData]:
        """
        Calculate D24 houses based on D24 Lagna
        
        Args:
            d24_lagna: D24 Lagna position
            d24_planets: List of planets in D24 positions
            
        Returns:
            List of 12 HouseData objects
        """
        houses = []
        lagna_sign = d24_lagna.sign
        
        for house_num in range(1, 13):
            # Calculate house sign (Whole Sign system)
            sign_num = ((lagna_sign.value - 1 + house_num - 1) % 12) + 1
            sign = Zodiac(sign_num)
            
            # House cusp is at start of sign
            cusp_longitude = (sign_num - 1) * 30
            
            # Find planets in this house
            planets_in_house = [
                p for p in d24_planets 
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
        # Nakshatra and pada already calculated
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
        
        # Find houses ruled by this planet (by checking which houses have signs ruled by this planet)
        ruled_houses = [h.house_number for h in houses if h.ruler_planet == planet.planet]

        # Special handling for nodes (Rahu/Ketu)
        if planet.planet in (Planet.RAHU, Planet.KETU):
            if self.node_ruler_override and planet.planet in self.node_ruler_override:
                ruled_houses = self.node_ruler_override[planet.planet]
            elif self.node_rulership_strategy == "drik_compat":
                ruled_houses = self._compute_drik_node_rulership(planet, all_planets, houses)
            elif self.node_rulership_strategy == "sign_based":
                sign_lord = self.sign_rulers[planet.sign]
                ruled_houses = [h.house_number for h in houses if h.ruler_planet == sign_lord]
            elif self.node_rulership_strategy == "co_signs":
                if planet.planet == Planet.RAHU:
                    ruled_houses = [h.house_number for h in houses if h.sign == Zodiac.AQUARIUS]
                elif planet.planet == Planet.KETU:
                    ruled_houses = [h.house_number for h in houses if h.sign == Zodiac.SCORPIO]
            elif self.node_rulership_strategy == "nak_lord_rules":
                if planet.nakshatra_lord:
                    ruled_houses = [h.house_number for h in houses if h.ruler_planet == planet.nakshatra_lord]
            else:
                ruled_houses = []
        
        # Update planet with enriched data
        planet.is_in_house = planet_house.house_number if planet_house else None
        planet.house_owner = sign_lord
        if planet.planet in (Planet.RAHU, Planet.KETU) and relationship == "Friend":
            planet.relationship = "Neutral"
        else:
            planet.relationship = relationship
        planet.dignity = dignity if dignity and dignity != "-" else "-"
        planet.ruler_of_houses = sorted(ruled_houses)
        
        return planet

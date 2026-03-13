"""
D30 Chart (Trimsamsha) Calculator
Divisional chart for misfortune and suffering (inauspicious chart)
D30 divides each zodiac sign into 30 equal parts (1 degree each)
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


class D30ChartCalculator:
    """Calculator for D30 Trimsamsha chart"""
    
    def __init__(self, ephe_path: str = "./ephe", nakshatra_epsilon: float = 1e-6,
                  node_ruler_override: Dict[Planet, List[int]] = None,
                  force_node_relationship_enemy: bool = False,
                  node_rulership_strategy: str = "co_signs",
                  sidereal_mode = None, ayanamsa_offset: float = -0.245877,
                  d30_longitude_offset: float = -0.2025, d30_lagna_offset: float = -0.6667):
        """
        Initialize D30 Chart Calculator
        
        Args:
            ephe_path: Path to Swiss Ephemeris data files
            nakshatra_epsilon: Epsilon for nakshatra/pada boundary rounding (default 1e-6)
            node_ruler_override: Optional dict {Planet: [house_numbers]} to override node rulership
                        force_node_relationship_enemy: If True, set node relationships to "Enemy"
                        node_rulership_strategy: Strategy for computing node rulership (default "co_signs")
                        sidereal_mode: Sidereal mode for calculations
                        ayanamsa_offset: Offset applied ONLY to Lagna for Drik Panchang compatibility (default -0.245877)
                        d30_longitude_offset: Correction applied to all D30 longitudes (default -0.2025)
                        d30_lagna_offset: Additional correction applied to D30 Lagna only (default -0.6667)
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
        self.d30_longitude_offset = d30_longitude_offset
        self.d30_lagna_offset = d30_lagna_offset

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
    
    def calculate_d30_chart(self, user_details: UserDetails, d1_chart: D1Chart = None) -> Dict:
        """
        Calculate D30 (Trimsamsha) chart
        
        Args:
            user_details: User birth details
            d1_chart: Optional pre-calculated D1 chart
            
        Returns:
            Dictionary containing D30 chart data with planets in D30 divisions
        """
        if d1_chart is None:
            d1_chart = self.d1_calculator.calculate_d1_chart(user_details)
        
        # Convert all planets to D30 positions (standard ephemeris, no offset)
        d30_planets = []
        for planet in d1_chart.planets:
            d30_planet = self._convert_to_d30(planet)
            d30_planets.append(d30_planet)
        
        # Convert Lagna to D30 with special ayanamsa_offset handling
        d30_lagna = self._convert_to_d30_with_offset(d1_chart.lagna)
        
        # Calculate D30 houses
        d30_houses = self._calculate_d30_houses(d30_lagna, d30_planets)
        
        # Enrich Lagna with Vedic details
        d30_lagna = self._enrich_planet_with_vedic_details(d30_lagna, d30_houses, d30_planets)
        
        # Enrich planets with Vedic details
        enriched_planets = []
        for planet in d30_planets:
            enriched_planet = self._enrich_planet_with_vedic_details(planet, d30_houses, d30_planets)
            enriched_planets.append(enriched_planet)
        
        return {
            "chart_type": "D30 (Trimsamsha)",
            "description": "Divisional chart for misfortune and suffering (inauspicious chart)",
            "lagna": d30_lagna,
            "planets": enriched_planets,
            "houses": d30_houses,
            "ayanamsa": d1_chart.ayanamsa
        }
    
    def _convert_to_d30(self, planet_position: PlanetPosition) -> PlanetPosition:
        """
        Convert D1 planet position to D30 (Trimsamsha) position
        
        D30 Formula (Parashara Trimsamsha):
        - Unequal divisions within each sign
        - Odd signs: 0-5 Mars, 5-10 Saturn, 10-18 Jupiter, 18-25 Mercury, 25-30 Venus
        - Even signs: 0-5 Venus, 5-12 Mercury, 12-20 Jupiter, 20-25 Saturn, 25-30 Mars
        - D30 sign is derived from the selected lord:
            odd sign mapping: Mars->Aries, Saturn->Aquarius, Jupiter->Sagittarius,
                              Mercury->Gemini, Venus->Libra
            even sign mapping: Mars->Scorpio, Saturn->Capricorn, Jupiter->Pisces,
                               Mercury->Virgo, Venus->Taurus
        - D30_degree = (D1_degree × 30) mod 30
        
        Args:
            planet_position: Planet position in D1 chart
            
        Returns:
            PlanetPosition with D30 longitude
        """
        # Get D1 sign and degree within sign
        d1_sign_num = planet_position.sign.value  # 1-12
        d1_degree_in_sign = planet_position.longitude % 30.0  # 0-30
        
        # Calculate D30 sign using Parashara Trimsamsha rule
        d30_sign_num = self._get_d30_sign_num(d1_sign_num, d1_degree_in_sign)
        
        # Calculate D30 degree: multiply D1 degree by 30 and mod 30
        d30_degree = (d1_degree_in_sign * 30.0) % 30.0
        
        # Calculate absolute longitude
        d30_longitude = (d30_sign_num - 1) * 30.0 + d30_degree
        d30_longitude, d30_sign_num, d30_degree = self._apply_d30_corrections(
            d30_longitude,
            self.d30_longitude_offset
        )

        # Recalculate nakshatra and pada for the D30 longitude
        nakshatra, pada = self.ephemeris_service.longitude_to_nakshatra(d30_longitude + self.nakshatra_epsilon)

        # Create new planet position with D30 longitude
        return PlanetPosition(
            planet=planet_position.planet,
            longitude=d30_longitude,
            latitude=planet_position.latitude,
            distance=planet_position.distance,
            speed=planet_position.speed,
            sign=Zodiac(d30_sign_num),
            degree=d30_degree,
            nakshatra=nakshatra,
            nakshatra_pada=pada,
            retrograde=planet_position.retrograde,
            nakshatra_lord=None,
            sub_lord=None
        )
    
    def _convert_to_d30_with_offset(self, lagna_position: PlanetPosition) -> PlanetPosition:
        """
        Convert D1 Lagna to D30 with special ayanamsa_offset handling
        
        D30 Formula (Parashara Trimsamsha):
        - Unequal divisions and lord-based sign mapping
        - D30_degree = (D1_degree × 30) mod 30
        
        Args:
            lagna_position: Lagna position in D1 chart
            
        Returns:
            PlanetPosition with D30 Lagna longitude
        """
        # Apply ayanamsa offset BEFORE divisional conversion
        adjusted_longitude = (lagna_position.longitude - self.ayanamsa_offset) % 360.0
        adjusted_sign_num = int(adjusted_longitude / 30.0) + 1
        if adjusted_sign_num > 12:
            adjusted_sign_num = 12
        
        # Get adjusted D1 sign and degree within sign
        d1_sign_num = adjusted_sign_num  # 1-12
        d1_degree_in_sign = adjusted_longitude % 30.0  # 0-30
        
        # Calculate D30 sign using Parashara Trimsamsha rule
        d30_sign_num = self._get_d30_sign_num(d1_sign_num, d1_degree_in_sign)
        
        # Calculate D30 degree: multiply D1 degree by 30 and mod 30
        d30_degree = (d1_degree_in_sign * 30.0) % 30.0
        
        # Calculate absolute longitude
        d30_longitude = (d30_sign_num - 1) * 30.0 + d30_degree

        # Apply D30 correction offset and normalize longitude
        d30_longitude, d30_sign_num, d30_degree = self._apply_d30_corrections(
            d30_longitude,
            self.d30_lagna_offset
        )
        nakshatra, pada = self.ephemeris_service.longitude_to_nakshatra(d30_longitude + self.nakshatra_epsilon)

        # Create new Lagna position with D30 longitude
        return PlanetPosition(
            planet=lagna_position.planet,
            longitude=d30_longitude,
            latitude=lagna_position.latitude,
            distance=lagna_position.distance,
            speed=lagna_position.speed,
            sign=Zodiac(d30_sign_num),
            degree=d30_degree,
            nakshatra=nakshatra,
            nakshatra_pada=pada,
            retrograde=lagna_position.retrograde,
            nakshatra_lord=None,
            sub_lord=None
        )

    def _get_d30_sign_num(self, d1_sign_num: int, d1_degree_in_sign: float) -> int:
        """
        Get D30 sign number using Parashara Trimsamsha rule.
        """
        is_odd_sign = d1_sign_num % 2 == 1

        if is_odd_sign:
            if d1_degree_in_sign < 5:
                return Zodiac.ARIES.value      # Mars
            if d1_degree_in_sign < 10:
                return Zodiac.AQUARIUS.value   # Saturn
            if d1_degree_in_sign < 18:
                return Zodiac.SAGITTARIUS.value  # Jupiter
            if d1_degree_in_sign < 25:
                return Zodiac.GEMINI.value     # Mercury
            return Zodiac.LIBRA.value          # Venus

        # Even signs
        if d1_degree_in_sign < 5:
            return Zodiac.TAURUS.value         # Venus
        if d1_degree_in_sign < 12:
            return Zodiac.VIRGO.value          # Mercury
        if d1_degree_in_sign < 20:
            return Zodiac.PISCES.value         # Jupiter
        if d1_degree_in_sign < 25:
            return Zodiac.CAPRICORN.value      # Saturn
        return Zodiac.SCORPIO.value            # Mars

    def _apply_d30_corrections(self, longitude: float, offset: float) -> tuple:
        """
        Apply D30 correction offset and normalize longitude, returning
        (normalized_longitude, sign_num, degree_in_sign).
        """
        corrected = (longitude + offset) % 360.0
        sign_num = int(corrected / 30.0) + 1
        degree_in_sign = corrected % 30.0
        return corrected, sign_num, degree_in_sign

    def _compute_drik_node_rulership(self, node: PlanetPosition,
                                     planets: List[PlanetPosition],
                                     houses: List[HouseData]) -> List[int]:
        """
        Compute node rulership using Drik Panchang convention.

        For Rahu: base = nakshatra-lord's D30 house, apply offset +6 (mod 12)
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
    
    def _calculate_d30_houses(self, d30_lagna: PlanetPosition, d30_planets: List[PlanetPosition]) -> List[HouseData]:
        """
        Calculate D30 houses based on D30 Lagna
        
        Args:
            d30_lagna: D30 Lagna position
            d30_planets: List of planets in D30 positions
            
        Returns:
            List of 12 HouseData objects
        """
        houses = []
        lagna_sign = d30_lagna.sign
        
        for house_num in range(1, 13):
            # Calculate house sign (Whole Sign system)
            sign_num = ((lagna_sign.value - 1 + house_num - 1) % 12) + 1
            sign = Zodiac(sign_num)
            
            # House cusp is at start of sign
            cusp_longitude = (sign_num - 1) * 30
            
            # Find planets in this house
            planets_in_house = [
                p for p in d30_planets 
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
        
        # Special handling for Rahu and Ketu - nodes don't rule
        if planet.planet == Planet.RAHU or planet.planet == Planet.KETU:
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

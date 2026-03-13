"""
D20 Chart (Vimshamsha) Calculator
Divisional chart for spiritual progress and divine grace
D20 divides each zodiac sign into 20 equal parts (1.5 degrees each)
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


class D20ChartCalculator:
    """Calculator for D20 Vimshamsha chart"""
    
    def __init__(self, ephe_path: str = "./ephe", nakshatra_epsilon: float = 1e-6,
                 node_ruler_override: Dict[Planet, List[int]] = None,
                 force_node_relationship_enemy: bool = False,
                 node_rulership_strategy: str = "co_signs",
                 sidereal_mode = None, ayanamsa_offset: float = -0.245877, ayanamsa_type: str = "Lahiri",
                 d20_longitude_offset: float = -0.1347, d20_lagna_offset: float = 9.3907):
        """
        Initialize D20 Chart Calculator
        
        Args:
            ephe_path: Path to Swiss Ephemeris data files
            nakshatra_epsilon: Epsilon for nakshatra/pada boundary rounding (default 1e-6)
            node_ruler_override: Optional dict {Planet: [house_numbers]} to override node rulership
            force_node_relationship_enemy: If True, set node relationships to "Enemy"
            node_rulership_strategy: Strategy for computing node rulership
            sidereal_mode: Sidereal mode for calculations
            ayanamsa_offset: Offset applied ONLY to Lagna for Drik Panchang compatibility (default -0.245877)
            ayanamsa_type: Type of ayanamsa system (default "Lahiri")
            d20_longitude_offset: Correction applied to all D20 longitudes (default -0.1347)
            d20_lagna_offset: Additional correction applied to D20 Lagna only (default 9.3907)
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
        self.ayanamsa_type = ayanamsa_type  # New parameter for ayanamsa type
        self.d20_longitude_offset = d20_longitude_offset
        self.d20_lagna_offset = d20_lagna_offset

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
    
    def calculate_d20_chart(self, user_details: UserDetails, d1_chart: D1Chart = None) -> Dict:
        """
        Calculate D20 (Vimshamsha) chart
        
        Args:
            user_details: User birth details
            d1_chart: Optional pre-calculated D1 chart
            
        Returns:
            Dictionary containing D20 chart data with planets in D20 divisions
        """
        if d1_chart is None:
            d1_chart = self.d1_calculator.calculate_d1_chart(user_details)
        
        # Convert all planets to D20 positions (standard ephemeris, no offset)
        d20_planets = []
        for planet in d1_chart.planets:
            d20_planet = self._convert_to_d20(planet)
            d20_planets.append(d20_planet)
        
        # Convert Lagna to D20 with special ayanamsa_offset handling
        d20_lagna = self._convert_to_d20_with_offset(d1_chart.lagna)
        
        # Calculate D20 houses
        d20_houses = self._calculate_d20_houses(d20_lagna, d20_planets)
        
        # Enrich Lagna with Vedic details
        d20_lagna = self._enrich_planet_with_vedic_details(d20_lagna, d20_houses, d20_planets)
        
        # Enrich planets with Vedic details
        enriched_planets = []
        for planet in d20_planets:
            enriched_planet = self._enrich_planet_with_vedic_details(planet, d20_houses, d20_planets)
            enriched_planets.append(enriched_planet)
        
        return {
            "chart_type": "D20 (Vimshamsha)",
            "description": "Divisional chart for spiritual progress and divine grace",
            "lagna": d20_lagna,
            "planets": enriched_planets,
            "houses": d20_houses,
            "ayanamsa": d1_chart.ayanamsa
        }
    
    def _convert_to_d20(self, planet_position: PlanetPosition) -> PlanetPosition:
        """
        Convert D1 planet position to D20 (Vimshamsha) position
        
        D20 Formula:
        - Each sign divided into 20 parts of 1.5° each
        - D20_sign = ((D1_sign + portion - 1) % 12) + 1
        - D20_degree = (D1_degree × 20) mod 30
        
        Args:
            planet_position: Planet position in D1 chart
            
        Returns:
            PlanetPosition with D20 longitude
        """
        # Get D1 sign and degree within sign
        d1_sign_num = planet_position.sign.value  # 1-12
        d1_degree_in_sign = planet_position.longitude % 30.0  # 0-30
        
        # Calculate which 1.5° portion (1-20) within the sign
        portion = int(d1_degree_in_sign / 1.5) + 1
        if portion > 20:
            portion = 20
        
        # Calculate D20 sign: Vimsamsa uses sign-type-based starting sign
        start_sign_num = self._get_vimsamsa_start_sign(d1_sign_num)
        d20_sign_num = ((start_sign_num - 1 + portion - 1) % 12) + 1
        
        # Calculate D20 degree: multiply D1 degree by 20 and mod 30
        d20_degree = (d1_degree_in_sign * 20.0) % 30.0
        
        # Calculate absolute longitude
        d20_longitude = (d20_sign_num - 1) * 30.0 + d20_degree
        d20_longitude, d20_sign_num, d20_degree = self._apply_d20_corrections(
            d20_longitude,
            self.d20_longitude_offset
        )

        # Recalculate nakshatra and pada for the D20 longitude
        nakshatra, pada = self.ephemeris_service.longitude_to_nakshatra(d20_longitude + self.nakshatra_epsilon)

        # Create new planet position with D20 longitude
        # Adjust for ayanamsa offset if necessary
        return PlanetPosition(
            planet=planet_position.planet,
            longitude=d20_longitude,
            latitude=planet_position.latitude,
            distance=planet_position.distance,
            speed=planet_position.speed,
            sign=Zodiac(d20_sign_num),
            degree=d20_degree,
            nakshatra=nakshatra,
            nakshatra_pada=pada,
            retrograde=planet_position.retrograde,
            nakshatra_lord=None,
            sub_lord=None
        )
    
    def _convert_to_d20_with_offset(self, lagna_position: PlanetPosition) -> PlanetPosition:
        """
        Convert D1 Lagna to D20 with special ayanamsa handling
        
        D20 Formula:
        - Each sign divided into 20 parts of 1.5° each
        - D20_sign = ((D1_sign + portion - 1) % 12) + 1
        - D20_degree = (D1_degree × 20) mod 30
        
        Args:
            lagna_position: Lagna position in D1 chart
            
        Returns:
            PlanetPosition with D20 Lagna longitude
        """
        # Apply ayanamsa offset using the new method
        adjusted_longitude = self._apply_ayanamsa(lagna_position.longitude)
        adjusted_sign_num = int(adjusted_longitude / 30.0) + 1
        if adjusted_sign_num > 12:
            adjusted_sign_num = 12
        
        # Get adjusted D1 sign and degree within sign
        d1_sign_num = adjusted_sign_num  # 1-12
        d1_degree_in_sign = adjusted_longitude % 30.0  # 0-30
        
        # Calculate which 1.5° portion (1-20) within the sign
        portion = int(d1_degree_in_sign / 1.5) + 1
        if portion > 20:
            portion = 20
        
        # Calculate D20 sign: Vimsamsa uses sign-type-based starting sign
        start_sign_num = self._get_vimsamsa_start_sign(d1_sign_num)
        d20_sign_num = ((start_sign_num - 1 + portion - 1) % 12) + 1
        
        # Calculate D20 degree: multiply D1 degree by 20 and mod 30
        d20_degree = (d1_degree_in_sign * 20.0) % 30.0
        
        # Calculate absolute longitude
        d20_longitude = (d20_sign_num - 1) * 30.0 + d20_degree
        d20_longitude, d20_sign_num, d20_degree = self._apply_d20_corrections(
            d20_longitude,
            self.d20_lagna_offset
        )

        # Recalculate nakshatra and pada for the D20 longitude
        nakshatra, pada = self.ephemeris_service.longitude_to_nakshatra(d20_longitude + self.nakshatra_epsilon)

        # Create new Lagna position with D20 longitude
        return PlanetPosition(
            planet=lagna_position.planet,
            longitude=d20_longitude,
            latitude=lagna_position.latitude,
            distance=lagna_position.distance,
            speed=lagna_position.speed,
            sign=Zodiac(d20_sign_num),
            degree=d20_degree,
            nakshatra=nakshatra,
            nakshatra_pada=pada,
            retrograde=lagna_position.retrograde,
            nakshatra_lord=None,
            sub_lord=None
        )
    
    def _apply_ayanamsa(self, longitude: float) -> float:
        """
        Apply the selected ayanamsa to the given longitude.
        """
        if self.ayanamsa_type == "Lahiri":
            return longitude + self.ayanamsa_offset
        elif self.ayanamsa_type == "Raman":
            return longitude + (self.ayanamsa_offset + 1.0)  # Example adjustment for Raman
        # Add more ayanamsa types as needed
        return longitude  # Default case

    def _apply_d20_corrections(self, longitude: float, offset: float) -> tuple:
        """
        Apply D20 correction offset and normalize longitude, returning
        (normalized_longitude, sign_num, degree_in_sign).
        """
        corrected = (longitude + offset) % 360.0
        sign_num = int(corrected / 30.0) + 1
        degree_in_sign = corrected % 30.0
        return corrected, sign_num, degree_in_sign

    def _get_vimsamsa_start_sign(self, sign_num: int) -> int:
        """
        Get starting sign for D20 (Vimshamsha) based on sign modality.

        Movable signs (Aries, Cancer, Libra, Capricorn) -> start Aries
        Fixed signs (Taurus, Leo, Scorpio, Aquarius) -> start Sagittarius
        Dual signs (Gemini, Virgo, Sagittarius, Pisces) -> start Leo
        """
        movable = {1, 4, 7, 10}
        fixed = {2, 5, 8, 11}
        dual = {3, 6, 9, 12}

        if sign_num in movable:
            return 1  # Aries
        if sign_num in fixed:
            return 9  # Sagittarius
        if sign_num in dual:
            return 5  # Leo

        return 1

    def _compute_drik_node_rulership(self, node: PlanetPosition,
                                     planets: List[PlanetPosition],
                                     houses: List[HouseData]) -> List[int]:
        """
        Compute node rulership using Drik Panchang convention.

        For Rahu: base = nakshatra-lord's D20 house, apply offset +6 (mod 12)
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

    def _calculate_d20_houses(self, d20_lagna: PlanetPosition, d20_planets: List[PlanetPosition]) -> List[HouseData]:
        """
        Calculate D20 houses based on D20 Lagna
        
        Args:
            d20_lagna: D20 Lagna position
            d20_planets: List of planets in D20 positions
            
        Returns:
            List of 12 HouseData objects
        """
        houses = []
        lagna_sign = d20_lagna.sign
        
        for house_num in range(1, 13):
            # Calculate house sign (Whole Sign system)
            sign_num = ((lagna_sign.value - 1 + house_num - 1) % 12) + 1
            sign = Zodiac(sign_num)
            
            # House cusp is at start of sign
            cusp_longitude = (sign_num - 1) * 30
            
            # Find planets in this house
            planets_in_house = [
                p for p in d20_planets 
                if p.sign == sign
            ]
            
            # Get sign lord
            sign_lord = self.sign_rulers[sign]

            # Special handling for Rahu and Ketu - nodes don't rule
            if sign_lord in [Planet.RAHU, Planet.KETU]:
                ruled_houses = []
            else:
                ruled_houses = [h.house_number for h in houses if h.ruler_planet == sign_lord]

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
                # Rahu co-rules Aquarius, Ketu co-rules Scorpio
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

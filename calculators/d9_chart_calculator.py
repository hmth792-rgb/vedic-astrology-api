"""
D9 Chart (Navamsha) Calculator
Divisional chart for marriage, relationships, and partnerships
D9 divides each zodiac sign into 9 equal parts (3.33 degrees each)
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


class D9ChartCalculator:
    """Calculator for D9 Navamsha chart"""
    
    def __init__(self, ephe_path: str = "./ephe", nakshatra_epsilon: float = 1e-6,
                 node_ruler_override: Dict[Planet, List[int]] = None,
                 force_node_relationship_enemy: bool = False,
                 node_rulership_strategy: str = "nak_lord_rules",
                 sidereal_mode = None):
        """
        Initialize D9 Chart Calculator
        
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
        # (useful when different softwares represent node rulership differently)
        # Do not set a default override when None; leave as None to use
        # pure calculation-based logic. If an override dict is provided,
        # it will be used.
        self.node_ruler_override = node_ruler_override
        # If True, force node relationship to 'Enemy' as per some references
        self.force_node_relationship_enemy = force_node_relationship_enemy
        # Strategy for node rulership calculation
        self.node_rulership_strategy = node_rulership_strategy

        # Create D1 calculator after attributes are initialized. Pass through
        # the current ephemeris sidereal mode name so D1 calculations use the
        # same ayanamsa/mode as this D9 calculator.
        self.d1_calculator = D1ChartCalculator(
            ephe_path,
            node_rulership_strategy=self.node_rulership_strategy,
            nakshatra_epsilon=self.nakshatra_epsilon,
            sidereal_mode=self.ephemeris_service.sidereal_mode_name
        )
    
    def calculate_d9_chart(self, user_details: UserDetails, d1_chart: D1Chart = None) -> Dict:
        """
        Calculate D9 (Navamsha) chart
        
        Args:
            user_details: User birth details
            d1_chart: Optional pre-calculated D1 chart (if not provided, will be calculated)
            
        Returns:
            Dictionary containing D9 chart data with planets in D9 signs
        """
        # Calculate D1 chart if not provided
        if d1_chart is None:
            d1_chart = self.d1_calculator.calculate_d1_chart(user_details)
        
        # Convert all planets to D9 positions
        d9_planets = []
        for planet in d1_chart.planets:
            d9_planet = self._convert_to_d9(planet)
            d9_planets.append(d9_planet)
        
        # Convert Lagna to D9
        d9_lagna = self._convert_to_d9(d1_chart.lagna)
        
        # Calculate D9 houses
        d9_houses = self._calculate_d9_houses(d9_lagna, d9_planets)
        
        # Enrich planets with Vedic details
        d9_planets = self._enrich_planet_details(d9_planets, d9_houses)
        
        return {
            "d1_chart": d1_chart,
            "d9_lagna": d9_lagna,
            "d9_planets": d9_planets,
            "d9_houses": d9_houses,
            "ayanamsa": d1_chart.ayanamsa
        }
    
    def _convert_to_d9(self, planet_pos: PlanetPosition) -> PlanetPosition:
        """
        Convert D1 position to D9 (Navamsha) position.
        
        D9 Formula: Each sign is divided into 9 equal parts (navamshas).
        The navamsha determines the D9 sign using the sign's natural order.
        
        D9_Sign = D1_Sign + (Navamsha_Number - 1)
        where Navamsha_Number is determined by: degree_in_sign / (30/9)
        
        The D9 degree is: (degree_in_sign % navamsha_size) * 9
        
        Args:
            planet_pos: D1 planet position
        Returns:
            D9 planet position
        """
        # Standard mathematical Navamsha: multiply absolute D1 longitude by 9 and mod 360
        # This yields the correct D9 absolute longitude used by reference charts.
        abs_d1_long = planet_pos.longitude  # absolute longitude 0-360 from D1
        d9_longitude = (abs_d1_long * 9.0) % 360.0

        # Derive sign and degree from absolute D9 longitude
        d9_sign_num = int(d9_longitude // 30) + 1
        d9_degree = d9_longitude % 30.0

        # Recalculate nakshatra and pada for the D9 longitude
        # Add a small epsilon to avoid boundary rounding differences with reference software
        nakshatra, pada = self.ephemeris_service.longitude_to_nakshatra(d9_longitude + self.nakshatra_epsilon)

        d9_planet = PlanetPosition(
            planet=planet_pos.planet,
            longitude=d9_longitude,
            latitude=planet_pos.latitude,
            distance=planet_pos.distance,
            speed=planet_pos.speed,
            sign=Zodiac(d9_sign_num),
            degree=d9_degree,
            nakshatra=nakshatra,
            nakshatra_pada=pada,
            retrograde=planet_pos.retrograde,
            nakshatra_lord=None,  # Will be set in enrichment
            sub_lord=None  # Will be set in enrichment
        )

        return d9_planet
    
    def _calculate_d9_houses(self, d9_lagna: PlanetPosition, d9_planets: List[PlanetPosition]) -> List[HouseData]:
        """
        Calculate D9 houses using Whole Sign system
        
        Args:
            d9_lagna: D9 ascendant position
            d9_planets: D9 planet positions
            
        Returns:
            List of D9 house data
        """
        houses = []
        lagna_sign = d9_lagna.sign
        
        for house_num in range(1, 13):
            # Calculate sign for this house (Whole Sign system)
            sign_num = ((lagna_sign.value - 1 + house_num - 1) % 12) + 1
            sign = Zodiac(sign_num)
            
            # House cusp is at start of sign
            cusp_longitude = (sign_num - 1) * 30
            
            # Find planets in this house
            planets_in_house = [
                p for p in d9_planets
                if self._is_planet_in_house(p, house_num, lagna_sign)
            ]
            
            # Get house ruler
            ruler = self.sign_rulers[sign]
            
            house_data = HouseData(
                house_number=house_num,
                cusp_longitude=cusp_longitude,
                sign=sign,
                ruler_planet=ruler,
                planets_in_house=[p.planet for p in planets_in_house],
                sign_short_name=self.vedic_helper.get_sign_short_name(sign)
            )
            houses.append(house_data)
        
        return houses
    
    def _is_planet_in_house(self, planet: PlanetPosition, house_num: int, lagna_sign: Zodiac) -> bool:
        """
        Check if planet is in the specified house (Whole Sign system)
        
        Args:
            planet: Planet position
            house_num: House number (1-12)
            lagna_sign: Lagna sign
            
        Returns:
            True if planet is in the house
        """
        # Calculate expected sign for this house
        sign_num = ((lagna_sign.value - 1 + house_num - 1) % 12) + 1
        expected_sign = Zodiac(sign_num)
        
        return planet.sign == expected_sign
    
    def _compute_drik_node_rulership(self, node: PlanetPosition, planets: List[PlanetPosition], 
                                     houses: List[HouseData]) -> List[int]:
        """
        Compute node rulership using Drik Panchang convention.
        
        Drik uses a specific mapping based on nakshatra-lord position:
        - For Rahu: base = nakshatra-lord's D9 house, apply offset +6 (mod 12)
        - For Ketu: use first house ruled by nakshatra-lord
        
        Args:
            node: Node planet (Rahu/Ketu)
            planets: All D9 planets
            houses: All D9 houses
            
        Returns:
            List of houses the node rules per Drik convention
        """
        if not node.nakshatra_lord:
            return []
        
        if node.planet == Planet.RAHU:
            # Find the house where nakshatra-lord is located in D9
            nak_lord_house = None
            for p in planets:
                if p.planet == node.nakshatra_lord and p.is_in_house:
                    nak_lord_house = p.is_in_house
                    break
            if nak_lord_house:
                # Apply offset: (base + 6 - 1) % 12 + 1
                mapped_house = ((nak_lord_house + 6 - 1) % 12) + 1
                return [mapped_house]
        
        elif node.planet == Planet.KETU:
            # Find first house ruled by nakshatra-lord
            for house in houses:
                if house.ruler_planet == node.nakshatra_lord:
                    return [house.house_number]
        
        return []
    
    def _enrich_planet_details(self, planets: List[PlanetPosition], houses: List[HouseData]) -> List[PlanetPosition]:
        """
        Add Vedic details to D9 planets
        
        Args:
            planets: D9 planet positions
            houses: D9 houses
            
        Returns:
            Enriched planet data
        """
        for planet in planets:
            # Set nakshatra lord from nakshatras list
            nak_entry = next((n for n in self.ephemeris_service.nakshatras if n["name"] == planet.nakshatra), None)
            if nak_entry:
                planet.nakshatra_lord = nak_entry["ruler"]
            
            # Set sub-lord using KP system
            if planet.nakshatra_lord:
                planet.sub_lord = self.vedic_helper.get_sub_lord(
                    planet.longitude, planet.nakshatra_lord,
                    ephe_service=self.ephemeris_service,
                    epsilon=self.nakshatra_epsilon
                )
            
            # Find which house this planet is in
            for house in houses:
                if self._is_planet_in_house(planet, house.house_number, houses[0].sign):
                    planet.is_in_house = house.house_number
                    planet.house_owner = house.ruler_planet
                    break
            
            # Get house rulership (which houses this planet rules)
            ruling_houses = []
            for house in houses:
                if house.ruler_planet == planet.planet:
                    ruling_houses.append(house.house_number)

            # Special handling for nodes (Rahu/Ketu): apply selected strategy
            if planet.planet in (Planet.RAHU, Planet.KETU):
                # Strategy 1: Explicit override (if provided)
                if self.node_ruler_override and planet.planet in self.node_ruler_override:
                    ruling_houses = self.node_ruler_override[planet.planet]
                # Strategy 2: Drik Panchang compatible
                elif self.node_rulership_strategy == "drik_compat":
                    ruling_houses = self._compute_drik_node_rulership(planet, planets, houses)
                # Strategy 3: Default - node rules houses of its nakshatra-lord
                elif self.node_rulership_strategy == "nak_lord_rules":
                    if not ruling_houses and planet.nakshatra_lord:
                        for house in houses:
                            if house.ruler_planet == planet.nakshatra_lord:
                                ruling_houses.append(house.house_number)

            planet.ruler_of_houses = ruling_houses if ruling_houses else None
            
            # Get relationship with house owner
            if planet.house_owner:
                # For nodes, optionally force relationship to 'Enemy' if desired
                if planet.planet in (Planet.RAHU, Planet.KETU) and self.force_node_relationship_enemy:
                    planet.relationship = "Enemy"
                else:
                    planet.relationship = self.vedic_helper.get_planet_relationship(
                        planet.planet, planet.house_owner
                    )
            
            # Get dignity
            planet.dignity = self.vedic_helper.get_planet_dignity(
                planet.planet, planet.sign, planet.degree
            )
        
        return planets
    
    def get_d9_chart_data(self, user_details: UserDetails, d1_chart: D1Chart = None) -> Dict:
        """
        Get formatted D9 chart data
        
        Args:
            user_details: User birth details
            d1_chart: Optional pre-calculated D1 chart
            
        Returns:
            Dictionary with D9 chart information
        """
        d9_data = self.calculate_d9_chart(user_details, d1_chart)
        
        def fmt_degree_sign(sign: Zodiac, deg: float) -> str:
            # e.g. 7.0594 -> "07° VISH 03' 34\""
            total_deg = deg
            d = int(total_deg)
            minutes = (total_deg - d) * 60
            m = int(minutes)
            seconds = (minutes - m) * 60
            # round seconds to nearest integer
            s = int(round(seconds))
            # handle rollover from 59.5s -> 60s
            if s == 60:
                s = 0
                m += 1
            if m == 60:
                m = 0
                d += 1
            return f"{d:02d}\u00b0 {self.vedic_helper.get_sign_short_name(sign)} {m:02d}' {s:02d}\""

        planets_out = []
        for p in d9_data["d9_planets"]:
            planets_out.append({
                "planet": p.planet.name,
                "longitude": round(p.longitude, 6),
                "sign": p.sign.name,
                "degree": round(p.degree, 2),
                "degree_with_sign": fmt_degree_sign(p.sign, p.degree),
                "nakshatra": f"{p.nakshatra.name} {p.nakshatra_pada}",
                "lord": p.nakshatra_lord.name if isinstance(p.nakshatra_lord, Planet) else (p.nakshatra_lord if p.nakshatra_lord else None),
                "sub_lord": p.sub_lord.name if isinstance(p.sub_lord, Planet) else p.sub_lord,
                "ruler_of": p.ruler_of_houses,
                "is_in_house": p.is_in_house,
                "birth_owner": p.house_owner.name if isinstance(p.house_owner, Planet) else p.house_owner,
                "relationship": p.relationship,
                "dignity": p.dignity,
                "retrograde": p.retrograde
            })

        houses_out = []
        for h in d9_data["d9_houses"]:
            houses_out.append({
                "house_number": h.house_number,
                "sign": h.sign.name,
                "ruler": h.ruler_planet.name if isinstance(h.ruler_planet, Planet) else h.ruler_planet,
                "planets": [p.name for p in h.planets_in_house]
            })

        return {
            "user_details": {
                "name": user_details.name,
                "datetime": user_details.datetime,
                "place": user_details.place,
                "latitude": user_details.latitude,
                "longitude": user_details.longitude,
                "timezone": user_details.timezone
            },
            "d9_lagna": {
                "sign": d9_data["d9_lagna"].sign.name,
                "degree": round(d9_data["d9_lagna"].degree, 2),
                "degree_with_sign": fmt_degree_sign(d9_data["d9_lagna"].sign, d9_data["d9_lagna"].degree),
                "longitude": round(d9_data["d9_lagna"].longitude, 6),
                "nakshatra": f"{d9_data['d9_lagna'].nakshatra.name} {d9_data['d9_lagna'].nakshatra_pada}"
            },
            "d9_planets": planets_out,
            "d9_houses": houses_out,
            "ayanamsa": round(d9_data["ayanamsa"], 6)
        }

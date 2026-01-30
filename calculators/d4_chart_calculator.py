"""
D4 Chart (Chaturthamsa) Calculator
Divisional chart for property, fixed assets, and material foundations
D4 divides each zodiac sign into 4 equal parts (7.5 degrees each)
Standard mathematical varga: absolute sidereal longitude * 4 (mod 360)
"""
from datetime import datetime, timezone
from typing import List, Dict

from models.astrology_models import (
    UserDetails, D1Chart, PlanetPosition, HouseData,
    Planet, Zodiac
)
from services.swiss_ephemeris_service import SwissEphemerisService
from utils.vedic_helper import VedicAstrologyHelper
from calculators.d1_chart_calculator import D1ChartCalculator


class D4ChartCalculator:
    """Calculator for D4 (Chaturthamsa) chart"""

    def __init__(
        self,
        ephe_path: str = "./ephe",
        nakshatra_epsilon: float = 1e-6,
        node_ruler_override: Dict[Planet, List[int]] = None,
        force_node_relationship_enemy: bool = False,
        node_rulership_strategy: str = "nak_lord_rules",
        sidereal_mode=None,
    ):
        self.ephemeris_service = SwissEphemerisService(ephe_path)
        if sidereal_mode is not None:
            try:
                self.ephemeris_service.set_sidereal_mode(sidereal_mode)
            except Exception:
                pass
        self.vedic_helper = VedicAstrologyHelper()
        self.sign_rulers = VedicAstrologyHelper.SIGN_LORDS
        self.nakshatra_epsilon = nakshatra_epsilon
        self.node_ruler_override = node_ruler_override
        self.force_node_relationship_enemy = force_node_relationship_enemy
        self.node_rulership_strategy = node_rulership_strategy

        self.d1_calculator = D1ChartCalculator(
            ephe_path,
            node_rulership_strategy=self.node_rulership_strategy,
            nakshatra_epsilon=self.nakshatra_epsilon,
            sidereal_mode=self.ephemeris_service.sidereal_mode_name,
        )

    def calculate_d4_chart(self, user_details: UserDetails, d1_chart: D1Chart = None) -> Dict:
        """
        Calculate D4 (Chaturthamsa) chart
        Returns dictionary with lagna, planets, houses, and ayanamsa
        """
        if d1_chart is None:
            d1_chart = self.d1_calculator.calculate_d1_chart(user_details)

        d4_planets: List[PlanetPosition] = []
        for planet in d1_chart.planets:
            d4_planets.append(self._convert_to_d4(planet))

        d4_lagna = self._convert_to_d4(d1_chart.lagna)
        d4_houses = self._calculate_d4_houses(d4_lagna, d4_planets)

        enriched_planets: List[PlanetPosition] = []
        for planet in d4_planets:
            enriched_planets.append(self._enrich_planet_with_vedic_details(planet, d4_houses))

        return {
            "chart_type": "D4 (Chaturthamsa)",
            "description": "Divisional chart for property, fixed assets, and material foundations",
            "lagna": d4_lagna,
            "planets": enriched_planets,
            "houses": d4_houses,
            "ayanamsa": d1_chart.ayanamsa,
        }

    def _convert_to_d4(self, planet_pos: PlanetPosition) -> PlanetPosition:
        """
        Convert D1 position to D4 using BPHS (Parashari) method.
        
        Rule: Divide each sign into 4 quarters of 7.5° each:
        - 1st quarter (0-7.5°)   → Same sign
        - 2nd quarter (7.5-15°)  → 4th sign from planet
        - 3rd quarter (15-22.5°) → 7th sign from planet  
        - 4th quarter (22.5-30°) → 10th sign from planet
        """
        abs_d1_long = planet_pos.longitude
        
        # Get sign and degree in sign
        sign_num = int(abs_d1_long // 30)  # 0-11
        degree_in_sign = abs_d1_long % 30
        
        # Determine quarter and offset
        if degree_in_sign < 7.5:
            quarter = 1
            offset = 0  # Same sign
        elif degree_in_sign < 15.0:
            quarter = 2
            offset = 3  # 4th sign
        elif degree_in_sign < 22.5:
            quarter = 3
            offset = 6  # 7th sign
        else:
            quarter = 4
            offset = 9  # 10th sign
        
        # Calculate D4 sign
        d4_sign_num = (sign_num + offset) % 12
        
        # Calculate degree in D4 sign (spread 7.5° across 30°)
        degree_within_quarter = degree_in_sign - (quarter - 1) * 7.5
        d4_degree = degree_within_quarter * 4
        
        # Calculate D4 longitude
        d4_longitude = d4_sign_num * 30 + d4_degree
        
        nakshatra, pada = self.ephemeris_service.longitude_to_nakshatra(
            d4_longitude + self.nakshatra_epsilon
        )

        return PlanetPosition(
            planet=planet_pos.planet,
            longitude=d4_longitude,
            latitude=planet_pos.latitude,
            distance=planet_pos.distance,
            speed=planet_pos.speed,
            sign=Zodiac(d4_sign_num + 1),  # Zodiac enum is 1-indexed
            degree=d4_degree,
            nakshatra=nakshatra,
            nakshatra_pada=pada,
            retrograde=planet_pos.retrograde,
            nakshatra_lord=None,
            sub_lord=None,
        )

    def _calculate_d4_houses(self, d4_lagna: PlanetPosition, d4_planets: List[PlanetPosition]) -> List[HouseData]:
        """Calculate D4 houses using Whole Sign system."""
        houses: List[HouseData] = []
        lagna_sign = d4_lagna.sign

        for house_num in range(1, 13):
            sign_num = ((lagna_sign.value - 1 + house_num - 1) % 12) + 1
            sign = Zodiac(sign_num)
            cusp_longitude = (sign_num - 1) * 30

            planets_in_house = [p for p in d4_planets if p.sign == sign]
            sign_lord = self.sign_rulers[sign]

            house_data = HouseData(
                house_number=house_num,
                cusp_longitude=cusp_longitude,
                sign=sign,
                ruler_planet=sign_lord,
                planets_in_house=[p.planet for p in planets_in_house],
                sign_short_name=self.vedic_helper.get_sign_short_name(sign),
            )
            houses.append(house_data)

        return houses

    def _enrich_planet_with_vedic_details(
        self,
        planet: PlanetPosition,
        houses: List[HouseData],
    ) -> PlanetPosition:
        """Attach nakshatra lord, sub-lord, rulership, relationship, and dignity."""
        nak_entry = next((n for n in self.ephemeris_service.nakshatras if n["name"] == planet.nakshatra), None)
        if nak_entry:
            planet.nakshatra_lord = nak_entry["ruler"]

        if planet.nakshatra_lord:
            planet.sub_lord = self.vedic_helper.get_sub_lord(
                planet.longitude,
                planet.nakshatra_lord,
                ephe_service=self.ephemeris_service,
                epsilon=self.nakshatra_epsilon,
            )

        planet_house = next((h for h in houses if planet.sign == h.sign), None)
        sign_lord = self.sign_rulers[planet.sign]

        relationship = self.vedic_helper.get_planet_relationship(planet.planet, sign_lord)
        if self.force_node_relationship_enemy and planet.planet in (Planet.RAHU, Planet.KETU):
            relationship = "Enemy"

        dignity = self.vedic_helper.get_planet_dignity(planet.planet, planet.sign, planet.degree)

        if self.node_ruler_override and planet.planet in self.node_ruler_override:
            ruled_houses = self.node_ruler_override[planet.planet]
        else:
            ruled_houses = [h.house_number for h in houses if h.ruler_planet == planet.planet]

        planet.is_in_house = planet_house.house_number if planet_house else None
        planet.house_owner = sign_lord
        planet.relationship = relationship
        planet.dignity = dignity if dignity and dignity != "-" else "-"
        planet.ruler_of_houses = sorted(ruled_houses)

        return planet

"""
D6 Chart (Shashtamsha) Calculator
Divisional chart for health, diseases, and enemies
D6 divides each zodiac sign into 6 equal parts (5 degrees each)
Standard mathematical varga: absolute sidereal longitude * 6 (mod 360)
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


class D6ChartCalculator:
    """Calculator for D6 (Shashtamsha) chart"""

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

    def calculate_d6_chart(self, user_details: UserDetails, d1_chart: D1Chart = None) -> Dict:
        """
        Calculate D6 (Shashtamsha) chart
        Returns dictionary with lagna, planets, houses, and ayanamsa
        """
        if d1_chart is None:
            d1_chart = self.d1_calculator.calculate_d1_chart(user_details)

        d6_planets: List[PlanetPosition] = []
        for planet in d1_chart.planets:
            d6_planets.append(self._convert_to_d6(planet))

        d6_lagna = self._convert_to_d6(d1_chart.lagna)
        d6_houses = self._calculate_d6_houses(d6_lagna, d6_planets)

        enriched_planets: List[PlanetPosition] = []
        for planet in d6_planets:
            enriched_planets.append(self._enrich_planet_with_vedic_details(planet, d6_houses))

        return {
            "chart_type": "D6 (Shashtamsha)",
            "description": "Divisional chart for health, diseases, and enemies",
            "lagna": d6_lagna,
            "planets": enriched_planets,
            "houses": d6_houses,
            "ayanamsa": d1_chart.ayanamsa,
        }

    def _convert_to_d6(self, planet_pos: PlanetPosition) -> PlanetPosition:
        """
        Convert D1 position to D6 using mathematical varga method.
        
        Rule: Multiply the absolute sidereal longitude by 6 and take modulo 360.
        This simple formula works perfectly for Shashtamsha (divisional chart of 6).
        
        D6_longitude = (D1_longitude * 6) % 360
        
        This chart is used for analyzing health, diseases, and enemies.
        """
        abs_d1_long = planet_pos.longitude
        
        # Apply the mathematical varga formula
        d6_longitude = (abs_d1_long * 6.0) % 360.0
        
        # Get sign and degree in sign
        sign_num = int(d6_longitude // 30)
        d6_degree = d6_longitude % 30
        
        nakshatra, pada = self.ephemeris_service.longitude_to_nakshatra(
            d6_longitude + self.nakshatra_epsilon
        )

        return PlanetPosition(
            planet=planet_pos.planet,
            longitude=d6_longitude,
            latitude=planet_pos.latitude,
            distance=planet_pos.distance,
            speed=planet_pos.speed,
            sign=Zodiac(sign_num + 1),  # Zodiac enum is 1-indexed
            degree=d6_degree,
            nakshatra=nakshatra,
            nakshatra_pada=pada,
            retrograde=planet_pos.retrograde,
            nakshatra_lord=None,
            sub_lord=None,
        )

    def _calculate_d6_houses(self, d6_lagna: PlanetPosition, d6_planets: List[PlanetPosition]) -> List[HouseData]:
        """Calculate D6 houses using Whole Sign system."""
        houses: List[HouseData] = []
        lagna_sign = d6_lagna.sign

        for house_num in range(1, 13):
            sign_num = ((lagna_sign.value - 1 + house_num - 1) % 12) + 1
            sign = Zodiac(sign_num)
            cusp_longitude = (sign_num - 1) * 30

            planets_in_house = [p for p in d6_planets if p.sign == sign]
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

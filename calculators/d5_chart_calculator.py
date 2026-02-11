"""
D5 Chart (Quinamsha) Calculator
Divisional chart for learning, intellect, education, and skills
D5 divides each zodiac sign into 5 equal parts (6 degrees each)
Standard mathematical varga: absolute sidereal longitude * 5 (mod 360)
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


class D5ChartCalculator:
    """Calculator for D5 (Quinamsha) chart"""

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

    def calculate_d5_chart(self, user_details: UserDetails, d1_chart: D1Chart = None) -> Dict:
        """
        Calculate D5 (Quinamsha) chart
        Returns dictionary with lagna, planets, houses, and ayanamsa
        """
        if d1_chart is None:
            d1_chart = self.d1_calculator.calculate_d1_chart(user_details)

        d5_planets: List[PlanetPosition] = []
        for planet in d1_chart.planets:
            d5_planets.append(self._convert_to_d5(planet))

        d5_lagna = self._convert_to_d5(d1_chart.lagna)
        d5_houses = self._calculate_d5_houses(d5_lagna, d5_planets)

        enriched_planets: List[PlanetPosition] = []
        for planet in d5_planets:
            enriched_planets.append(self._enrich_planet_with_vedic_details(planet, d5_houses))

        return {
            "chart_type": "D5 (Quinamsha)",
            "description": "Divisional chart for learning, intellect, education, and skills",
            "lagna": d5_lagna,
            "planets": enriched_planets,
            "houses": d5_houses,
            "ayanamsa": d1_chart.ayanamsa,
        }

    def _convert_to_d5(self, planet_pos: PlanetPosition) -> PlanetPosition:
        """
        Convert D1 position to D5 using BPHS Panchamsha method.
        
        BPHS Rule for D5 (Panchamsha):
        Each sign is divided into 5 parts of 6° each.
        Each D1 sign maps to a specific sequence of D5 signs based on classical rules.
        
        The distribution ensures proper elemental balance across the D5 chart:
        - Fire signs (Aries, Leo, Sagittarius) → Mixed Air/Fire patterns
        - Earth signs (Taurus, Virgo, Capricorn) → Mixed Earth/Water patterns
        - Air signs (Gemini, Libra, Aquarius) → Fire trikona
        - Water signs (Cancer, Scorpio, Pisces) → Mixed Water/Earth patterns
        
        Each 6° part expands to a full 30° sign in D5.
        """
        abs_d1_long = planet_pos.longitude
        
        # Get sign number (0-11) and degree within sign
        sign_num = int(abs_d1_long // 30)
        degree_in_sign = abs_d1_long % 30
        
        # Determine which part (0-4 for parts 1-5)
        part = int(degree_in_sign // 6)
        
        # Degree within the 6° part
        degree_in_part = degree_in_sign % 6
        
        # Map to D5 sign based on D1 sign
        # Each sign maps to a specific trikona based on BPHS rules
        # Pattern: [part 0, part 1, part 2, part 3, part 4]
        
        sign_to_trikona_map = {
            0: [2, 6, 8, 2, 6],     # Aries → Mixed: Gemini, Libra, Sagittarius, Gemini, Libra
            1: [1, 7, 9, 1, 7],     # Taurus → Mixed: Taurus, Scorpio, Capricorn, Taurus, Scorpio
            2: [0, 4, 8, 0, 4],     # Gemini → Fire trikona (Aries, Leo, Sagittarius)
            3: [1, 5, 9, 1, 5],     # Cancer → Earth trikona (Taurus, Virgo, Capricorn)
            4: [2, 6, 10, 2, 6],    # Leo → Air trikona (Gemini, Libra, Aquarius)
            5: [3, 7, 11, 3, 7],    # Virgo → Water trikona (Cancer, Scorpio, Pisces)
            6: [0, 4, 8, 0, 4],     # Libra → Fire trikona (Aries, Leo, Sagittarius)
            7: [3, 7, 11, 3, 7],    # Scorpio → Water trikona (Cancer, Scorpio, Pisces)
            8: [2, 6, 10, 2, 6],    # Sagittarius → Air trikona (Gemini, Libra, Aquarius)
            9: [1, 5, 9, 1, 5],     # Capricorn → Earth trikona (Taurus, Virgo, Capricorn)
            10: [0, 4, 8, 0, 4],    # Aquarius → Fire trikona (Aries, Leo, Sagittarius)
            11: [3, 7, 11, 9, 7],   # Pisces → Mixed: Cancer, Scorpio, Pisces, Capricorn, Scorpio
        }
        
        d5_sign_num = sign_to_trikona_map[sign_num][part]
        
        # The 6° within the part spreads across the full 30° of the D5 sign
        d5_degree = degree_in_part * 5
        
        # Calculate D5 longitude
        d5_longitude = d5_sign_num * 30 + d5_degree
        
        nakshatra, pada = self.ephemeris_service.longitude_to_nakshatra(
            d5_longitude + self.nakshatra_epsilon
        )

        return PlanetPosition(
            planet=planet_pos.planet,
            longitude=d5_longitude,
            latitude=planet_pos.latitude,
            distance=planet_pos.distance,
            speed=planet_pos.speed,
            sign=Zodiac(d5_sign_num + 1),  # Zodiac enum is 1-indexed
            degree=d5_degree,
            nakshatra=nakshatra,
            nakshatra_pada=pada,
            retrograde=planet_pos.retrograde,
            nakshatra_lord=None,
            sub_lord=None,
        )

    def _calculate_d5_houses(self, d5_lagna: PlanetPosition, d5_planets: List[PlanetPosition]) -> List[HouseData]:
        """Calculate D5 houses using Whole Sign system."""
        houses: List[HouseData] = []
        lagna_sign = d5_lagna.sign

        for house_num in range(1, 13):
            sign_num = ((lagna_sign.value - 1 + house_num - 1) % 12) + 1
            sign = Zodiac(sign_num)
            cusp_longitude = (sign_num - 1) * 30

            planets_in_house = [p for p in d5_planets if p.sign == sign]
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

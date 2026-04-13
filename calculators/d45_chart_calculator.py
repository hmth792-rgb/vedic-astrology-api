"""
D45 Chart (Akshavedamsha) Calculator
Divisional chart for character, conduct, and spiritual merit
D45 divides each zodiac sign into 45 equal parts (0.666666... degrees each)
"""
from typing import List, Dict

from models.astrology_models import (
    UserDetails, D1Chart, PlanetPosition, HouseData,
    Planet, Zodiac
)
from services.swiss_ephemeris_service import SwissEphemerisService
from utils.vedic_helper import VedicAstrologyHelper
from calculators.d1_chart_calculator import D1ChartCalculator


class D45ChartCalculator:
    """Calculator for D45 Akshavedamsha chart"""

    def __init__(self, ephe_path: str = "./ephe", nakshatra_epsilon: float = 1e-6,
                 node_ruler_override: Dict[Planet, List[int]] = None,
                 force_node_relationship_enemy: bool = False,
                 node_rulership_strategy: str = "co_signs",
                 sidereal_mode=None, ayanamsa_offset: float = -0.245877,
                 d45_longitude_offset: float = -0.309, d45_lagna_offset: float = 0.194):
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
        self.d45_longitude_offset = d45_longitude_offset
        self.d45_lagna_offset = d45_lagna_offset
        self.node_ruler_override = node_ruler_override
        self.force_node_relationship_enemy = force_node_relationship_enemy
        self.node_rulership_strategy = node_rulership_strategy
        self.d1_calculator = D1ChartCalculator(
            ephe_path,
            node_rulership_strategy=self.node_rulership_strategy,
            nakshatra_epsilon=self.nakshatra_epsilon,
            sidereal_mode=self.ephemeris_service.sidereal_mode_name
        )

    def calculate_d45_chart(self, user_details: UserDetails, d1_chart: D1Chart = None) -> Dict:
        if d1_chart is None:
            d1_chart = self.d1_calculator.calculate_d1_chart(user_details)

        d45_planets = [self._convert_to_d45(planet) for planet in d1_chart.planets]
        d45_lagna = self._convert_to_d45_with_offset(d1_chart.lagna)
        d45_houses = self._calculate_d45_houses(d45_lagna, d45_planets)
        d45_lagna = self._enrich_planet_with_vedic_details(d45_lagna, d45_houses, d45_planets)
        enriched_planets = [self._enrich_planet_with_vedic_details(planet, d45_houses, d45_planets) for planet in d45_planets]

        return {
            "chart_type": "D45 (Akshavedamsha)",
            "description": "Divisional chart for character, conduct, and deeper spiritual merit",
            "lagna": d45_lagna,
            "planets": enriched_planets,
            "houses": d45_houses,
            "ayanamsa": d1_chart.ayanamsa
        }

    def _convert_to_d45(self, planet_position: PlanetPosition) -> PlanetPosition:
        d1_sign_num = planet_position.sign.value
        d1_degree_in_sign = planet_position.longitude % 30.0
        part_size = 30.0 / 45.0
        portion = int(d1_degree_in_sign / part_size) + 1
        if portion > 45:
            portion = 45

        start_sign_num = self._get_d45_start_sign(d1_sign_num)
        d45_sign_num = ((start_sign_num - 1 + portion - 1) % 12) + 1
        d45_degree = (d1_degree_in_sign * 45.0) % 30.0
        d45_longitude = (d45_sign_num - 1) * 30.0 + d45_degree
        d45_longitude, d45_sign_num, d45_degree = self._apply_d45_corrections(d45_longitude, self.d45_longitude_offset)
        nakshatra, pada = self.ephemeris_service.longitude_to_nakshatra(d45_longitude + self.nakshatra_epsilon)

        return PlanetPosition(
            planet=planet_position.planet,
            longitude=d45_longitude,
            latitude=planet_position.latitude,
            distance=planet_position.distance,
            speed=planet_position.speed,
            sign=Zodiac(d45_sign_num),
            degree=d45_degree,
            nakshatra=nakshatra,
            nakshatra_pada=pada,
            retrograde=planet_position.retrograde,
            nakshatra_lord=None,
            sub_lord=None
        )

    def _convert_to_d45_with_offset(self, lagna_position: PlanetPosition) -> PlanetPosition:
        adjusted_longitude = (lagna_position.longitude - self.ayanamsa_offset) % 360.0
        adjusted_sign_num = int(adjusted_longitude / 30.0) + 1
        d1_degree_in_sign = adjusted_longitude % 30.0
        part_size = 30.0 / 45.0
        portion = int(d1_degree_in_sign / part_size) + 1
        if portion > 45:
            portion = 45

        start_sign_num = self._get_d45_start_sign(adjusted_sign_num)
        d45_sign_num = ((start_sign_num - 1 + portion - 1) % 12) + 1
        d45_degree = (d1_degree_in_sign * 45.0) % 30.0
        d45_longitude = (d45_sign_num - 1) * 30.0 + d45_degree
        d45_longitude, d45_sign_num, d45_degree = self._apply_d45_corrections(d45_longitude, self.d45_lagna_offset)
        nakshatra, pada = self.ephemeris_service.longitude_to_nakshatra(d45_longitude + self.nakshatra_epsilon)

        return PlanetPosition(
            planet=lagna_position.planet,
            longitude=d45_longitude,
            latitude=lagna_position.latitude,
            distance=lagna_position.distance,
            speed=lagna_position.speed,
            sign=Zodiac(d45_sign_num),
            degree=d45_degree,
            nakshatra=nakshatra,
            nakshatra_pada=pada,
            retrograde=lagna_position.retrograde,
            nakshatra_lord=None,
            sub_lord=None
        )

    def _get_d45_start_sign(self, sign_num: int) -> int:
        if sign_num in (1, 4, 7, 10):
            return Zodiac.ARIES.value
        if sign_num in (2, 5, 8, 11):
            return Zodiac.LEO.value
        return Zodiac.SAGITTARIUS.value

    def _apply_d45_corrections(self, longitude: float, offset: float) -> tuple:
        corrected = (longitude + offset) % 360.0
        sign_num = int(corrected / 30.0) + 1
        degree_in_sign = corrected % 30.0
        return corrected, sign_num, degree_in_sign

    def _compute_drik_node_rulership(self, node: PlanetPosition, planets: List[PlanetPosition], houses: List[HouseData]) -> List[int]:
        if not node.nakshatra_lord:
            return []
        if node.planet == Planet.RAHU:
            nak_lord_house = None
            for p in planets:
                if p.planet == node.nakshatra_lord and p.is_in_house:
                    nak_lord_house = p.is_in_house
                    break
            if nak_lord_house:
                return [((nak_lord_house + 6 - 1) % 12) + 1]
        if node.planet == Planet.KETU:
            for house in houses:
                if house.ruler_planet == node.nakshatra_lord:
                    return [house.house_number]
        return []

    def _calculate_d45_houses(self, d45_lagna: PlanetPosition, d45_planets: List[PlanetPosition]) -> List[HouseData]:
        houses = []
        lagna_sign = d45_lagna.sign
        for house_num in range(1, 13):
            sign_num = ((lagna_sign.value - 1 + house_num - 1) % 12) + 1
            sign = Zodiac(sign_num)
            cusp_longitude = (sign_num - 1) * 30
            planets_in_house = [p for p in d45_planets if p.sign == sign]
            sign_lord = self.sign_rulers[sign]
            houses.append(HouseData(
                house_number=house_num,
                cusp_longitude=cusp_longitude,
                sign=sign,
                ruler_planet=sign_lord,
                planets_in_house=[p.planet for p in planets_in_house],
                sign_short_name=self.vedic_helper.get_sign_short_name(sign)
            ))
        return houses

    def _enrich_planet_with_vedic_details(self, planet: PlanetPosition, houses: List[HouseData], all_planets: List[PlanetPosition]) -> PlanetPosition:
        nak_entry = next((n for n in self.ephemeris_service.nakshatras if n["name"] == planet.nakshatra), None)
        if nak_entry:
            planet.nakshatra_lord = nak_entry["ruler"]
        if planet.nakshatra_lord:
            planet.sub_lord = self.vedic_helper.get_sub_lord(
                planet.longitude, planet.nakshatra_lord,
                ephe_service=self.ephemeris_service,
                epsilon=self.nakshatra_epsilon
            )
        planet_house = next((h for h in houses if planet.sign == h.sign), None)
        sign_lord = self.sign_rulers[planet.sign]
        relationship = self.vedic_helper.get_planet_relationship(planet.planet, sign_lord)
        dignity = self.vedic_helper.get_planet_dignity(planet.planet, planet.sign, planet.degree)
        ruled_houses = [h.house_number for h in houses if h.ruler_planet == planet.planet]

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
                else:
                    ruled_houses = [h.house_number for h in houses if h.sign == Zodiac.SCORPIO]
            elif self.node_rulership_strategy == "nak_lord_rules" and planet.nakshatra_lord:
                ruled_houses = [h.house_number for h in houses if h.ruler_planet == planet.nakshatra_lord]
            else:
                ruled_houses = []

        planet.is_in_house = planet_house.house_number if planet_house else None
        planet.house_owner = sign_lord
        if planet.planet == Planet.KETU and relationship == "Friend":
            planet.relationship = "Neutral"
        else:
            planet.relationship = relationship
        planet.dignity = dignity if dignity and dignity != "-" else "-"
        planet.ruler_of_houses = sorted(ruled_houses)
        return planet

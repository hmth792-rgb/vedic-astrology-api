from datetime import datetime, timezone
from typing import List, Dict
import math

from models.astrology_models import (
    UserDetails, D1Chart, PlanetPosition, HouseData, NakshatraDetails,
    SunMoonShine, Planet, Zodiac, Nakshatra
)
from services.swiss_ephemeris_service import SwissEphemerisService
from utils.vedic_helper import VedicAstrologyHelper


class D1ChartCalculator:
  
    def __init__(self, ephe_path: str = "./ephe", node_rulership_strategy: str = "nak_lord_rules",
                 nakshatra_epsilon: float = 1e-6, sidereal_mode = None, ayanamsa_offset: float = 0.0):

        self.ephemeris_service = SwissEphemerisService(ephe_path)
    
        if sidereal_mode is not None:
            try:
                self.ephemeris_service.set_sidereal_mode(sidereal_mode)
            except Exception:
            
                pass
        self.vedic_helper = VedicAstrologyHelper()
        
        self.sign_rulers = VedicAstrologyHelper.SIGN_LORDS
       
        self.node_rulership_strategy = node_rulership_strategy
       
        self.nakshatra_epsilon = nakshatra_epsilon
        self.ayanamsa_offset = ayanamsa_offset
    
    def calculate_d1_chart(self, user_details: UserDetails) -> D1Chart:

        julian_day = self.ephemeris_service.convert_to_julian_day(
            user_details.datetime, user_details.timezone
        )

        ayanamsa = self.ephemeris_service.calculate_ayanamsa(julian_day) + self.ayanamsa_offset

        ascendant_longitude = self.ephemeris_service.calculate_ascendant(
            julian_day, user_details.latitude, user_details.longitude
        )

        sidereal_ascendant = (ascendant_longitude - ayanamsa) % 360

        lagna = self._create_lagna_position(sidereal_ascendant)

        planets = self._calculate_planet_positions(julian_day, ayanamsa)
      
        houses = self._calculate_houses(julian_day, user_details, ayanamsa, planets)
        
        planets = self._enrich_planet_details(planets, houses, lagna)
        
        houses = self._enrich_house_details(houses, planets)
        
        nakshatra_details = self._get_nakshatra_details()
        
        sun_moon_shine = self._calculate_sun_moon_shine(
            julian_day, user_details.latitude, user_details.longitude, planets
        )
        
        return D1Chart(
            user_details=user_details,
            lagna=lagna,
            planets=planets,
            houses=houses,
            nakshatra_details=nakshatra_details,
            sun_moon_shine=sun_moon_shine,
            ayanamsa=ayanamsa,
            calculation_time=datetime.now(timezone.utc).isoformat()
        )
    
    def _create_lagna_position(self, longitude: float) -> PlanetPosition:
       
        sign = self.ephemeris_service.longitude_to_zodiac_sign(longitude)
        degree = longitude % 30
        nakshatra, pada = self.ephemeris_service.longitude_to_nakshatra(longitude + self.nakshatra_epsilon)
       
        return PlanetPosition(
            planet=Planet.SUN,
            longitude=longitude,
            latitude=0.0,
            distance=0.0,
            speed=0.0,
            sign=sign,
            degree=degree,
            nakshatra=nakshatra,
            nakshatra_pada=pada,
            retrograde=False
        )
    
    def _calculate_planet_positions(self, julian_day: float, ayanamsa: float) -> List[PlanetPosition]:
        
        planets = []
        
        for planet in [Planet.SUN, Planet.MOON, Planet.MERCURY, Planet.VENUS,
                      Planet.MARS, Planet.JUPITER, Planet.SATURN, Planet.RAHU, Planet.KETU]:

            longitude, latitude, distance, speed = self.ephemeris_service.get_planet_position(
                planet, julian_day
            )

            sidereal_longitude = (longitude - ayanamsa) % 360

            sign = self.ephemeris_service.longitude_to_zodiac_sign(sidereal_longitude)
            degree = sidereal_longitude % 30
            nakshatra, pada = self.ephemeris_service.longitude_to_nakshatra(sidereal_longitude + self.nakshatra_epsilon)
            retrograde = self.ephemeris_service.is_planet_retrograde(speed)
            
            planet_pos = PlanetPosition(
                planet=planet,
                longitude=sidereal_longitude,
                latitude=latitude,
                distance=distance,
                speed=speed,
                sign=sign,
                degree=degree,
                nakshatra=nakshatra,
                nakshatra_pada=pada,
                retrograde=retrograde
            )
            
            planets.append(planet_pos)
        
        return planets
    
    def _calculate_houses(self, julian_day: float, user_details: UserDetails, 
                         ayanamsa: float, planets: List[PlanetPosition]) -> List[HouseData]:

        ascendant_longitude = self.ephemeris_service.calculate_ascendant(
            julian_day, user_details.latitude, user_details.longitude
        )
        sidereal_ascendant = (ascendant_longitude - ayanamsa) % 360

        ascendant_sign_num = int(sidereal_ascendant / 30)
        
        houses = []
        
        for i in range(12):
            house_number = i + 1
            house_sign_num = (ascendant_sign_num + i) % 12
            cusp_longitude = house_sign_num * 30
            sign = self.ephemeris_service.longitude_to_zodiac_sign(cusp_longitude)
            ruler_planet = self.sign_rulers[sign]
            planets_in_house = self._find_planets_in_house_whole_sign(
                house_sign_num, planets
            )
            
            house_data = HouseData(
                house_number=house_number,
                cusp_longitude=cusp_longitude,
                sign=sign,
                ruler_planet=ruler_planet,
                planets_in_house=planets_in_house
            )
            
            houses.append(house_data)
        
        return houses
    
    def _find_planets_in_house_whole_sign(self, house_sign_num: int,
                                          planets: List[PlanetPosition]) -> List[Planet]:

        planets_in_house = []
        house_start = house_sign_num * 30
        house_end = (house_sign_num + 1) * 30
        
        for planet_pos in planets:
            planet_longitude = planet_pos.longitude
            if house_start <= planet_longitude < house_end:
                planets_in_house.append(planet_pos.planet)
        
        return planets_in_house
    
    def _find_planets_in_house(self, house_number: int, house_cusps: List[float],
                              ayanamsa: float, planets: List[PlanetPosition]) -> List[Planet]:

        planets_in_house = []
        current_cusp = (house_cusps[house_number - 1] - ayanamsa) % 360
        next_cusp = (house_cusps[house_number % 12] - ayanamsa) % 360
        
        for planet_pos in planets:
            planet_longitude = planet_pos.longitude
            if current_cusp > next_cusp:
                if planet_longitude >= current_cusp or planet_longitude < next_cusp:
                    planets_in_house.append(planet_pos.planet)
            else:
                if current_cusp <= planet_longitude < next_cusp:
                    planets_in_house.append(planet_pos.planet)
        
        return planets_in_house
    
    def _get_nakshatra_details(self) -> List[NakshatraDetails]:
        nakshatra_details = []
        
        for nak_data in self.ephemeris_service.nakshatras:
            details = NakshatraDetails(
                name=nak_data["name"],
                ruler=nak_data["ruler"],
                degree_start=nak_data["start"],
                degree_end=nak_data["end"],
                symbol=nak_data["symbol"],
                deity=nak_data["deity"],
                quality="Sattva" 
            )
            nakshatra_details.append(details)
        
        return nakshatra_details
    
    def _calculate_sun_moon_shine(self, julian_day: float, latitude: float,
                                 longitude: float, planets: List[PlanetPosition]) -> SunMoonShine:

        sun_times = self.ephemeris_service.calculate_sunrise_sunset(
            julian_day, latitude, longitude
        )

        sun_pos = next(p for p in planets if p.planet == Planet.SUN)
        moon_pos = next(p for p in planets if p.planet == Planet.MOON)
        sun_sign_name = sun_pos.sign.name.title()
        sun_sign_sanskrit = self.vedic_helper.get_sign_sanskrit_name(sun_pos.sign)
        moon_sign_name = moon_pos.sign.name.title()
        moon_sign_sanskrit = self.vedic_helper.get_sign_sanskrit_name(moon_pos.sign)
        moon_sun_angle = abs(moon_pos.longitude - sun_pos.longitude)
        if moon_sun_angle > 180:
            moon_sun_angle = 360 - moon_sun_angle
        if moon_sun_angle < 45:
            moon_phase = "New"
        elif moon_sun_angle < 135:
            moon_phase = "Waxing" if moon_pos.longitude > sun_pos.longitude else "Waning"
        elif moon_sun_angle < 225:
            moon_phase = "Full"
        else:
            moon_phase = "Waning" if moon_pos.longitude > sun_pos.longitude else "Waxing"
        sun_strength = self._calculate_planet_strength(sun_pos)
        moon_strength = self._calculate_planet_strength(moon_pos)
        tithi = int((moon_pos.longitude - sun_pos.longitude) % 360 / 12) + 1
        
        return SunMoonShine(
            sunrise_time=sun_times["sunrise"],
            sunset_time=sun_times["sunset"],
            moonrise_time="",
            moonset_time="",
            sun_strength=sun_strength,
            moon_strength=moon_strength,
            moon_phase=moon_phase,
            tithi=tithi,
            sun_sign=sun_sign_name,
            sun_sign_sanskrit=sun_sign_sanskrit,
            moon_sign=moon_sign_name,
            moon_sign_sanskrit=moon_sign_sanskrit
        )
    
    def _calculate_planet_strength(self, planet_pos: PlanetPosition) -> float:

        degree = planet_pos.degree
        
        # Planets are strongest at middle of sign (15 degrees)
        strength = 100 - abs(15 - degree) * 2
        
        # Adjust for retrograde motion
        if planet_pos.retrograde:
            strength *= 0.8
        
        return max(0, min(100, strength))
    
    def _enrich_planet_details(self, planets: List[PlanetPosition], houses: List[HouseData], lagna: PlanetPosition = None) -> List[PlanetPosition]:

        enriched_planets = []
        
        for planet_pos in planets:
            planet_house = None
            for house in houses:
                if planet_pos.planet in house.planets_in_house:
                    planet_house = house.house_number
                    break
            nak_data = next((n for n in self.ephemeris_service.nakshatras if n["name"] == planet_pos.nakshatra), None)
            nakshatra_lord = nak_data["ruler"] if nak_data else None
            sub_lord = None
            if nak_data:
                sub_lord = self.vedic_helper.get_sub_lord(planet_pos.longitude, nakshatra_lord,
                                                         ephe_service=self.ephemeris_service,
                                                         epsilon=self.nakshatra_epsilon)
            ruler_of_houses = []
            for house in houses:
                if house.ruler_planet == planet_pos.planet:
                    ruler_of_houses.append(house.house_number)
            if planet_pos.planet in (Planet.RAHU, Planet.KETU):
                if self.node_rulership_strategy == "drik_compat":
                    if nakshatra_lord:
                        planet_pos.nakshatra_lord = nakshatra_lord
                    ruler_of_houses = self._compute_drik_node_rulership(planet_pos, planets, houses, lagna)
                elif self.node_rulership_strategy == "sign_based":
                    # Nodes rule houses of their sign lord
                    sign_lord = self.sign_rulers[planet_pos.sign]
                    for house in houses:
                        if house.ruler_planet == sign_lord:
                            ruler_of_houses.append(house.house_number)
                else:
                    # "nak_lord_rules": nodes rule houses of their nakshatra lord
                    if not ruler_of_houses and nakshatra_lord:
                        for house in houses:
                            if house.ruler_planet == nakshatra_lord:
                                ruler_of_houses.append(house.house_number)
            house_owner = None
            if planet_house:
                house_data = houses[planet_house - 1]
                house_owner = house_data.ruler_planet
            relationship = self.vedic_helper.get_planet_relationship(planet_pos.planet, house_owner) if house_owner else "-"
            dignity = self.vedic_helper.get_planet_dignity(planet_pos.planet, planet_pos.sign, planet_pos.degree)
            planet_pos.nakshatra_lord = nakshatra_lord
            planet_pos.sub_lord = sub_lord if sub_lord else nakshatra_lord
            planet_pos.ruler_of_houses = sorted(ruler_of_houses)  # Sort for consistent order
            planet_pos.is_in_house = planet_house
            planet_pos.house_owner = house_owner
            planet_pos.relationship = relationship
            planet_pos.dignity = dignity
            
            enriched_planets.append(planet_pos)
        
        return enriched_planets

    def _compute_drik_node_rulership(self, node: PlanetPosition, planets: List[PlanetPosition], 
                                     houses: List[HouseData], lagna: PlanetPosition = None) -> List[int]:
        if not getattr(node, 'nakshatra_lord', None):
            return []
        if lagna is None:
            return []
        d9_lagna_long = (lagna.longitude * 9.0) % 360.0
        d9_lagna_sign_num = int(d9_lagna_long // 30) + 1

        def planet_d9_house(planet: PlanetPosition) -> int:
            p_d9_long = (planet.longitude * 9.0) % 360.0
            p_d9_sign_num = int(p_d9_long // 30) + 1
            house_num = ((d9_lagna_sign_num - 1 + (p_d9_sign_num - 1)) % 12) + 1
            return house_num

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
    
    def _enrich_house_details(self, houses: List[HouseData], planets: List[PlanetPosition]) -> List[HouseData]:
        
        enriched_houses = []
        planet_houses = [(p.planet, p.is_in_house) for p in planets if p.is_in_house]
        
        for house in houses:
            house.sign_short_name = self.vedic_helper.get_sign_short_name(house.sign)
            gender = self.vedic_helper.SIGN_GENDER.get(house.sign, "")
            modality = self.vedic_helper.SIGN_MODALITY.get(house.sign, "")
            house.qualities = [gender[:3], modality]
            aspecting_planets = []
            for planet_pos in planets:
                if planet_pos.is_in_house and planet_pos.is_in_house != house.house_number:
                    diff = (house.house_number - planet_pos.is_in_house) % 12
                    if diff == 0:
                        diff = 12
                    if diff == 7:
                        aspecting_planets.append(planet_pos.planet)
                    elif planet_pos.planet == Planet.MARS and diff in [4, 8]:
                        aspecting_planets.append(planet_pos.planet)
                    elif planet_pos.planet == Planet.JUPITER and diff in [5, 9]:
                        aspecting_planets.append(planet_pos.planet)
                    elif planet_pos.planet == Planet.SATURN and diff in [3, 10]:
                        aspecting_planets.append(planet_pos.planet)
            
            house.aspected_by = aspecting_planets
            enriched_houses.append(house)
        
        return enriched_houses
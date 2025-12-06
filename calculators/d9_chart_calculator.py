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
    
    def __init__(self, ephe_path: str = "./ephe"):
        """
        Initialize D9 Chart Calculator
        
        Args:
            ephe_path: Path to Swiss Ephemeris data files
        """
        self.ephemeris_service = SwissEphemerisService(ephe_path)
        self.vedic_helper = VedicAstrologyHelper()
        self.d1_calculator = D1ChartCalculator(ephe_path)
        self.sign_rulers = VedicAstrologyHelper.SIGN_LORDS
    
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
        Convert planet position from D1 to D9
        
        D9 divides each 30-degree sign into 9 parts of 3.33 degrees each
        New Sign = (Planet's Sign - 1) * 9 + Navamsha Part + 1
        
        Args:
            planet_pos: D1 planet position
            
        Returns:
            D9 planet position
        """
        # Get current sign and degree within sign
        current_sign_num = planet_pos.sign.value  # 1-12
        degree_in_sign = planet_pos.degree  # 0-30
        
        # Calculate which of 9 parts (0-8)
        navamsha_part = int(degree_in_sign / (30 / 9))  # 0-8
        
        # Calculate new sign: (sign-1)*9 + navamsha_part + 1
        new_sign_num = ((current_sign_num - 1) * 9 + navamsha_part) % 12
        if new_sign_num == 0:
            new_sign_num = 12
        
        # Convert to Zodiac enum
        new_sign = Zodiac(new_sign_num)
        
        # Calculate new degree within sign
        # Each navamsha gets 3.33 degrees in the new sign
        new_degree = (navamsha_part * (30 / 9)) % 30
        
        # Calculate new longitude (360 degrees total)
        new_longitude = (new_sign_num - 1) * 30 + new_degree
        
        # Get nakshatra for new position
        nakshatra, pada = self.ephemeris_service.longitude_to_nakshatra(new_longitude)
        
        # Create new planet position with D9 values
        d9_planet = PlanetPosition(
            planet=planet_pos.planet,
            longitude=new_longitude,
            latitude=planet_pos.latitude,
            distance=planet_pos.distance,
            speed=planet_pos.speed,
            sign=new_sign,
            degree=new_degree,
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
                planet.sub_lord = self.vedic_helper.get_sub_lord(planet.longitude, planet.nakshatra_lord)
            
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
            planet.ruler_of_houses = ruling_houses if ruling_houses else None
            
            # Get relationship with house owner
            if planet.house_owner:
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
                "longitude": round(d9_data["d9_lagna"].longitude, 6)
            },
            "d9_planets": [
                {
                    "planet": p.planet.name,
                    "sign": p.sign.name,
                    "degree": round(p.degree, 2),
                    "longitude": round(p.longitude, 6),
                    "nakshatra": p.nakshatra.name,
                    "house": p.is_in_house,
                    "retrograde": p.retrograde
                }
                for p in d9_data["d9_planets"]
            ],
            "d9_houses": [
                {
                    "house_number": h.house_number,
                    "sign": h.sign.name,
                    "ruler": h.ruler_planet.name,
                    "planets": [p.name for p in h.planets_in_house]
                }
                for h in d9_data["d9_houses"]
            ],
            "ayanamsa": round(d9_data["ayanamsa"], 6)
        }

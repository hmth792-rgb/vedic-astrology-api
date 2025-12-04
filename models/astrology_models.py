"""
Astrology Models Module
Contains data models for astrology calculations
"""
from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum


class Planet(Enum):
    """Planet enumeration with Swiss Ephemeris constants"""
    SUN = 0
    MOON = 1
    MERCURY = 2
    VENUS = 3
    MARS = 4
    JUPITER = 5
    SATURN = 6
    URANUS = 7
    NEPTUNE = 8
    PLUTO = 9
    RAHU = 10  # North Node
    KETU = 11  # South Node


class Zodiac(Enum):
    """Zodiac signs enumeration"""
    ARIES = 1
    TAURUS = 2
    GEMINI = 3
    CANCER = 4
    LEO = 5
    VIRGO = 6
    LIBRA = 7
    SCORPIO = 8
    SAGITTARIUS = 9
    CAPRICORN = 10
    AQUARIUS = 11
    PISCES = 12


class Nakshatra(Enum):
    """27 Nakshatra enumeration"""
    ASHWINI = 1
    BHARANI = 2
    KRITTIKA = 3
    ROHINI = 4
    MRIGASHIRA = 5
    ARDRA = 6
    PUNARVASU = 7
    PUSHYA = 8
    ASHLESHA = 9
    MAGHA = 10
    PURVA_PHALGUNI = 11
    UTTARA_PHALGUNI = 12
    HASTA = 13
    CHITRA = 14
    SWATI = 15
    VISHAKHA = 16
    ANURADHA = 17
    JYESHTHA = 18
    MULA = 19
    PURVA_ASHADHA = 20
    UTTARA_ASHADHA = 21
    SHRAVANA = 22
    DHANISHTA = 23
    SHATABHISHA = 24
    PURVA_BHADRAPADA = 25
    UTTARA_BHADRAPADA = 26
    REVATI = 27


@dataclass
class UserDetails:
    """User birth details for chart calculation"""
    name: str
    datetime: str  # ISO format: YYYY-MM-DDTHH:MM:SS
    latitude: float
    longitude: float
    timezone: float  # Timezone offset in hours (e.g., 5.5 for IST, -5 for EST)
    place: str
    religion: Optional[str] = None


@dataclass
class PlanetPosition:
    """Planet position data"""
    planet: Planet
    longitude: float  # Tropical longitude in degrees
    latitude: float   # Latitude in degrees
    distance: float   # Distance from Earth
    speed: float      # Speed in degrees per day
    sign: Zodiac      # Zodiac sign
    degree: float     # Degree within sign (0-30)
    nakshatra: Nakshatra
    nakshatra_pada: int  # 1-4
    retrograde: bool
    # Additional Vedic details
    nakshatra_lord: Optional[Planet] = None
    sub_lord: Optional[Planet] = None
    ruler_of_houses: Optional[List[int]] = None  # Which houses this planet rules
    is_in_house: Optional[int] = None  # Which house the planet is in
    house_owner: Optional[Planet] = None  # Owner of the house planet is in
    relationship: Optional[str] = None  # Relationship with house owner
    dignity: Optional[str] = None  # Exalted, Own House, etc.


@dataclass
class HouseData:
    """House cusp and related data"""
    house_number: int  # 1-12
    cusp_longitude: float  # Longitude of house cusp
    sign: Zodiac          # Sign of house cusp
    ruler_planet: Planet  # Natural ruler of the sign
    planets_in_house: List[Planet]  # Planets positioned in this house
    # Additional Vedic details
    sign_short_name: Optional[str] = None  # Sanskrit name
    qualities: Optional[List[str]] = None  # Gender, Modality
    aspected_by: Optional[List[Planet]] = None  # Planets aspecting this house


@dataclass
class NakshatraDetails:
    """Detailed nakshatra information"""
    name: Nakshatra
    ruler: Planet
    degree_start: float
    degree_end: float
    symbol: str
    deity: str
    quality: str  # Rajas, Tamas, Sattva


@dataclass
class SunMoonShine:
    """Sun and Moon shine calculations"""
    sunrise_time: str
    sunset_time: str
    moonrise_time: str
    moonset_time: str
    sun_strength: float  # 0-100 percentage
    moon_strength: float # 0-100 percentage
    moon_phase: str      # New, Waxing, Full, Waning
    tithi: int          # Lunar day (1-30)


@dataclass
class D1Chart:
    """Complete D1 Rashi Chart data"""
    user_details: UserDetails
    lagna: PlanetPosition  # Ascendant
    planets: List[PlanetPosition]
    houses: List[HouseData]
    nakshatra_details: List[NakshatraDetails]
    sun_moon_shine: SunMoonShine
    ayanamsa: float  # Ayanamsa value used
    calculation_time: str  # UTC timestamp of calculation
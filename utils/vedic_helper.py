"""
Vedic Astrology Helper Functions
Contains helper methods for dignities, relationships, aspects, etc.
"""
from enum import Enum
from typing import List, Tuple
from models.astrology_models import Planet, Zodiac


class Dignity(Enum):
    """Planet dignity states"""
    EXALTED = "Exalted"
    OWN_HOUSE = "Own House"
    MOOLATRIKONA = "Moolatrikona"
    FRIEND_HOUSE = "Friend's House"
    NEUTRAL = "Neutral"
    ENEMY_HOUSE = "Enemy's House"
    DEBILITATED = "Debilitated"


class Relationship(Enum):
    """Planet relationship types"""
    FRIEND = "Friend"
    NEUTRAL = "Neutral"
    ENEMY = "Enemy"


class VedicAstrologyHelper:
    """Helper class for Vedic astrology calculations"""
    
    # Planet exaltation and debilitation
    EXALTATION = {
        Planet.SUN: (Zodiac.ARIES, 10),
        Planet.MOON: (Zodiac.TAURUS, 3),
        Planet.MARS: (Zodiac.CAPRICORN, 28),
        Planet.MERCURY: (Zodiac.VIRGO, 15),
        Planet.JUPITER: (Zodiac.CANCER, 5),
        Planet.VENUS: (Zodiac.PISCES, 27),
        Planet.SATURN: (Zodiac.LIBRA, 20)
    }
    
    DEBILITATION = {
        Planet.SUN: (Zodiac.LIBRA, 10),
        Planet.MOON: (Zodiac.SCORPIO, 3),
        Planet.MARS: (Zodiac.CANCER, 28),
        Planet.MERCURY: (Zodiac.PISCES, 15),
        Planet.JUPITER: (Zodiac.CAPRICORN, 5),
        Planet.VENUS: (Zodiac.VIRGO, 27),
        Planet.SATURN: (Zodiac.ARIES, 20)
    }
    
    # Planet natural friendships
    NATURAL_FRIENDS = {
        Planet.SUN: [Planet.MOON, Planet.MARS, Planet.JUPITER],
        Planet.MOON: [Planet.SUN, Planet.MERCURY],
        Planet.MARS: [Planet.SUN, Planet.MOON, Planet.JUPITER],
        Planet.MERCURY: [Planet.SUN, Planet.VENUS],
        Planet.JUPITER: [Planet.SUN, Planet.MOON, Planet.MARS],
        Planet.VENUS: [Planet.MERCURY, Planet.SATURN],
        Planet.SATURN: [Planet.MERCURY, Planet.VENUS]
    }
    
    NATURAL_ENEMIES = {
        Planet.SUN: [Planet.VENUS, Planet.SATURN],
        Planet.MOON: [],  # Moon has no natural enemies
        Planet.MARS: [Planet.MERCURY],
        Planet.MERCURY: [Planet.MOON],
        Planet.JUPITER: [Planet.MERCURY, Planet.VENUS],
        Planet.VENUS: [Planet.SUN, Planet.MOON],
        Planet.SATURN: [Planet.SUN, Planet.MOON, Planet.MARS]
    }
    
    # Sign lords (rulers)
    SIGN_LORDS = {
        Zodiac.ARIES: Planet.MARS,
        Zodiac.TAURUS: Planet.VENUS,
        Zodiac.GEMINI: Planet.MERCURY,
        Zodiac.CANCER: Planet.MOON,
        Zodiac.LEO: Planet.SUN,
        Zodiac.VIRGO: Planet.MERCURY,
        Zodiac.LIBRA: Planet.VENUS,
        Zodiac.SCORPIO: Planet.MARS,
        Zodiac.SAGITTARIUS: Planet.JUPITER,
        Zodiac.CAPRICORN: Planet.SATURN,
        Zodiac.AQUARIUS: Planet.SATURN,
        Zodiac.PISCES: Planet.JUPITER
    }
    
    # Planet rulership (which houses they rule)
    PLANET_HOUSE_RULERSHIP = {
        Planet.SUN: [Zodiac.LEO],
        Planet.MOON: [Zodiac.CANCER],
        Planet.MARS: [Zodiac.ARIES, Zodiac.SCORPIO],
        Planet.MERCURY: [Zodiac.GEMINI, Zodiac.VIRGO],
        Planet.JUPITER: [Zodiac.SAGITTARIUS, Zodiac.PISCES],
        Planet.VENUS: [Zodiac.TAURUS, Zodiac.LIBRA],
        Planet.SATURN: [Zodiac.CAPRICORN, Zodiac.AQUARIUS]
    }
    
    # Sign qualities
    SIGN_GENDER = {
        Zodiac.ARIES: "Masculine", Zodiac.TAURUS: "Feminine", Zodiac.GEMINI: "Masculine",
        Zodiac.CANCER: "Feminine", Zodiac.LEO: "Masculine", Zodiac.VIRGO: "Feminine",
        Zodiac.LIBRA: "Masculine", Zodiac.SCORPIO: "Feminine", Zodiac.SAGITTARIUS: "Masculine",
        Zodiac.CAPRICORN: "Feminine", Zodiac.AQUARIUS: "Masculine", Zodiac.PISCES: "Feminine"
    }
    
    SIGN_MODALITY = {
        Zodiac.ARIES: "Movable", Zodiac.TAURUS: "Fixed", Zodiac.GEMINI: "Common",
        Zodiac.CANCER: "Movable", Zodiac.LEO: "Fixed", Zodiac.VIRGO: "Common",
        Zodiac.LIBRA: "Movable", Zodiac.SCORPIO: "Fixed", Zodiac.SAGITTARIUS: "Common",
        Zodiac.CAPRICORN: "Movable", Zodiac.AQUARIUS: "Fixed", Zodiac.PISCES: "Common"
    }

    # Vimshottari dasha order and lengths (years)
    VIMSHOTTARI_ORDER = [
        Planet.KETU, Planet.VENUS, Planet.SUN, Planet.MOON,
        Planet.MARS, Planet.RAHU, Planet.JUPITER, Planet.SATURN, Planet.MERCURY
    ]
    VIMSHOTTARI_LENGTHS = {
        Planet.SUN: 6,
        Planet.MOON: 10,
        Planet.MARS: 7,
        Planet.RAHU: 18,
        Planet.JUPITER: 16,
        Planet.SATURN: 19,
        Planet.MERCURY: 17,
        Planet.KETU: 7,
        Planet.VENUS: 20
    }
    
    @staticmethod
    def get_planet_dignity(planet: Planet, sign: Zodiac, degree: float) -> str:
        """Calculate planet dignity"""
        if planet in [Planet.RAHU, Planet.KETU]:
            return "-"
            
        # Check exaltation
        if planet in VedicAstrologyHelper.EXALTATION:
            exalt_sign, exalt_degree = VedicAstrologyHelper.EXALTATION[planet]
            if sign == exalt_sign:
                return Dignity.EXALTED.value
        
        # Check debilitation
        if planet in VedicAstrologyHelper.DEBILITATION:
            debil_sign, debil_degree = VedicAstrologyHelper.DEBILITATION[planet]
            if sign == debil_sign:
                return Dignity.DEBILITATED.value
        
        # Check own house
        if planet in VedicAstrologyHelper.PLANET_HOUSE_RULERSHIP:
            if sign in VedicAstrologyHelper.PLANET_HOUSE_RULERSHIP[planet]:
                return Dignity.OWN_HOUSE.value
        
        return "-"
    
    @staticmethod
    def get_planet_relationship(planet: Planet, sign_lord: Planet) -> str:
        """Get relationship between planet and sign lord"""
        if planet == sign_lord:
            return "Own House"
        
        if planet in [Planet.RAHU, Planet.KETU]:
            return "Neutral"
            
        if sign_lord in VedicAstrologyHelper.NATURAL_FRIENDS.get(planet, []):
            return Relationship.FRIEND.value
        elif sign_lord in VedicAstrologyHelper.NATURAL_ENEMIES.get(planet, []):
            return Relationship.ENEMY.value
        else:
            return Relationship.NEUTRAL.value
    
    @staticmethod
    def calculate_aspects(planet: Planet, planet_house: int, all_houses: List[int]) -> List[Planet]:
        """
        Calculate which planets aspect this house
        - All planets aspect 7th house from their position
        - Mars aspects 4th, 7th, 8th
        - Jupiter aspects 5th, 7th, 9th
        - Saturn aspects 3rd, 7th, 10th
        """
        aspecting_planets = []
        
        for other_planet, other_house in all_houses:
            if other_planet == planet:
                continue
                
            # Calculate house difference
            diff = (planet_house - other_house) % 12
            if diff == 0:
                diff = 12
            
            # All planets aspect 7th
            if diff == 7:
                aspecting_planets.append(other_planet)
            # Mars special aspects
            elif other_planet == Planet.MARS and diff in [4, 8]:
                aspecting_planets.append(other_planet)
            # Jupiter special aspects
            elif other_planet == Planet.JUPITER and diff in [5, 9]:
                aspecting_planets.append(other_planet)
            # Saturn special aspects
            elif other_planet == Planet.SATURN and diff in [3, 10]:
                aspecting_planets.append(other_planet)
        
        return aspecting_planets
    
    @staticmethod
    def format_longitude_dms(longitude: float, sign: Zodiac) -> str:
        """Format longitude in degrees, minutes, seconds within sign"""
        degree_in_sign = longitude % 30
        degrees = int(degree_in_sign)
        minutes = int((degree_in_sign - degrees) * 60)
        seconds = int(((degree_in_sign - degrees) * 60 - minutes) * 60)
        
        return f"{degrees:02d}° {sign.name.title()} {minutes:02d}′ {seconds:02d}″"
    
    @staticmethod
    def get_sign_short_name(sign: Zodiac) -> str:
        """Get short Sanskrit name for sign"""
        names = {
            Zodiac.ARIES: "Mesha", Zodiac.TAURUS: "Vrishabha", Zodiac.GEMINI: "Mithuna",
            Zodiac.CANCER: "Karka", Zodiac.LEO: "Simha", Zodiac.VIRGO: "Kanya",
            Zodiac.LIBRA: "Tula", Zodiac.SCORPIO: "Vrishchika", Zodiac.SAGITTARIUS: "Dhanu",
            Zodiac.CAPRICORN: "Makara", Zodiac.AQUARIUS: "Kumbha", Zodiac.PISCES: "Meena"
        }
        return names.get(sign, sign.name)

    @staticmethod
    def get_sanskrit_planet_name(planet: Planet) -> str:
        """Return common Sanskrit-style planet name (Shukra, Budha, etc.)"""
        names = {
            Planet.SUN: "Surya",
            Planet.MOON: "Chandra",
            Planet.MARS: "Mangal",
            Planet.MERCURY: "Budha",
            Planet.JUPITER: "Guru",
            Planet.VENUS: "Shukra",
            Planet.SATURN: "Shani",
            Planet.RAHU: "Rahu",
            Planet.KETU: "Ketu"
        }
        return names.get(planet, planet.name.title())

    def get_sub_lord(self, absolute_longitude: float, nakshatra_lord: Planet) -> Planet:
        """
        Compute KP sub-lord based on Vimshottari order segmented within a nakshatra.
        - Each nakshatra spans 13°20' (13.333333 degrees)
        - Sub-lords are nine segments proportionate to dasha lengths
        - Order starts from the nakshatra lord and proceeds cyclically
        """
        # Determine position inside nakshatra (0 to 13.333333)
        # Nakshatra boundaries start at 0 Aries and continue
        segment_span = 13.333333
        # Find the start degree of the current nakshatra
        from services.swiss_ephemeris_service import SwissEphemerisService
        svc = SwissEphemerisService()
        nak = None
        for n in svc.nakshatras:
            if n["start"] <= absolute_longitude < n["end"]:
                nak = n
                break
        if not nak:
            return nakshatra_lord
        pos_in_nak = absolute_longitude - nak["start"]

        # Build order starting from nakshatra lord
        order = []
        # rotate VIMSHOTTARI_ORDER so that it starts with nakshatra_lord
        base = self.VIMSHOTTARI_ORDER
        start_idx = base.index(nakshatra_lord) if nakshatra_lord in base else 0
        order = base[start_idx:] + base[:start_idx]

        # Compute cumulative segment boundaries in degrees
        total_years = sum(self.VIMSHOTTARI_LENGTHS[p] for p in order)
        # Proportion per planet within nakshatra
        boundaries = []
        acc = 0.0
        for p in order:
            proportion = self.VIMSHOTTARI_LENGTHS[p] / total_years
            acc += proportion * segment_span
            boundaries.append((acc, p))

        # Determine which boundary the position falls into
        for boundary_deg, p in boundaries:
            if pos_in_nak <= boundary_deg:
                return p
        return order[-1]
    
    @staticmethod
    def get_planet_symbol(planet: Planet) -> str:
        """Get planet symbol"""
        symbols = {
            Planet.SUN: "☉", Planet.MOON: "☾", Planet.MARS: "♂",
            Planet.MERCURY: "☿", Planet.JUPITER: "♃", Planet.VENUS: "♀",
            Planet.SATURN: "♄", Planet.RAHU: "☊", Planet.KETU: "☋"
        }
        return symbols.get(planet, "")
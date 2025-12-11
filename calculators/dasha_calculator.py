"""
Dasha Calculator
Calculates Mahadasha and Antardasha periods using Vimshottari dasha system
Based on Moon's nakshatra at birth
"""
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass

from models.astrology_models import UserDetails, Planet
from calculators.d1_chart_calculator import D1ChartCalculator


@dataclass
class DashaPeriod:
    """Single dasha period information"""
    planet: Planet
    planet_name: str
    start_date: str  # ISO format
    end_date: str    # ISO format
    duration_years: float
    duration_months: int
    duration_days: int
    lord: Planet
    sub_lord: Planet
    start_age_years: float
    end_age_years: float


@dataclass
class DashaYear:
    """All dashas (Maha + Antar) for a specific year"""
    year: int
    mahadasha: DashaPeriod
    antardasha_periods: List[DashaPeriod]
    active_mahadasha: str  # Planet name
    active_antardasha: Optional[str]  # Planet name


class DashaCalculator:
    """Calculator for Vimshottari Mahadasha and Antardasha periods"""
    
    # Vimshottari dasha order and lengths (in years)
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
    
    PLANET_NAMES = {
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
    
    def __init__(self, ephe_path: str = "./ephe", sidereal_mode=None):
        """
        Initialize Dasha Calculator
        
        Args:
            ephe_path: Path to Swiss Ephemeris data
            sidereal_mode: Optional sidereal mode for consistency
        """
        self.d1_calculator = D1ChartCalculator(
            ephe_path=ephe_path,
            sidereal_mode=sidereal_mode
        )
        self.ephe_path = ephe_path
        self.sidereal_mode = sidereal_mode
    
    def get_dasha_for_year(self, user_details: UserDetails, year: int) -> DashaYear:
        """
        Get Mahadasha and Antardasha periods active during a given year
        
        Args:
            user_details: User birth details
            year: Year to calculate dasha for (e.g., 2024)
            
        Returns:
            DashaYear object containing all dasha information
        """
        # Calculate D1 chart to get Moon's nakshatra
        d1_chart = self.d1_calculator.calculate_d1_chart(user_details)
        
        # Get Moon's nakshatra details
        moon_planet = next((p for p in d1_chart.planets if p.planet == Planet.MOON), None)
        if not moon_planet:
            raise ValueError("Moon not found in D1 chart")
        
        # Extract nakshatra name from enum
        moon_nak_name = moon_planet.nakshatra.name.replace("_", " ").title()
        moon_nak_pada = moon_planet.nakshatra_pada
        
        # Calculate Vimshottari start and age at birth
        birth_dt = datetime.fromisoformat(user_details.datetime)
        vimshottari_start, birth_age_days = self._calculate_vimshottari_start(
            moon_nak_name, moon_nak_pada, birth_dt, d1_chart
        )
        
        # Get Mahadasha and Antardasha for the given year
        return self._get_dasha_for_year(
            user_details, year, vimshottari_start, birth_dt, birth_age_days
        )
    
    def get_dasha_for_date_range(
        self, user_details: UserDetails, start_date: str, end_date: str
    ) -> Dict:
        """
        Get all Mahadasha and Antardasha periods within a date range
        
        Args:
            user_details: User birth details
            start_date: Start date (ISO format YYYY-MM-DD)
            end_date: End date (ISO format YYYY-MM-DD)
            
        Returns:
            Dictionary with dasha periods for the range
        """
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
        
        # Calculate D1 chart
        d1_chart = self.d1_calculator.calculate_d1_chart(user_details)
        
        # Get Moon's nakshatra
        moon_planet = next((p for p in d1_chart.planets if p.planet == Planet.MOON), None)
        if not moon_planet:
            raise ValueError("Moon not found in D1 chart")
        
        moon_nak_name = moon_planet.nakshatra.name.replace("_", " ").title()
        moon_nak_pada = moon_planet.nakshatra_pada
        
        # Calculate Vimshottari start
        birth_dt = datetime.fromisoformat(user_details.datetime)
        vimshottari_start, birth_age_days = self._calculate_vimshottari_start(
            moon_nak_name, moon_nak_pada, birth_dt, d1_chart
        )
        
        # Calculate all dasha periods in range
        periods = self._calculate_dasha_periods(
            vimshottari_start, birth_dt, start, end
        )
        
        return {
            "user": {
                "name": user_details.name,
                "birth_date": user_details.datetime,
                "moon_nakshatra": moon_nak_name,
                "moon_pada": moon_nak_pada
            },
            "range": {
                "start": start_date,
                "end": end_date
            },
            "dasha_periods": periods
        }
    
    def _calculate_vimshottari_start(
        self, moon_nak_name: str, moon_nak_pada: int, 
        birth_dt: datetime, d1_chart
    ) -> tuple:
        """
        Calculate Vimshottari start point and remaining dasha at birth
        
        Returns:
            (start_planet, birth_age_in_days)
        """
        # Nakshatra to starting Mahadasha lord mapping
        # Nakshatras 1, 4, 7, 10, 13, 16, 19, 22, 25 start with Ketu
        nak_map = {
            "Ashwini": Planet.KETU, "Bharani": Planet.KETU, "Krittika": Planet.KETU,
            "Rohini": Planet.VENUS, "Mrigashira": Planet.VENUS, "Ardra": Planet.VENUS,
            "Punarvasu": Planet.SUN, "Pushya": Planet.SUN, "Ashlesha": Planet.SUN,
            "Magha": Planet.MOON, "Purva_Phalguni": Planet.MOON, "Uttara_Phalguni": Planet.MOON,
            "Hasta": Planet.MARS, "Chitra": Planet.MARS, "Swati": Planet.MARS,
            "Vishakha": Planet.RAHU, "Anuradha": Planet.RAHU, "Jyeshtha": Planet.RAHU,
            "Mula": Planet.JUPITER, "Purva_Ashadha": Planet.JUPITER, "Uttara_Ashadha": Planet.JUPITER,
            "Shravana": Planet.SATURN, "Dhanishta": Planet.SATURN, "Shatabhisha": Planet.SATURN,
            "Purva_Bhadrapada": Planet.MERCURY, "Uttara_Bhadrapada": Planet.MERCURY, "Revati": Planet.MERCURY
        }
        
        # Get starting dasha planet
        moon_nak_clean = moon_nak_name.replace(" ", "_")
        start_planet = nak_map.get(moon_nak_clean, Planet.KETU)
        
        # Calculate remaining dasha in current Mahadasha based on pada
        # Each nakshatra is 13°20' (13.333 degrees), divided into 4 padas of 3°20' each
        # Pada determines position within nakshatra (0.25, 0.50, 0.75, 1.0 of nakshatra span)
        dasha_lord_length = self.VIMSHOTTARI_LENGTHS[start_planet]
        
        # Pada-based remaining calculation
        # If born in pada 1: 75% of dasha remaining
        # If born in pada 2: 50% of dasha remaining
        # If born in pada 3: 25% of dasha remaining
        # If born in pada 4: 100% of next dasha's lord (transition point)
        
        pada_remaining_factor = {
            1: 0.75,  # 3/4 remaining
            2: 0.50,  # 2/4 remaining
            3: 0.25,  # 1/4 remaining
            4: 0.00   # Transition to next
        }
        
        remaining_factor = pada_remaining_factor.get(moon_nak_pada, 0.75)
        remaining_days = dasha_lord_length * 365.25 * remaining_factor
        
        # Calculate birth age (age in days from Vimshottari start perspective)
        birth_age_days = remaining_days
        
        return start_planet, birth_age_days
    
    def _get_dasha_for_year(
        self, user_details: UserDetails, year: int,
        vimshottari_start: Planet, birth_dt: datetime, birth_age_days: float
    ) -> DashaYear:
        """
        Get Mahadasha and Antardasha active during a specific year
        """
        # Create date range for the year
        start_of_year = datetime(year, 1, 1)
        end_of_year = datetime(year, 12, 31)
        
        # Get all dasha periods for this year
        periods = self._calculate_dasha_periods(
            vimshottari_start, birth_dt, start_of_year, end_of_year
        )
        
        # Find which Mahadasha is active
        mahadasha_planet = None
        antardasha_planets = []
        
        for period in periods:
            period_start = datetime.fromisoformat(period["start_date"])
            period_end = datetime.fromisoformat(period["end_date"])
            
            if period["level"] == "Mahadasha":
                if period_start <= start_of_year <= period_end:
                    mahadasha_planet = period
            elif period["level"] == "Antardasha":
                if period_start <= start_of_year <= period_end:
                    antardasha_planets.append(period)
        
        # Format response
        return DashaYear(
            year=year,
            mahadasha=mahadasha_planet,
            antardasha_periods=antardasha_planets,
            active_mahadasha=self.PLANET_NAMES.get(
                mahadasha_planet["planet"], "Unknown"
            ) if mahadasha_planet else "Unknown",
            active_antardasha=self.PLANET_NAMES.get(
                antardasha_planets[0]["planet"], "Unknown"
            ) if antardasha_planets else None
        )
    
    def _calculate_dasha_periods(
        self, start_planet: Planet, birth_dt: datetime,
        start_date: datetime, end_date: datetime
    ) -> List[Dict]:
        """
        Calculate all Mahadasha and Antardasha periods within a date range
        """
        periods = []
        
        # Calculate birth age in days
        birth_age_days = (start_date - birth_dt).days
        if birth_age_days < 0:
            birth_age_days = 0
        
        # Calculate total elapsed days since Vimshottari start
        total_elapsed_days = birth_age_days
        
        # Current dasha state
        current_idx = self.VIMSHOTTARI_ORDER.index(start_planet)
        current_age = total_elapsed_days
        
        # Generate Mahadasha periods
        while current_age < (end_date - birth_dt).days + 100000:  # Safety limit
            current_planet = self.VIMSHOTTARI_ORDER[current_idx % 9]
            dasha_length_days = self.VIMSHOTTARI_LENGTHS[current_planet] * 365.25
            
            start_offset = current_age
            end_offset = current_age + dasha_length_days
            
            maha_start = birth_dt + timedelta(days=start_offset)
            maha_end = birth_dt + timedelta(days=end_offset)
            
            # Only include if within our date range
            if maha_end >= start_date and maha_start <= end_date:
                # Add Mahadasha
                periods.append({
                    "level": "Mahadasha",
                    "planet": current_planet,
                    "planet_name": self.PLANET_NAMES[current_planet],
                    "start_date": maha_start.isoformat(),
                    "end_date": maha_end.isoformat(),
                    "duration_years": self.VIMSHOTTARI_LENGTHS[current_planet],
                    "duration_days": int(dasha_length_days)
                })
                
                # Add Antardasha periods for this Mahadasha
                antardasha_periods = self._get_antardasha_periods(
                    current_planet, maha_start, maha_end, start_date, end_date
                )
                periods.extend(antardasha_periods)
            
            current_age = end_offset
            current_idx += 1
            
            # Stop if we've gone past our date range
            if maha_start > end_date:
                break
        
        return periods
    
    def _get_antardasha_periods(
        self, mahadasha_planet: Planet, maha_start: datetime, maha_end: datetime,
        date_start: datetime, date_end: datetime
    ) -> List[Dict]:
        """
        Get all Antardasha periods within a Mahadasha period
        """
        antardasha_periods = []
        
        # Antardasha cycles are in the same order as Mahadasha
        total_maha_days = (maha_end - maha_start).days
        
        current_idx = self.VIMSHOTTARI_ORDER.index(mahadasha_planet)
        current_date = maha_start
        
        for _ in range(9):  # 9 Antardashas per Mahadasha
            current_planet = self.VIMSHOTTARI_ORDER[current_idx % 9]
            
            # Antardasha duration is proportionate to Mahadasha length
            dasha_proportion = self.VIMSHOTTARI_LENGTHS[current_planet] / 120  # Total is 120 years
            antar_duration = total_maha_days * dasha_proportion
            
            antar_start = current_date
            antar_end = current_date + timedelta(days=antar_duration)
            
            # Only include if within our date range
            if antar_end >= date_start and antar_start <= date_end:
                antardasha_periods.append({
                    "level": "Antardasha",
                    "mahadasha_planet": mahadasha_planet,
                    "mahadasha_planet_name": self.PLANET_NAMES[mahadasha_planet],
                    "planet": current_planet,
                    "planet_name": self.PLANET_NAMES[current_planet],
                    "start_date": antar_start.isoformat(),
                    "end_date": antar_end.isoformat(),
                    "duration_days": int(antar_duration),
                    "lord": current_planet,
                    "sub_lord": current_planet
                })
            
            current_date = antar_end
            current_idx += 1
            
            if antar_start > date_end:
                break
        
        return antardasha_periods

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
        
        # Calculate Vimshottari start and balance at birth
        birth_dt = datetime.fromisoformat(user_details.datetime)
        vimshottari_start, balance_days = self._calculate_vimshottari_start(
            moon_planet, birth_dt
        )
        
        # Get Mahadasha and Antardasha for the given year
        return self._get_dasha_for_year(
            user_details, year, vimshottari_start, birth_dt, balance_days
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
        vimshottari_start, balance_days = self._calculate_vimshottari_start(
            moon_planet, birth_dt
        )
        
        # Calculate all dasha periods in range
        periods = self._calculate_dasha_periods(
            vimshottari_start, birth_dt, balance_days, start, end
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
        self,
        moon_planet,
        birth_dt: datetime
    ) -> tuple:
        """
        Calculate starting Mahadasha lord and balance at birth using exact Moon longitude.
        Returns:
            (start_planet, remaining_days_in_current_mahadasha)
        """

        # Correct Vimshottari nakshatra-to-lord mapping (9 lords cycle every 3 nakshatras)
        nak_map = {
            "Ashwini": Planet.KETU,
            "Bharani": Planet.VENUS,
            "Krittika": Planet.SUN,
            "Rohini": Planet.MOON,
            "Mrigashira": Planet.MARS,
            "Ardra": Planet.RAHU,
            "Punarvasu": Planet.JUPITER,
            "Pushya": Planet.SATURN,
            "Ashlesha": Planet.MERCURY,
            "Magha": Planet.KETU,
            "Purva Phalguni": Planet.VENUS,
            "Uttara Phalguni": Planet.SUN,
            "Hasta": Planet.MOON,
            "Chitra": Planet.MARS,
            "Swati": Planet.RAHU,
            "Vishakha": Planet.JUPITER,
            "Anuradha": Planet.SATURN,
            "Jyeshtha": Planet.MERCURY,
            "Mula": Planet.KETU,
            "Purva Ashadha": Planet.VENUS,
            "Uttara Ashadha": Planet.SUN,
            "Shravana": Planet.MOON,
            "Dhanishta": Planet.MARS,
            "Shatabhisha": Planet.RAHU,
            "Purva Bhadrapada": Planet.JUPITER,
            "Uttara Bhadrapada": Planet.SATURN,
            "Revati": Planet.MERCURY,
        }

        moon_nak_clean = moon_planet.nakshatra.name.replace("_", " ").title()
        start_planet = nak_map.get(moon_nak_clean, Planet.KETU)

        # Exact balance: remaining portion of current nakshatra * Mahadasha length
        nakshatra_span = 360 / 27.0  # 13°20'
        moon_long = moon_planet.longitude % 360
        # Start of this nakshatra from 0° Aries
        start_deg = (moon_planet.nakshatra.value - 1) * nakshatra_span
        fraction_elapsed = ((moon_long - start_deg) % nakshatra_span) / nakshatra_span
        fraction_elapsed = max(0.0, min(1.0, fraction_elapsed))

        dasha_length_years = self.VIMSHOTTARI_LENGTHS[start_planet]
        remaining_years = dasha_length_years * (1 - fraction_elapsed)
        remaining_days = remaining_years * 365.25

        return start_planet, remaining_days
    
    def _get_dasha_for_year(
        self, user_details: UserDetails, year: int,
        vimshottari_start: Planet, birth_dt: datetime, balance_days: float
    ) -> DashaYear:
        """
        Get Mahadasha and Antardasha active during a specific year
        """
        # Create date range for the year
        start_of_year = datetime(year, 1, 1)
        end_of_year = datetime(year, 12, 31)
        
        # Get all dasha periods for this year
        periods = self._calculate_dasha_periods(
            vimshottari_start, birth_dt, balance_days, start_of_year, end_of_year
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
        self,
        start_planet: Planet,
        birth_dt: datetime,
        balance_days: float,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict]:
        """
        Calculate all Mahadasha and Antardasha periods within a date range.
        Uses exact balance at birth to anchor the first Mahadasha start time.
        """
        periods = []

        # Length of starting Mahadasha
        start_maha_days = self.VIMSHOTTARI_LENGTHS[start_planet] * 365.25

        # Elapsed portion before birth (if any) to anchor the cycle
        elapsed_before_birth = start_maha_days - balance_days
        first_maha_start = birth_dt - timedelta(days=elapsed_before_birth)

        current_idx = self.VIMSHOTTARI_ORDER.index(start_planet)
        current_maha_start = first_maha_start

        # Generate Mahadasha periods until we pass the requested end date
        while current_maha_start <= end_date:
            current_planet = self.VIMSHOTTARI_ORDER[current_idx % 9]
            dasha_length_days = self.VIMSHOTTARI_LENGTHS[current_planet] * 365.25

            maha_start = current_maha_start
            maha_end = maha_start + timedelta(days=dasha_length_days)

            if maha_end >= start_date and maha_start <= end_date:
                periods.append({
                    "level": "Mahadasha",
                    "planet": current_planet,
                    "planet_name": self.PLANET_NAMES[current_planet],
                    "start_date": maha_start.isoformat(),
                    "end_date": maha_end.isoformat(),
                    "duration_years": self.VIMSHOTTARI_LENGTHS[current_planet],
                    "duration_days": int(dasha_length_days)
                })

                antardasha_periods = self._get_antardasha_periods(
                    current_planet, maha_start, maha_end, start_date, end_date
                )
                periods.extend(antardasha_periods)

            # Advance to next Mahadasha
            current_maha_start = maha_end
            current_idx += 1

            # Safety: stop after full 120-year cycle beyond the requested range
            if current_maha_start - first_maha_start > timedelta(days=120 * 365.25 + 1):
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
        total_maha_days = (maha_end - maha_start).total_seconds() / 86400.0
        
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

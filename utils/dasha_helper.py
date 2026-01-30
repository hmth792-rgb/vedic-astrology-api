"""
Numerology and Dasha Analysis Utilities
"""
from datetime import datetime
from typing import Dict, Tuple, Optional


class NumerologyHelper:
    """Helper for numerology calculations"""
    
    @staticmethod
    def calculate_number(name: str) -> int:
        """
        Calculate name number using A=1, B=2, ..., Z=26 mapping
        Then reduce to single digit
        """
        name_upper = name.upper().replace(" ", "")
        total = 0
        
        for char in name_upper:
            if char.isalpha():
                # A=1, B=2, ..., Z=26
                value = ord(char) - ord('A') + 1
                total += value
        
        # Reduce to single digit (unless it's a master number 11, 22, 33)
        return NumerologyHelper._reduce_to_single(total)
    
    @staticmethod
    def calculate_destiny_number(birth_date_str: str) -> int:
        """
        Calculate destiny number from birth date (YYYY-MM-DD format)
        Sum all digits and reduce to single digit
        """
        # Remove hyphens and sum all digits
        date_digits = birth_date_str.replace("-", "")
        total = sum(int(d) for d in date_digits if d.isdigit())
        
        return NumerologyHelper._reduce_to_single(total)
    
    @staticmethod
    def calculate_basic_number(day: int) -> int:
        """
        Calculate basic number from birth day of month
        """
        return NumerologyHelper._reduce_to_single(day)
    
    @staticmethod
    def _reduce_to_single(num: int) -> int:
        """Reduce number to single digit, keeping master numbers (11, 22, 33, etc.)"""
        while num >= 10:
            # Check for master numbers
            if num in [11, 22, 33, 44, 55, 66, 77, 88, 99]:
                return num
            # Sum digits
            num = sum(int(d) for d in str(num))
        return num


class DashaAnalysisHelper:
    """Helper for detailed dasha analysis"""
    
    @staticmethod
    def get_current_dasha_details(
        birth_date_str: str,
        all_periods: list,
        today: Optional[datetime] = None
    ) -> Dict:
        """
        Analyze and get current Mahadasha, Antardasha, and Pratantardasha
        
        Args:
            birth_date_str: Birth date in ISO format (YYYY-MM-DDTHH:MM:SS)
            all_periods: List of all dasha periods calculated
            today: Reference date (defaults to now)
            
        Returns:
            Dictionary with detailed analysis
        """
        if today is None:
            today = datetime.now()
        
        # Parse birth date
        try:
            birth = datetime.fromisoformat(birth_date_str)
        except:
            birth = datetime.now()
        
        # Find current Mahadasha
        current_mahadasha = None
        current_mahadasha_period = None
        
        for period in all_periods:
            if period.get("level") != "Mahadasha":
                continue
            
            start = datetime.fromisoformat(period["start_date"])
            end = datetime.fromisoformat(period["end_date"])
            
            if start <= today <= end:
                current_mahadasha = period
                current_mahadasha_period = (start, end)
                break
        
        # Find current Antardasha
        current_antardasha = None
        current_antardasha_period = None
        
        if current_mahadasha:
            mahadasha_lord = current_mahadasha["planet"]
            for period in all_periods:
                if period.get("level") != "Antardasha":
                    continue
                if period.get("mahadasha_planet") != mahadasha_lord:
                    continue
                
                start = datetime.fromisoformat(period["start_date"])
                end = datetime.fromisoformat(period["end_date"])
                
                if start <= today <= end:
                    current_antardasha = period
                    current_antardasha_period = (start, end)
                    break
        
        # Calculate progress for Mahadasha
        mahadasha_progress = None
        if current_mahadasha_period:
            start, end = current_mahadasha_period
            total_duration = (end - start).days
            elapsed = (today - start).days
            years_total = current_mahadasha.get("duration_years", 0)
            years_elapsed = (elapsed / 365.25) if total_duration > 0 else 0
            
            mahadasha_progress = {
                "total_years": years_total,
                "elapsed_years": round(years_elapsed, 1),
                "remaining_years": round(years_total - years_elapsed, 1),
                "start_date": start.strftime("%d-%m-%Y"),
                "end_date": end.strftime("%d-%m-%Y"),
                "percentage": round((elapsed / total_duration) * 100, 1) if total_duration > 0 else 0
            }
        
        # Calculate progress for Antardasha
        antardasha_progress = None
        if current_antardasha_period:
            start, end = current_antardasha_period
            total_duration = (end - start).days
            elapsed = (today - start).days
            
            antardasha_progress = {
                "duration_days": total_duration,
                "elapsed_days": elapsed,
                "remaining_days": total_duration - elapsed,
                "start_date": start.strftime("%d-%m-%Y"),
                "end_date": end.strftime("%d-%m-%Y"),
                "percentage": round((elapsed / total_duration) * 100, 1) if total_duration > 0 else 0
            }
        
        # Find Pratantardasha (sub-periods within Antardasha)
        # For simplicity, we'll calculate it based on Vimshottari order
        pratantardasha_info = None
        if current_antardasha and current_antardasha_period:
            antardasha_lord = current_antardasha["planet"]
            antardasha_period_days = current_antardasha.get("duration_days", 0)
            
            # Pratantardasha would be further subdivisions
            # Starting planet would be the same as Antardasha lord
            pratantardasha_info = {
                "starting_lord": antardasha_lord,
                "current_lord": antardasha_lord,  # Simplified
                "started": current_antardasha_period[0].strftime("%d-%m-%Y"),
                "expected_end": current_antardasha_period[1].strftime("%d-%m-%Y"),
                "duration_days": antardasha_period_days
            }
        
        return {
            "current_mahadasha": current_mahadasha,
            "current_mahadasha_progress": mahadasha_progress,
            "current_antardasha": current_antardasha,
            "current_antardasha_progress": antardasha_progress,
            "pratantardasha": pratantardasha_info
        }

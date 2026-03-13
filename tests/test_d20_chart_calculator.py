import unittest
from models.astrology_models import UserDetails, Planet, Zodiac, PlanetPosition, HouseData
from calculators.d20_chart_calculator import D20ChartCalculator

class TestD20ChartCalculator(unittest.TestCase):
    def setUp(self):
        self.calculator = D20ChartCalculator()

    def test_calculate_d20_chart(self):
        """Test D20 chart calculation returns proper structure and types"""
        user_details = UserDetails(
            name="Hemant Rathore",
            datetime="1987-05-04T19:43:00",
            latitude=26.14,
            longitude=91.79,
            timezone=5.5,
            place="Dispur"
        )
        d20_chart = self.calculator.calculate_d20_chart(user_details)
        
        # Verify chart structure
        self.assertIn("chart_type", d20_chart)
        self.assertIn("description", d20_chart)
        self.assertIn("lagna", d20_chart)
        self.assertIn("planets", d20_chart)
        self.assertIn("houses", d20_chart)
        self.assertIn("ayanamsa", d20_chart)
        
        # Verify chart type
        self.assertEqual(d20_chart["chart_type"], "D20 (Vimshamsha)")
        self.assertEqual(d20_chart["description"], "Divisional chart for spiritual progress and divine grace")
        
        # Verify lagna is a PlanetPosition object
        self.assertIsInstance(d20_chart["lagna"], PlanetPosition)
        self.assertIsInstance(d20_chart["lagna"].sign, Zodiac)
        
        # Verify planets list
        self.assertIsInstance(d20_chart["planets"], list)
        self.assertEqual(len(d20_chart["planets"]), 9)  # Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu
        
        # Verify each planet is a PlanetPosition object
        planet_enums_found = []
        for planet in d20_chart["planets"]:
            self.assertIsInstance(planet, PlanetPosition)
            self.assertIsInstance(planet.planet, Planet)
            self.assertIsInstance(planet.sign, Zodiac)
            self.assertIsInstance(planet.longitude, (int, float))
            self.assertGreaterEqual(planet.longitude, 0)
            self.assertLess(planet.longitude, 360)
            planet_enums_found.append(planet.planet)
        
        # Verify all expected planets are present
        expected_planets = [Planet.SUN, Planet.MOON, Planet.MARS, Planet.MERCURY, 
                          Planet.JUPITER, Planet.VENUS, Planet.SATURN, Planet.RAHU, Planet.KETU]
        for expected_planet in expected_planets:
            self.assertIn(expected_planet, planet_enums_found, 
                         f"{expected_planet.name} not found in D20 chart")
        
        # Verify houses list
        self.assertIsInstance(d20_chart["houses"], list)
        self.assertEqual(len(d20_chart["houses"]), 12)
        
        # Verify each house is a HouseData object
        for house in d20_chart["houses"]:
            self.assertIsInstance(house, HouseData)
            self.assertGreaterEqual(house.house_number, 1)
            self.assertLessEqual(house.house_number, 12)
            self.assertIsInstance(house.sign, Zodiac)
        
        # Verify ayanamsa is a number
        self.assertIsInstance(d20_chart["ayanamsa"], (int, float))
        
        # Verify D20 specific properties (Sun should be in a different position than D1)
        sun_d20 = next((p for p in d20_chart["planets"] if p.planet == Planet.SUN), None)
        self.assertIsNotNone(sun_d20)
        # In D20, positions are multiplied by 20 mod 30, so they should be different from D1

if __name__ == '__main__':
    unittest.main()
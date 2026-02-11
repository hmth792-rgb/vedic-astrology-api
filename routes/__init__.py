"""
Routes Package
Contains API route blueprints for D1, D2, D3, D4, D5, D6, D7, and D9 chart divisional calculations, Dasha periods, and Transits
"""
from .d1_routes import d1_bp
from .d2_routes import d2_bp
from .d3_routes import d3_bp
from .d4_routes import d4_bp
from .d5_routes import d5_bp
from .d6_routes import d6_bp
from .d7_routes import d7_bp
from .d8_routes import d8_bp
from .d9_routes import d9_bp
from .d10_routes import d10_bp
from .dasha_routes import dasha_bp
from .transit_routes import transit_bp

__all__ = ['d1_bp', 'd2_bp', 'd3_bp', 'd4_bp', 'd5_bp', 'd6_bp', 'd7_bp', 'd8_bp', 'd9_bp', 'd10_bp', 'dasha_bp', 'transit_bp']

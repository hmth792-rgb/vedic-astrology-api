"""
Routes Package
Contains API route blueprints for D1, D2, D3, D4, D5, D6, D7, D8, D9, D10, D11, D12, D16 chart divisional calculations, Dasha periods, and Transits
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
from .d11_routes import d11_bp
from .d12_routes import d12_bp
from .d16_routes import d16_bp
from .d40_routes import d40_routes
from .d45_routes import d45_routes
from .d60_routes import d60_routes
from .d27_routes import d27_routes
from .dasha_routes import dasha_bp
from .transit_routes import transit_bp

__all__ = ['d1_bp', 'd2_bp', 'd3_bp', 'd4_bp', 'd5_bp', 'd6_bp', 'd7_bp', 'd8_bp', 'd9_bp', 'd10_bp', 'd11_bp', 'd12_bp', 'd16_bp', 'd27_routes', 'd40_routes', 'd45_routes', 'd60_routes', 'dasha_bp', 'transit_bp']

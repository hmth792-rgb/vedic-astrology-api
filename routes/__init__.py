"""
Routes Package
Contains all API route blueprints for different chart types
"""
from .d1_routes import d1_bp
from .d9_routes import d9_bp

__all__ = ['d1_bp', 'd9_bp']

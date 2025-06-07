"""
Easy Mirror Modules Package
Contains modular components for the Easy Mirror application.
"""

from .anthropometric import AnthropometricMeasurements
from .prediction import SexPredictor
from .filters import BasicFilters, ClothingOverlay
from .base import CameraManager

__all__ = [
    'AnthropometricMeasurements',
    'SexPredictor', 
    'BasicFilters',
    'ClothingOverlay',
    'CameraManager'
]
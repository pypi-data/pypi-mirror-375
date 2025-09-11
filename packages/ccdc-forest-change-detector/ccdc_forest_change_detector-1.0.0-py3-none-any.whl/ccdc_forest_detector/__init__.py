"""
CCDC Forest Change Detector

Una librería para detección de cambios forestales usando CCDC con Google Earth Engine
"""

__version__ = "1.0.0"
__author__ = "Tu Nombre"
__email__ = "tu.email@example.com"

from .detector import CCDCForestDetector
from .visualization import ForestVisualization
from .utils import CloudScorePlus

__all__ = ['CCDCForestDetector', 'ForestVisualization', 'CloudScorePlus']

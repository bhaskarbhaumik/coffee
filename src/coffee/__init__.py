"""Coffee Script - Keep your system awake with style."""

__version__ = "0.1.0"
__author__ = "Bhaskar Bhaumik"
__email__ = "your.email@example.com"
__description__ = "A Python script that combines ASCII time display with power management"

from .main import main
from .power import PowerManager, get_power_visual, get_power_data

__all__ = ["main", "PowerManager", "get_power_visual", "get_power_data"]
"""
xwolfx - An unofficial Python API for WOLF (AKA Palringo)
Python port of the wolf.js library
"""

from .client.wolf import WOLF
from .commands.command import Command

__version__ = "1.0.0"
__author__ = "Python Port of wolf.js"

__all__ = ['WOLF', 'Command']
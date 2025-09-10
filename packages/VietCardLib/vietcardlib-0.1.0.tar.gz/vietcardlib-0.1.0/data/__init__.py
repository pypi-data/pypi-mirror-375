"""
Data package for VietCardLib

Chứa data models, database management và card information
"""

try:
    from .CardInfo import CardInfo, CardSide
except ImportError:
    CardInfo = None
    CardSide = None

try:
    from .database import VietCardDatabase
except ImportError:
    VietCardDatabase = None

__all__ = [
    'CardInfo',
    'CardSide', 
    'VietCardDatabase'
]
"""
VietCardLib - Thư viện xử lý ORB, tiền xử lý và OCR giấy tờ tùy thân Việt Nam

Tác giả: Đoàn Ngọc Thành
Email: dnt.doanngocthanh@gmail.com
"""

from .orb import ORBImageAligner, SmartORBAligner
from .data import CardInfo, VietCardDatabase
from .utils import ImageQualityChecker, ImageAutoAdjuster

__version__ = "0.1.0"
__author__ = "Đoàn Ngọc Thành"
__email__ = "dnt.doanngocthanh@gmail.com"

# Export main classes
__all__ = [
    'ORBImageAligner',
    'SmartORBAligner',
    'CardInfo',
    'VietCardDatabase',
    'ImageQualityChecker',
    'ImageAutoAdjuster'
]
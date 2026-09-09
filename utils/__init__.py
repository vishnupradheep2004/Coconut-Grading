"""
Coconut-Grading-AI Utility Modules
Core utilities for detection, grading, pricing, and advanced features
"""

# Original modules
from .detector import load_yolo_model, detect_coconuts, resolve_model_path
from .grading import calculate_grade_and_summary, calculate_grade
from .pricing import load_price_model, predict_market_price, calculate_market_valuation, DEFAULT_MARKET_RATES

# New modules
from .config import Config, get_config, ensure_directories
from .validation import (
    validate_image, validate_confidence_threshold, validate_market_rates,
    validate_detection_counts, validate_username, validate_password, validate_email,
    ValidationError
)
from .database import Database
from .auth import AuthManager, USER_ROLES
from .image_processor import ImageProcessor
from .export import ReportGenerator
from .analytics import Analytics
from .logging_manager import LoggingManager, PerformanceMonitor
from .cache import Cache, ModelCache
from .api import APIResponse, APIEndpoints, APIValidator

__all__ = [
    # Original
    'load_yolo_model', 'detect_coconuts', 'resolve_model_path',
    'calculate_grade_and_summary', 'calculate_grade',
    'load_price_model', 'predict_market_price', 'calculate_market_valuation',
    'DEFAULT_MARKET_RATES',
    
    # New
    'Config', 'get_config', 'ensure_directories',
    'validate_image', 'validate_confidence_threshold', 'validate_market_rates',
    'validate_detection_counts', 'validate_username', 'validate_password',
    'validate_email', 'ValidationError',
    'Database',
    'AuthManager', 'USER_ROLES',
    'ImageProcessor',
    'ReportGenerator',
    'Analytics',
    'LoggingManager', 'PerformanceMonitor',
    'Cache', 'ModelCache',
    'APIResponse', 'APIEndpoints', 'APIValidator'
]


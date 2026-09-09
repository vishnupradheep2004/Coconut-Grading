"""
utils/config.py
Configuration management for Coconut Grading AI
Handles environment variables, settings profiles, and app configuration
"""

import os
from typing import Dict, Any
from pathlib import Path

# Module-level BASE_DIR
BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
    """Base configuration class"""
    
    # App Settings
    APP_NAME = "Coconut Grading AI"
    APP_VERSION = "3.0"
    DEBUG = False
    
    # Model Paths
    MODELS_DIR = BASE_DIR / "models"
    YOLO_MODEL_PATH = MODELS_DIR / "coconut_yolo_v3" / "weights" / "best.pt"
    PRICE_MODEL_PATH = MODELS_DIR / "price_prediction_model.pkl"
    
    # Detection Settings
    DEFAULT_CONFIDENCE_THRESHOLD = 0.25
    MIN_CONFIDENCE_THRESHOLD = 0.10
    MAX_CONFIDENCE_THRESHOLD = 0.90
    CONFIDENCE_STEP = 0.05
    
    # Image Settings
    MAX_IMAGE_SIZE = 50 * 1024 * 1024  # 50MB
    SUPPORTED_FORMATS = ["jpg", "jpeg", "png", "webp"]
    MIN_IMAGE_WIDTH = 100
    MIN_IMAGE_HEIGHT = 100
    
    # Database Settings
    DB_PATH = BASE_DIR / "data" / "coconut_grading.db"
    EXPORT_DIR = BASE_DIR / "exports"
    
    # Default Market Rates (in ₹)
    DEFAULT_MARKET_RATES = {
        "dry": 50.0,
        "green": 35.0,
        "tender": 25.0
    }
    
    # Logging Settings
    LOG_DIR = BASE_DIR / "logs"
    LOG_LEVEL = "INFO"
    
    # Caching Settings
    ENABLE_CACHE = True
    CACHE_TTL = 3600  # seconds


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    LOG_LEVEL = "DEBUG"


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    LOG_LEVEL = "INFO"


class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    DB_PATH: Path = BASE_DIR / "data" / "test_coconut_grading.db"
    ENABLE_CACHE = False


def get_config(env: str = None) -> Config:
    """Get configuration based on environment"""
    if env is None:
        env = os.getenv("ENVIRONMENT", "development")
    
    config_map = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
        "testing": TestingConfig
    }
    
    return config_map.get(env, DevelopmentConfig)()


def ensure_directories():
    """Create necessary directories if they don't exist"""
    config = get_config()
    
    for directory in [config.DB_PATH.parent, config.EXPORT_DIR, config.LOG_DIR]:
        directory.mkdir(parents=True, exist_ok=True)

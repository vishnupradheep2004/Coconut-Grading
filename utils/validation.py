"""
utils/validation.py
Input validation and error handling for Coconut Grading AI
Validates images, parameters, and user inputs
"""

from typing import Tuple, Dict, Any
from PIL import Image
import os


class ValidationError(Exception):
    """Custom validation exception"""
    pass


def validate_image(image: Any, max_size: int = 50 * 1024 * 1024) -> Tuple[bool, str]:
    """
    Validate uploaded image
    
    Args:
        image: PIL Image or file path
        max_size: Maximum file size in bytes
    
    Returns:
        (is_valid, error_message)
    """
    try:
        # Check if image is PIL Image
        if isinstance(image, Image.Image):
            if image.size[0] < 100 or image.size[1] < 100:
                return False, "Image dimensions too small (minimum 100x100 pixels)"
            return True, ""
        
        # Check if file exists
        if isinstance(image, str) and not os.path.exists(image):
            return False, "Image file not found"
        
        # Check file size
        if isinstance(image, str):
            file_size = os.path.getsize(image)
            if file_size > max_size:
                return False, f"Image file too large (max {max_size / 1024 / 1024:.0f}MB)"
        
        return True, ""
    
    except Exception as e:
        return False, f"Image validation error: {str(e)}"


def validate_confidence_threshold(confidence: float, min_val: float = 0.10, max_val: float = 0.90) -> Tuple[bool, str]:
    """Validate confidence threshold value"""
    if not isinstance(confidence, (int, float)):
        return False, "Confidence must be a number"
    
    if confidence < min_val or confidence > max_val:
        return False, f"Confidence must be between {min_val} and {max_val}"
    
    return True, ""


def validate_market_rates(rates: Dict[str, float]) -> Tuple[bool, str]:
    """Validate market rate values"""
    required_keys = ["dry", "green", "tender"]
    
    # Check all keys present
    if not all(key in rates for key in required_keys):
        return False, "Market rates must include: dry, green, tender"
    
    # Check all values are positive numbers
    for key, value in rates.items():
        if not isinstance(value, (int, float)):
            return False, f"Rate for {key} must be a number"
        if value < 0:
            return False, f"Rate for {key} cannot be negative"
    
    return True, ""


def validate_detection_counts(counts: Dict[str, int]) -> Tuple[bool, str]:
    """Validate detection count dictionary"""
    required_keys = ["dry", "green", "tender"]
    
    if not all(key in counts for key in required_keys):
        return False, "Counts must include: dry, green, tender"
    
    for key, value in counts.items():
        if not isinstance(value, int):
            return False, f"Count for {key} must be an integer"
        if value < 0:
            return False, f"Count for {key} cannot be negative"
    
    return True, ""


def validate_username(username: str) -> Tuple[bool, str]:
    """Validate username format"""
    if not username or len(username) < 3:
        return False, "Username must be at least 3 characters"
    
    if len(username) > 50:
        return False, "Username must be less than 50 characters"
    
    if not username.isalnum() and "_" not in username:
        return False, "Username can only contain letters, numbers, and underscore"
    
    return True, ""


def validate_password(password: str) -> Tuple[bool, str]:
    """Validate password strength"""
    if not password or len(password) < 6:
        return False, "Password must be at least 6 characters"
    
    if len(password) > 100:
        return False, "Password must be less than 100 characters"
    
    return True, ""


def validate_email(email: str) -> Tuple[bool, str]:
    """Validate email format"""
    import re
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(pattern, email):
        return False, "Invalid email format"
    
    return True, ""

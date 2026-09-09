"""
utils/image_processor.py
Image preprocessing and enhancement for Coconut Grading AI
Handles image validation, enhancement, and preparation for analysis
"""

import cv2
import numpy as np
from PIL import Image, ImageEnhance
from typing import Tuple, Optional


class ImageProcessor:
    """Image processing utilities"""
    
    @staticmethod
    def enhance_image(image: Image.Image, brightness: float = 1.0, 
                     contrast: float = 1.0, saturation: float = 1.0) -> Image.Image:
        """
        Enhance image brightness, contrast, and saturation
        
        Args:
            image: PIL Image
            brightness: Brightness factor (1.0 = original)
            contrast: Contrast factor (1.0 = original)
            saturation: Saturation factor (1.0 = original)
        
        Returns:
            Enhanced PIL Image
        """
        # Brightness
        if brightness != 1.0:
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(brightness)
        
        # Contrast
        if contrast != 1.0:
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(contrast)
        
        # Saturation (Color)
        if saturation != 1.0:
            enhancer = ImageEnhance.Color(image)
            image = enhancer.enhance(saturation)
        
        return image
    
    @staticmethod
    def resize_image(image: Image.Image, max_width: int = 1920, 
                    max_height: int = 1440, maintain_aspect: bool = True) -> Image.Image:
        """
        Resize image to fit within bounds
        
        Args:
            image: PIL Image
            max_width: Maximum width
            max_height: Maximum height
            maintain_aspect: Keep aspect ratio
        
        Returns:
            Resized PIL Image
        """
        if maintain_aspect:
            image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        else:
            image = image.resize((max_width, max_height), Image.Resampling.LANCZOS)
        
        return image
    
    @staticmethod
    def auto_enhance(image: Image.Image) -> Image.Image:
        """
        Auto enhance image for better detection
        Increases contrast and sharpness
        """
        # Convert to numpy array
        img_array = np.array(image)
        
        # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
        lab = cv2.cvtColor(img_array, cv2.COLOR_RGB2LAB)
        l, a, b = cv2.split(lab)
        
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        
        enhanced = cv2.merge([l, a, b])
        enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2RGB)
        
        return Image.fromarray(enhanced.astype('uint8'))
    
    @staticmethod
    def get_image_statistics(image: Image.Image) -> dict:
        """Get image statistics (brightness, contrast, etc.)"""
        img_array = np.array(image)
        
        return {
            "width": image.width,
            "height": image.height,
            "size_kb": img_array.nbytes / 1024,
            "mean_brightness": float(np.mean(img_array)),
            "brightness_std": float(np.std(img_array)),
            "mean_rgb": {
                "r": float(np.mean(img_array[:,:,0])),
                "g": float(np.mean(img_array[:,:,1])),
                "b": float(np.mean(img_array[:,:,2]))
            }
        }
    
    @staticmethod
    def detect_image_quality(image: Image.Image) -> Tuple[float, str]:
        """
        Assess image quality for detection
        
        Returns:
            (quality_score, quality_level) where score is 0-100
        """
        stats = ImageProcessor.get_image_statistics(image)
        
        brightness = stats["mean_brightness"]
        brightness_std = stats["brightness_std"]
        
        score = 100.0
        
        # Penalize if too dark or too bright
        if brightness < 30:
            score -= 30
        elif brightness > 220:
            score -= 20
        
        # Penalize if low contrast
        if brightness_std < 20:
            score -= 25
        
        # Penalize if too small
        if image.width < 200 or image.height < 200:
            score -= 20
        
        score = max(0, min(100, score))
        
        if score >= 80:
            quality = "Excellent"
        elif score >= 60:
            quality = "Good"
        elif score >= 40:
            quality = "Fair"
        else:
            quality = "Poor"
        
        return score, quality

"""
utils/detector.py
Handles YOLO model loading, image inference, and detection bounding-box parsing.
"""

import os
from typing import Dict, Any, List
from PIL import Image
import streamlit as st
from ultralytics import YOLO


def resolve_model_path(default_rel_path: str, fallback_paths: List[str] = None) -> str:
    """Resolve model path checking local relative path first, then fallbacks."""
    if os.path.exists(default_rel_path):
        return default_rel_path
    
    if fallback_paths:
        for p in fallback_paths:
            if os.path.exists(p):
                return p
                
    return default_rel_path


@st.cache_resource
def load_yolo_model(model_path: str) -> YOLO:
    """Load and cache YOLO model."""
    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"YOLO model weights not found at: {model_path}\n"
            "Please ensure 'best.pt' is placed in the models directory."
        )
    return YOLO(model_path)


def detect_coconuts(
    model: YOLO,
    image: Image.Image,
    conf_threshold: float = 0.25
) -> Dict[str, Any]:
    """
    Run YOLO detection on an input PIL image and return structured results.
    
    Returns:
        dict: {
            "result": Ultralytics Results object,
            "plotted_image": np.ndarray (BGR image with boxes),
            "counts": {"dry": int, "green": int, "tender": int},
            "total": int,
            "average_confidence": float,
            "confidences": list of floats,
            "boxes_data": list of dicts
        }
    """
    # Core YOLO inference
    results = model.predict(
        source=image,
        conf=conf_threshold,
        verbose=False
    )
    result = results[0]
    
    # Render plotted bounding boxes
    plotted_image = result.plot()
    
    names = model.names
    counts = {
        "dry": 0,
        "green": 0,
        "tender": 0
    }
    confidences = []
    boxes_data = []
    
    if result.boxes is not None and len(result.boxes) > 0:
        for box in result.boxes:
            class_id = int(box.cls[0])
            confidence = float(box.conf[0])
            class_name = names[class_id].lower().strip()
            
            if class_name in counts:
                counts[class_name] += 1
                confidences.append(confidence)
                
            boxes_data.append({
                "class_id": class_id,
                "class_name": class_name,
                "confidence": confidence,
                "xyxy": box.xyxy[0].tolist() if hasattr(box, "xyxy") else []
            })
            
    total = sum(counts.values())
    average_confidence = (sum(confidences) / len(confidences)) if confidences else 0.0
    
    return {
        "result": result,
        "plotted_image": plotted_image,
        "counts": counts,
        "total": total,
        "average_confidence": average_confidence,
        "confidences": confidences,
        "boxes_data": boxes_data
    }

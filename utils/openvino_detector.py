"""
utils/openvino_detector.py

OpenVINO inference layer for Coconut Grading AI.
Keeps the same output structure as utils/detector.py.
"""

import os
from pathlib import Path
from typing import Dict, Any

from PIL import Image
import streamlit as st
from ultralytics import YOLO


# ============================================================
# MODEL LOADING
# ============================================================

@st.cache_resource
def load_openvino_model(model_path: str):
    """
    Load and cache the exported OpenVINO model.
    """

    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"OpenVINO model not found at:\n{model_path}"
        )

    return YOLO(model_path)


# ============================================================
# OPENVINO DETECTION
# ============================================================

def detect_coconuts_openvino(
    model,
    image: Image.Image,
    conf_threshold: float = 0.25
) -> Dict[str, Any]:
    """
    Run coconut detection using OpenVINO.

    Returns the same structure as utils.detector.detect_coconuts()
    so the existing grading/pricing/database modules continue working.
    """

    results = model.predict(
        source=image,
        conf=conf_threshold,
        imgsz=640,
        device="intel:cpu",
        verbose=False
    )

    result = results[0]

    # --------------------------------------------------------
    # DRAW DETECTION BOXES
    # --------------------------------------------------------

    plotted_image = result.plot()

    # --------------------------------------------------------
    # COUNTS
    # --------------------------------------------------------

    counts = {
        "dry": 0,
        "green": 0,
        "tender": 0
    }

    confidences = []
    boxes_data = []

    names = result.names

    # --------------------------------------------------------
    # PARSE DETECTIONS
    # --------------------------------------------------------

    if result.boxes is not None and len(result.boxes) > 0:

        for box in result.boxes:

            class_id = int(box.cls[0])
            confidence = float(box.conf[0])

            class_name = (
                names[class_id]
                .lower()
                .strip()
            )

            if class_name in counts:
                counts[class_name] += 1
                confidences.append(confidence)

            boxes_data.append({
                "class_id": class_id,
                "class_name": class_name,
                "confidence": confidence,
                "xyxy": (
                    box.xyxy[0].tolist()
                    if hasattr(box, "xyxy")
                    else []
                )
            })

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    total = sum(counts.values())

    average_confidence = (
        sum(confidences) / len(confidences)
        if confidences
        else 0.0
    )

    return {
        "result": result,
        "plotted_image": plotted_image,
        "counts": counts,
        "total": total,
        "average_confidence": average_confidence,
        "confidences": confidences,
        "boxes_data": boxes_data
    }
"""
utils/grading.py
Encapsulates coconut maturity grading, distribution analysis, and batch explanation.
"""

from typing import Dict, Tuple, Any


def calculate_grade_and_summary(
    counts: Dict[str, int],
    avg_conf: float = 0.0
) -> Dict[str, Any]:
    """
    Determine dominant coconut maturity type, quality grade, distribution,
    and a clear explanation of the batch.
    
    Grading Rules:
      - All Dry                 -> Grade A (Mature Dry Coconut - Copra & Oil)
      - Predominantly Green     -> Grade B (Fresh Green Coconut - Culinary)
      - Predominantly Tender    -> Grade C (Tender Coconut - Water & Beverage)
      - Mixed distribution      -> Mixed Batch with dominant breakdown
      - No coconuts             -> Unknown / No Detection
      
    Returns:
        dict: {
            "grade": str,
            "badge_color": str,
            "description": str,
            "dominant_type": str,
            "distribution": Dict[str, float],
            "is_mixed": bool
        }
    """
    total = sum(counts.values())
    
    if total == 0:
        return {
            "grade": "Unknown",
            "badge_color": "gray",
            "description": "No coconuts detected in the image.",
            "dominant_type": "None",
            "distribution": {"dry": 0.0, "green": 0.0, "tender": 0.0},
            "is_mixed": False
        }
        
    distribution = {
        k: (v / total) * 100.0 for k, v in counts.items()
    }
    
    dominant_type = max(counts, key=counts.get)
    non_zero_classes = sum(1 for v in counts.values() if v > 0)
    is_mixed = non_zero_classes > 1
    
    if counts.get("dry", 0) == total:
        grade = "Grade A (Mature Dry)"
        badge_color = "#2e7d32"  # dark green / success
        description = "Uniform batch of mature dry coconuts. Ideal for copra production, desiccated coconut, and oil extraction."
    elif counts.get("green", 0) == total:
        grade = "Grade B (Fresh Green)"
        badge_color = "#1565c0"  # deep blue / quality
        description = "Uniform batch of fresh green coconuts with thick meat. Ideal for household culinary use and retail markets."
    elif counts.get("tender", 0) == total:
        grade = "Grade C (Tender Water)"
        badge_color = "#e65100"  # amber / orange
        description = "Uniform batch of tender coconuts rich in mineral water. Ideal for fresh beverage consumption."
    elif counts.get("dry", 0) > counts.get("green", 0) and counts.get("dry", 0) > counts.get("tender", 0):
        grade = "Grade A Mixed (Dry Dominant)"
        badge_color = "#2e7d32"
        description = f"Mixed harvest with {distribution['dry']:.1f}% Mature Dry coconuts dominating the lot."
    elif counts.get("green", 0) >= counts.get("dry", 0) and counts.get("green", 0) > counts.get("tender", 0):
        grade = "Grade B Mixed (Green Dominant)"
        badge_color = "#1565c0"
        description = f"Mixed harvest with {distribution['green']:.1f}% Fresh Green coconuts dominating the lot."
    else:
        grade = "Grade C Mixed (Tender Dominant)"
        badge_color = "#e65100"
        description = f"Mixed harvest with {distribution['tender']:.1f}% Tender coconuts dominating the lot."
        
    return {
        "grade": grade,
        "badge_color": badge_color,
        "description": description,
        "dominant_type": dominant_type,
        "distribution": distribution,
        "is_mixed": is_mixed
    }


def calculate_grade(counts: Dict[str, int]) -> Tuple[str, str]:
    """
    Backwards-compatible wrapper returning (grade_letter, dominant_type).
    """
    summary = calculate_grade_and_summary(counts)
    dom = summary["dominant_type"]
    if dom == "dry":
        return "A", dom
    elif dom == "green":
        return "B", dom
    elif dom == "tender":
        return "C", dom
    return "Unknown", dom


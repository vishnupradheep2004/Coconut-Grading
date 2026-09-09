"""
utils/pricing.py
Handles market valuation calculation and optional price regressor inference.
"""

import os
from typing import Dict, Any, Optional, Tuple
import pandas as pd
import joblib
import streamlit as st

# Benchmark market rates (₹ per coconut / standard kg equivalent)
DEFAULT_MARKET_RATES = {
    "dry": 35.0,     # ₹ per mature dry coconut
    "green": 28.0,   # ₹ per fresh green coconut
    "tender": 40.0   # ₹ per tender water coconut
}


@st.cache_resource
def load_price_model(model_path: str) -> Optional[Any]:
    """Load and cache the trained price prediction model if present."""
    if not os.path.exists(model_path):
        return None
    try:
        return joblib.load(model_path)
    except Exception as e:
        st.warning(f"Unable to load price model: {e}")
        return None


def calculate_market_valuation(
    counts: Dict[str, int],
    market_rates: Dict[str, float] = None
) -> Tuple[float, Dict[str, Dict[str, Any]]]:
    """
    Calculate transparent market valuation with per-maturity itemized breakdown.
    
    Returns:
        tuple: (total_valuation, breakdown_dict)
    """
    if market_rates is None:
        market_rates = DEFAULT_MARKET_RATES
        
    breakdown = {}
    total_val = 0.0
    
    for ctype in ["dry", "green", "tender"]:
        cnt = counts.get(ctype, 0)
        rate = market_rates.get(ctype, 30.0)
        subtotal = cnt * rate
        breakdown[ctype] = {
            "count": cnt,
            "rate": rate,
            "subtotal": subtotal
        }
        total_val += subtotal
        
    return total_val, breakdown


def predict_market_price(
    price_model: Any,
    counts: Dict[str, int],
    total: int,
    average_confidence: float
) -> float:
    """
    Predict market price per kg using the trained Random Forest regressor (if available),
    or falls back to average weighted valuation per coconut.
    """
    if total == 0:
        return 0.0
        
    if price_model is not None:
        input_data = pd.DataFrame([{
            "dry_count": counts.get("dry", 0),
            "green_count": counts.get("green", 0),
            "tender_count": counts.get("tender", 0),
            "total_coconuts": total,
            "average_confidence": float(average_confidence)
        }])
        
        try:
            predicted = float(price_model.predict(input_data)[0])
            return max(0.0, predicted)
        except Exception:
            pass
            
    # Fallback to weighted unit calculation
    total_val, _ = calculate_market_valuation(counts)
    return total_val / total if total > 0 else 0.0


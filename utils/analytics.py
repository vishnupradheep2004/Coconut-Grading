"""
utils/analytics.py
Advanced analytics for Coconut Grading AI
Provides insights, trends, and statistical analysis
"""

from typing import Dict, List, Any
from datetime import datetime, timedelta
import statistics


class Analytics:
    """Analytics and insights for analysis results"""
    
    @staticmethod
    def calculate_batch_statistics(results: List[Dict]) -> Dict[str, Any]:
        """
        Calculate aggregate statistics for batch results
        
        Args:
            results: List of analysis results
        
        Returns:
            Dictionary with statistics
        """
        if not results:
            return {}
        
        total_counts = {"dry": 0, "green": 0, "tender": 0}
        total_values = []
        confidence_scores = []
        
        for result in results:
            counts = result.get("counts", {})
            for key, value in counts.items():
                total_counts[key] = total_counts.get(key, 0) + value
            
            total_values.append(result.get("total_value", 0))
            confidence_scores.append(result.get("avg_confidence", 0))
        
        total_coconuts = sum(total_counts.values())
        
        return {
            "total_images": len(results),
            "total_coconuts": total_coconuts,
            "coconut_distribution": {
                "dry": total_counts["dry"],
                "green": total_counts["green"],
                "tender": total_counts["tender"],
                "dry_pct": (total_counts["dry"] / total_coconuts * 100) if total_coconuts > 0 else 0,
                "green_pct": (total_counts["green"] / total_coconuts * 100) if total_coconuts > 0 else 0,
                "tender_pct": (total_counts["tender"] / total_coconuts * 100) if total_coconuts > 0 else 0
            },
            "valuation": {
                "total_value": sum(total_values),
                "average_value_per_image": sum(total_values) / len(results) if results else 0,
                "min_value": min(total_values) if total_values else 0,
                "max_value": max(total_values) if total_values else 0,
                "value_median": statistics.median(total_values) if total_values else 0
            },
            "confidence": {
                "average": sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0,
                "min": min(confidence_scores) if confidence_scores else 0,
                "max": max(confidence_scores) if confidence_scores else 0
            },
            "coconuts_per_image": total_coconuts / len(results) if results else 0
        }
    
    @staticmethod
    def get_trend_analysis(history: List[Dict], days: int = 30) -> Dict[str, Any]:
        """
        Analyze trends over time
        
        Args:
            history: List of historical results with timestamps
            days: Number of days to analyze
        
        Returns:
            Trend analysis
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        
        recent_results = [
            r for r in history 
            if datetime.fromisoformat(r.get("created_at", "")) > cutoff_date
        ]
        
        if not recent_results:
            return {}
        
        total_analyses = len(recent_results)
        total_coconuts_processed = sum(r.get("total", 0) for r in recent_results)
        avg_grade_distribution = Analytics.calculate_batch_statistics(recent_results)
        
        return {
            "period_days": days,
            "analyses_performed": total_analyses,
            "coconuts_processed": total_coconuts_processed,
            "coconuts_per_day": total_coconuts_processed / days,
            "analyses_per_day": total_analyses / days,
            "grade_distribution": avg_grade_distribution.get("coconut_distribution", {}),
            "total_value_trend": sum(r.get("total_value", 0) for r in recent_results)
        }
    
    @staticmethod
    def get_quality_insights(results: List[Dict]) -> Dict[str, Any]:
        """
        Generate quality insights from results
        
        Args:
            results: List of analysis results
        
        Returns:
            Quality insights and recommendations
        """
        if not results:
            return {}
        
        stats = Analytics.calculate_batch_statistics(results)
        dist = stats.get("coconut_distribution", {})
        
        insights = {
            "predominant_type": None,
            "quality_level": None,
            "recommendations": []
        }
        
        # Determine predominant type
        if dist.get("dry_pct", 0) > dist.get("green_pct", 0) and dist.get("dry_pct", 0) > dist.get("tender_pct", 0):
            insights["predominant_type"] = "Dry/Mature"
            insights["quality_level"] = "Grade A"
            insights["recommendations"] = [
                "Suitable for copra and oil production",
                "Good for desiccated coconut manufacturing",
                "Consider bulk sales to processing facilities"
            ]
        elif dist.get("green_pct", 0) >= dist.get("dry_pct", 0) and dist.get("green_pct", 0) > dist.get("tender_pct", 0):
            insights["predominant_type"] = "Fresh Green"
            insights["quality_level"] = "Grade B"
            insights["recommendations"] = [
                "Target household and retail markets",
                "Quick sale recommended for freshness",
                "Premium pricing available for culinary markets"
            ]
        else:
            insights["predominant_type"] = "Tender Water"
            insights["quality_level"] = "Grade C"
            insights["recommendations"] = [
                "Best for fresh beverage consumption",
                "High demand in summer months",
                "Target juice and beverage manufacturers"
            ]
        
        # Confidence-based recommendations
        avg_confidence = stats.get("confidence", {}).get("average", 0)
        if avg_confidence > 0.9:
            insights["recommendations"].append("High detection confidence - results are very reliable")
        elif avg_confidence < 0.5:
            insights["recommendations"].append("Low detection confidence - consider re-imaging with better lighting")
        
        return insights
    
    @staticmethod
    def compare_batches(batch1: List[Dict], batch2: List[Dict]) -> Dict[str, Any]:
        """
        Compare two batches for analysis
        
        Args:
            batch1: First batch results
            batch2: Second batch results
        
        Returns:
            Comparison analysis
        """
        stats1 = Analytics.calculate_batch_statistics(batch1)
        stats2 = Analytics.calculate_batch_statistics(batch2)
        
        return {
            "batch1": stats1,
            "batch2": stats2,
            "differences": {
                "total_coconuts_diff": stats2.get("total_coconuts", 0) - stats1.get("total_coconuts", 0),
                "total_value_diff": stats2.get("valuation", {}).get("total_value", 0) - stats1.get("valuation", {}).get("total_value", 0),
                "avg_confidence_diff": stats2.get("confidence", {}).get("average", 0) - stats1.get("confidence", {}).get("average", 0)
            }
        }

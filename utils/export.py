"""
utils/export.py
Report generation and data export for Coconut Grading AI
Generates PDF and CSV reports of analysis results
"""

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any


class ReportGenerator:
    """Generate reports in various formats"""
    
    def __init__(self, export_dir: Path):
        """Initialize report generator"""
        self.export_dir = export_dir
        self.export_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_csv_report(self, filename: str, results: List[Dict]) -> str:
        """
        Generate CSV report
        
        Args:
            filename: Output filename
            results: List of analysis results
        
        Returns:
            Path to generated file
        """
        filepath = self.export_dir / f"{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        if not results:
            return str(filepath)
        
        fieldnames = results[0].keys()
        
        with open(filepath, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        
        return str(filepath)
    
    def generate_json_report(self, filename: str, data: Dict[str, Any]) -> str:
        """
        Generate JSON report
        
        Args:
            filename: Output filename
            data: Report data
        
        Returns:
            Path to generated file
        """
        filepath = self.export_dir / f"{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filepath, 'w') as jsonfile:
            json.dump(data, jsonfile, indent=2)
        
        return str(filepath)
    
    def generate_text_report(self, filename: str, analysis_data: Dict) -> str:
        """
        Generate text report
        
        Args:
            filename: Output filename
            analysis_data: Analysis results
        
        Returns:
            Path to generated file
        """
        filepath = self.export_dir / f"{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(filepath, 'w') as txtfile:
            txtfile.write("=" * 80 + "\n")
            txtfile.write("COCONUT GRADING AI - ANALYSIS REPORT\n")
            txtfile.write("=" * 80 + "\n\n")
            
            txtfile.write(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            txtfile.write(f"Filename: {filename}\n\n")
            
            # Detection Results
            if "counts" in analysis_data:
                txtfile.write("-" * 40 + "\n")
                txtfile.write("DETECTION RESULTS\n")
                txtfile.write("-" * 40 + "\n")
                counts = analysis_data["counts"]
                txtfile.write(f"Total Coconuts Detected: {sum(counts.values())}\n")
                txtfile.write(f"  - Dry (Mature): {counts.get('dry', 0)}\n")
                txtfile.write(f"  - Green (Fresh): {counts.get('green', 0)}\n")
                txtfile.write(f"  - Tender (Water): {counts.get('tender', 0)}\n\n")
            
            # Grading
            if "grade" in analysis_data:
                txtfile.write("-" * 40 + "\n")
                txtfile.write("QUALITY GRADING\n")
                txtfile.write("-" * 40 + "\n")
                txtfile.write(f"Overall Grade: {analysis_data['grade']}\n")
                if "description" in analysis_data:
                    txtfile.write(f"Description: {analysis_data['description']}\n\n")
            
            # Valuation
            if "total_value" in analysis_data:
                txtfile.write("-" * 40 + "\n")
                txtfile.write("MARKET VALUATION\n")
                txtfile.write("-" * 40 + "\n")
                txtfile.write(f"Total Estimated Value: ₹{analysis_data['total_value']:.2f}\n")
                if "breakdown" in analysis_data:
                    breakdown = analysis_data["breakdown"]
                    for key, data in breakdown.items():
                        txtfile.write(f"\n{key.capitalize()}:\n")
                        txtfile.write(f"  Count: {data['count']}\n")
                        txtfile.write(f"  Rate: ₹{data['rate']:.2f}/pc\n")
                        txtfile.write(f"  Subtotal: ₹{data['subtotal']:.2f}\n")
            
            # Additional Info
            if "avg_confidence" in analysis_data:
                txtfile.write(f"\nAverage Detection Confidence: {analysis_data['avg_confidence'] * 100:.2f}%\n")
        
        return str(filepath)
    
    def generate_batch_summary(self, batch_name: str, batch_results: List[Dict]) -> str:
        """
        Generate batch processing summary
        
        Args:
            batch_name: Name of batch
            batch_results: List of individual analysis results
        
        Returns:
            Path to generated file
        """
        filepath = self.export_dir / f"batch_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(filepath, 'w') as txtfile:
            txtfile.write("=" * 80 + "\n")
            txtfile.write("BATCH PROCESSING SUMMARY\n")
            txtfile.write("=" * 80 + "\n\n")
            
            txtfile.write(f"Batch Name: {batch_name}\n")
            txtfile.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            txtfile.write(f"Total Images: {len(batch_results)}\n\n")
            
            # Aggregate statistics
            total_coconuts = sum(r.get('total', 0) for r in batch_results)
            total_value = sum(r.get('total_value', 0) for r in batch_results)
            
            txtfile.write("-" * 40 + "\n")
            txtfile.write("AGGREGATE STATISTICS\n")
            txtfile.write("-" * 40 + "\n")
            txtfile.write(f"Total Coconuts: {total_coconuts}\n")
            txtfile.write(f"Total Batch Value: ₹{total_value:.2f}\n")
            txtfile.write(f"Average Value per Image: ₹{total_value / len(batch_results):.2f}\n\n")
            
            # Individual results
            txtfile.write("-" * 40 + "\n")
            txtfile.write("INDIVIDUAL RESULTS\n")
            txtfile.write("-" * 40 + "\n")
            
            for idx, result in enumerate(batch_results, 1):
                txtfile.write(f"\nImage {idx}: {result.get('filename', 'Unknown')}\n")
                txtfile.write(f"  Coconuts: {result.get('total', 0)}\n")
                txtfile.write(f"  Grade: {result.get('grade', 'N/A')}\n")
                txtfile.write(f"  Value: ₹{result.get('total_value', 0):.2f}\n")
        
        return str(filepath)

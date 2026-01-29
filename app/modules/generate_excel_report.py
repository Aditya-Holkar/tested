# generate_excel_report.py - Standalone script for Excel report generation
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.report_generator import ReportGenerator
from modules.test_case_manager import TestCaseManager
import json
from datetime import datetime

def generate_excel_from_json(json_file, output_file=None):
    """Generate Excel report from JSON file"""
    try:
        # Read JSON file
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        # Generate report
        report_generator = ReportGenerator()
        excel_data = report_generator.generate_report(data, 'detailed_excel')
        
        # Determine output filename
        if not output_file:
            base_name = os.path.splitext(json_file)[0]
            output_file = f"{base_name}_detailed_report.xlsx"
        
        # Save to file
        with open(output_file, 'wb') as f:
            f.write(excel_data if isinstance(excel_data, bytes) else excel_data.encode())
        
        print(f"Excel report generated: {output_file}")
        return True
        
    except Exception as e:
        print(f"Error generating Excel report: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_excel_report.py <input_json_file> [output_excel_file]")
        print("Example: python generate_excel_report.py test_results.json website_report.xlsx")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found")
        sys.exit(1)
    
    generate_excel_from_json(input_file, output_file)
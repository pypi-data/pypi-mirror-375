"""
Report Generator for SmartTest
Creates detailed reports with analysis results
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any

class ReportGenerator:
    def __init__(self):
        self.report_data = {}
        
    def create_report(self, analysis_results: Dict[str, Any]) -> str:
        self.report_data = analysis_results
        return self.generate_html_report()
        
    def generate_html_report(self) -> str:
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SmartTest Report</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f5f5;
            color: #333;
        }}
        .container {{ max-width: 1000px; margin: 0 auto; padding: 20px; }}
        .header {{ 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; 
            padding: 40px; 
            border-radius: 15px; 
            text-align: center; 
            margin-bottom: 30px;
        }}
        .summary {{ 
            background: white; 
            padding: 30px; 
            border-radius: 15px; 
            margin-bottom: 20px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        .section {{ 
            background: white; 
            padding: 25px; 
            border-radius: 15px; 
            margin-bottom: 20px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        .error {{ color: #dc3545; background: #f8d7da; padding: 10px; border-radius: 5px; margin: 5px 0; }}
        .warning {{ color: #856404; background: #fff3cd; padding: 10px; border-radius: 5px; margin: 5px 0; }}
        .suggestion {{ color: #0c5460; background: #d1ecf1; padding: 10px; border-radius: 5px; margin: 5px 0; }}
        .status-excellent {{ color: #28a745; font-weight: bold; }}
        .status-good {{ color: #ffc107; font-weight: bold; }}
        .status-needs_attention {{ color: #dc3545; font-weight: bold; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; }}
        .stat-card {{ 
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white; 
            padding: 20px; 
            border-radius: 10px; 
            text-align: center;
        }}
        .stat-number {{ font-size: 2em; font-weight: bold; margin-bottom: 10px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧠 SmartTest Report</h1>
            <p>Intelligent Code Analysis Report</p>
            <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="summary">
            <h2>📊 Summary</h2>
            <p><strong>File:</strong> {self.report_data.get('file_path', 'N/A')}</p>
            <p><strong>Status:</strong> <span class="status-{self.report_data.get('summary', {}).get('status', 'unknown')}">{self.report_data.get('summary', {}).get('message', 'Unknown')}</span></p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{self.report_data.get('summary', {}).get('total_issues', 0)}</div>
                <div>Total Issues</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{self.report_data.get('summary', {}).get('error_count', 0)}</div>
                <div>Errors</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{self.report_data.get('summary', {}).get('warning_count', 0)}</div>
                <div>Warnings</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{self.report_data.get('summary', {}).get('suggestion_count', 0)}</div>
                <div>Suggestions</div>
            </div>
        </div>
        
        {self.generate_errors_section()}
        {self.generate_warnings_section()}
        {self.generate_suggestions_section()}
    </div>
</body>
</html>
        """
        
        return html
        
    def generate_errors_section(self) -> str:
        errors = self.report_data.get('errors', [])
        if not errors:
            return '<div class="section"><h2>✅ No Errors Found</h2><p>Your code has no syntax or runtime errors!</p></div>'
            
        html = '<div class="section"><h2>❌ Errors</h2>'
        for error in errors:
            html += f'<div class="error">{error}</div>'
        html += '</div>'
        return html
        
    def generate_warnings_section(self) -> str:
        warnings = self.report_data.get('warnings', [])
        if not warnings:
            return '<div class="section"><h2>✅ No Warnings</h2><p>Your code has no warnings!</p></div>'
            
        html = '<div class="section"><h2>⚠️ Warnings</h2>'
        for warning in warnings:
            html += f'<div class="warning">{warning}</div>'
        html += '</div>'
        return html
        
    def generate_suggestions_section(self) -> str:
        suggestions = self.report_data.get('suggestions', [])
        if not suggestions:
            return '<div class="section"><h2>✅ No Suggestions</h2><p>Your code follows best practices!</p></div>'
            
        html = '<div class="section"><h2>💡 Suggestions</h2>'
        for suggestion in suggestions:
            html += f'<div class="suggestion">{suggestion}</div>'
        html += '</div>'
        return html
        
    def save_report(self, report_html: str, filename: str = None) -> str:
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'smarttest_report_{timestamp}.html'
            
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report_html)
            
        return filename

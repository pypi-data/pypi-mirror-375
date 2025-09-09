"""
Simple Local Dashboard for Clyrdia CLI MVP
This module provides a simple, always-available local dashboard
"""

import webbrowser
import socket
import threading
import time
import sqlite3
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import base64
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.columns import Columns
from rich.align import Align

console = Console()

class SimpleDashboardHandler(BaseHTTPRequestHandler):
    """Simple HTTP request handler for the dashboard"""
    
    def log_message(self, format, *args):
        """Suppress HTTP server logging - users don't need to see this"""
        return
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
        if path == "/" or path == "":
            self.send_dashboard_page()
        elif path == "/api/status":
            self.send_api_response(self.get_status_data())
        elif path == "/api/metrics":
            self.send_api_response(self.get_metrics_data())
        elif path == "/api/benchmarks":
            self.send_api_response(self.get_benchmarks_data())
        elif path == "/api/models":
            self.send_api_response(self.get_models_data())
        elif path == "/api/costs":
            self.send_api_response(self.get_costs_data())
        elif path == "/api/export":
            self.handle_export_request(parsed_url.query)
        elif path == "/api/detailed-results":
            self.send_api_response(self.get_detailed_results())
        elif path == "/api/performance-trends":
            self.send_api_response(self.get_performance_trends())
        elif path == "/api/model-comparison":
            self.send_api_response(self.get_model_comparison())
        else:
            self.send_error(404, "Not Found")
    
    def send_dashboard_page(self):
        """Send the main dashboard HTML page"""
        html = self.generate_dashboard_html()
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())
    
    def send_api_response(self, data: Dict[str, Any]):
        """Send JSON API response"""
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def do_OPTIONS(self):
        """Handle OPTIONS request for CORS preflight"""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
    
    def get_status_data(self) -> Dict[str, Any]:
        """Get dashboard status data"""
        db_path = Path.home() / ".clyrdia" / "clyrdia.db"
        if not db_path.exists():
            return {
                "status": "no_data",
                "message": "No benchmark data found",
                "database_exists": False,
                "total_results": 0,
                "total_models": 0,
                "total_tests": 0
            }
        
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Check if tables exist first
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='benchmark_results'")
            if not cursor.fetchone():
                conn.close()
                return {
                    "status": "no_data",
                    "message": "Database exists but no benchmark tables found",
                    "database_exists": True,
                    "total_results": 0,
                    "total_models": 0,
                    "total_tests": 0
                }
            
            # Get basic stats with safe defaults
            cursor.execute("SELECT COUNT(*) FROM benchmark_results")
            total_results = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT COUNT(DISTINCT model) FROM benchmark_results")
            total_models = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT COUNT(DISTINCT test_name) FROM benchmark_results")
            total_tests = cursor.fetchone()[0] or 0
            
            conn.close()
            
            return {
                "status": "ready",
                "database_exists": True,
                "total_results": total_results,
                "total_models": total_models,
                "total_tests": total_tests
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "database_exists": True,
                "total_results": 0,
                "total_models": 0,
                "total_tests": 0
            }
    
    def get_metrics_data(self) -> Dict[str, Any]:
        """Get metrics data"""
        db_path = Path.home() / ".clyrdia" / "clyrdia.db"
        if not db_path.exists():
            return {"error": "Database not found", "recent_benchmarks": [], "total_count": 0}
        
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Check if table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='benchmark_results'")
            if not cursor.fetchone():
                conn.close()
                return {"error": "No benchmark data available", "recent_benchmarks": [], "total_count": 0}
            
            # Get recent benchmarks with safe column names
            cursor.execute("""
                SELECT test_name, model, quality_score, cost, timestamp
                FROM benchmark_results
                ORDER BY timestamp DESC
                LIMIT 10
            """)
            
            recent_benchmarks = []
            for row in cursor.fetchall():
                recent_benchmarks.append({
                    "test_name": row[0] or "Unknown Test",
                    "model_name": row[1] or "Unknown Model",
                    "quality_score": row[2] or 0.0,
                    "total_cost": row[3] or 0.0,
                    "timestamp": row[4] or "Unknown"
                })
            
            conn.close()
            
            return {
                "recent_benchmarks": recent_benchmarks,
                "total_count": len(recent_benchmarks)
            }
        except Exception as e:
            return {"error": str(e), "recent_benchmarks": [], "total_count": 0}
    
    def get_benchmarks_data(self) -> Dict[str, Any]:
        """Get benchmarks data"""
        return self.get_metrics_data()
    
    def get_models_data(self) -> Dict[str, Any]:
        """Get models data"""
        db_path = Path.home() / ".clyrdia" / "clyrdia.db"
        if not db_path.exists():
            return {"error": "Database not found", "models": []}
        
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Check if table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='benchmark_results'")
            if not cursor.fetchone():
                conn.close()
                return {"error": "No benchmark data available", "models": []}
            
            # Get model performance with safe column names
            cursor.execute("""
                SELECT model, AVG(quality_score) as avg_score, COUNT(*) as test_count
                FROM benchmark_results
                GROUP BY model
                ORDER BY avg_score DESC
            """)
            
            models = []
            for row in cursor.fetchall():
                models.append({
                    "model_name": row[0] or "Unknown Model",
                    "avg_score": round(row[1], 3) if row[1] else 0,
                    "test_count": row[2] or 0
                })
            
            conn.close()
            
            return {"models": models}
        except Exception as e:
            return {"error": str(e), "models": []}
    
    def get_costs_data(self) -> Dict[str, Any]:
        """Get costs data"""
        db_path = Path.home() / ".clyrdia" / "clyrdia.db"
        if not db_path.exists():
            return {"error": "Database not found", "total_cost": 0, "avg_cost": 0, "total_tests": 0}
        
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Check if table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='benchmark_results'")
            if not cursor.fetchone():
                conn.close()
                return {"error": "No benchmark data available", "total_cost": 0, "avg_cost": 0, "total_tests": 0}
            
            # Get cost summary with safe column names
            cursor.execute("""
                SELECT 
                    SUM(cost) as total_cost,
                    AVG(cost) as avg_cost,
                    COUNT(*) as total_tests
                FROM benchmark_results
            """)
            
            row = cursor.fetchone()
            if row:
                cost_data = {
                    "total_cost": round(row[0], 4) if row[0] else 0,
                    "avg_cost": round(row[1], 4) if row[1] else 0,
                    "total_tests": row[2] or 0
                }
            else:
                cost_data = {"total_cost": 0, "avg_cost": 0, "total_tests": 0}
            
            conn.close()
            
            return cost_data
        except Exception as e:
            return {"error": str(e), "total_cost": 0, "avg_cost": 0, "total_tests": 0}
    
    def handle_export_request(self, query_string: str):
        """Handle data export requests"""
        try:
            from urllib.parse import parse_qs
            params = parse_qs(query_string)
            format_type = params.get('format', ['json'])[0]
            
            if format_type == 'csv':
                self.send_csv_export()
            elif format_type == 'json':
                self.send_json_export()
            elif format_type == 'excel':
                self.send_excel_export()
            else:
                self.send_error(400, "Unsupported format")
        except Exception as e:
            self.send_error(500, f"Export error: {str(e)}")
    
    def send_csv_export(self):
        """Send CSV export of all benchmark data"""
        try:
            db_path = Path.home() / ".clyrdia" / "clyrdia.db"
            if not db_path.exists():
                self.send_error(404, "No data to export")
                return
            
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Get all benchmark results
            cursor.execute("""
                SELECT model, test_name, prompt, response, quality_score, 
                       latency_ms, cost, input_tokens, output_tokens, 
                       success, error, timestamp
                FROM benchmark_results
                ORDER BY timestamp DESC
            """)
            
            results = cursor.fetchall()
            conn.close()
            
            # Generate CSV
            csv_data = "Model,Test Name,Quality Score,Latency (ms),Cost ($),Input Tokens,Output Tokens,Success,Error,Timestamp\n"
            for row in results:
                csv_data += f'"{row[0]}","{row[1]}",{row[4]},{row[5]},{row[6]},{row[7]},{row[8]},{row[9]},"{row[10] or ""}","{row[11]}"\n'
            
            self.send_response(200)
            self.send_header("Content-type", "text/csv")
            self.send_header("Content-Disposition", "attachment; filename=clyrdia_benchmark_data.csv")
            self.end_headers()
            self.wfile.write(csv_data.encode())
            
        except Exception as e:
            self.send_error(500, f"CSV export error: {str(e)}")
    
    def send_json_export(self):
        """Send JSON export of all benchmark data"""
        try:
            db_path = Path.home() / ".clyrdia" / "clyrdia.db"
            if not db_path.exists():
                self.send_error(404, "No data to export")
                return
            
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Get all benchmark results
            cursor.execute("""
                SELECT model, test_name, prompt, response, quality_score, 
                       latency_ms, cost, input_tokens, output_tokens, 
                       success, error, timestamp
                FROM benchmark_results
                ORDER BY timestamp DESC
            """)
            
            results = cursor.fetchall()
            conn.close()
            
            # Convert to JSON
            export_data = {
                "export_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_results": len(results),
                "benchmark_results": []
            }
            
            for row in results:
                export_data["benchmark_results"].append({
                    "model": row[0],
                    "test_name": row[1],
                    "prompt": row[2],
                    "response": row[3],
                    "quality_score": row[4],
                    "latency_ms": row[5],
                    "cost": row[6],
                    "input_tokens": row[7],
                    "output_tokens": row[8],
                    "success": bool(row[9]),
                    "error": row[10],
                    "timestamp": row[11]
                })
            
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Content-Disposition", "attachment; filename=clyrdia_benchmark_data.json")
            self.end_headers()
            self.wfile.write(json.dumps(export_data, indent=2).encode())
            
        except Exception as e:
            self.send_error(500, f"JSON export error: {str(e)}")
    
    def send_excel_export(self):
        """Send Excel export of all benchmark data"""
        try:
            # For now, send CSV as Excel (can be enhanced with openpyxl later)
            self.send_csv_export()
        except Exception as e:
            self.send_error(500, f"Excel export error: {str(e)}")
    
    def get_detailed_results(self) -> Dict[str, Any]:
        """Get detailed benchmark results with full data"""
        db_path = Path.home() / ".clyrdia" / "clyrdia.db"
        if not db_path.exists():
            return {"error": "Database not found", "results": []}
        
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Check if table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='benchmark_results'")
            if not cursor.fetchone():
                conn.close()
                return {"error": "No benchmark data available", "results": []}
            
            # Get detailed results
            cursor.execute("""
                SELECT model, test_name, prompt, response, quality_score, 
                       latency_ms, cost, input_tokens, output_tokens, 
                       success, error, timestamp
                FROM benchmark_results
                ORDER BY timestamp DESC
                LIMIT 100
            """)
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    "model": row[0],
                    "test_name": row[1],
                    "prompt": row[2][:200] + "..." if len(row[2]) > 200 else row[2],  # Truncate long prompts
                    "response": row[3][:200] + "..." if len(row[3]) > 200 else row[3],  # Truncate long responses
                    "quality_score": row[4],
                    "latency_ms": row[5],
                    "cost": row[6],
                    "input_tokens": row[7],
                    "output_tokens": row[8],
                    "success": bool(row[9]),
                    "error": row[10],
                    "timestamp": row[11]
                })
            
            conn.close()
            
            return {"results": results, "total_count": len(results)}
        except Exception as e:
            return {"error": str(e), "results": []}
    
    def get_performance_trends(self) -> Dict[str, Any]:
        """Get performance trends over time"""
        db_path = Path.home() / ".clyrdia" / "clyrdia.db"
        if not db_path.exists():
            return {"error": "Database not found", "trends": []}
        
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Check if table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='benchmark_results'")
            if not cursor.fetchone():
                conn.close()
                return {"error": "No benchmark data available", "trends": []}
            
            # Get trends by date
            cursor.execute("""
                SELECT DATE(timestamp) as date, 
                       AVG(quality_score) as avg_quality,
                       AVG(latency_ms) as avg_latency,
                       SUM(cost) as total_cost,
                       COUNT(*) as test_count
                FROM benchmark_results
                WHERE success = 1
                GROUP BY DATE(timestamp)
                ORDER BY date DESC
                LIMIT 30
            """)
            
            trends = []
            for row in cursor.fetchall():
                trends.append({
                    "date": row[0],
                    "avg_quality": round(row[1], 3) if row[1] else 0,
                    "avg_latency": round(row[2], 2) if row[2] else 0,
                    "total_cost": round(row[3], 4) if row[3] else 0,
                    "test_count": row[4]
                })
            
            conn.close()
            
            return {"trends": trends}
        except Exception as e:
            return {"error": str(e), "trends": []}
    
    def get_model_comparison(self) -> Dict[str, Any]:
        """Get detailed model comparison data"""
        db_path = Path.home() / ".clyrdia" / "clyrdia.db"
        if not db_path.exists():
            return {"error": "Database not found", "comparison": []}
        
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Check if table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='benchmark_results'")
            if not cursor.fetchone():
                conn.close()
                return {"error": "No benchmark data available", "comparison": []}
            
            # Get model comparison data
            cursor.execute("""
                SELECT model,
                       COUNT(*) as total_tests,
                       AVG(quality_score) as avg_quality,
                       AVG(latency_ms) as avg_latency,
                       SUM(cost) as total_cost,
                       AVG(cost) as avg_cost,
                       SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_tests
                FROM benchmark_results
                GROUP BY model
                ORDER BY avg_quality DESC
            """)
            
            comparison = []
            for row in cursor.fetchall():
                success_rate = (row[6] / row[1]) * 100 if row[1] > 0 else 0
                comparison.append({
                    "model": row[0],
                    "total_tests": row[1],
                    "avg_quality": round(row[2], 3) if row[2] else 0,
                    "avg_latency": round(row[3], 2) if row[3] else 0,
                    "total_cost": round(row[4], 4) if row[4] else 0,
                    "avg_cost": round(row[5], 4) if row[5] else 0,
                    "success_rate": round(success_rate, 1)
                })
            
            conn.close()
            
            return {"comparison": comparison}
        except Exception as e:
            return {"error": str(e), "comparison": []}
    
    def generate_dashboard_html(self) -> str:
        """Generate the dashboard HTML page"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Clyrdia Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            text-align: center;
            margin-bottom: 40px;
            color: white;
        }
        
        .header h1 {
            font-size: 3rem;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .header p {
            font-size: 1.2rem;
            opacity: 0.9;
        }
        
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }
        
        .card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 20px 40px rgba(0,0,0,0.15);
        }
        
        .card h2 {
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.5rem;
        }
        
        .metric {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 0;
            border-bottom: 1px solid #eee;
        }
        
        .metric:last-child {
            border-bottom: none;
        }
        
        .metric-label {
            font-weight: 500;
            color: #666;
        }
        
        .metric-value {
            font-weight: bold;
            color: #333;
            font-size: 1.1rem;
        }
        
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        
        .status-online {
            background: #4CAF50;
        }
        
        .status-offline {
            background: #f44336;
        }
        
        .refresh-btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 1rem;
            transition: background 0.3s ease;
            margin-bottom: 20px;
        }
        
        .refresh-btn:hover {
            background: #5a6fd8;
        }
        
        .loading {
            text-align: center;
            padding: 40px;
            color: #666;
        }
        
        .error {
            background: #ffebee;
            color: #c62828;
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
        }
        
        .success {
            background: #e8f5e8;
            color: #2e7d32;
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
        }
        
        .export-buttons {
            margin-top: 20px;
            display: flex;
            gap: 10px;
            justify-content: center;
            flex-wrap: wrap;
        }
        
        .export-btn {
            background: #28a745;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 20px;
            cursor: pointer;
            font-size: 0.9rem;
            transition: background 0.3s ease;
        }
        
        .export-btn:hover {
            background: #218838;
        }
        
        .controls {
            display: flex;
            gap: 10px;
            justify-content: center;
            margin-bottom: 20px;
        }
        
        .advanced-section {
            display: none;
            margin-top: 30px;
        }
        
        .advanced-section.show {
            display: block;
        }
        
        .chart-container {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        
        .chart-title {
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.3rem;
        }
        
        .data-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }
        
        .data-table th,
        .data-table td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }
        
        .data-table th {
            background: #f8f9fa;
            font-weight: 600;
            color: #495057;
        }
        
        .data-table tr:hover {
            background: #f8f9fa;
        }
        
        .metric-card {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
            border-left: 4px solid #667eea;
        }
        
        .metric-card h4 {
            margin: 0 0 10px 0;
            color: #495057;
        }
        
        .metric-card .value {
            font-size: 1.5rem;
            font-weight: bold;
            color: #667eea;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Clyrdia Dashboard</h1>
            <p>AI Benchmarking & Performance Analytics</p>
            <div class="export-buttons">
                <button class="export-btn" onclick="exportData('csv')">📊 Export CSV</button>
                <button class="export-btn" onclick="exportData('json')">📋 Export JSON</button>
                <button class="export-btn" onclick="exportData('excel')">📈 Export Excel</button>
            </div>
        </div>
        
        <div class="controls">
            <button class="refresh-btn" onclick="refreshData()">🔄 Refresh Data</button>
            <button class="refresh-btn" onclick="toggleAdvancedView()">🔍 Advanced View</button>
        </div>
        
        <div class="dashboard-grid">
            <div class="card">
                <h2>📊 System Status</h2>
                <div id="status-content">
                    <div class="loading">Loading...</div>
                </div>
            </div>
            
            <div class="card">
                <h2>🤖 Model Performance</h2>
                <div id="models-content">
                    <div class="loading">Loading...</div>
                </div>
            </div>
            
            <div class="card">
                <h2>💰 Cost Analysis</h2>
                <div id="costs-content">
                    <div class="loading">Loading...</div>
                </div>
            </div>
            
            <div class="card">
                <h2>📈 Recent Benchmarks</h2>
                <div id="benchmarks-content">
                    <div class="loading">Loading...</div>
                </div>
            </div>
        </div>
        
        <!-- Advanced Analytics Section -->
        <div class="advanced-section" id="advanced-section">
            <div class="chart-container">
                <h2 class="chart-title">📈 Performance Trends</h2>
                <div id="trends-content">
                    <div class="loading">Loading trends...</div>
                </div>
            </div>
            
            <div class="chart-container">
                <h2 class="chart-title">🤖 Model Comparison</h2>
                <div id="comparison-content">
                    <div class="loading">Loading comparison...</div>
                </div>
            </div>
            
            <div class="chart-container">
                <h2 class="chart-title">📋 Detailed Results</h2>
                <div id="detailed-content">
                    <div class="loading">Loading detailed results...</div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Load data on page load
        document.addEventListener('DOMContentLoaded', function() {
            loadAllData();
        });
        
        function loadAllData() {
            loadStatus();
            loadModels();
            loadCosts();
            loadBenchmarks();
            
            // Load advanced data if advanced view is shown
            if (document.getElementById('advanced-section').classList.contains('show')) {
                loadTrends();
                loadComparison();
                loadDetailedResults();
            }
        }
        
        function refreshData() {
            // Show loading state
            document.querySelectorAll('.loading').forEach(el => {
                el.style.display = 'block';
            });
            
            // Clear previous content
            document.getElementById('status-content').innerHTML = '<div class="loading">Refreshing...</div>';
            document.getElementById('models-content').innerHTML = '<div class="loading">Refreshing...</div>';
            document.getElementById('costs-content').innerHTML = '<div class="loading">Refreshing...</div>';
            document.getElementById('benchmarks-content').innerHTML = '<div class="loading">Refreshing...</div>';
            
            // Load fresh data
            loadAllData();
            
            // Show success message
            setTimeout(() => {
                const refreshBtn = document.querySelector('.refresh-btn');
                const originalText = refreshBtn.textContent;
                refreshBtn.textContent = '✅ Refreshed!';
                refreshBtn.style.background = '#4CAF50';
                
                setTimeout(() => {
                    refreshBtn.textContent = originalText;
                    refreshBtn.style.background = '#667eea';
                }, 2000);
            }, 500);
        }
        
        async function loadStatus() {
            try {
                const response = await fetch('/api/status');
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                const data = await response.json();
                displayStatus(data);
            } catch (error) {
                console.error('Status load error:', error);
                document.getElementById('status-content').innerHTML = `
                    <div class="error">
                        <strong>Error loading status:</strong><br>
                        ${error.message}<br>
                        <small>Try refreshing the page or restarting the dashboard</small>
                    </div>
                `;
            }
        }
        
        async function loadModels() {
            try {
                const response = await fetch('/api/models');
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                const data = await response.json();
                displayModels(data);
            } catch (error) {
                console.error('Models load error:', error);
                document.getElementById('models-content').innerHTML = `
                    <div class="error">
                        <strong>Error loading models:</strong><br>
                        ${error.message}<br>
                        <small>Try refreshing the page or restarting the dashboard</small>
                    </div>
                `;
            }
        }
        
        async function loadCosts() {
            try {
                const response = await fetch('/api/costs');
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                const data = await response.json();
                displayCosts(data);
            } catch (error) {
                console.error('Costs load error:', error);
                document.getElementById('costs-content').innerHTML = `
                    <div class="error">
                        <strong>Error loading costs:</strong><br>
                        ${error.message}<br>
                        <small>Try refreshing the page or restarting the dashboard</small>
                    </div>
                `;
            }
        }
        
        async function loadBenchmarks() {
            try {
                const response = await fetch('/api/benchmarks');
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                const data = await response.json();
                displayBenchmarks(data);
            } catch (error) {
                console.error('Benchmarks load error:', error);
                document.getElementById('benchmarks-content').innerHTML = `
                    <div class="error">
                        <strong>Error loading benchmarks:</strong><br>
                        ${error.message}<br>
                        <small>Try refreshing the page or restarting the dashboard</small>
                    </div>
                `;
            }
        }
        
        function displayStatus(data) {
            const content = document.getElementById('status-content');
            
            if (data.error) {
                content.innerHTML = `<div class="error">${data.error}</div>`;
                return;
            }
            
            if (data.status === 'no_data') {
                content.innerHTML = `
                    <div class="metric">
                        <span class="metric-label">Status</span>
                        <span class="metric-value"><span class="status-indicator status-offline"></span>No Data</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Database</span>
                        <span class="metric-value">Not Found</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Message</span>
                        <span class="metric-value">Run your first benchmark</span>
                    </div>
                `;
            } else {
                content.innerHTML = `
                    <div class="metric">
                        <span class="metric-label">Status</span>
                        <span class="metric-value"><span class="status-indicator status-online"></span>Ready</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Total Results</span>
                        <span class="metric-value">${data.total_results}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Models Tested</span>
                        <span class="metric-value">${data.total_models}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Tests Run</span>
                        <span class="metric-value">${data.total_tests}</span>
                    </div>
                `;
            }
        }
        
        function displayModels(data) {
            const content = document.getElementById('models-content');
            
            if (data.error) {
                content.innerHTML = `<div class="error">${data.error}</div>`;
                return;
            }
            
            if (!data.models || data.models.length === 0) {
                content.innerHTML = '<div class="success">No models tested yet</div>';
                return;
            }
            
            let html = '';
            data.models.forEach(model => {
                html += `
                    <div class="metric">
                        <span class="metric-label">${model.model_name}</span>
                        <span class="metric-value">${model.avg_score} (${model.test_count} tests)</span>
                    </div>
                `;
            });
            
            content.innerHTML = html;
        }
        
        function displayCosts(data) {
            const content = document.getElementById('costs-content');
            
            if (data.error) {
                content.innerHTML = `<div class="error">${data.error}</div>`;
                return;
            }
            
            content.innerHTML = `
                <div class="metric">
                    <span class="metric-label">Total Cost</span>
                    <span class="metric-value">$${data.total_cost}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Average Cost</span>
                    <span class="metric-value">$${data.avg_cost}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Total Tests</span>
                    <span class="metric-value">${data.total_tests}</span>
                </div>
            `;
        }
        
        function displayBenchmarks(data) {
            const content = document.getElementById('benchmarks-content');
            
            if (data.error) {
                content.innerHTML = `<div class="error">${data.error}</div>`;
                return;
            }
            
            if (!data.recent_benchmarks || data.recent_benchmarks.length === 0) {
                content.innerHTML = '<div class="success">No benchmarks run yet</div>';
                return;
            }
            
            let html = '';
            data.recent_benchmarks.slice(0, 5).forEach(benchmark => {
                html += `
                    <div class="metric">
                        <span class="metric-label">${benchmark.test_name}</span>
                        <span class="metric-value">${benchmark.model_name}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Score</span>
                        <span class="metric-value">${benchmark.quality_score}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Cost</span>
                        <span class="metric-value">$${benchmark.total_cost}</span>
                    </div>
                `;
            });
            
            content.innerHTML = html;
        }
        
        function toggleAdvancedView() {
            const advancedSection = document.getElementById('advanced-section');
            const button = event.target;
            
            if (advancedSection.classList.contains('show')) {
                advancedSection.classList.remove('show');
                button.textContent = '🔍 Advanced View';
            } else {
                advancedSection.classList.add('show');
                button.textContent = '🔍 Hide Advanced';
                loadTrends();
                loadComparison();
                loadDetailedResults();
            }
        }
        
        function exportData(format) {
            const url = `/api/export?format=${format}`;
            const link = document.createElement('a');
            link.href = url;
            link.download = `clyrdia_benchmark_data.${format}`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
        
        async function loadTrends() {
            try {
                const response = await fetch('/api/performance-trends');
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                const data = await response.json();
                displayTrends(data);
            } catch (error) {
                console.error('Trends load error:', error);
                document.getElementById('trends-content').innerHTML = `
                    <div class="error">
                        <strong>Error loading trends:</strong><br>
                        ${error.message}
                    </div>
                `;
            }
        }
        
        async function loadComparison() {
            try {
                const response = await fetch('/api/model-comparison');
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                const data = await response.json();
                displayComparison(data);
            } catch (error) {
                console.error('Comparison load error:', error);
                document.getElementById('comparison-content').innerHTML = `
                    <div class="error">
                        <strong>Error loading comparison:</strong><br>
                        ${error.message}
                    </div>
                `;
            }
        }
        
        async function loadDetailedResults() {
            try {
                const response = await fetch('/api/detailed-results');
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                const data = await response.json();
                displayDetailedResults(data);
            } catch (error) {
                console.error('Detailed results load error:', error);
                document.getElementById('detailed-content').innerHTML = `
                    <div class="error">
                        <strong>Error loading detailed results:</strong><br>
                        ${error.message}
                    </div>
                `;
            }
        }
        
        function displayTrends(data) {
            const content = document.getElementById('trends-content');
            
            if (data.error) {
                content.innerHTML = `<div class="error">${data.error}</div>`;
                return;
            }
            
            if (!data.trends || data.trends.length === 0) {
                content.innerHTML = '<div class="success">No trend data available</div>';
                return;
            }
            
            let html = '<table class="data-table"><thead><tr><th>Date</th><th>Avg Quality</th><th>Avg Latency</th><th>Total Cost</th><th>Tests</th></tr></thead><tbody>';
            
            data.trends.forEach(trend => {
                html += `
                    <tr>
                        <td>${trend.date}</td>
                        <td>${trend.avg_quality}</td>
                        <td>${trend.avg_latency}ms</td>
                        <td>$${trend.total_cost}</td>
                        <td>${trend.test_count}</td>
                    </tr>
                `;
            });
            
            html += '</tbody></table>';
            content.innerHTML = html;
        }
        
        function displayComparison(data) {
            const content = document.getElementById('comparison-content');
            
            if (data.error) {
                content.innerHTML = `<div class="error">${data.error}</div>`;
                return;
            }
            
            if (!data.comparison || data.comparison.length === 0) {
                content.innerHTML = '<div class="success">No comparison data available</div>';
                return;
            }
            
            let html = '<table class="data-table"><thead><tr><th>Model</th><th>Tests</th><th>Avg Quality</th><th>Avg Latency</th><th>Total Cost</th><th>Success Rate</th></tr></thead><tbody>';
            
            data.comparison.forEach(model => {
                html += `
                    <tr>
                        <td><strong>${model.model}</strong></td>
                        <td>${model.total_tests}</td>
                        <td>${model.avg_quality}</td>
                        <td>${model.avg_latency}ms</td>
                        <td>$${model.total_cost}</td>
                        <td>${model.success_rate}%</td>
                    </tr>
                `;
            });
            
            html += '</tbody></table>';
            content.innerHTML = html;
        }
        
        function displayDetailedResults(data) {
            const content = document.getElementById('detailed-content');
            
            if (data.error) {
                content.innerHTML = `<div class="error">${data.error}</div>`;
                return;
            }
            
            if (!data.results || data.results.length === 0) {
                content.innerHTML = '<div class="success">No detailed results available</div>';
                return;
            }
            
            let html = '<table class="data-table"><thead><tr><th>Model</th><th>Test</th><th>Quality</th><th>Latency</th><th>Cost</th><th>Success</th><th>Time</th></tr></thead><tbody>';
            
            data.results.forEach(result => {
                html += `
                    <tr>
                        <td>${result.model}</td>
                        <td>${result.test_name}</td>
                        <td>${result.quality_score}</td>
                        <td>${result.latency_ms}ms</td>
                        <td>$${result.cost}</td>
                        <td>${result.success ? '✅' : '❌'}</td>
                        <td>${result.timestamp}</td>
                    </tr>
                `;
            });
            
            html += '</tbody></table>';
            content.innerHTML = html;
        }
        
        // Auto-refresh every 30 seconds
        setInterval(loadAllData, 30000);
    </script>
</body>
</html>
        """

class SimpleDashboard:
    """Simple dashboard server that works on any platform"""
    
    def __init__(self, host: str = "localhost", port: int = 3000):
        self.host = host
        self.port = port
        self.server = None
        self.thread = None
    
    def is_dashboard_running(self) -> bool:
        """Check if dashboard is running on the specified port"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex((self.host, self.port))
                return result == 0
        except Exception:
            return False
    
    def start_dashboard(self):
        """Start the simple HTTP dashboard server"""
        if self.is_dashboard_running():
            console.print(f"[green]✅ Dashboard is already running on port {self.port}[/green]")
            return True
        
        try:
            # Start HTTP server in a separate thread
            self.server = HTTPServer((self.host, self.port), SimpleDashboardHandler)
            self.thread = threading.Thread(target=self.server.serve_forever, daemon=False)
            self.thread.start()
            
            # Wait a moment for server to start
            time.sleep(2)
            
            if self.is_dashboard_running():
                console.print(f"[green]✅ Simple Dashboard started successfully on port {self.port}[/green]")
                console.print(f"[dim]💡 Dashboard will continue running in the background[/dim]")
                console.print(f"[dim]💡 You can close this terminal and dashboard will remain accessible[/dim]")
                return True
            else:
                console.print(f"[red]❌ Failed to start dashboard on port {self.port}[/red]")
                return False
                
        except Exception as e:
            console.print(f"[red]❌ Error starting dashboard: {str(e)}[/red]")
            return False
    
    def stop_dashboard(self):
        """Stop the dashboard server"""
        if self.server:
            self.server.shutdown()
            self.server = None
            console.print(f"[yellow]🛑 Dashboard stopped on port {self.port}[/yellow]")
        else:
            console.print(f"[yellow]🛑 No dashboard found running on port {self.port}[/yellow]")
    
    def open_dashboard_url(self):
        """Show the dashboard URL for user to click"""
        url = f"http://{self.host}:{self.port}"
        console.print(f"[green]🌐 Dashboard is ready![/green]")
        console.print(f"[blue]🔗 Dashboard URL: {url}[/blue]")
        console.print("[yellow]💡 To access your dashboard:[/yellow]")
        console.print(f"[yellow]   1. Copy this URL:[/yellow] [bold blue]{url}[/bold blue]")
        console.print("[yellow]   2. Paste it into your web browser[/yellow]")
        console.print(f"[yellow]   3. Or run:[/yellow] [bold]open {url}[/bold]")
        console.print(f"[dim]💡 If the link doesn't work, manually copy: {url}[/dim]")
        
        # Try to open the dashboard in the default browser
        try:
            webbrowser.open(url)
            console.print("[green]✅ Opened dashboard in your default browser![/green]")
        except Exception as e:
            console.print(f"[yellow]⚠️  Couldn't auto-open browser: {str(e)}[/yellow]")
            console.print(f"[yellow]   Please manually copy and paste: {url}[/yellow]")
        
        console.print(f"\n[dim]💡 Dashboard is now running in the background on port {self.port}[/dim]")
        console.print(f"[dim]💡 You can run other commands while the dashboard continues running[/dim]")
    
    def show_dashboard_instructions(self):
        """Display dashboard information"""
        console.print()
        
        if self.is_dashboard_running():
            self.open_dashboard_url()
        else:
            console.print(Panel.fit(
                "[bold yellow]⚠️  Dashboard not running[/bold yellow]\n\n"
                "Starting simple dashboard...",
                border_style="yellow",
                padding=(1, 2),
                title="[bold]Starting Dashboard[/bold]"
            ))
            
            if self.start_dashboard():
                self.open_dashboard_url()
            else:
                console.print("[red]❌ Failed to start dashboard[/red]")
    
    def check_dashboard_status(self):
        """Check and display dashboard status"""
        console.print()
        
        if self.is_dashboard_running():
            self.open_dashboard_url()
        else:
            console.print(Panel.fit(
                f"[yellow]⚠️  Dashboard is not running on port {self.port}[/yellow]\n\n"
                "Starting dashboard...",
                border_style="yellow",
                title="[bold]Dashboard Status[/bold]"
            ))
            
            if self.start_dashboard():
                self.check_dashboard_status()
            else:
                console.print("[red]❌ Failed to start dashboard[/red]")
    
    def migrate_data(self):
        """Provide instructions for data migration"""
        console.print()
        
        console.print(Panel.fit(
            "[bold bright_cyan]🔄 Data Migration[/bold bright_cyan]\n\n"
            "Your existing benchmark data is automatically compatible with the dashboard!\n\n"
            "[bold]The dashboard will:[/bold]\n"
            "• 📊 Show all your historical results\n"
            "• 🤖 Compare model performance over time\n"
            "• 💰 Track cost trends and optimization\n"
            "• 📈 Provide insights and analytics\n\n"
            "[bold]No manual migration needed:[/bold]\n"
            "• Just run benchmarks normally\n"
            "• Data appears automatically in the dashboard\n"
            "• Real-time updates as you test\n\n"
            "🚀 Start benchmarking and see your data in the dashboard!",
            border_style="bright_cyan",
            title="[bold]Data Migration Guide[/bold]"
        ))

# Create a global dashboard instance
dashboard = SimpleDashboard()

# Export functions for CLI use
def start_dashboard():
    """Start the dashboard"""
    return dashboard.start_dashboard()

def stop_dashboard():
    """Stop the dashboard"""
    return dashboard.stop_dashboard()

def check_dashboard_status():
    """Check dashboard status"""
    return dashboard.check_dashboard_status()

def show_dashboard_instructions():
    """Show dashboard instructions"""
    return dashboard.show_dashboard_instructions()

def open_dashboard_url():
    """Open dashboard URL"""
    return dashboard.open_dashboard_url()

def migrate_data():
    """Show data migration info"""
    return dashboard.migrate_data()

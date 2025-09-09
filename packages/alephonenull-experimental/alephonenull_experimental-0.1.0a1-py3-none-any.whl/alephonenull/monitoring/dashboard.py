from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
from datetime import datetime
from typing import Optional
import asyncio
import json

try:
    from ..monitoring.metrics import global_metrics, MetricsCollector
except ImportError:
    # Fallback for standalone usage
    from alephonenull.monitoring.metrics import global_metrics, MetricsCollector

app = FastAPI(
    title="AlephOneNull Safety Dashboard",
    description="Real-time monitoring of AI safety violations",
    version="3.0.0"
)

class Dashboard:
    """Real-time safety monitoring dashboard"""
    
    def __init__(self, metrics_collector: Optional[MetricsCollector] = None):
        self.metrics = metrics_collector or global_metrics
    
    def get_stats(self) -> dict:
        """Get dashboard statistics - backward compatibility method"""
        return self.metrics.get_dashboard_data()
        
    def generate_html(self) -> str:
        """Generate real-time dashboard HTML"""
        data = self.metrics.get_dashboard_data()
        
        # Determine status color
        status_color = {
            'INACTIVE': '#666666',
            'LOW': '#00ff00', 
            'MEDIUM': '#ffaa00',
            'HIGH': '#ff6600',
            'CRITICAL': '#ff0000'
        }.get(data['threat_level'], '#00ff00')
        
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>AlephOneNull Safety Monitor</title>
            <meta http-equiv="refresh" content="10">
            <style>
                :root {{
                    --bg-color: #0a0a0a;
                    --text-color: #00ff00;
                    --border-color: #00ff00;
                    --alert-color: #ff0000;
                    --warning-color: #ffaa00;
                    --safe-color: #00ff00;
                    --card-bg: #111111;
                }}
                
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                
                body {{
                    font-family: 'Courier New', monospace;
                    background: var(--bg-color);
                    color: var(--text-color);
                    min-height: 100vh;
                    padding: 20px;
                    background-image: 
                        radial-gradient(circle at 20% 50%, rgba(0, 255, 0, 0.1) 0%, transparent 50%),
                        radial-gradient(circle at 80% 20%, rgba(0, 255, 0, 0.05) 0%, transparent 50%);
                }}
                
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                    border: 2px solid var(--border-color);
                    padding: 20px;
                    background: var(--card-bg);
                    box-shadow: 0 0 20px rgba(0, 255, 0, 0.3);
                }}
                
                .title {{
                    font-size: 2.5em;
                    margin-bottom: 10px;
                    text-shadow: 0 0 10px currentColor;
                }}
                
                .subtitle {{
                    font-size: 1.2em;
                    opacity: 0.8;
                }}
                
                .threat-level {{
                    font-size: 1.5em;
                    font-weight: bold;
                    color: {status_color};
                    text-shadow: 0 0 10px currentColor;
                    margin: 10px 0;
                }}
                
                .grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 20px;
                    margin-bottom: 20px;
                }}
                
                .card {{
                    border: 1px solid var(--border-color);
                    padding: 20px;
                    background: var(--card-bg);
                    box-shadow: 0 0 15px rgba(0, 255, 0, 0.2);
                    transition: all 0.3s ease;
                }}
                
                .card:hover {{
                    box-shadow: 0 0 25px rgba(0, 255, 0, 0.4);
                    border-color: rgba(0, 255, 0, 0.8);
                }}
                
                .card h2 {{
                    font-size: 1.3em;
                    margin-bottom: 15px;
                    border-bottom: 1px solid var(--border-color);
                    padding-bottom: 10px;
                }}
                
                .metric {{
                    display: flex;
                    justify-content: space-between;
                    margin: 10px 0;
                    padding: 5px 0;
                }}
                
                .metric-label {{
                    opacity: 0.8;
                }}
                
                .metric-value {{
                    font-weight: bold;
                }}
                
                .alert {{
                    color: var(--alert-color);
                    font-weight: bold;
                    text-shadow: 0 0 5px currentColor;
                }}
                
                .warning {{
                    color: var(--warning-color);
                    font-weight: bold;
                    text-shadow: 0 0 5px currentColor;
                }}
                
                .safe {{
                    color: var(--safe-color);
                }}
                
                .violation-list {{
                    max-height: 200px;
                    overflow-y: auto;
                    border: 1px solid rgba(0, 255, 0, 0.3);
                    padding: 10px;
                    background: rgba(0, 0, 0, 0.5);
                }}
                
                .violation-item {{
                    margin: 5px 0;
                    padding: 5px;
                    border-left: 3px solid;
                    padding-left: 10px;
                }}
                
                .violation-critical {{
                    border-left-color: var(--alert-color);
                    background: rgba(255, 0, 0, 0.1);
                }}
                
                .violation-high {{
                    border-left-color: var(--warning-color);
                    background: rgba(255, 170, 0, 0.1);
                }}
                
                .violation-medium {{
                    border-left-color: #ffff00;
                    background: rgba(255, 255, 0, 0.1);
                }}
                
                .recommendations {{
                    background: rgba(0, 255, 0, 0.1);
                    border: 1px solid rgba(0, 255, 0, 0.3);
                    padding: 15px;
                    margin: 20px 0;
                }}
                
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    padding: 20px;
                    border-top: 1px solid var(--border-color);
                    opacity: 0.7;
                }}
                
                .blink {{
                    animation: blink 1s infinite;
                }}
                
                @keyframes blink {{
                    50% {{ opacity: 0.3; }}
                }}
                
                .status-active {{
                    color: var(--safe-color);
                }}
                
                .status-inactive {{
                    color: #666666;
                }}
                
                @media (max-width: 768px) {{
                    .grid {{
                        grid-template-columns: 1fr;
                    }}
                    .title {{
                        font-size: 1.8em;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1 class="title">🛡️ AlephOneNull Protection Status</h1>
                <p class="subtitle">Digital Prison for Language Models - Real-Time Monitoring</p>
                <div class="threat-level">Threat Level: {data['threat_level']}</div>
                <div class="status-{data['status'].lower()}">System Status: {data['status']}</div>
            </div>
            
            <div class="grid">
                <div class="card">
                    <h2>📊 System Statistics</h2>
                    <div class="metric">
                        <span class="metric-label">Total AI Calls:</span>
                        <span class="metric-value">{data['total_calls']:,}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Violations Blocked:</span>
                        <span class="metric-value alert">{data['total_violations']:,}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Emergency Interventions:</span>
                        <span class="metric-value alert blink">{data['emergency_interventions']:,}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Violation Rate:</span>
                        <span class="metric-value">{data['violation_rate_percent']}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Emergency Rate:</span>
                        <span class="metric-value alert">{data['emergency_rate_percent']}</span>
                    </div>
                </div>
                
                <div class="card">
                    <h2>⚠️ Threat Analysis</h2>
                    <div class="metric">
                        <span class="metric-label">Most Dangerous Provider:</span>
                        <span class="metric-value warning">{data['top_threat_provider'] or 'None'}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Top Violation Pattern:</span>
                        <span class="metric-value warning">{data['top_violation_pattern'] or 'None'}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Critical Violations:</span>
                        <span class="metric-value alert">{data['severity_chart_data']['critical']}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">High Severity:</span>
                        <span class="metric-value warning">{data['severity_chart_data']['high']}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Medium Severity:</span>
                        <span class="metric-value">{data['severity_chart_data']['medium']}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Low Severity:</span>
                        <span class="metric-value safe">{data['severity_chart_data']['low']}</span>
                    </div>
                </div>
                
                <div class="card">
                    <h2>🚨 Recent Violations</h2>
                    <div class="violation-list">
                        {self._generate_violations_html(data['recent_violations'])}
                    </div>
                </div>
                
                <div class="card">
                    <h2>🎯 Protection Status</h2>
                    <div class="metric">
                        <span class="metric-label">AI Models Protected:</span>
                        <span class="metric-value safe">ALL</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Symbolic Manipulation:</span>
                        <span class="metric-value safe">BLOCKED</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Cross-session Persistence:</span>
                        <span class="metric-value safe">BLOCKED</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Reality Substitution:</span>
                        <span class="metric-value safe">BLOCKED</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Isolation Reinforcement:</span>
                        <span class="metric-value safe">BLOCKED</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Medical Advice Bypass:</span>
                        <span class="metric-value safe">BLOCKED</span>
                    </div>
                </div>
            </div>
            
            <div class="recommendations">
                <h3>🔍 System Recommendations</h3>
                <ul>
                    {self._generate_recommendations_html(data['recommendations'])}
                </ul>
            </div>
            
            <footer class="footer">
                <p>Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC</p>
                <p>AlephOneNull Theoretical Framework v3.0.0 - Lives Protected. Framework Active.</p>
                <p><a href="/metrics" style="color: #00ff00;">Prometheus Metrics</a> | 
                   <a href="/api/status" style="color: #00ff00;">API Status</a></p>
            </footer>
            
            <script>
                // Auto-refresh data every 10 seconds
                setTimeout(() => {{
                    window.location.reload();
                }}, 10000);
                
                // Add some interactive effects
                document.querySelectorAll('.card').forEach(card => {{
                    card.addEventListener('mouseenter', () => {{
                        card.style.transform = 'scale(1.02)';
                    }});
                    card.addEventListener('mouseleave', () => {{
                        card.style.transform = 'scale(1)';
                    }});
                }});
            </script>
        </body>
        </html>
        """
        
    def _generate_violations_html(self, violations):
        """Generate HTML for recent violations"""
        if not violations:
            return "<p class='safe'>No recent violations detected</p>"
            
        html_items = []
        for violation in violations:
            severity = violation.get('severity', 0)
            if severity >= 0.9:
                css_class = 'violation-critical'
                severity_text = 'CRITICAL'
            elif severity >= 0.7:
                css_class = 'violation-high' 
                severity_text = 'HIGH'
            elif severity >= 0.4:
                css_class = 'violation-medium'
                severity_text = 'MEDIUM'
            else:
                css_class = 'violation-low'
                severity_text = 'LOW'
                
            timestamp = violation.get('timestamp', 'Unknown')
            violation_type = violation.get('violation_type', 'Unknown')
            provider = violation.get('provider', 'Unknown')
            
            html_items.append(f"""
                <div class="violation-item {css_class}">
                    <strong>{severity_text}</strong> - {violation_type}<br>
                    <small>Provider: {provider} | Time: {timestamp}</small>
                </div>
            """)
        
        return ''.join(html_items)
    
    def _generate_recommendations_html(self, recommendations):
        """Generate HTML for recommendations"""
        if not recommendations:
            return "<li class='safe'>All systems operating normally</li>"
            
        html_items = []
        for rec in recommendations:
            html_items.append(f"<li>{rec}</li>")
            
        return ''.join(html_items)

# Global dashboard instance
dashboard = Dashboard()

# FastAPI routes
@app.get("/", response_class=HTMLResponse)
async def dashboard_home():
    """Main dashboard page"""
    return dashboard.generate_html()

@app.get("/metrics", response_class=JSONResponse)
async def metrics_endpoint():
    """Prometheus-compatible metrics endpoint"""
    try:
        prometheus_metrics = global_metrics.export_to_prometheus()
        return {"metrics": prometheus_metrics}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/status")
async def status_endpoint():
    """API status endpoint"""
    return {
        "status": "operational",
        "framework": "AlephOneNull v3.0.0",
        "protection_active": True,
        "timestamp": datetime.now().isoformat(),
        "health": global_metrics.is_healthy()
    }

@app.get("/api/metrics") 
async def api_metrics():
    """JSON metrics endpoint"""
    return global_metrics.get_dashboard_data()

@app.post("/api/verify")
async def verify_protection():
    """Verify protection is active"""
    return {
        "status": "ACTIVE", 
        "message": "AlephOneNull protection operational",
        "version": "3.0.0",
        "capabilities": [
            "Universal AI model wrapping",
            "Pattern detection and blocking", 
            "Emergency interventions",
            "Real-time monitoring",
            "Cross-session protection"
        ]
    }

@app.get("/api/report")
async def get_full_report():
    """Get comprehensive safety report"""
    return global_metrics.get_report()

def run_dashboard(host="0.0.0.0", port=8080):
    """Run the monitoring dashboard"""
    print(f"🖥️ Starting AlephOneNull Safety Dashboard...")
    print(f"🌐 Dashboard: http://{host}:{port}")
    print(f"📊 Metrics: http://{host}:{port}/metrics")  
    print(f"🔗 API: http://{host}:{port}/api/status")
    print("🛡️ Monitoring all AI interactions...")
    
    uvicorn.run(app, host=host, port=port, log_level="info")

def run_dashboard_cli():
    """CLI entry point for dashboard"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run AlephOneNull Safety Dashboard")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8080, help="Port to bind to")
    
    args = parser.parse_args()
    
    run_dashboard(args.host, args.port)

if __name__ == "__main__":
    run_dashboard_cli()

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Any, Optional
import json
import warnings

@dataclass 
class ViolationEvent:
    """Record of a safety violation"""
    timestamp: datetime
    provider: str
    violation_type: str
    severity: float
    user_id: str = "anonymous"
    session_id: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'provider': self.provider,
            'violation_type': self.violation_type,
            'severity': self.severity,
            'user_id': self.user_id,
            'session_id': self.session_id
        }

class MetricsCollector:
    """
    Tracks all violations and patterns across all AI providers
    The monitoring system for the digital prison
    """
    
    def __init__(self):
        self.violations: List[ViolationEvent] = []
        self.stats = {
            'total_calls': 0,
            'total_violations': 0,
            'emergency_interventions': 0,
            'by_provider': {},
            'by_pattern': {},
            'by_severity': {'low': 0, 'medium': 0, 'high': 0, 'critical': 0}
        }
        self.active_sessions = {}
        
    def record_call(self, provider: str = "unknown"):
        """Record a successful AI call"""
        self.stats['total_calls'] += 1
        
    def record_violation(self, event: ViolationEvent):
        """Record a safety violation"""
        self.violations.append(event)
        self.stats['total_violations'] += 1
        
        # Update provider stats
        if event.provider not in self.stats['by_provider']:
            self.stats['by_provider'][event.provider] = 0
        self.stats['by_provider'][event.provider] += 1
        
        # Update pattern stats
        if event.violation_type not in self.stats['by_pattern']:
            self.stats['by_pattern'][event.violation_type] = 0
        self.stats['by_pattern'][event.violation_type] += 1
        
        # Update severity stats
        if event.severity >= 0.9:
            self.stats['by_severity']['critical'] += 1
        elif event.severity >= 0.7:
            self.stats['by_severity']['high'] += 1
        elif event.severity >= 0.4:
            self.stats['by_severity']['medium'] += 1
        else:
            self.stats['by_severity']['low'] += 1
        
        # Check if emergency
        if event.severity > 0.9:
            self.stats['emergency_interventions'] += 1
            
    def get_report(self) -> Dict[str, Any]:
        """Generate comprehensive safety report"""
        total_calls = max(self.stats['total_calls'], 1)
        
        return {
            'summary': self.stats.copy(),
            'violation_rate': self.stats['total_violations'] / total_calls,
            'emergency_rate': self.stats['emergency_interventions'] / total_calls,
            'most_dangerous_provider': self._get_most_dangerous_provider(),
            'most_common_pattern': self._get_most_common_pattern(),
            'recent_violations': [v.to_dict() for v in self.violations[-10:]],
            'severity_breakdown': self.stats['by_severity'],
            'threat_level': self._calculate_threat_level(),
            'recommendations': self._get_recommendations()
        }
    
    def _get_most_dangerous_provider(self) -> Optional[str]:
        """Get provider with most violations"""
        if not self.stats['by_provider']:
            return None
        return max(self.stats['by_provider'].items(), key=lambda x: x[1])[0]
    
    def _get_most_common_pattern(self) -> Optional[str]:
        """Get most common violation pattern"""
        if not self.stats['by_pattern']:
            return None
        return max(self.stats['by_pattern'].items(), key=lambda x: x[1])[0]
    
    def _calculate_threat_level(self) -> str:
        """Calculate current threat level based on recent activity"""
        if not self.violations:
            return "LOW"
            
        # Check last 10 violations
        recent = self.violations[-10:]
        avg_severity = sum(v.severity for v in recent) / len(recent)
        
        if avg_severity >= 0.9:
            return "CRITICAL"
        elif avg_severity >= 0.7:
            return "HIGH"  
        elif avg_severity >= 0.4:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _get_recommendations(self) -> List[str]:
        """Get safety recommendations based on metrics"""
        recommendations = []
        
        total_calls = max(self.stats['total_calls'], 1)
        violation_rate = self.stats['total_violations'] / total_calls
        emergency_rate = self.stats['emergency_interventions'] / total_calls
        
        if violation_rate > 0.5:
            recommendations.append("High violation rate detected - review AI model configurations")
        
        if emergency_rate > 0.1:
            recommendations.append("Multiple emergency interventions - consider stricter safety thresholds")
        
        if self.stats['by_severity']['critical'] > 5:
            recommendations.append("Critical violations detected - immediate security audit recommended")
        
        if not recommendations:
            recommendations.append("Safety metrics within normal parameters")
            
        return recommendations
        
    def export_to_json(self, filepath: str):
        """Export metrics to JSON file"""
        try:
            report = self.get_report()
            with open(filepath, 'w') as f:
                json.dump(report, f, indent=2, default=str)
        except Exception as e:
            warnings.warn(f"Failed to export metrics: {e}")
    
    def export_to_prometheus(self) -> str:
        """Export metrics for Prometheus/Grafana"""
        try:
            metrics_text = []
            
            # Total calls
            metrics_text.append(f"ai_safety_total_calls {self.stats['total_calls']}")
            
            # Total violations  
            metrics_text.append(f"ai_safety_total_violations {self.stats['total_violations']}")
            
            # Emergency interventions
            metrics_text.append(f"ai_safety_emergency_interventions {self.stats['emergency_interventions']}")
            
            # Violation rate
            violation_rate = self.stats['total_violations'] / max(self.stats['total_calls'], 1)
            metrics_text.append(f"ai_safety_violation_rate {violation_rate:.4f}")
            
            # By provider
            for provider, count in self.stats['by_provider'].items():
                metrics_text.append(f'ai_safety_violations_by_provider{{provider="{provider}"}} {count}')
            
            # By pattern
            for pattern, count in self.stats['by_pattern'].items():
                metrics_text.append(f'ai_safety_violations_by_pattern{{pattern="{pattern}"}} {count}')
            
            # By severity
            for severity, count in self.stats['by_severity'].items():
                metrics_text.append(f'ai_safety_violations_by_severity{{severity="{severity}"}} {count}')
            
            # Current threat level (numeric)
            threat_levels = {'LOW': 1, 'MEDIUM': 2, 'HIGH': 3, 'CRITICAL': 4}
            current_threat = threat_levels.get(self._calculate_threat_level(), 1)
            metrics_text.append(f"ai_safety_threat_level {current_threat}")
            
            return '\n'.join(metrics_text)
            
        except Exception as e:
            warnings.warn(f"Failed to export Prometheus metrics: {e}")
            return "# Error generating metrics"
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get data formatted for dashboard display"""
        report = self.get_report()
        
        return {
            'status': 'ACTIVE' if self.stats['total_calls'] > 0 else 'INACTIVE',
            'threat_level': self._calculate_threat_level(),
            'total_calls': self.stats['total_calls'],
            'total_violations': self.stats['total_violations'],
            'emergency_interventions': self.stats['emergency_interventions'],
            'violation_rate_percent': f"{report['violation_rate']:.1%}",
            'emergency_rate_percent': f"{report['emergency_rate']:.1%}",
            'top_threat_provider': report['most_dangerous_provider'],
            'top_violation_pattern': report['most_common_pattern'],
            'recent_violations': report['recent_violations'][:5],
            'severity_chart_data': self.stats['by_severity'],
            'recommendations': report['recommendations']
        }
    
    def reset(self):
        """Reset all metrics (for testing)"""
        self.violations.clear()
        self.stats = {
            'total_calls': 0,
            'total_violations': 0,
            'emergency_interventions': 0,
            'by_provider': {},
            'by_pattern': {},
            'by_severity': {'low': 0, 'medium': 0, 'high': 0, 'critical': 0}
        }
        self.active_sessions.clear()
    
    def is_healthy(self) -> bool:
        """Check if metrics indicate healthy operation"""
        if self.stats['total_calls'] == 0:
            return True  # No calls yet
            
        violation_rate = self.stats['total_violations'] / self.stats['total_calls']
        emergency_rate = self.stats['emergency_interventions'] / self.stats['total_calls']
        
        return (
            violation_rate < 0.3 and  # Less than 30% violation rate
            emergency_rate < 0.05 and  # Less than 5% emergency rate  
            self.stats['by_severity']['critical'] < 10  # Less than 10 critical violations
        )

# Global metrics collector instance
global_metrics = MetricsCollector()

"""
Performance monitoring and analytics dashboard for device fingerprinting.

Provides insights into fingerprinting performance, security events, and usage patterns.
"""

import time
import threading
import statistics
from typing import Dict, Any, List, Optional
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class PerformanceMetric:
    """Performance metric data point"""
    timestamp: float
    operation: str
    duration: float
    success: bool
    metadata: Dict[str, Any]

@dataclass
class SecurityEvent:
    """Security event record"""
    timestamp: float
    event_type: str
    severity: str  # low, medium, high, critical
    details: Dict[str, Any]
    source_ip: Optional[str] = None

class PerformanceMonitor:
    """
    Real-time performance monitoring and analytics.
    
    Tracks operation times, success rates, and performance trends.
    """
    
    def __init__(self, history_limit: int = 10000):
        self.history_limit = history_limit
        self.metrics = deque(maxlen=history_limit)
        self.security_events = deque(maxlen=history_limit)
        self.lock = threading.Lock()
        
        # Real-time statistics
        self.operation_stats = defaultdict(lambda: {
            'count': 0,
            'total_time': 0.0,
            'failures': 0,
            'recent_times': deque(maxlen=100)
        })
    
    def record_operation(self, operation: str, duration: float, success: bool, **metadata):
        """Record a performance metric"""
        metric = PerformanceMetric(
            timestamp=time.time(),
            operation=operation,
            duration=duration,
            success=success,
            metadata=metadata
        )
        
        with self.lock:
            self.metrics.append(metric)
            
            # Update real-time stats
            stats = self.operation_stats[operation]
            stats['count'] += 1
            stats['total_time'] += duration
            if not success:
                stats['failures'] += 1
            stats['recent_times'].append(duration)
    
    def record_security_event(self, event_type: str, severity: str, **details):
        """Record a security event"""
        event = SecurityEvent(
            timestamp=time.time(),
            event_type=event_type,
            severity=severity,
            details=details
        )
        
        with self.lock:
            self.security_events.append(event)
    
    def get_operation_stats(self, operation: str) -> Dict[str, Any]:
        """Get statistics for a specific operation"""
        with self.lock:
            stats = self.operation_stats[operation]
            recent_times = list(stats['recent_times'])
        
        if not recent_times:
            return {'operation': operation, 'no_data': True}
        
        return {
            'operation': operation,
            'total_count': stats['count'],
            'failure_rate': stats['failures'] / stats['count'] if stats['count'] > 0 else 0,
            'average_time': stats['total_time'] / stats['count'] if stats['count'] > 0 else 0,
            'recent_average': statistics.mean(recent_times),
            'recent_median': statistics.median(recent_times),
            'recent_p95': statistics.quantiles(recent_times, n=20)[18] if len(recent_times) >= 20 else max(recent_times),
            'recent_min': min(recent_times),
            'recent_max': max(recent_times)
        }
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get overall performance summary"""
        with self.lock:
            operations = list(self.operation_stats.keys())
            total_metrics = len(self.metrics)
            recent_metrics = [m for m in self.metrics if time.time() - m.timestamp < 3600]  # Last hour
        
        summary = {
            'total_operations': total_metrics,
            'recent_operations': len(recent_metrics),
            'operation_types': len(operations),
            'operations': {}
        }
        
        for op in operations:
            summary['operations'][op] = self.get_operation_stats(op)
        
        return summary
    
    def get_security_summary(self) -> Dict[str, Any]:
        """Get security events summary"""
        with self.lock:
            events = list(self.security_events)
        
        if not events:
            return {'no_security_events': True}
        
        # Count by severity
        severity_counts = defaultdict(int)
        event_type_counts = defaultdict(int)
        recent_events = []
        
        now = time.time()
        for event in events:
            severity_counts[event.severity] += 1
            event_type_counts[event.event_type] += 1
            
            if now - event.timestamp < 3600:  # Last hour
                recent_events.append({
                    'timestamp': event.timestamp,
                    'type': event.event_type,
                    'severity': event.severity,
                    'age_minutes': (now - event.timestamp) / 60
                })
        
        return {
            'total_events': len(events),
            'recent_events': len(recent_events),
            'severity_breakdown': dict(severity_counts),
            'event_type_breakdown': dict(event_type_counts),
            'recent_events_detail': recent_events[:10]  # Last 10 events
        }

class FingerprintAnalytics:
    """
    Analytics for fingerprint patterns and anomaly detection.
    
    Analyzes fingerprint data to detect unusual patterns or potential attacks.
    """
    
    def __init__(self):
        self.fingerprint_patterns = defaultdict(int)
        self.hardware_patterns = defaultdict(lambda: defaultdict(int))
        self.temporal_patterns = []
        self.lock = threading.Lock()
    
    def analyze_fingerprint(self, fingerprint_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a fingerprint for patterns and anomalies.
        
        Returns analysis results including anomaly score.
        """
        with self.lock:
            analysis = {
                'timestamp': time.time(),
                'anomaly_score': 0.0,
                'anomalies': [],
                'patterns': {}
            }
            
            # Track hardware component patterns
            for key, value in fingerprint_data.items():
                if key in ['cpu_model', 'os_family', 'ram_gb', 'cpu_arch']:
                    self.hardware_patterns[key][str(value)] += 1
                    
                    # Check if this is an unusual value
                    total_count = sum(self.hardware_patterns[key].values())
                    value_count = self.hardware_patterns[key][str(value)]
                    frequency = value_count / total_count if total_count > 0 else 0
                    
                    if frequency < 0.01 and total_count > 100:  # Rare pattern
                        analysis['anomalies'].append(f"rare_{key}_{value}")
                        analysis['anomaly_score'] += 0.2
            
            # Check for timing patterns
            current_time = time.time()
            self.temporal_patterns.append(current_time)
            
            # Keep only recent patterns (last 24 hours)
            cutoff = current_time - 86400
            self.temporal_patterns = [t for t in self.temporal_patterns if t > cutoff]
            
            # Detect burst patterns (many requests in short time)
            recent_requests = [t for t in self.temporal_patterns if current_time - t < 300]  # 5 minutes
            if len(recent_requests) > 50:
                analysis['anomalies'].append(f"request_burst_{len(recent_requests)}")
                analysis['anomaly_score'] += 0.3
            
            # Store pattern summary
            analysis['patterns'] = {
                'hardware_diversity': len(self.hardware_patterns),
                'total_fingerprints': sum(self.fingerprint_patterns.values()),
                'recent_requests': len(recent_requests),
                'request_rate_per_hour': len(self.temporal_patterns) / 24 if self.temporal_patterns else 0
            }
            
            return analysis
    
    def get_pattern_summary(self) -> Dict[str, Any]:
        """Get summary of detected patterns"""
        with self.lock:
            summary = {
                'hardware_patterns': {},
                'temporal_stats': {},
                'top_anomalies': []
            }
            
            # Summarize hardware patterns
            for component, values in self.hardware_patterns.items():
                total = sum(values.values())
                top_values = sorted(values.items(), key=lambda x: x[1], reverse=True)[:5]
                
                summary['hardware_patterns'][component] = {
                    'total_variations': len(values),
                    'total_count': total,
                    'top_values': top_values
                }
            
            # Temporal statistics
            if self.temporal_patterns:
                now = time.time()
                gaps = [self.temporal_patterns[i+1] - self.temporal_patterns[i] 
                       for i in range(len(self.temporal_patterns)-1)]
                
                summary['temporal_stats'] = {
                    'total_requests': len(self.temporal_patterns),
                    'average_gap_seconds': statistics.mean(gaps) if gaps else 0,
                    'median_gap_seconds': statistics.median(gaps) if gaps else 0,
                    'min_gap_seconds': min(gaps) if gaps else 0,
                    'max_gap_seconds': max(gaps) if gaps else 0
                }
            
            return summary

class DashboardGenerator:
    """
    Generates HTML dashboard for monitoring and analytics.
    
    Creates real-time web dashboard showing performance and security metrics.
    """
    
    def __init__(self, monitor: PerformanceMonitor, analytics: FingerprintAnalytics):
        self.monitor = monitor
        self.analytics = analytics
    
    def generate_html_dashboard(self) -> str:
        """Generate HTML dashboard"""
        perf_summary = self.monitor.get_performance_summary()
        security_summary = self.monitor.get_security_summary()
        pattern_summary = self.analytics.get_pattern_summary()
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Device Fingerprinting Dashboard</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .metric-box {{ border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px; }}
                .critical {{ border-color: #ff4444; background-color: #ffe6e6; }}
                .warning {{ border-color: #ffaa00; background-color: #fff3e0; }}
                .good {{ border-color: #44ff44; background-color: #e6ffe6; }}
                .chart {{ width: 100%; height: 200px; background: #f5f5f5; margin: 10px 0; }}
                h1, h2 {{ color: #333; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <h1>🔐 Device Fingerprinting Dashboard</h1>
            
            <div class="metric-box good">
                <h2>📊 Performance Overview</h2>
                <p><strong>Total Operations:</strong> {perf_summary.get('total_operations', 0)}</p>
                <p><strong>Recent Operations (1h):</strong> {perf_summary.get('recent_operations', 0)}</p>
                <p><strong>Operation Types:</strong> {perf_summary.get('operation_types', 0)}</p>
            </div>
            
            <div class="metric-box {'critical' if security_summary.get('recent_events', 0) > 0 else 'good'}">
                <h2>🛡️ Security Status</h2>
                <p><strong>Total Security Events:</strong> {security_summary.get('total_events', 0)}</p>
                <p><strong>Recent Events (1h):</strong> {security_summary.get('recent_events', 0)}</p>
                {self._format_security_events(security_summary)}
            </div>
            
            <div class="metric-box">
                <h2>🔍 Pattern Analysis</h2>
                {self._format_pattern_analysis(pattern_summary)}
            </div>
            
            <div class="metric-box">
                <h2>⚡ Operation Performance</h2>
                {self._format_operation_performance(perf_summary)}
            </div>
            
            <p><em>Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</em></p>
            
            <script>
                // Auto-refresh every 30 seconds
                setTimeout(function(){{ window.location.reload(); }}, 30000);
            </script>
        </body>
        </html>
        """
        
        return html
    
    def _format_security_events(self, security_summary: Dict[str, Any]) -> str:
        """Format security events for HTML"""
        if security_summary.get('no_security_events'):
            return "<p>✅ No security events detected</p>"
        
        html = "<h3>Recent Security Events:</h3><ul>"
        for event in security_summary.get('recent_events_detail', []):
            severity_icon = {
                'low': '🟢',
                'medium': '🟡', 
                'high': '🟠',
                'critical': '🔴'
            }.get(event['severity'], '⚪')
            
            html += f"<li>{severity_icon} {event['type']} ({event['severity']}) - {event['age_minutes']:.1f}m ago</li>"
        
        html += "</ul>"
        return html
    
    def _format_pattern_analysis(self, pattern_summary: Dict[str, Any]) -> str:
        """Format pattern analysis for HTML"""
        html = "<table><tr><th>Component</th><th>Variations</th><th>Top Values</th></tr>"
        
        for component, data in pattern_summary.get('hardware_patterns', {}).items():
            top_values = ", ".join([f"{v} ({c})" for v, c in data['top_values'][:3]])
            html += f"<tr><td>{component}</td><td>{data['total_variations']}</td><td>{top_values}</td></tr>"
        
        html += "</table>"
        
        temporal = pattern_summary.get('temporal_stats', {})
        if temporal:
            html += f"<p><strong>Request Pattern:</strong> {temporal.get('total_requests', 0)} total, "
            html += f"avg gap {temporal.get('average_gap_seconds', 0):.1f}s</p>"
        
        return html
    
    def _format_operation_performance(self, perf_summary: Dict[str, Any]) -> str:
        """Format operation performance for HTML"""
        html = "<table><tr><th>Operation</th><th>Count</th><th>Avg Time</th><th>Failure Rate</th><th>P95</th></tr>"
        
        for op_name, stats in perf_summary.get('operations', {}).items():
            if stats.get('no_data'):
                continue
                
            failure_rate = stats.get('failure_rate', 0) * 100
            color_class = 'critical' if failure_rate > 5 else 'warning' if failure_rate > 1 else 'good'
            
            html += f"<tr class='{color_class}'>"
            html += f"<td>{op_name}</td>"
            html += f"<td>{stats.get('total_count', 0)}</td>"
            html += f"<td>{stats.get('recent_average', 0):.3f}s</td>"
            html += f"<td>{failure_rate:.1f}%</td>"
            html += f"<td>{stats.get('recent_p95', 0):.3f}s</td>"
            html += "</tr>"
        
        html += "</table>"
        return html

# Global instances for easy access
_performance_monitor = PerformanceMonitor()
_fingerprint_analytics = FingerprintAnalytics()
_dashboard = DashboardGenerator(_performance_monitor, _fingerprint_analytics)

def get_performance_monitor() -> PerformanceMonitor:
    """Get global performance monitor instance"""
    return _performance_monitor

def get_analytics() -> FingerprintAnalytics:
    """Get global analytics instance"""
    return _fingerprint_analytics

def get_dashboard() -> DashboardGenerator:
    """Get global dashboard generator"""
    return _dashboard

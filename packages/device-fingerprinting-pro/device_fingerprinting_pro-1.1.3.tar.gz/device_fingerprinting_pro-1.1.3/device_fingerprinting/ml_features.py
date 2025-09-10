"""
AI/ML-enhanced features for intelligent device fingerprinting.

Uses machine learning for anomaly detection, behavioral analysis, and adaptive security.
"""

import time
import json
import hashlib
import numpy as np
from typing import Dict, Any, List, Tuple, Optional
from collections import defaultdict, deque
from dataclasses import dataclass

@dataclass
class BehaviorPattern:
    """User behavior pattern data"""
    user_id: str
    session_duration: float
    request_frequency: float
    operation_sequence: List[str]
    timestamp: float

class MLAnomalyDetector:
    """
    Machine learning-based anomaly detector for device fingerprints.
    
    Uses statistical models and pattern recognition to detect suspicious activity.
    """
    
    def __init__(self, learning_rate: float = 0.01, window_size: int = 1000):
        self.learning_rate = learning_rate
        self.window_size = window_size
        
        # Feature tracking
        self.feature_stats = defaultdict(lambda: {'mean': 0, 'std': 1, 'count': 0})
        self.pattern_frequencies = defaultdict(int)
        self.user_profiles = defaultdict(lambda: {
            'typical_patterns': [],
            'session_stats': {'mean_duration': 0, 'std_duration': 1},
            'last_seen': 0
        })
        
        # Sliding window for recent data
        self.recent_patterns = deque(maxlen=window_size)
        
    def extract_features(self, fingerprint_data: Dict[str, Any], 
                        session_info: Optional[Dict[str, Any]] = None) -> np.ndarray:
        """Extract numerical features from fingerprint data for ML analysis"""
        features = []
        
        # Hardware-based features
        cpu_model = fingerprint_data.get('cpu_model', '')
        features.append(hash(cpu_model) % 10000)  # Hash to number
        
        features.append(fingerprint_data.get('ram_gb', 0))
        
        os_family = fingerprint_data.get('os_family', '')
        features.append({'Windows': 1, 'Linux': 2, 'Darwin': 3}.get(os_family, 0))
        
        cpu_arch = fingerprint_data.get('cpu_arch', '')
        features.append({'x86_64': 1, 'AMD64': 1, 'arm64': 2}.get(cpu_arch, 0))
        
        # Network and timing features
        mac_hash = fingerprint_data.get('mac_hash', '')
        features.append(int(mac_hash[:8], 16) % 10000 if mac_hash else 0)
        
        # Session-based features
        if session_info:
            features.append(session_info.get('duration', 0))
            features.append(session_info.get('request_count', 0))
            features.append(session_info.get('time_since_last', 3600))  # Default 1 hour
        else:
            features.extend([0, 0, 3600])
        
        # Temporal features
        current_time = time.time()
        hour_of_day = int((current_time % 86400) / 3600)  # 0-23
        day_of_week = int((current_time / 86400) % 7)     # 0-6
        features.extend([hour_of_day, day_of_week])
        
        return np.array(features, dtype=float)
    
    def update_model(self, features: np.ndarray, is_anomaly: bool = False):
        """Update the anomaly detection model with new data"""
        # Update feature statistics using online learning
        for i, feature_value in enumerate(features):
            stats = self.feature_stats[f'feature_{i}']
            stats['count'] += 1
            
            # Online mean and variance calculation
            delta = feature_value - stats['mean']
            stats['mean'] += delta / stats['count']
            
            if stats['count'] > 1:
                delta2 = feature_value - stats['mean']
                stats['std'] = np.sqrt(((stats['count'] - 2) * stats['std']**2 + delta * delta2) / (stats['count'] - 1))
        
        # Store pattern for clustering
        self.recent_patterns.append((features, is_anomaly, time.time()))
    
    def calculate_anomaly_score(self, features: np.ndarray) -> float:
        """Calculate anomaly score for given features"""
        if len(self.feature_stats) == 0:
            return 0.0  # No baseline yet
        
        total_score = 0.0
        feature_count = 0
        
        # Calculate z-scores for each feature
        for i, feature_value in enumerate(features):
            stats = self.feature_stats.get(f'feature_{i}')
            if stats and stats['count'] > 10:  # Need minimum samples
                z_score = abs(feature_value - stats['mean']) / max(stats['std'], 0.1)
                
                # Convert z-score to anomaly contribution (sigmoid-like)
                anomaly_contribution = 1 / (1 + np.exp(-max(z_score - 2, 0)))
                total_score += anomaly_contribution
                feature_count += 1
        
        return total_score / max(feature_count, 1)
    
    def detect_anomaly(self, fingerprint_data: Dict[str, Any], 
                      session_info: Optional[Dict[str, Any]] = None,
                      user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Detect anomalies in fingerprint data using ML models.
        
        Returns:
            Dictionary with anomaly score and detailed analysis
        """
        features = self.extract_features(fingerprint_data, session_info)
        anomaly_score = self.calculate_anomaly_score(features)
        
        # Additional checks for known attack patterns
        attack_indicators = self._check_attack_patterns(fingerprint_data, session_info)
        
        # User behavior analysis if user_id provided
        behavior_anomaly = 0.0
        if user_id:
            behavior_anomaly = self._analyze_user_behavior(user_id, session_info or {})
        
        # Combine scores
        final_score = (anomaly_score * 0.6 + 
                      len(attack_indicators) * 0.2 + 
                      behavior_anomaly * 0.2)
        
        # Update model (assume non-anomalous unless score is very high)
        is_anomaly = final_score > 0.7
        self.update_model(features, is_anomaly)
        
        return {
            'anomaly_score': final_score,
            'ml_score': anomaly_score,
            'behavior_score': behavior_anomaly,
            'attack_indicators': attack_indicators,
            'is_anomaly': is_anomaly,
            'confidence': min(len(self.recent_patterns) / self.window_size, 1.0),
            'feature_contributions': self._get_feature_contributions(features)
        }
    
    def _check_attack_patterns(self, fingerprint_data: Dict[str, Any], 
                              session_info: Optional[Dict[str, Any]]) -> List[str]:
        """Check for known attack patterns"""
        indicators = []
        
        # VM detection patterns
        cpu_model = fingerprint_data.get('cpu_model', '').lower()
        if any(vm_sig in cpu_model for vm_sig in ['vmware', 'virtualbox', 'qemu']):
            indicators.append('vm_cpu_signature')
        
        # Suspicious session patterns
        if session_info:
            # Very short sessions might indicate automation
            if session_info.get('duration', 0) < 1:
                indicators.append('very_short_session')
            
            # High request frequency might indicate scripted access
            if session_info.get('request_count', 0) > 100:
                indicators.append('high_request_frequency')
        
        # Hardware inconsistencies
        ram_gb = fingerprint_data.get('ram_gb', 0)
        if ram_gb > 128:  # Suspiciously high RAM
            indicators.append('excessive_ram')
        
        return indicators
    
    def _analyze_user_behavior(self, user_id: str, session_info: Dict[str, Any]) -> float:
        """Analyze user behavior patterns for anomalies"""
        profile = self.user_profiles[user_id]
        
        if profile['last_seen'] == 0:
            # First time seeing this user
            profile['last_seen'] = time.time()
            return 0.0
        
        anomaly_score = 0.0
        
        # Check session duration anomaly
        duration = session_info.get('duration', 0)
        if profile['session_stats']['mean_duration'] > 0:
            duration_z_score = abs(duration - profile['session_stats']['mean_duration']) / max(profile['session_stats']['std_duration'], 1)
            if duration_z_score > 3:  # 3 standard deviations
                anomaly_score += 0.3
        
        # Check time-of-access patterns
        current_time = time.time()
        time_since_last = current_time - profile['last_seen']
        
        if time_since_last < 60:  # Less than 1 minute since last access
            anomaly_score += 0.2
        
        # Update user profile
        self._update_user_profile(user_id, session_info)
        
        return min(anomaly_score, 1.0)
    
    def _update_user_profile(self, user_id: str, session_info: Dict[str, Any]):
        """Update user behavioral profile"""
        profile = self.user_profiles[user_id]
        
        duration = session_info.get('duration', 0)
        
        # Update session duration statistics
        if profile['session_stats']['mean_duration'] == 0:
            profile['session_stats']['mean_duration'] = duration
            profile['session_stats']['std_duration'] = 1
        else:
            # Online update of mean and std
            old_mean = profile['session_stats']['mean_duration']
            profile['session_stats']['mean_duration'] = old_mean * 0.9 + duration * 0.1
            
            std_update = abs(duration - old_mean)
            profile['session_stats']['std_duration'] = profile['session_stats']['std_duration'] * 0.9 + std_update * 0.1
        
        profile['last_seen'] = time.time()
    
    def _get_feature_contributions(self, features: np.ndarray) -> Dict[str, float]:
        """Get individual feature contributions to anomaly score"""
        contributions = {}
        feature_names = [
            'cpu_model_hash', 'ram_gb', 'os_family', 'cpu_arch', 'mac_hash',
            'session_duration', 'request_count', 'time_since_last',
            'hour_of_day', 'day_of_week'
        ]
        
        for i, (feature_value, name) in enumerate(zip(features, feature_names)):
            stats = self.feature_stats.get(f'feature_{i}')
            if stats and stats['count'] > 10:
                z_score = abs(feature_value - stats['mean']) / max(stats['std'], 0.1)
                contributions[name] = min(z_score / 5.0, 1.0)  # Normalize to 0-1
        
        return contributions

class AdaptiveSecurityManager:
    """
    Adaptive security manager that adjusts security levels based on ML insights.
    
    Dynamically changes security requirements based on detected patterns and risks.
    """
    
    def __init__(self, anomaly_detector: MLAnomalyDetector):
        self.anomaly_detector = anomaly_detector
        self.security_levels = {
            'low': {'threshold': 0.95, 'checks': ['basic']},
            'medium': {'threshold': 0.85, 'checks': ['basic', 'timing']},
            'high': {'threshold': 0.75, 'checks': ['basic', 'timing', 'vm_detection']},
            'critical': {'threshold': 0.60, 'checks': ['basic', 'timing', 'vm_detection', 'forensic']}
        }
        self.current_level = 'medium'
        self.threat_indicators = deque(maxlen=100)
    
    def assess_security_level(self, fingerprint_data: Dict[str, Any], 
                            session_info: Optional[Dict[str, Any]] = None,
                            user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Assess appropriate security level based on ML analysis.
        
        Returns:
            Dictionary with recommended security level and reasoning
        """
        # Get ML anomaly analysis
        ml_result = self.anomaly_detector.detect_anomaly(fingerprint_data, session_info, user_id)
        
        # Track threat indicators over time
        self.threat_indicators.append({
            'timestamp': time.time(),
            'anomaly_score': ml_result['anomaly_score'],
            'is_anomaly': ml_result['is_anomaly']
        })
        
        # Calculate recent threat level
        recent_threats = [t for t in self.threat_indicators if time.time() - t['timestamp'] < 3600]  # Last hour
        recent_anomaly_rate = sum(1 for t in recent_threats if t['is_anomaly']) / max(len(recent_threats), 1)
        avg_anomaly_score = sum(t['anomaly_score'] for t in recent_threats) / max(len(recent_threats), 1)
        
        # Determine security level
        if recent_anomaly_rate > 0.3 or avg_anomaly_score > 0.8:
            recommended_level = 'critical'
        elif recent_anomaly_rate > 0.2 or avg_anomaly_score > 0.6:
            recommended_level = 'high'
        elif recent_anomaly_rate > 0.1 or avg_anomaly_score > 0.4:
            recommended_level = 'medium'
        else:
            recommended_level = 'low'
        
        # Get specific recommendations
        recommendations = self._get_security_recommendations(ml_result, recommended_level)
        
        # Update current level with hysteresis to prevent oscillation
        if recommended_level != self.current_level:
            level_order = ['low', 'medium', 'high', 'critical']
            current_index = level_order.index(self.current_level)
            recommended_index = level_order.index(recommended_level)
            
            # Only change if difference is significant or consistently recommended
            if abs(recommended_index - current_index) > 1 or len([t for t in recent_threats[-5:] if self._get_level_for_score(t['anomaly_score']) == recommended_level]) >= 3:
                self.current_level = recommended_level
        
        return {
            'current_level': self.current_level,
            'recommended_level': recommended_level,
            'ml_analysis': ml_result,
            'threat_metrics': {
                'recent_anomaly_rate': recent_anomaly_rate,
                'avg_anomaly_score': avg_anomaly_score,
                'total_recent_events': len(recent_threats)
            },
            'security_requirements': self.security_levels[self.current_level],
            'recommendations': recommendations
        }
    
    def _get_level_for_score(self, score: float) -> str:
        """Get security level for a given anomaly score"""
        if score > 0.8:
            return 'critical'
        elif score > 0.6:
            return 'high'
        elif score > 0.4:
            return 'medium'
        else:
            return 'low'
    
    def _get_security_recommendations(self, ml_result: Dict[str, Any], level: str) -> List[str]:
        """Get specific security recommendations based on ML analysis"""
        recommendations = []
        
        if 'vm_cpu_signature' in ml_result.get('attack_indicators', []):
            recommendations.append("Enable VM detection checks")
        
        if ml_result.get('behavior_score', 0) > 0.5:
            recommendations.append("Require additional user authentication")
        
        if ml_result.get('ml_score', 0) > 0.7:
            recommendations.append("Increase fingerprint verification frequency")
        
        if level in ['high', 'critical']:
            recommendations.append("Enable forensic logging")
            recommendations.append("Require multi-factor authentication")
        
        if level == 'critical':
            recommendations.append("Consider blocking until manual review")
            recommendations.append("Alert security team")
        
        return recommendations

# Global ML instances
_anomaly_detector = MLAnomalyDetector()
_adaptive_security = AdaptiveSecurityManager(_anomaly_detector)

def get_anomaly_detector() -> MLAnomalyDetector:
    """Get global anomaly detector instance"""
    return _anomaly_detector

def get_adaptive_security() -> AdaptiveSecurityManager:
    """Get global adaptive security manager"""
    return _adaptive_security

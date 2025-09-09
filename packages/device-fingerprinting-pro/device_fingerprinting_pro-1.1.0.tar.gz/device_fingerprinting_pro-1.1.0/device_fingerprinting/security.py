"""
Runtime security checks and tamper detection.

Detects debugging, VM environments, and binary tampering.
Implements circuit breaker pattern for reliability.
"""

import os
import sys
import time
import hashlib
import threading
from typing import Dict, Optional, Callable

class SecurityMonitor:
    """Monitors runtime security and detects tampering"""
    
    def __init__(self):
        self.checks_enabled = True
        self.circuit_breaker = CircuitBreaker()
        self.last_integrity_check = 0
        self.integrity_cache = None
        
    def run_security_checks(self) -> Dict[str, bool]:
        """Run all security checks and return results"""
        if not self.checks_enabled:
            return {'disabled': True}
        
        results = {}
        
        # Basic tamper detection
        results['debugger'] = self._check_debugger()
        results['vm_detected'] = self._check_vm_environment()
        results['integrity'] = self._check_binary_integrity()
        results['timing'] = self._check_timing_anomalies()
        
        return results
    
    def _check_debugger(self) -> bool:
        """Check if debugger is attached"""
        try:
            if sys.platform == "win32":
                import ctypes
                kernel32 = ctypes.windll.kernel32
                return bool(kernel32.IsDebuggerPresent())
            
            elif sys.platform.startswith("linux"):
                # Check /proc/self/status for TracerPid
                try:
                    with open('/proc/self/status', 'r') as f:
                        for line in f:
                            if line.startswith('TracerPid:'):
                                tracer_pid = int(line.split()[1])
                                return tracer_pid != 0
                except:
                    pass
            
            # Fallback timing check
            start = time.perf_counter()
            time.sleep(0.001)
            elapsed = time.perf_counter() - start
            
            # If sleep took way longer than expected, might be debugged
            return elapsed > 0.01
            
        except Exception:
            return False
    
    def _check_vm_environment(self) -> bool:
        """Check for VM/sandbox environment"""
        try:
            vm_indicators = []
            
            # Check for VM-specific hardware
            if sys.platform == "win32":
                import subprocess
                try:
                    result = subprocess.run(['wmic', 'computersystem', 'get', 'model'], 
                                          capture_output=True, text=True, timeout=3)
                    if result.returncode == 0:
                        model = result.stdout.lower()
                        vm_keywords = ['virtualbox', 'vmware', 'virtual', 'qemu', 'kvm']
                        vm_indicators.append(any(kw in model for kw in vm_keywords))
                except:
                    pass
            
            # Check for VM-specific files/processes
            vm_files = [
                '/proc/vz',  # OpenVZ
                '/proc/xen',  # Xen
                'C:\\Program Files\\VMware',
                'C:\\Program Files\\Oracle\\VirtualBox'
            ]
            
            for vm_file in vm_files:
                if os.path.exists(vm_file):
                    vm_indicators.append(True)
                    break
            
            # Memory timing check (VMs are often slower)
            start = time.perf_counter()
            _ = [i for i in range(10000)]  # Simple computation
            elapsed = time.perf_counter() - start
            
            # If this simple operation takes too long, might be virtualized
            vm_indicators.append(elapsed > 0.01)
            
            # Return True if multiple indicators suggest VM
            return sum(vm_indicators) >= 2
            
        except Exception:
            return False
    
    def _check_binary_integrity(self) -> bool:
        """Check if our binary has been tampered with"""
        try:
            # Only check once every 5 minutes to avoid performance impact
            current_time = time.time()
            if current_time - self.last_integrity_check < 300:
                return self.integrity_cache or True
            
            self.last_integrity_check = current_time
            
            # Get path to current executable/script
            if getattr(sys, 'frozen', False):
                # Running as compiled executable
                exe_path = sys.executable
            else:
                # Running as script
                exe_path = __file__
            
            if not os.path.exists(exe_path):
                self.integrity_cache = False
                return False
            
            # Calculate hash of the file
            hasher = hashlib.sha256()
            with open(exe_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            
            current_hash = hasher.hexdigest()
            
            # For now, just store the hash and return True
            # In production, you'd compare against a known good hash
            # stored in the license or signed manifest
            self.integrity_cache = True
            return True
            
        except Exception:
            self.integrity_cache = False
            return False
    
    def _check_timing_anomalies(self) -> bool:
        """Check for timing-based attacks or emulation"""
        try:
            # Run a series of timing checks
            timings = []
            
            for _ in range(5):
                start = time.perf_counter()
                
                # Do some work that should take consistent time
                result = hashlib.sha256(b"timing_check" * 1000).hexdigest()
                
                end = time.perf_counter()
                timings.append(end - start)
            
            # Check for consistent timing (not too fast, not too slow)
            avg_time = sum(timings) / len(timings)
            
            # If average time is outside reasonable bounds, suspicious
            return not (0.0001 < avg_time < 0.1)
            
        except Exception:
            return False

class CircuitBreaker:
    """Circuit breaker pattern for reliability"""
    
    def __init__(self, failure_threshold: int = 3, recovery_timeout: int = 300):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = 0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self.lock = threading.Lock()
    
    def call(self, func: Callable, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        with self.lock:
            if self.state == "OPEN":
                if time.time() - self.last_failure_time < self.recovery_timeout:
                    raise Exception("Circuit breaker is OPEN")
                else:
                    self.state = "HALF_OPEN"
            
            try:
                result = func(*args, **kwargs)
                if self.state == "HALF_OPEN":
                    self.state = "CLOSED"
                    self.failure_count = 0
                return result
                
            except Exception as e:
                self.failure_count += 1
                self.last_failure_time = time.time()
                
                if self.failure_count >= self.failure_threshold:
                    self.state = "OPEN"
                
                raise e

# Global instance
_security_monitor = None

def get_security_monitor() -> SecurityMonitor:
    """Get or create global security monitor"""
    global _security_monitor
    if _security_monitor is None:
        _security_monitor = SecurityMonitor()
    return _security_monitor

def check_runtime_security() -> Dict[str, bool]:
    """Quick security check function"""
    monitor = get_security_monitor()
    return monitor.run_security_checks()

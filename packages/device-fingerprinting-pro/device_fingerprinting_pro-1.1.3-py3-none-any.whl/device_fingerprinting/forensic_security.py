"""
Advanced anti-tampering and forensic analysis for device fingerprinting.

Detects virtualization, debugging, and provides tamper evidence.
"""

import os
import sys
import time
import hashlib
from typing import Dict, Any, List, Tuple
from ..backends import SecurityCheck

class ForensicSecurityCheck(SecurityCheck):
    """
    Advanced security check with forensic capabilities.
    
    Detects:
    - Virtual machines and containers
    - Debuggers and analysis tools  
    - Code tampering and injection
    - Timing anomalies
    - Hardware inconsistencies
    """
    
    def __init__(self, paranoia_level: int = 3):
        """
        Initialize forensic security check.
        
        Args:
            paranoia_level: 1-5 (higher = more checks, slower)
        """
        self.paranoia_level = paranoia_level
        self.checks_performed = []
        self.evidence_log = []
    
    def check(self) -> Tuple[bool, str]:
        """Perform comprehensive security analysis"""
        suspicious_score = 0
        max_score = 0
        
        checks = [
            self._check_virtualization,
            self._check_debugger_presence,
            self._check_code_integrity,
            self._check_timing_anomalies,
            self._check_process_hollowing,
        ]
        
        if self.paranoia_level >= 4:
            checks.extend([
                self._check_hardware_consistency,
                self._check_memory_layout,
                self._check_system_calls,
            ])
        
        for check_func in checks:
            try:
                is_suspicious, score, evidence = check_func()
                suspicious_score += score if is_suspicious else 0
                max_score += score
                
                self.checks_performed.append(check_func.__name__)
                if evidence:
                    self.evidence_log.append(evidence)
                    
            except Exception as e:
                # Even check failures are suspicious
                suspicious_score += 1
                self.evidence_log.append(f"Check {check_func.__name__} failed: {type(e).__name__}")
        
        # Calculate suspicion ratio
        suspicion_ratio = suspicious_score / max(max_score, 1)
        
        if suspicion_ratio > 0.5:
            return True, f"high_suspicion_score_{int(suspicion_ratio * 100)}"
        elif suspicion_ratio > 0.3:
            return True, f"medium_suspicion_score_{int(suspicion_ratio * 100)}"
        else:
            return False, "security_checks_passed"
    
    def _check_virtualization(self) -> Tuple[bool, int, str]:
        """Detect virtual machine or container environment"""
        vm_indicators = []
        
        # Check for VM-specific hardware
        try:
            import platform
            system_info = platform.uname()
            
            vm_signatures = [
                'vmware', 'virtualbox', 'qemu', 'xen', 'kvm',
                'bochs', 'parallels', 'hyperv', 'docker'
            ]
            
            for signature in vm_signatures:
                if signature in str(system_info).lower():
                    vm_indicators.append(f"vm_signature_{signature}")
        except:
            pass
        
        # Check MAC address prefixes (VM vendors use specific ranges)
        try:
            import uuid
            mac = uuid.getnode()
            mac_str = f"{mac:012x}"
            
            vm_mac_prefixes = [
                '000569',  # VMware
                '080027',  # VirtualBox
                '525400',  # QEMU
                '001c42',  # Parallels
            ]
            
            for prefix in vm_mac_prefixes:
                if mac_str.startswith(prefix):
                    vm_indicators.append(f"vm_mac_{prefix}")
        except:
            pass
        
        # Check for VM-specific processes (Windows)
        if os.name == 'nt':
            try:
                import psutil
                vm_processes = [
                    'vmtoolsd.exe', 'vboxservice.exe', 'vboxtray.exe',
                    'vmwaretray.exe', 'vmwareuser.exe'
                ]
                
                for proc in psutil.process_iter(['name']):
                    if proc.info['name'] and proc.info['name'].lower() in vm_processes:
                        vm_indicators.append(f"vm_process_{proc.info['name']}")
            except:
                pass
        
        is_vm = len(vm_indicators) > 0
        evidence = f"vm_indicators: {vm_indicators}" if is_vm else ""
        
        return is_vm, 3, evidence
    
    def _check_debugger_presence(self) -> Tuple[bool, int, str]:
        """Detect debugger attachment or analysis tools"""
        debugger_signs = []
        
        # Windows debugger detection
        if os.name == 'nt':
            try:
                import ctypes
                
                # Check IsDebuggerPresent
                if ctypes.windll.kernel32.IsDebuggerPresent():
                    debugger_signs.append("windows_debugger_present")
                
                # Check for debug heap
                heap_flags = ctypes.c_ulong()
                ctypes.windll.kernel32.GetProcessHeap()
                # More sophisticated heap analysis would go here
                
            except:
                pass
        
        # Check for common analysis tools
        try:
            import psutil
            analysis_tools = [
                'ollydbg.exe', 'x64dbg.exe', 'windbg.exe', 'ida.exe', 'ida64.exe',
                'cheatengine.exe', 'processhacker.exe', 'procmon.exe', 'wireshark.exe'
            ]
            
            for proc in psutil.process_iter(['name']):
                if proc.info['name'] and proc.info['name'].lower() in analysis_tools:
                    debugger_signs.append(f"analysis_tool_{proc.info['name']}")
        except:
            pass
        
        # Timing-based debugger detection
        start_time = time.time()
        # Perform some operations that debuggers slow down
        for i in range(1000):
            hash(i)
        elapsed = time.time() - start_time
        
        if elapsed > 0.01:  # Suspiciously slow
            debugger_signs.append(f"timing_anomaly_{elapsed:.4f}")
        
        is_debugged = len(debugger_signs) > 0
        evidence = f"debugger_signs: {debugger_signs}" if is_debugged else ""
        
        return is_debugged, 4, evidence
    
    def _check_code_integrity(self) -> Tuple[bool, int, str]:
        """Verify code hasn't been tampered with"""
        integrity_issues = []
        
        try:
            # Check if running from expected location
            current_file = __file__
            if 'temp' in current_file.lower() or 'appdata' in current_file.lower():
                integrity_issues.append("suspicious_execution_location")
            
            # Check module loading anomalies
            loaded_modules = list(sys.modules.keys())
            suspicious_modules = [
                'frida', 'winappdbg', 'pykd', 'volatility', 'capstone'
            ]
            
            for module in suspicious_modules:
                if any(module in mod.lower() for mod in loaded_modules):
                    integrity_issues.append(f"suspicious_module_{module}")
            
            # Check for code injection indicators
            if hasattr(sys, 'ps1'):  # Interactive interpreter
                integrity_issues.append("interactive_interpreter")
            
        except Exception as e:
            integrity_issues.append(f"integrity_check_failed_{type(e).__name__}")
        
        is_tampered = len(integrity_issues) > 0
        evidence = f"integrity_issues: {integrity_issues}" if is_tampered else ""
        
        return is_tampered, 2, evidence
    
    def _check_timing_anomalies(self) -> Tuple[bool, int, str]:
        """Detect timing-based attacks or analysis"""
        timing_issues = []
        
        # Measure execution time variance
        times = []
        for _ in range(10):
            start = time.perf_counter()
            # Simple operation
            hashlib.sha256(b"timing_test").hexdigest()
            times.append(time.perf_counter() - start)
        
        # Check for excessive variance (debugging/analysis)
        avg_time = sum(times) / len(times)
        max_time = max(times)
        
        if max_time > avg_time * 5:  # 5x variance is suspicious
            timing_issues.append(f"execution_variance_{max_time/avg_time:.2f}")
        
        if avg_time > 0.001:  # Suspiciously slow for simple hash
            timing_issues.append(f"slow_execution_{avg_time:.6f}")
        
        has_anomalies = len(timing_issues) > 0
        evidence = f"timing_issues: {timing_issues}" if has_anomalies else ""
        
        return has_anomalies, 2, evidence
    
    def _check_process_hollowing(self) -> Tuple[bool, int, str]:
        """Detect process hollowing or injection"""
        hollowing_signs = []
        
        try:
            # Check process memory layout
            import os
            pid = os.getpid()
            
            # On Windows, check for suspicious memory regions
            if os.name == 'nt':
                try:
                    import ctypes
                    from ctypes import wintypes
                    
                    # Check for executable memory regions that don't match our image
                    # This is a simplified check - full implementation would be more complex
                    
                    # Check if our process name matches expected
                    import psutil
                    proc = psutil.Process(pid)
                    if 'python' not in proc.name().lower():
                        hollowing_signs.append(f"unexpected_process_name_{proc.name()}")
                        
                except:
                    pass
            
        except Exception as e:
            hollowing_signs.append(f"hollowing_check_failed_{type(e).__name__}")
        
        is_hollowed = len(hollowing_signs) > 0
        evidence = f"hollowing_signs: {hollowing_signs}" if is_hollowed else ""
        
        return is_hollowed, 3, evidence
    
    def _check_hardware_consistency(self) -> Tuple[bool, int, str]:
        """Check for hardware inconsistencies (paranoia level 4+)"""
        inconsistencies = []
        
        # This would implement more sophisticated hardware validation
        # For now, basic checks
        
        try:
            import platform
            
            # Check if CPU info is consistent
            cpu_count_methods = [
                os.cpu_count(),
                len(os.sched_getaffinity(0)) if hasattr(os, 'sched_getaffinity') else None
            ]
            
            cpu_counts = [c for c in cpu_count_methods if c is not None]
            if len(set(cpu_counts)) > 1:
                inconsistencies.append(f"cpu_count_mismatch_{cpu_counts}")
                
        except:
            pass
        
        has_inconsistencies = len(inconsistencies) > 0
        evidence = f"hw_inconsistencies: {inconsistencies}" if has_inconsistencies else ""
        
        return has_inconsistencies, 1, evidence
    
    def _check_memory_layout(self) -> Tuple[bool, int, str]:
        """Check memory layout for anomalies (paranoia level 4+)"""
        # Advanced memory layout analysis would go here
        return False, 1, ""
    
    def _check_system_calls(self) -> Tuple[bool, int, str]:
        """Monitor system call patterns (paranoia level 4+)"""
        # System call monitoring would go here
        return False, 1, ""
    
    def get_forensic_report(self) -> Dict[str, Any]:
        """Generate detailed forensic report"""
        return {
            'checks_performed': self.checks_performed,
            'evidence_collected': self.evidence_log,
            'paranoia_level': self.paranoia_level,
            'timestamp': time.time(),
            'system_info': {
                'platform': os.name,
                'python_version': sys.version,
                'executable': sys.executable
            }
        }

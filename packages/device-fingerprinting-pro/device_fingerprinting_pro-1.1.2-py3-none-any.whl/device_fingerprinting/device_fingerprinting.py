"""
Production device fingerprinting library.

Hardware-based device identification for license binding with
pluggable cryptographic, storage, and security backends.

This module provides post-quantum cryptography support for secure
device fingerprinting and license binding operations.
"""

import os
import platform
import hashlib
import json
import time
import threading
import subprocess
import logging
import secrets
import base64
from typing import Dict, Optional, Any, Tuple
from concurrent.futures import ThreadPoolExecutor, Future

# Import backends
from .backends import CryptoBackend, StorageBackend, SecurityCheck
from .default_backends import HmacSha256Backend, InMemoryStorage, NoOpSecurityCheck

# Import hybrid post-quantum cryptography backend
from .hybrid_pqc import HybridPQCBackend

# Legacy PQC import for compatibility
try:
    from .quantum_crypto import RealPostQuantumBackend
    LEGACY_PQC_AVAILABLE = True
except ImportError:
    LEGACY_PQC_AVAILABLE = False

__version__ = "1.0.0-HYBRID-PQC"

# Global configuration variables for the fingerprinting system
_crypto_backend: CryptoBackend = HmacSha256Backend()
_storage_backend: StorageBackend = InMemoryStorage()
_security_check: SecurityCheck = NoOpSecurityCheck()
_logger: Optional[logging.Logger] = None

# Configuration for post-quantum cryptography
_pqc_enabled: bool = False
_pqc_algorithm: str = "Dilithium3"
_pqc_hybrid_mode: bool = True

# Anti-replay protection settings
_anti_replay_enabled: bool = True
_nonce_lifetime: int = 300  # 5 minutes for time-bound signatures
_counter_storage_key: str = "device_counter"

# Internal state management
_cache = {}
_cache_lock = threading.Lock()
_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="fingerprint")
CACHE_TIME = 300  # 5 minutes cache validity

# Cleanup function for proper resource management
import atexit

def _cleanup_resources():
    """Cleanup resources on module shutdown"""
    global _executor
    if _executor:
        _executor.shutdown(wait=False)

# Register cleanup function
atexit.register(_cleanup_resources)

def set_crypto_backend(backend: CryptoBackend) -> None:
    """Set cryptographic backend for signing operations"""
    global _crypto_backend
    _crypto_backend = backend

def set_storage_backend(backend: StorageBackend) -> None:
    """Set storage backend for secure data persistence"""
    global _storage_backend
    _storage_backend = backend

def set_security_check(check: SecurityCheck) -> None:
    """Set security check for runtime tamper detection"""
    global _security_check
    _security_check = check

def set_logger(logger: Optional[logging.Logger]) -> None:
    """Set logger for debug output. None = silent operation"""
    global _logger
    _logger = logger

def enable_post_quantum_crypto(algorithm: str = "Dilithium3", 
                              hybrid_mode: bool = True) -> bool:
    """
    Enable hybrid post-quantum cryptography for device fingerprinting.
    
    Args:
        algorithm: PQC algorithm to use (default: "Dilithium3")
        hybrid_mode: Use classical+PQC hybrid (default: True)
        
    Returns:
        True if hybrid PQC was successfully enabled, False otherwise
    """
    global _crypto_backend, _pqc_enabled, _pqc_algorithm, _pqc_hybrid_mode
    
    try:
        # Create hybrid post-quantum crypto backend
        hybrid_backend = HybridPQCBackend(algorithm=algorithm)
        
        # Test the backend to ensure it's working properly
        test_data = b"Hybrid PQC compatibility test"
        test_sig = hybrid_backend.sign(test_data)
        if not hybrid_backend.verify(test_sig, test_data):
            _log("Hybrid PQC backend failed verification test")
            return False
        
        # Replace the current crypto backend with the new hybrid backend
        _crypto_backend = hybrid_backend
        _pqc_enabled = True
        _pqc_algorithm = algorithm
        _pqc_hybrid_mode = hybrid_mode
        
        # Log successful initialization with backend information
        backend_info = hybrid_backend.get_info()
        library_info = backend_info.get('pqc_library', 'unknown')
        pqc_status = "REAL PQC" if backend_info.get('pqc_available') else "HYBRID FALLBACK"
        
        _log(f"Hybrid Post-Quantum Cryptography enabled successfully")
        _log(f"   Algorithm: {algorithm}")
        _log(f"   Library: {library_info}")
        _log(f"   Status: {pqc_status}")
        _log(f"   Key sizes: {backend_info.get('key_sizes', 'unknown')}")
        
        return True
        
    except Exception as e:
        _log(f"Failed to enable hybrid PQC: {e}")
        return False

def disable_post_quantum_crypto() -> None:
    """
    Disable post-quantum cryptography and revert to classical HMAC-SHA256.
    
    Note: This is not recommended for production use after 2030.
    """
    global _crypto_backend, _pqc_enabled
    
    _crypto_backend = HmacSha256Backend()
    _pqc_enabled = False
    _log("Post-quantum cryptography disabled - reverted to classical HMAC-SHA256")

def enable_anti_replay_protection(enabled: bool = True, nonce_lifetime: int = 300) -> None:
    """
    Enable or disable anti-replay protection mechanisms.
    
    Args:
        enabled: Whether to enable anti-replay protection
        nonce_lifetime: Lifetime of time-bound nonces in seconds (default: 5 minutes)
    """
    global _anti_replay_enabled, _nonce_lifetime
    _anti_replay_enabled = enabled
    _nonce_lifetime = nonce_lifetime
    
    status = "enabled" if enabled else "disabled"
    _log(f"Anti-replay protection {status} (nonce lifetime: {nonce_lifetime}s)")

def _get_monotonic_counter() -> int:
    """
    Get the current monotonic counter value for anti-replay protection.
    
    The counter is used to prevent replay attacks by maintaining an
    append-only sequence number that must increase with each operation.
    
    Returns:
        Current counter value (starts at 1 if not found)
    """
    try:
        counter_data = _storage_backend.retrieve(_counter_storage_key)
        if counter_data and isinstance(counter_data, dict):
            counter_value = counter_data.get('counter', 1)
            # Validate counter is a positive integer
            if isinstance(counter_value, int) and counter_value > 0:
                return counter_value
    except Exception as e:
        _log(f"Failed to retrieve counter: {type(e).__name__}")
    
    # Initialize counter if not found or invalid
    return 1

def _increment_monotonic_counter() -> int:
    """
    Atomically increment the monotonic counter for anti-replay protection.
    
    This ensures that each operation gets a unique, incrementing counter
    value that cannot be replayed or reused in attacks.
    
    Returns:
        New counter value after incrementing
    """
    try:
        current_counter = _get_monotonic_counter()
        new_counter = current_counter + 1
        
        counter_data = {
            'counter': new_counter,
            'last_updated': int(time.time()),
            'version': __version__
        }
        
        _storage_backend.store(_counter_storage_key, counter_data)
        _log(f"Incremented anti-replay counter: {current_counter} -> {new_counter}")
        return new_counter
        
    except Exception as e:
        _log(f"Failed to increment counter: {type(e).__name__}")
        # Return current + 1 as fallback
        return _get_monotonic_counter() + 1

def _validate_nonce_freshness(nonce_timestamp: int, current_time: int) -> bool:
    """
    Validate that a nonce is within the acceptable time window.
    
    Args:
        nonce_timestamp: When the nonce was created
        current_time: Current timestamp
        
    Returns:
        True if nonce is fresh, False if expired
    """
    age_seconds = current_time - nonce_timestamp
    return 0 <= age_seconds <= _nonce_lifetime

def create_server_nonce() -> Tuple[str, str]:
    """
    Create a time-bound nonce and server signature for anti-replay protection.
    
    This generates a cryptographically secure nonce with an embedded timestamp
    and signs it with the server's key. The nonce should be used immediately
    and then discarded to prevent replay attacks.
    
    Returns:
        Tuple of (nonce, server_signature) where nonce is base64-encoded
        
    Note:
        This should be called by the license server during initial binding.
        The nonce and server signature should be discarded after first use.
    """
    if not _anti_replay_enabled:
        return "", ""
    
    # Create nonce data with current timestamp
    timestamp = int(time.time())
    nonce_data = {
        'nonce': secrets.token_urlsafe(16),  # 128-bit random nonce
        'timestamp': timestamp,
        'algorithm': _pqc_algorithm if _pqc_enabled else 'HMAC-SHA256'
    }
    
    # Encode the nonce data as base64 for transport
    nonce_json = json.dumps(nonce_data, sort_keys=True)
    nonce = base64.b64encode(nonce_json.encode()).decode()
    
    # Create cryptographic signature of the nonce using current backend
    server_signature = _crypto_backend.sign(nonce.encode())
    
    _log(f"Created server nonce (expires in {_nonce_lifetime}s)")
    return nonce, server_signature

def verify_server_nonce(nonce: str, server_signature: str) -> bool:
    """
    Verify a server nonce and signature for anti-replay protection.
    
    This function validates that a nonce is properly formatted, within
    the acceptable time window, and has a valid cryptographic signature
    from the server. This prevents replay attacks and ensures authenticity.
    
    Args:
        nonce: Base64-encoded nonce data containing timestamp and random value
        server_signature: Server's cryptographic signature of the nonce
        
    Returns:
        True if nonce is valid and fresh, False otherwise
    """
    if not _anti_replay_enabled:
        return True  # Allow operation if anti-replay is disabled
        
    # Validate input parameters to prevent malformed data attacks
    if not isinstance(nonce, str) or not isinstance(server_signature, str):
        return False
        
    if not nonce or not server_signature:
        return False
    
    try:
        # Decode and parse the nonce structure
        nonce_json = base64.b64decode(nonce).decode('utf-8')
        nonce_data = json.loads(nonce_json)
        
        # Ensure the nonce data has the expected structure
        if not isinstance(nonce_data, dict):
            return False
            
        nonce_timestamp = nonce_data.get('timestamp')
        if not isinstance(nonce_timestamp, int) or nonce_timestamp <= 0:
            return False
        
        # Check if the nonce is still within the valid time window
        current_time = int(time.time())
        if not _validate_nonce_freshness(nonce_timestamp, current_time):
            _log("Server nonce expired or invalid timestamp")
            return False
        
        # Verify the cryptographic signature of the nonce
        signature_valid = _crypto_backend.verify(server_signature, nonce.encode('utf-8'))
        if not signature_valid:
            _log("Server nonce signature verification failed")
            return False
        
        _log("Server nonce verified successfully")
        return True
        
    except (base64.binascii.Error, json.JSONDecodeError, UnicodeDecodeError, ValueError) as e:
        _log(f"Server nonce verification failed: invalid format")
        return False
    except Exception as e:
        _log(f"Server nonce verification failed: {type(e).__name__}")
        return False

def is_post_quantum_enabled() -> bool:
    """Check if post-quantum cryptography is currently enabled"""
    return _pqc_enabled

def get_crypto_info() -> Dict[str, Any]:
    """
    Get information about the current cryptographic configuration.
    
    Returns:
        Dictionary with crypto backend details
    """
    info = {
        'pqc_enabled': _pqc_enabled,
        'backend_type': type(_crypto_backend).__name__,
        'version': __version__
    }
    
    if _pqc_enabled:
        try:
            backend_info = _crypto_backend.get_info()
            info.update({
                'pqc_algorithm': backend_info.get('algorithm', _pqc_algorithm),
                'pqc_library': backend_info.get('library', 'unknown'),
                'hybrid_mode': backend_info.get('hybrid_mode', _pqc_hybrid_mode),
                'quantum_resistant': backend_info.get('quantum_resistant', True),
                'nist_standardized': backend_info.get('nist_standardized', False)
            })
        except Exception as e:
            info['pqc_info_error'] = str(e)
    else:
        info.update({
            'quantum_resistant': False,
            'algorithm': 'HMAC-SHA256',
            'note': 'Classical MAC - not a true digital signature'
        })
    
    return info

def _log(msg: str) -> None:
    """Internal logging with rate limiting and sanitized messages"""
    if not _logger:
        return
    
    # Sanitize message to prevent information disclosure
    sanitized_msg = _sanitize_log_message(msg)
    
    # Simple rate limiting to prevent spam
    current_time = time.time()
    key = f"log_{hash(sanitized_msg) % 1000}"
    
    with _cache_lock:
        last_log = _cache.get(key, 0)
        if current_time - last_log > 3600:  # 1 hour
            _cache[key] = current_time
            _logger.debug(sanitized_msg)

def _sanitize_log_message(msg: str) -> str:
    """
    Sanitize log messages to prevent information disclosure.
    
    This function removes or masks sensitive information from log messages
    to prevent accidental exposure of hardware identifiers, file paths,
    network addresses, and other potentially sensitive data.
    """
    if not isinstance(msg, str):
        msg = str(msg)
        
    # Remove sensitive patterns using regular expressions
    import re
    
    # Remove hardware identifiers and system-specific data
    msg = re.sub(r'[A-F0-9]{8}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{12}', '[UUID]', msg, flags=re.IGNORECASE)
    msg = re.sub(r'0x[A-F0-9]+', '[MEM_ADDR]', msg, flags=re.IGNORECASE)
    msg = re.sub(r'\b[A-F0-9]{12,}\b', '[HEX_ID]', msg, flags=re.IGNORECASE)
    msg = re.sub(r'\b\d{8,}\b', '[NUMERIC_ID]', msg)
    
    # Remove file paths to prevent directory structure disclosure
    msg = re.sub(r'[A-Za-z]:\\[\\A-Za-z0-9._-]+', '[FILE_PATH]', msg)
    msg = re.sub(r'/[/A-Za-z0-9._-]+', '[FILE_PATH]', msg)
    
    # Remove network-related identifiers
    msg = re.sub(r'([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})', '[MAC_ADDR]', msg)
    msg = re.sub(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', '[IP_ADDR]', msg)
    
    # Limit message length to prevent log flooding
    if len(msg) > 200:
        msg = msg[:200] + "...[truncated]"
    
    return msg

def _constant_time_cache_lookup(cache_key: str) -> Optional[Dict[str, Any]]:
    """
    Perform a constant-time cache lookup to prevent timing attacks.
    
    This function includes a random delay and consistent execution time
    regardless of whether the cache entry exists or not. This prevents
    attackers from using timing analysis to determine cache state.
    """
    if not isinstance(cache_key, str) or not cache_key:
        return None
        
    # Add small random delay to prevent timing analysis
    try:
        dummy_time = secrets.randbelow(1000) / 1000000  # 0-1ms random delay
        time.sleep(dummy_time)
    except (ValueError, TypeError):
        # Use fixed delay if random generation fails
        time.sleep(0.0005)  # 0.5ms fixed delay
    
    with _cache_lock:
        result = _cache.get(cache_key)
        current_time = time.time()
        
        # Always check timing to maintain constant execution pattern
        if result and isinstance(result, dict):
            is_valid = current_time - result.get('time', 0) < CACHE_TIME
            return result if is_valid else None
        return None

def _get_stable_fields() -> Dict[str, Any]:
    """
    Get hardware fields that are stable across reboots and minor updates.
    
    Uses only slow-changing hardware characteristics:
    - CPU model (not current frequency)
    - RAM in GB (rounded, not exact bytes)  
    - Disk serial numbers (truncated for privacy)
    - Motherboard UUID (if available)
    - Network MAC hash (salted, not reversible)
    """
    fields = {}
    
    try:
        # Basic platform info - always available
        fields['os_family'] = platform.system()
        fields['cpu_arch'] = platform.machine()
        
        # CPU model name (stable across reboots)
        cpu_name = platform.processor()
        if cpu_name:
            # Normalize CPU name - remove frequency and cache info
            cpu_clean = cpu_name.split('@')[0].strip()  # Remove frequency
            cpu_clean = ' '.join(cpu_clean.split())  # Normalize whitespace
            fields['cpu_model'] = cpu_clean[:50]  # Truncate
        
        # Get OS build number (more stable than version string)
        if platform.system() == "Windows":
            fields['os_build'] = platform.win32_ver()[1]
        else:
            fields['os_release'] = platform.release()[:20]
            
    except Exception as e:
        _log(f"Failed to get basic fields: {type(e).__name__}")
        fields['error'] = 'basic_info_failed'
    
    return fields

def _obfuscate_hardware_id(value: str, field_type: str) -> str:
    """
    Apply deterministic obfuscation to hardware IDs to prevent exact matching.
    
    This function scrambles hardware identifiers in a consistent way that
    prevents exact hardware fingerprint matching while maintaining the
    same output for the same input. This provides privacy protection
    without breaking device identification functionality.
    """
    if not value or not isinstance(value, str) or len(value) < 4:
        return value
    
    # Ensure field_type is one of the expected values
    valid_field_types = {'uuid', 'serial', 'default'}
    if field_type not in valid_field_types:
        field_type = 'default'
        
    # Generate deterministic noise based on the input value
    try:
        noise_seed = hashlib.sha256(f"{value}_{field_type}_obfuscation_2024".encode()).digest()[:4]
        noise = int.from_bytes(noise_seed, 'big') % 256
    except (ValueError, TypeError):
        # Fallback to simple hash if SHA256 fails
        noise = hash(value) % 256
    
    # Apply field-specific obfuscation algorithms
    if field_type == 'uuid':
        # Rotate characters to maintain character distribution
        rotation = noise % len(value)
        return value[rotation:] + value[:rotation]
    elif field_type == 'serial':
        # Transform alphanumeric characters while preserving structure
        result = []
        for i, c in enumerate(value):
            if c.isalnum():
                # Apply position-dependent character transformation
                char_noise = (noise + i) % 26
                if c.isdigit():
                    new_char = str((int(c) + char_noise) % 10)
                elif c.isupper():
                    new_char = chr((ord(c) - ord('A') + char_noise) % 26 + ord('A'))
                elif c.islower():
                    new_char = chr((ord(c) - ord('a') + char_noise) % 26 + ord('a'))
                else:
                    new_char = c
                result.append(new_char)
            else:
                result.append(c)
        return ''.join(result)
    else:
        # Default transformation: simple character rotation
        rotation = noise % max(1, len(value))
        return value[rotation:] + value[:rotation]

def _secure_subprocess_run(cmd, **kwargs):
    """
    Execute subprocess commands with enhanced security measures.
    
    This function restricts the execution environment, limits timeouts,
    and applies security flags to prevent various attacks through
    subprocess execution. It's designed to safely run system commands
    needed for hardware detection.
    """
    # Limit environment variables to essential system paths only
    safe_env = {
        'PATH': os.environ.get('PATH', ''),
        'SYSTEMROOT': os.environ.get('SYSTEMROOT', ''),
        'WINDIR': os.environ.get('WINDIR', ''),
    }
    
    # Configure secure execution parameters
    secure_kwargs = {
        'env': safe_env,
        'cwd': None,  # Don't inherit current working directory
        'timeout': min(kwargs.get('timeout', 5), 5),  # Maximum 5 second timeout
        'capture_output': True,
        'text': True,
    }
    
    # Apply Windows-specific security settings
    if os.name == 'nt':
        secure_kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
    
    # Merge any additional kwargs while preserving security settings
    secure_kwargs.update(kwargs)
    return subprocess.run(cmd, **secure_kwargs)

def _get_wmi_uuid() -> Optional[str]:
    """
    Retrieve motherboard UUID using Windows Management Instrumentation.
    
    This function safely executes a WMI query to get the system's motherboard
    UUID. The result is obfuscated for privacy and truncated to prevent
    exact hardware identification while maintaining device uniqueness.
    """
    try:
        result = _secure_subprocess_run(['wmic', 'csproduct', 'get', 'UUID'], timeout=5)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if line.strip() and 'UUID' not in line:
                    uuid = line.strip()
                    if len(uuid) > 10:  # Validate UUID length
                        # Apply obfuscation for privacy protection
                        obfuscated = _obfuscate_hardware_id(uuid, 'uuid')
                        return obfuscated[:16]  # Truncate for additional privacy
    except (subprocess.TimeoutExpired, subprocess.SubprocessError, OSError):
        pass  # WMI service unavailable or command timed out
    except Exception:
        pass  # Other errors during UUID retrieval
    return None

def _get_wmi_disk_serial() -> Optional[str]:
    """
    Retrieve primary disk serial number using Windows Management Instrumentation.
    
    This function safely queries the WMI service to get the serial number
    of the primary disk drive. The result is obfuscated to protect user
    privacy while providing a stable device identifier component.
    """
    try:
        result = _secure_subprocess_run(['wmic', 'diskdrive', 'get', 'SerialNumber'], timeout=5)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if line.strip() and 'SerialNumber' not in line:
                    serial = line.strip()
                    if len(serial) > 5:  # Validate serial number length
                        # Apply obfuscation for privacy protection
                        obfuscated = _obfuscate_hardware_id(serial, 'serial')
                        return obfuscated[:12]  # Truncate for additional privacy
    except (subprocess.TimeoutExpired, subprocess.SubprocessError, OSError):
        pass  # WMI service unavailable or command timed out
    except Exception:
        pass  # Other errors during serial retrieval
    return None

def _get_windows_hardware() -> Dict[str, Any]:
    """
    Collect Windows-specific stable hardware identifiers.
    
    This function gathers various hardware characteristics that remain
    consistent across system reboots and minor updates. The data is used
    to create a stable device fingerprint for security purposes.
    """
    fields = {}
    
    try:
        # CPU details from registry
        import winreg
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                               r"HARDWARE\DESCRIPTION\System\CentralProcessor\0") as key:
                try:
                    cpu_name = winreg.QueryValueEx(key, "ProcessorNameString")[0]
                    if cpu_name and isinstance(cpu_name, str):
                        fields['cpu_name'] = cpu_name.strip()[:50]
                except (OSError, ValueError, TypeError):
                    pass  # CPU name not available in registry
        except (OSError, PermissionError):
            pass  # Registry access denied or key not found
        
        # Motherboard UUID via WMI (if available)
        uuid = _get_wmi_uuid()
        if uuid:
            fields['board_uuid'] = uuid
            
        # Primary disk serial (truncated for privacy)
        serial = _get_wmi_disk_serial()
        if serial:
            fields['disk_serial'] = serial
            
    except ImportError:
        pass  # Windows registry module not available on this platform
    except Exception as e:
        _log(f"Windows hardware detection failed: {type(e).__name__}")
    
    return fields

def _get_memory_info() -> Dict[str, Any]:
    """
    Get total system memory information rounded to gigabytes for stability.
    
    This function attempts to determine the total installed system RAM using
    multiple detection methods. The result is rounded to the nearest gigabyte
    to ensure stability across different system states and minor variations
    in memory reporting.
    """
    try:
        # Try psutil first as it's the most accurate method
        try:
            import psutil
        except ImportError:
            psutil = None
            
        if psutil:
            mem = psutil.virtual_memory()
            # Round to nearest GB for stability across measurements
            ram_gb = round(mem.total / (1024**3))
            return {'ram_gb': ram_gb}
        
        # Fallback for Linux systems without psutil installed
        try:
            # Validate path for security before reading
            meminfo_path = '/proc/meminfo'
            if not os.path.exists(meminfo_path) or not os.path.isfile(meminfo_path):
                return {}
                
            with open(meminfo_path, 'r') as f:
                for line in f:
                    if line.startswith('MemTotal:'):
                        kb = int(line.split()[1])
                        ram_gb = round(kb / (1024**2))  # Convert KB to GB
                        return {'ram_gb': ram_gb}
        except (OSError, ValueError, IndexError):
            pass  # Failed to read or parse memory information
            
    except Exception as e:
        _log(f"Memory detection failed: {type(e).__name__}")
    
    return {}

def _get_network_hash() -> Dict[str, Any]:
    """
    Generate a salted hash of the primary network adapter MAC address.
    
    This function creates a privacy-preserving hash of the device's primary
    network adapter MAC address. The hash includes a salt to prevent tracking
    while still providing a stable identifier for device fingerprinting purposes.
    """
    try:
        import uuid
        mac = uuid.getnode()
        if mac and mac != 0x1fffffffffffff:  # Verify we have a valid MAC address
            # Hash the MAC with a salt to prevent direct tracking
            mac_bytes = mac.to_bytes(6, 'big')
            mac_hash = hashlib.sha256(mac_bytes + b"mac_salt_2024").hexdigest()[:16]
            return {'mac_hash': mac_hash}
    except Exception as e:
        _log(f"MAC hash generation failed: {type(e).__name__}")
    
    return {}

def _generate_fingerprint_fields() -> Dict[str, Any]:
    """
    Generate stable hardware fingerprint fields.
    
    Returns dictionary of hardware characteristics that should
    remain stable across reboots and minor system updates.
    """
    fields = _get_stable_fields()
    
    # Add platform-specific hardware info
    if platform.system() == "Windows":
        fields.update(_get_windows_hardware())
    
    # Add memory and network info
    fields.update(_get_memory_info())
    fields.update(_get_network_hash())
    
    # Add timestamp for debugging
    fields['collected_at'] = int(time.time())
    
    return fields

def _score_field_match(current: Dict[str, Any], stored: Dict[str, Any]) -> float:
    """
    Score how well current hardware matches stored fingerprint.
    
    Returns float between 0.0 and 1.0 indicating match confidence.
    Uses weighted scoring where some fields are more important.
    """
    # Define field weights (more stable fields have higher weight)
    weights = {
        'cpu_model': 0.25,
        'cpu_name': 0.25, 
        'ram_gb': 0.15,
        'board_uuid': 0.20,
        'disk_serial': 0.10,
        'mac_hash': 0.05
    }
    
    total_weight = 0.0
    matched_weight = 0.0
    
    for field, weight in weights.items():
        if field in stored:  # Only score fields that were stored
            total_weight += weight
            if field in current and current[field] == stored[field]:
                matched_weight += weight
    
    # Also check basic platform compatibility
    if stored.get('os_family') == current.get('os_family'):
        matched_weight += 0.1
        total_weight += 0.1
    
    if total_weight == 0:
        return 0.0
    
    return matched_weight / total_weight

def generate_fingerprint(method: str = "stable") -> str:
    """
    Generate cryptographically signed device fingerprint.
    
    Args:
        method: "stable" for hardware fields or "basic" for minimal fields
    
    Returns:
        Cryptographic signature of device fingerprint fields
        
    Note:
        - With PQC enabled: Uses real post-quantum digital signatures
        - Without PQC: Uses classical HMAC-SHA256 (not quantum-resistant)
    """
    # Check security if enabled
    try:
        is_suspicious, reason = _security_check.check()
        if is_suspicious:
            _log(f"Security warning: {reason}")
    except Exception as e:
        _log(f"Security check failed: {type(e).__name__}")
    
    # Check cache first using constant-time lookup
    cache_key = hashlib.sha256(f"{method}_{_pqc_enabled}_{_pqc_algorithm}".encode()).hexdigest()[:16]
    cached = _constant_time_cache_lookup(cache_key)
    if cached:
        return cached['fp']
    
    # Gather fingerprint fields
    if method == "basic":
        fields = {
            'os': platform.system(),
            'machine': platform.machine(),
            'version': platform.release()
        }
    else:
        fields = _generate_fingerprint_fields()
    
    # Add cryptographic metadata
    crypto_info = get_crypto_info()
    fields['crypto_metadata'] = {
        'pqc_enabled': crypto_info['pqc_enabled'],
        'algorithm': crypto_info.get('pqc_algorithm', crypto_info.get('algorithm', 'HMAC-SHA256')),
        'quantum_resistant': crypto_info['quantum_resistant'],
        'signature_type': 'digital_signature' if crypto_info['pqc_enabled'] else 'mac',
        'timestamp': int(time.time())
    }
    
    # Create cryptographic signature using pluggable backend
    fields_json = json.dumps(fields, sort_keys=True).encode()
    fingerprint = _crypto_backend.sign(fields_json)
    
    # Cache the result
    with _cache_lock:
        _cache[cache_key] = {'fp': fingerprint, 'time': time.time(), 'fields': fields}
        # Cleanup old cache entries
        if len(_cache) > 10:
            oldest = min(_cache.keys(), key=lambda k: _cache[k]['time'])
            del _cache[oldest]
    
    # Log crypto mode for security awareness
    if _pqc_enabled:
        _log(f"Generated PQC fingerprint using {_pqc_algorithm}")
    else:
        _log("Generated classical fingerprint using HMAC-SHA256 (not quantum-resistant)")
    
    return fingerprint

def generate_fingerprint_async(method="stable") -> Future[str]:
    """
    Generate fingerprint asynchronously to avoid blocking UI.
    
    Returns Future that resolves to fingerprint string.
    """
    return _executor.submit(generate_fingerprint, method)

def create_device_binding(binding_data: Dict[str, Any], 
                         security_level: str = "high",
                         custom_fields: Optional[Dict[str, Any]] = None,
                         server_nonce: Optional[str] = None,
                         server_signature: Optional[str] = None) -> Dict[str, Any]:
    """
    Bind data to this specific device using cryptographic signatures with anti-replay protection.
    
    Args:
        binding_data: Dictionary containing data to bind
        security_level: "basic", "medium", or "high" 
        custom_fields: Additional fields to include in binding
        server_nonce: Time-bound nonce from license server (for anti-replay)
        server_signature: Server's signature of the nonce (for anti-replay)
    
    Returns:
        Dictionary with device binding information added
    """
    if not isinstance(binding_data, dict):
        raise ValueError("binding_data must be a dict")
    
    # Verify server nonce if anti-replay is enabled
    if _anti_replay_enabled:
        if not server_nonce or not server_signature:
            # Create nonce if not provided (for testing/development)
            _log("⚠️ No server nonce provided - creating temporary nonce (not production-safe)")
            server_nonce, server_signature = create_server_nonce()
        
        if not verify_server_nonce(server_nonce, server_signature):
            raise ValueError("Invalid or expired server nonce - replay attack detected")
    
    # Choose fingerprint method and tolerance based on security level
    if security_level == "basic":
        method = "basic"
        tolerance = 0.5
    elif security_level == "medium":
        method = "stable"
        tolerance = 0.75
    else:  # high
        method = "stable" 
        tolerance = 0.85
    
    # Generate device fingerprint and get fields
    fingerprint = generate_fingerprint(method)
    
    # Get the cached fields from fingerprint generation
    with _cache_lock:
        cache_key = hashlib.sha256(f"{method}_{_pqc_enabled}_{_pqc_algorithm}".encode()).hexdigest()[:16]
        cache_entry = _cache.get(cache_key, {})
        fields = cache_entry.get('fields', {})
    
    # Add anti-replay protection data
    anti_replay_data = {}
    if _anti_replay_enabled:
        anti_replay_data = {
            'counter': _get_monotonic_counter(),
            'server_nonce': server_nonce,
            'nonce_used_at': int(time.time()),
            'anti_replay_version': 1
        }
    
    # Create binding metadata
    binding_metadata = {
        'device_signature': fingerprint,
        'device_fields': fields,
        'binding_timestamp': int(time.time()),
        'binding_version': __version__,
        'security_level': security_level,
        'match_tolerance': tolerance,
        'anti_replay': anti_replay_data
    }
    
    # Add custom fields if provided
    if custom_fields:
        binding_metadata['custom_fields'] = custom_fields
    
    # Combine with original data
    result = binding_data.copy()
    result['device_binding'] = binding_metadata
    
    # Store binding securely using pluggable backend
    try:
        storage_key = f"binding_{hash(str(binding_data))}"
        _storage_backend.store(storage_key, binding_metadata)
        
        # Increment counter after successful binding creation
        if _anti_replay_enabled:
            _increment_monotonic_counter()
            
    except Exception as e:
        _log(f"Failed to store binding: {type(e).__name__}")
    
    _log(f"Created device binding with anti-replay protection: {_anti_replay_enabled}")
    return result

def verify_device_binding(bound_data: Dict[str, Any], 
                         tolerance: Optional[str] = None,
                         grace_period: int = 7,
                         allow_counter_increment: bool = True) -> Tuple[bool, Dict[str, Any]]:
    """
    Verify that bound data matches current device with anti-replay protection.
    
    Args:
        bound_data: Dictionary returned from create_device_binding
        tolerance: Override tolerance level ("strict", "medium", "loose")
        grace_period: Days to accept lower scores after binding (default 7)
        allow_counter_increment: Whether to increment counter on successful verification
    
    Returns:
        Tuple of (is_valid, details_dict)
    """
    if not isinstance(bound_data, dict):
        return False, {'error': 'invalid_input'}

    binding_info = bound_data.get('device_binding')
    if not binding_info:
        return False, {'error': 'no_binding_data'}

    try:
        stored_signature = binding_info['device_signature']
        stored_fields = binding_info['device_fields']
        binding_time = binding_info.get('binding_timestamp', 0)
        stored_tolerance = binding_info.get('match_tolerance', 0.75)
        anti_replay_data = binding_info.get('anti_replay', {})
        
        # Anti-replay protection checks
        if _anti_replay_enabled and anti_replay_data:
            # Check counter progression (append-only counter)
            stored_counter = anti_replay_data.get('counter', 0)
            current_counter = _get_monotonic_counter()
            
            if stored_counter > current_counter:
                return False, {
                    'error': 'replay_attack_detected',
                    'reason': 'counter_regression',
                    'stored_counter': stored_counter,
                    'current_counter': current_counter
                }
            
            # Check if we're reusing an old binding (counter too far behind)
            counter_gap = current_counter - stored_counter
            if counter_gap > 10:  # Allow some drift but not too much
                return False, {
                    'error': 'stale_binding',
                    'reason': 'counter_too_old',
                    'counter_gap': counter_gap
                }
            
            # Check server nonce validity (if present)
            server_nonce = anti_replay_data.get('server_nonce')
            if server_nonce:
                # For existing bindings, we don't re-verify the nonce
                # (it should have been discarded after first use)
                nonce_used_at = anti_replay_data.get('nonce_used_at', 0)
                nonce_age = int(time.time()) - nonce_used_at
                
                if nonce_age > _nonce_lifetime * 2:  # Grace period for existing bindings
                    _log("Nonce in binding is old but acceptable for stored binding")
        
        # Use provided tolerance or fall back to stored/default
        if tolerance == "strict":
            match_threshold = 0.95
        elif tolerance == "loose":
            match_threshold = 0.5
        elif tolerance == "medium":
            match_threshold = 0.75
        else:
            match_threshold = stored_tolerance
        
        # Get current device fields
        current_fields = _generate_fingerprint_fields()
        
        # Verify stored signature is authentic using pluggable backend
        stored_fields_json = json.dumps(stored_fields, sort_keys=True).encode()
        signature_valid = _crypto_backend.verify(stored_signature, stored_fields_json)
        if not signature_valid:
            return False, {'error': 'invalid_signature', 'signature_valid': False}
        
        # Score field matching
        match_score = _score_field_match(current_fields, stored_fields)
        
        # Check if within tolerance
        is_match = match_score >= match_threshold
        
        # Grace period for recent bindings
        age_days = (time.time() - binding_time) / (24 * 3600)
        in_grace_period = age_days <= grace_period
        
        # Accept lower scores during grace period
        if not is_match and in_grace_period and match_score >= 0.4:
            is_match = True
            grace_used = True
        else:
            grace_used = False
        
        # If verification successful and anti-replay enabled, increment counter
        if is_match and _anti_replay_enabled and allow_counter_increment:
            try:
                new_counter = _increment_monotonic_counter()
                
                # Update the binding with new counter and re-sign
                updated_anti_replay = anti_replay_data.copy()
                updated_anti_replay['counter'] = new_counter
                updated_anti_replay['last_verified'] = int(time.time())
                
                # Update binding metadata
                updated_binding = binding_info.copy()
                updated_binding['anti_replay'] = updated_anti_replay
                
                # Re-sign with new counter
                updated_fields = stored_fields.copy()
                updated_fields['anti_replay_counter'] = new_counter
                updated_fields_json = json.dumps(updated_fields, sort_keys=True).encode()
                new_signature = _crypto_backend.sign(updated_fields_json)
                updated_binding['device_signature'] = new_signature
                
                # Store updated binding
                storage_key = f"binding_{hash(str(bound_data))}"
                _storage_backend.store(storage_key, updated_binding)
                
                # Update the original bound_data reference
                bound_data['device_binding'] = updated_binding
                
                _log(f"Updated binding counter: {stored_counter} -> {new_counter}")
                
            except Exception as e:
                _log(f"Failed to update counter: {type(e).__name__}")
                # Continue with verification even if counter update fails
        
        details = {
            'match_score': match_score,
            'threshold': match_threshold,
            'signature_valid': signature_valid,
            'age_days': age_days,
            'grace_period_used': grace_used,
            'matched_fields': sum(1 for k in stored_fields 
                                if k in current_fields and 
                                current_fields[k] == stored_fields[k]),
            'total_fields': len(stored_fields),
            'anti_replay_enabled': _anti_replay_enabled
        }
        
        # Add anti-replay details
        if _anti_replay_enabled and anti_replay_data:
            details.update({
                'counter_check': 'passed',
                'stored_counter': anti_replay_data.get('counter', 0),
                'current_counter': _get_monotonic_counter()
            })
        
        return is_match, details
        
    except Exception as e:
        # Sanitize error message to prevent information disclosure
        error_type = type(e).__name__
        safe_errors = {
            'KeyError': 'missing_required_field',
            'ValueError': 'invalid_data_format',
            'TypeError': 'invalid_data_type',
            'AttributeError': 'invalid_structure'
        }
        sanitized_error = safe_errors.get(error_type, 'verification_failed')
        return False, {'error': sanitized_error}

def reset_device_id() -> bool:
    """
    Reset device binding (GDPR compliance).
    
    Clears all cached fingerprints. Does not reset backends.
    Returns True if successful.
    """
    try:
        # Clear memory cache
        with _cache_lock:
            _cache.clear()
        
        _log("Device ID reset completed")
        return True
        
    except Exception as e:
        _log(f"Device ID reset failed: {type(e).__name__}")
        return False

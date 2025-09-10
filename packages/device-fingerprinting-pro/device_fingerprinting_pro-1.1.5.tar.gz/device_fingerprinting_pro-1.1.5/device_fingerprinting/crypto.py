"""
Cryptographic primitives for device fingerprinting.

Uses HMAC-SHA-256 for authentication instead of plain hashing.
Includes constant-time comparison and obfuscation helpers.
"""

import os
import hmac
import hashlib
import json
from typing import Optional, Tuple

class CryptoManager:
    """Handles cryptographic operations for device binding"""
    
    def __init__(self, key: Optional[bytes] = None):
        self.key = key or self._get_or_create_key()
    
    def _get_or_create_key(self) -> bytes:
        """Get existing key or create new one"""
        # For now, use a deterministic key derivation
        # In production, this should come from secure storage
        machine_id = self._get_machine_id()
        app_secret = b"correctpqc_v2024"
        
        # Derive key using PBKDF2
        return hashlib.pbkdf2_hmac('sha256', app_secret, machine_id, 100000)
    
    def _get_machine_id(self) -> bytes:
        """Get a stable machine identifier"""
        import platform
        try:
            # Try to get a stable machine ID
            if platform.system() == "Windows":
                import subprocess
                result = subprocess.run(['wmic', 'csproduct', 'get', 'UUID'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    for line in lines:
                        if line.strip() and 'UUID' not in line:
                            return line.strip().encode()
            
            # Fallback to hostname + some system info
            fallback = platform.node() + platform.machine() + platform.system()
            return fallback.encode()
            
        except Exception:
            # Last resort fallback
            return b"fallback_machine_id"
    
    def sign(self, data: bytes) -> str:
        """Create HMAC signature for data"""
        return hmac.new(self.key, data, hashlib.sha256).hexdigest()
    
    def verify(self, signature: str, data: bytes) -> bool:
        """Verify HMAC signature with constant-time comparison"""
        expected_sig = self.sign(data)
        return hmac.compare_digest(signature, expected_sig)
    
    def obfuscate(self, data: str) -> str:
        """Simple XOR obfuscation to hide fingerprint in memory dumps"""
        key_byte = self.key[0] % 256
        obfuscated = bytes(b ^ key_byte for b in data.encode())
        return obfuscated.hex()
    
    def deobfuscate(self, hex_data: str) -> str:
        """Reverse the XOR obfuscation"""
        try:
            obfuscated = bytes.fromhex(hex_data)
            key_byte = self.key[0] % 256
            original = bytes(b ^ key_byte for b in obfuscated)
            return original.decode()
        except Exception:
            return ""

# Global instance
_crypto_manager = None

def get_crypto_manager() -> CryptoManager:
    """Get or create global crypto manager"""
    global _crypto_manager
    if _crypto_manager is None:
        _crypto_manager = CryptoManager()
    return _crypto_manager

def sign_data(data: dict) -> str:
    """Sign a data dictionary with HMAC"""
    payload = json.dumps(data, sort_keys=True).encode()
    return get_crypto_manager().sign(payload)

def verify_signature(signature: str, data: dict) -> bool:
    """Verify HMAC signature of data dictionary"""
    payload = json.dumps(data, sort_keys=True).encode()
    return get_crypto_manager().verify(signature, payload)

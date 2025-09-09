"""
Default implementations of pluggable backends.

Provides basic implementations that work out of the box
without external dependencies.
"""

import os
import hmac
import hashlib
import json
import secrets
import time
from typing import Dict, Any, Optional, Tuple

from .backends import CryptoBackend, StorageBackend, SecurityCheck

class HmacSha256Backend(CryptoBackend):
    """HMAC-SHA256 crypto backend with enhanced key generation"""
    
    def __init__(self, key: Optional[bytes] = None):
        self.key = key or self._generate_secure_key()
    
    def _generate_secure_key(self) -> bytes:
        """Generate cryptographically secure key with multiple entropy sources"""
        # Gather multiple entropy sources for enhanced security
        system_entropy = os.urandom(32)
        time_entropy = int(time.time() * 1000000).to_bytes(8, 'big')
        process_entropy = os.getpid().to_bytes(4, 'big')
        random_entropy = secrets.token_bytes(16)
        
        # Combine all entropy sources
        combined_entropy = system_entropy + time_entropy + process_entropy + random_entropy
        
        # Use SHA-256 to derive final key from combined entropy
        return hashlib.sha256(combined_entropy).digest()
    
    def sign(self, data: bytes) -> str:
        return hmac.new(self.key, data, hashlib.sha256).hexdigest()
    
    def verify(self, signature: str, data: bytes) -> bool:
        expected = self.sign(data)
        return hmac.compare_digest(signature, expected)

class InMemoryStorage(StorageBackend):
    """Simple in-memory storage backend"""
    
    def __init__(self):
        self._data = {}
    
    def store(self, key: str, data: Dict[str, Any]) -> bool:
        try:
            self._data[key] = data.copy()
            return True
        except Exception:
            return False
    
    def load(self, key: str) -> Optional[Dict[str, Any]]:
        return self._data.get(key)
    
    def delete(self, key: str) -> bool:
        try:
            self._data.pop(key, None)
            return True
        except Exception:
            return False

class NoOpSecurityCheck(SecurityCheck):
    """No-op security check for default behavior"""
    
    def check(self) -> Tuple[bool, str]:
        return False, "no_checks_enabled"

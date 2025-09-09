"""
Abstract base classes for pluggable backends.

Defines interfaces for crypto, storage, and security checks
that applications can implement with their own backends.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Tuple

class CryptoBackend(ABC):
    """Interface for cryptographic operations"""
    
    @abstractmethod
    def sign(self, data: bytes) -> str:
        """Create signature for data"""
        pass
    
    @abstractmethod
    def verify(self, signature: str, data: bytes) -> bool:
        """Verify signature against data"""
        pass

class StorageBackend(ABC):
    """Interface for secure storage operations"""
    
    @abstractmethod
    def store(self, key: str, data: Dict[str, Any]) -> bool:
        """Store data under key"""
        pass
    
    @abstractmethod
    def load(self, key: str) -> Optional[Dict[str, Any]]:
        """Load data by key"""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete data by key"""
        pass

class SecurityCheck(ABC):
    """Interface for runtime security checks"""
    
    @abstractmethod
    def check(self) -> Tuple[bool, str]:
        """Run security check, return (is_suspicious, reason)"""
        pass

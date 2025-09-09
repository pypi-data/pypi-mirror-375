"""Test backend implementations"""

import pytest
import os
from device_fingerprinting.default_backends import HmacSha256Backend, InMemoryStorage, NoOpSecurityCheck

class TestHmacSha256Backend:
    """Test HMAC-SHA256 crypto backend"""
    
    def test_init_with_default_key(self):
        backend = HmacSha256Backend()
        assert len(backend.key) == 32
    
    def test_init_with_custom_key(self):
        key = b"test_key_32_bytes_long_exactly_"
        backend = HmacSha256Backend(key)
        assert backend.key == key
    
    def test_sign_and_verify(self):
        backend = HmacSha256Backend()
        data = b"test data"
        
        signature = backend.sign(data)
        assert isinstance(signature, str)
        assert len(signature) == 64  # SHA256 hex
        
        # Should verify correctly
        assert backend.verify(signature, data)
        
        # Should fail with different data
        assert not backend.verify(signature, b"different data")
    
    def test_different_keys_different_signatures(self):
        backend1 = HmacSha256Backend(b"key1" + b"0" * 28)
        backend2 = HmacSha256Backend(b"key2" + b"0" * 28)
        
        data = b"same data"
        sig1 = backend1.sign(data)
        sig2 = backend2.sign(data)
        
        assert sig1 != sig2
        assert backend1.verify(sig1, data)
        assert not backend2.verify(sig1, data)

class TestInMemoryStorage:
    """Test in-memory storage backend"""
    
    def test_store_and_load(self):
        storage = InMemoryStorage()
        data = {"test": "value", "number": 42}
        
        result = storage.store("test_key", data)
        assert result is True
        
        loaded = storage.load("test_key")
        assert loaded == data
        assert loaded is not data  # Should be a copy
    
    def test_load_nonexistent(self):
        storage = InMemoryStorage()
        result = storage.load("nonexistent")
        assert result is None
    
    def test_delete(self):
        storage = InMemoryStorage()
        storage.store("test_key", {"data": "value"})
        
        result = storage.delete("test_key")
        assert result is True
        
        # Should be gone
        assert storage.load("test_key") is None
    
    def test_delete_nonexistent(self):
        storage = InMemoryStorage()
        result = storage.delete("nonexistent")
        assert result is True  # Should not fail
    
    def test_isolation(self):
        storage1 = InMemoryStorage()
        storage2 = InMemoryStorage()
        
        storage1.store("key", {"instance": 1})
        storage2.store("key", {"instance": 2})
        
        assert storage1.load("key")["instance"] == 1
        assert storage2.load("key")["instance"] == 2

class TestNoOpSecurityCheck:
    """Test no-op security check"""
    
    def test_check_returns_safe(self):
        check = NoOpSecurityCheck()
        is_suspicious, reason = check.check()
        
        assert is_suspicious is False
        assert reason == "no_checks_enabled"
    
    def test_multiple_calls_consistent(self):
        check = NoOpSecurityCheck()
        
        for _ in range(5):
            is_suspicious, reason = check.check()
            assert is_suspicious is False
            assert reason == "no_checks_enabled"

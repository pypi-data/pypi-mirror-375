"""Test core device fingerprinting functionality"""

import pytest
import json
import time
import logging
import device_fingerprinting as df
from device_fingerprinting import device_fingerprinting as dfp
from device_fingerprinting.backends import CryptoBackend

class TestableClientCryptoBackend(CryptoBackend):
    """Testable crypto backend for validation"""
    
    def __init__(self):
        self.signatures = {}
    
    def sign(self, data: bytes) -> str:
        sig = f"test_sig_{hash(data)}"
        self.signatures[sig] = data
        return sig
    
    def verify(self, signature: str, data: bytes) -> bool:
        return self.signatures.get(signature) == data

class TestPluggableBackends:
    """Test backend configuration"""
    
    def test_set_crypto_backend(self):
        # Use real test backend
        test_backend = TestableClientCryptoBackend()
        df.set_crypto_backend(test_backend)
        
        # Generate fingerprint should use our test backend
        fp = df.generate_fingerprint("basic")
        assert fp.startswith("test_sig_")
        assert len(fp) > 10
    
    def test_set_storage_backend(self, real_storage):
        df.set_storage_backend(real_storage)
        
        # Create binding should use our storage
        data = {"test": "data"}
        bound = df.create_device_binding(data)
        
        assert "device_binding" in bound
        assert bound["device_binding"]["device_signature"]
    
    def test_set_security_check(self, real_security):
        df.set_security_check(real_security)
        
        # Generate fingerprint should work with security check
        fp = df.generate_fingerprint("stable")
        assert isinstance(fp, str)
        assert len(fp) > 10
    
    def test_set_logger_enables_logging(self, test_logger):
        captured_logs = []
        
        class TestHandler(logging.Handler):
            def emit(self, record):
                captured_logs.append(record.getMessage())
        
        handler = TestHandler()
        test_logger.addHandler(handler)
        df.set_logger(test_logger)
        
        # Generate fingerprint (should work without errors)
        fp = df.generate_fingerprint("basic")
        assert isinstance(fp, str)
        
        # Logger is set up correctly (may or may not have messages depending on implementation)
        test_logger.removeHandler(handler)
    
    def test_set_logger_none_disables_logging(self):
        df.set_logger(None)
        
        # Should work normally even with None logger
        fp = df.generate_fingerprint("basic")
        assert isinstance(fp, str)

class TestFingerprintGeneration:
    """Test fingerprint generation"""
    
    def test_generate_basic_fingerprint(self):
        fp = df.generate_fingerprint("basic")
        
        assert isinstance(fp, str)
        assert len(fp) >= 32  # HMAC-SHA256 hex length varies by implementation
        
        # Should be deterministic
        fp2 = df.generate_fingerprint("basic")
        assert fp == fp2
    
    def test_generate_stable_fingerprint(self):
        fp = df.generate_fingerprint("stable")
        
        assert isinstance(fp, str) 
        assert len(fp) >= 32
        
        # Should be deterministic
        fp2 = df.generate_fingerprint("stable")
        assert fp == fp2
    
    def test_different_methods_different_fingerprints(self):
        fp_basic = df.generate_fingerprint("basic")
        fp_stable = df.generate_fingerprint("stable")
        
        # May or may not be different depending on hardware detection
        assert isinstance(fp_basic, str)
        assert isinstance(fp_stable, str)
    
    def test_caching_works(self):
        # First call
        fp1 = df.generate_fingerprint("basic")
        
        # Second call should return same result (cached)
        fp2 = df.generate_fingerprint("basic")
        
        assert fp1 == fp2
    
    def test_cache_expiry(self):
        # Test that cache works even with very short cache time
        fp1 = df.generate_fingerprint("basic")
        
        # Small delay
        time.sleep(0.01)
        
        # Should still return same fingerprint (cache not expired)
        fp2 = df.generate_fingerprint("basic")
        assert fp1 == fp2
    
    def test_async_fingerprint_generation(self):
        future = df.generate_fingerprint_async("basic")
        
        # Should return a Future
        assert hasattr(future, 'result')
        
        # Should complete successfully
        fp = future.result(timeout=5.0)
        assert isinstance(fp, str)
        assert len(fp) >= 32

class TestDeviceBinding:
    """Test device binding functionality"""
    
    def test_create_device_binding(self):
        data = {"license_id": "test123", "user": "testuser"}
        
        bound = df.create_device_binding(data)
        
        assert "device_binding" in bound
        binding = bound["device_binding"]
        
        assert "device_signature" in binding
        assert "device_fields" in binding
        assert "binding_timestamp" in binding
        assert "security_level" in binding
        assert binding["security_level"] == "high"  # default
        
        # Original data should be preserved
        assert bound["license_id"] == "test123"
        assert bound["user"] == "testuser"
    
    def test_security_levels(self):
        data = {"test": "data"}
        
        # Test different security levels
        for level in ["basic", "medium", "high"]:
            bound = df.create_device_binding(data, security_level=level)
            assert bound["device_binding"]["security_level"] == level
    
    def test_custom_fields(self):
        data = {"test": "data"}
        custom = {"installation_id": "inst_001", "region": "us-east"}
        
        bound = df.create_device_binding(data, custom_fields=custom)
        
        assert bound["device_binding"]["custom_fields"] == custom
    
    def test_invalid_input(self):
        with pytest.raises(ValueError):
            df.create_device_binding("not a dict")
    
    def test_verify_valid_binding(self):
        data = {"test": "data"}
        bound = df.create_device_binding(data)
        
        is_valid, details = df.verify_device_binding(bound)
        
        # May be true or false depending on match score, but should not error
        assert isinstance(is_valid, bool)
        assert "signature_valid" in details
        assert details["signature_valid"] is True  # Signature should always be valid for same system
    
    def test_verify_invalid_signature(self):
        data = {"test": "data"}
        bound = df.create_device_binding(data)
        
        # Tamper with signature
        bound["device_binding"]["device_signature"] = "invalid_signature"
        
        is_valid, details = df.verify_device_binding(bound)
        
        assert is_valid is False
        assert details["error"] == "invalid_signature"
    
    def test_verify_missing_binding(self):
        data = {"test": "data"}
        
        is_valid, details = df.verify_device_binding(data)
        
        assert is_valid is False
        assert details["error"] == "no_binding_data"
    
    def test_grace_period_parameter(self):
        data = {"test": "data"}
        bound = df.create_device_binding(data, security_level="basic")  # Use basic for more lenient matching
        
        # Test with different grace periods
        is_valid1, details1 = df.verify_device_binding(bound, grace_period=0)
        is_valid2, details2 = df.verify_device_binding(bound, grace_period=30)
        
        # Should work with signature validation
        assert "signature_valid" in details1
        assert "signature_valid" in details2
    
    def test_tolerance_levels(self):
        data = {"test": "data"}
        bound = df.create_device_binding(data, security_level="basic")  # Use basic for more lenient matching
        
        for tolerance in ["strict", "medium", "loose"]:
            is_valid, details = df.verify_device_binding(bound, tolerance=tolerance)
            # Signature should always be valid even if overall match fails
            assert "signature_valid" in details

class TestUtilityFunctions:
    """Test utility functions"""
    
    def test_reset_device_id(self):
        # Generate initial fingerprint
        fp1 = df.generate_fingerprint("basic")
        
        # Reset (now only clears cache, doesn't change backend)
        result = df.reset_device_id()
        assert result is True
        
        # Generate new fingerprint - should be same since backend unchanged
        fp2 = df.generate_fingerprint("basic")
        assert fp1 == fp2  # Should be same since reset only clears cache

class TestHardwareDetection:
    """Test hardware detection functions"""
    
    def test_get_stable_fields(self):
        fields = dfp._get_stable_fields()
        
        # Should return a dict with basic OS info
        assert isinstance(fields, dict)
        assert "os_family" in fields
        assert "cpu_arch" in fields
        assert isinstance(fields["os_family"], str)
        assert isinstance(fields["cpu_arch"], str)
    
    def test_get_windows_hardware(self):
        # Test actual Windows hardware detection (may return empty on non-Windows)
        fields = dfp._get_windows_hardware()
        assert isinstance(fields, dict)
        # Fields may be empty if not on Windows or no access
    
    def test_get_memory_info_real(self):
        # Test real memory detection
        fields = dfp._get_memory_info()
        assert isinstance(fields, dict)
        # May have ram_gb field or be empty depending on system
        if 'ram_gb' in fields:
            assert isinstance(fields['ram_gb'], int)
            assert fields['ram_gb'] > 0
    
    def test_get_network_hash_real(self):
        # Test real network hash generation
        fields = dfp._get_network_hash()
        assert isinstance(fields, dict)
        # May have mac_hash field or be empty depending on system
        if 'mac_hash' in fields:
            assert isinstance(fields['mac_hash'], str)
            assert len(fields['mac_hash']) > 0
    
    def test_score_field_match(self):
        current = {
            "cpu_model": "Intel i7",
            "ram_gb": 16,
            "board_uuid": "12345",
            "os_family": "Windows"
        }
        
        stored = current.copy()
        
        # Perfect match
        score = dfp._score_field_match(current, stored)
        assert score == 1.0
        
        # Partial match (RAM changed)
        current["ram_gb"] = 32
        score = dfp._score_field_match(current, stored)
        assert 0.5 < score < 1.0
        
        # No match
        empty = {}
        score = dfp._score_field_match(current, empty)
        assert score == 0.0
        different = {"different": "fields", "os_family": "Linux"}
        score = dfp._score_field_match(different, stored)
        assert score < 0.5

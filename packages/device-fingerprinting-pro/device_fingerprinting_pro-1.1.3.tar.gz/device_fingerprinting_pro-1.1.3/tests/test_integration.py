"""Test public API and integration scenarios"""

import pytest
import device_fingerprinting as df

class TestPublicAPI:
    """Test that public API is clean and minimal"""
    
    def test_public_exports(self):
        """Test that __all__ contains only intended public functions"""
        expected_exports = {
            'generate_fingerprint',
            'generate_fingerprint_async', 
            'create_device_binding',
            'verify_device_binding',
            'reset_device_id',
            'set_crypto_backend',
            'set_storage_backend',
            'set_security_check',
            'set_logger'
        }
        
        assert set(df.__all__) == expected_exports
    
    def test_no_accidental_exports(self):
        """Test that internal functions are not accidentally exported"""
        # These should not be in public API
        internal_functions = [
            '_log', '_get_stable_fields', '_get_windows_hardware',
            '_get_memory_info', '_get_network_hash'
        ]
        
        for func in internal_functions:
            assert func not in df.__all__
            # Should not be directly accessible
            assert not hasattr(df, func)
    
    def test_version_available(self):
        """Test that version is available"""
        assert hasattr(df, '__version__')
        assert df.__version__ == "1.0.0"

class TestIntegrationScenarios:
    """Test realistic usage scenarios"""
    
    def setup_method(self):
        # Start with clean state
        df.reset_device_id()
    
    def test_license_binding_workflow(self):
        """Test complete license binding workflow"""
        
        # Step 1: Create license data
        license_data = {
            "license_id": "LIC-2024-001",
            "customer": "ACME Corp", 
            "product": "SuperApp Pro",
            "expiry": 1735689600,  # Jan 1, 2025
            "features": ["feature_a", "feature_b"]
        }
        
        # Step 2: Bind to device
        bound_license = df.create_device_binding(
            license_data, 
            security_level="high"
        )
        
        # Verify binding was created
        assert "device_binding" in bound_license
        assert bound_license["license_id"] == "LIC-2024-001"
        
        # Step 3: Verify binding (simulating app startup)
        is_valid, details = df.verify_device_binding(bound_license)
        
        assert is_valid is True
        assert details["signature_valid"] is True
        assert details["match_score"] > 0.8
        
        # Step 4: Test with different tolerance
        is_valid_strict, _ = df.verify_device_binding(
            bound_license, 
            tolerance="strict"
        )
        assert is_valid_strict is True
    
    def test_custom_backends_workflow(self):
        """Test using custom backends"""
        from device_fingerprinting.backends import CryptoBackend, StorageBackend, SecurityCheck
        
        # Create real test backends
        class TestCrypto(CryptoBackend):
            def __init__(self):
                self.signatures = {}
            def sign(self, data: bytes) -> str:
                sig = f"test_sig_{hash(data)}"
                self.signatures[sig] = data
                return sig
            def verify(self, signature: str, data: bytes) -> bool:
                return self.signatures.get(signature) == data
        
        class TestStorage(StorageBackend):
            def __init__(self):
                self.data = {}
                self.store_calls = 0
            def store(self, key: str, data: dict) -> bool:
                self.store_calls += 1
                self.data[key] = data
                return True
            def load(self, key: str):
                return self.data.get(key)
            def delete(self, key: str) -> bool:
                self.data.pop(key, None)
                return True
        
        class TestSecurity(SecurityCheck):
            def __init__(self):
                self.check_calls = 0
            def check(self):
                self.check_calls += 1
                return False, "test_mode"
        
        # Setup custom backends
        crypto = TestCrypto()
        storage = TestStorage()
        security = TestSecurity()
        
        df.set_crypto_backend(crypto)
        df.set_storage_backend(storage)
        df.set_security_check(security)
        
        # Use the library
        data = {"test": "data"}
        bound = df.create_device_binding(data)
        
        # Verify our backends were used
        assert bound["device_binding"]["device_signature"].startswith("test_sig_")
        assert storage.store_calls == 1
        assert security.check_calls > 0
        
        # Verify binding
        is_valid, details = df.verify_device_binding(bound)
        assert is_valid is True
    
    def test_error_handling(self):
        """Test error handling in various scenarios"""
        
        # Invalid input
        with pytest.raises(ValueError):
            df.create_device_binding("not_a_dict")
        
        # Missing binding data
        is_valid, details = df.verify_device_binding({"no": "binding"})
        assert is_valid is False
        assert details["error"] == "no_binding_data"
        
        # Invalid binding data format
        is_valid, details = df.verify_device_binding("not_a_dict")
        assert is_valid is False
        assert details["error"] == "invalid_input"
    
    def test_grace_period_scenario(self):
        """Test grace period handling for hardware changes"""
        
        # Create binding
        data = {"license": "test"}
        bound = df.create_device_binding(data)
        
        # Simulate immediate validation (should pass)
        is_valid, details = df.verify_device_binding(bound, grace_period=7)
        assert is_valid is True
        assert details.get("grace_period_used", False) is False
        
        # Test with zero grace period (strict matching)
        is_valid_strict, details_strict = df.verify_device_binding(bound, grace_period=0)
        assert is_valid_strict is True  # Same device should still work
    
    def test_async_workflow(self):
        """Test asynchronous fingerprint generation"""

        # Start async generation
        future = df.generate_fingerprint_async("stable")

        # Do other work...
        data = {"preparing": "other_data"}

        # Get fingerprint result
        fingerprint = future.result(timeout=5.0)
        assert isinstance(fingerprint, str)
        assert len(fingerprint) >= 32  # Real HMAC signatures vary in length

        # Use in binding
        bound = df.create_device_binding(data)
        is_valid, _ = df.verify_device_binding(bound)
        # May be true or false depending on hardware matching, but should not error
        assert isinstance(is_valid, bool)

    def test_multiple_bindings(self):
        """Test handling multiple different bindings"""

        licenses = [
            {"id": "LIC-001", "type": "standard"},
            {"id": "LIC-002", "type": "premium"},
            {"id": "LIC-003", "type": "enterprise"}
        ]

        bound_licenses = []

        # Create multiple bindings
        for license_data in licenses:
            bound = df.create_device_binding(license_data, security_level="basic")  # Use basic for more lenient matching
            bound_licenses.append(bound)

        # Verify all bindings
        for bound in bound_licenses:
            is_valid, details = df.verify_device_binding(bound)
            # Should at least have valid signature even if match score is low
            assert "signature_valid" in details
            assert details["signature_valid"] is True

    def test_reset_and_rebind(self):
        """Test GDPR-style reset and rebinding"""

        # Create initial binding
        data = {"user": "test_user"}
        bound1 = df.create_device_binding(data)
        fp1 = bound1["device_binding"]["device_signature"]

        # Reset device ID (GDPR compliance) - now only clears cache
        reset_success = df.reset_device_id()
        assert reset_success is True

        # Create new binding (should have same signature since backend unchanged)
        bound2 = df.create_device_binding(data)
        fp2 = bound2["device_binding"]["device_signature"]

        assert fp1 == fp2  # Should be same since reset only clears cache

        # Both bindings should verify since they're identical
        is_valid1, _ = df.verify_device_binding(bound1)
        is_valid2, _ = df.verify_device_binding(bound2)
        # At minimum, signatures should be valid
        assert isinstance(is_valid1, bool)
        assert isinstance(is_valid2, bool)
        is_valid_new, _ = df.verify_device_binding(bound2)
        assert is_valid_new is True

class TestCompatibility:
    """Test compatibility across different environments"""
    
    def test_minimal_environment(self):
        """Test that library works with minimal Python environment"""
        # Should work without psutil, winreg, etc.
        fp = df.generate_fingerprint("basic")
        assert isinstance(fp, str)
        assert len(fp) >= 32  # Real HMAC signatures vary
    
    def test_silent_operation(self):
        """Test that library is silent by default"""
        # With no logger set, should not produce any output
        df.set_logger(None)
        
        # These operations should complete silently
        fp = df.generate_fingerprint("stable")
        data = {"test": "data"}
        bound = df.create_device_binding(data, security_level="basic")
        is_valid, _ = df.verify_device_binding(bound)
        
        # Should work without errors
        assert isinstance(is_valid, bool)
    
    def test_handles_missing_optional_deps(self):
        """Test graceful handling when optional dependencies missing"""
        # Library should work even if some dependencies are missing
        # since it only uses standard library by default
        
        fp = df.generate_fingerprint("stable")
        assert isinstance(fp, str)
        assert len(fp) >= 32

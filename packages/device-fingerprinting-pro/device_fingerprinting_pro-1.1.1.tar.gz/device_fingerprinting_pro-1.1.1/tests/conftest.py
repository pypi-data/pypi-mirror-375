"""Test configuration and fixtures"""

import pytest
import logging
from device_fingerprinting.default_backends import HmacSha256Backend, InMemoryStorage, NoOpSecurityCheck

@pytest.fixture(autouse=True)
def reset_backends():
    """Reset backends to defaults before each test"""
    import device_fingerprinting as df
    df.set_crypto_backend(HmacSha256Backend())
    df.set_storage_backend(InMemoryStorage())
    df.set_security_check(NoOpSecurityCheck())
    df.set_logger(None)  # Silent by default
    yield
    # Reset after test too
    df.reset_device_id()

@pytest.fixture
def test_logger():
    logger = logging.getLogger("test_device_fp")
    logger.setLevel(logging.DEBUG)
    return logger

@pytest.fixture
def real_crypto():
    """Real HMAC crypto backend"""
    return HmacSha256Backend()

@pytest.fixture  
def real_storage():
    """Real in-memory storage backend"""
    return InMemoryStorage()

@pytest.fixture
def real_security():
    """Real no-op security check"""
    return NoOpSecurityCheck()

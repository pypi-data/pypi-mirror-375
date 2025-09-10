"""
Production device fingerprinting library.

Hardware-based device identification with pluggable backends.
"""

from .device_fingerprinting import (
    generate_fingerprint,
    generate_fingerprint_async,
    create_device_binding,
    verify_device_binding,
    reset_device_id,
    set_crypto_backend,
    set_storage_backend,
    set_security_check,
    set_logger,
    enable_post_quantum_crypto,
    disable_post_quantum_crypto,
    get_crypto_info,
    enable_anti_replay_protection,
    create_server_nonce,
    verify_server_nonce
)

__all__ = [
    'generate_fingerprint',
    'generate_fingerprint_async', 
    'create_device_binding',
    'verify_device_binding',
    'reset_device_id',
    'set_crypto_backend',
    'set_storage_backend',
    'set_security_check',
    'set_logger',
    'enable_post_quantum_crypto',
    'disable_post_quantum_crypto',
    'get_crypto_info',
    'enable_anti_replay_protection',
    'create_server_nonce',
    'verify_server_nonce'
]

__version__ = "1.0.0-HYBRID-PQC-ANTI-REPLAY"

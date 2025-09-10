# Device Fingerprinting Library

A Python library for generating unique device identifiers based on hardware characteristics. Includes post-quantum cryptographic signatures using NIST-standardized algorithms.

## Features

- **Hardware Detection**: CPU, memory, storage, and network interface identification
- **Cross-Platform**: Windows, macOS, and Linux support
- **Post-Quantum Crypto**: ML-DSA (Dilithium) signatures via pqcrypto library
- **Configurable**: Choose which hardware components to include
- **Persistent**: Device IDs remain stable across software changes

## Installation

```bash
pip install device-fingerprinting-pro
```

## Quick Start

### Basic Usage

```python
from device_fingerprinting import generate_fingerprint

# Generate device fingerprint
fingerprint = generate_fingerprint()
print(f"Device ID: {fingerprint}")
```

### With Post-Quantum Cryptography

```python
from device_fingerprinting import enable_post_quantum_crypto, generate_fingerprint

# Enable quantum-resistant signatures
enable_post_quantum_crypto(algorithm="Dilithium3")

# Generate signed fingerprint
fingerprint = generate_fingerprint()
print(f"Quantum-safe device ID: {fingerprint}")
```

### Custom Configuration

```python
from device_fingerprinting import DeviceFingerprinter

fingerprinter = DeviceFingerprinter(
    include_cpu=True,
    include_memory=True,
    include_storage=True,
    include_network=False,  # Skip network interfaces
    hash_algorithm='sha256'
)

device_id = fingerprinter.generate()
```

## Hardware Components

### CPU Information
- Processor model and architecture
- Core count and thread count
- CPU features and instruction sets

### Memory Details
- Total physical memory
- Memory module configuration
- Memory type and speed

### Storage Devices
- Disk serial numbers and models
- Storage interface types
- Drive capacity and health status

### Network Interfaces
- MAC addresses
- Interface types (Ethernet, WiFi, etc.)
- Network adapter hardware IDs

## Post-Quantum Cryptography

### Supported Algorithms
- **ML-DSA (Dilithium)**: NIST-standardized signature scheme
- **Security Levels**: NIST Level 3 equivalent
- **Key Sizes**: 1952/4032 bytes (public/private)
- **Signature Size**: ~6KB

### Implementation Details
```python
from device_fingerprinting import enable_post_quantum_crypto, get_crypto_info

# Enable PQC with specific algorithm
success = enable_post_quantum_crypto(
    algorithm="Dilithium3",
    hybrid_mode=True
)

# Check current crypto configuration
info = get_crypto_info()
print(f"Algorithm: {info['algorithm']}")
print(f"Library: {info['pqc_library']}")
print(f"Quantum Resistant: {info['quantum_resistant']}")
```

## Use Cases

- **Device Authentication**: Verify device identity for access control
- **Software Licensing**: Bind licenses to specific hardware configurations
- **Fraud Detection**: Identify suspicious login attempts from new devices
- **Asset Management**: Track and inventory computing devices
- **Security Auditing**: Monitor device changes in enterprise environments

## Cross-Platform Support

| Platform | CPU | Memory | Storage | Network | Status |
|----------|-----|--------|---------|---------|--------|
| Windows  | ✅  | ✅     | ✅      | ✅      | Stable |
| macOS    | ✅  | ✅     | ✅      | ✅      | Stable |
| Linux    | ✅  | ✅     | ✅      | ✅      | Stable |

## Performance

- **Generation Time**: 50-200ms typical
- **Memory Usage**: <5MB
- **Dependencies**: psutil, pqcrypto (optional)
- **Caching**: Configurable hardware info caching

## Requirements

- Python 3.7+
- psutil (for hardware detection)
- pqcrypto (for post-quantum cryptography, optional)

## License

MIT License - see LICENSE file for details.

## Links

- [GitHub Repository](https://github.com/Johnsonajibi/DeviceFingerprinting)
- [Issue Tracker](https://github.com/Johnsonajibi/DeviceFingerprinting/issues)
- [Documentation](https://github.com/Johnsonajibi/DeviceFingerprinting#readme)

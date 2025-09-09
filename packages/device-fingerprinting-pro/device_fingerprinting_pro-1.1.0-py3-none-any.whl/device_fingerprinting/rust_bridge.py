"""
Python Bridge to Rust PQC Module

This provides a clean Python interface to the real PQC implementations in Rust.
"""

import os
import sys
import subprocess
from typing import Optional, Tuple, Dict, Any

class RustPQCBridge:
    """Bridge to communicate with Rust PQC module"""
    
    def __init__(self):
        self.rust_module = None
        self._load_rust_module()
    
    def _load_rust_module(self):
        """Load the Rust PQC module"""
        try:
            # Try to import the compiled Rust module
            import pqc_rust
            self.rust_module = pqc_rust
            print("✅ Real Rust PQC module loaded successfully!")
            
        except ImportError as e:
            print(f"❌ Rust PQC module not found: {e}")
            print("💡 Run: pip install maturin && maturin develop")
            self.rust_module = None
    
    def is_available(self) -> bool:
        """Check if Rust PQC is available"""
        return self.rust_module is not None
    
    def get_info(self) -> Dict[str, Any]:
        """Get PQC information"""
        if not self.is_available():
            return {"error": "Rust PQC not available"}
        
        try:
            return self.rust_module.get_pqc_info()
        except Exception as e:
            return {"error": f"Failed to get info: {e}"}
    
    def test_dilithium(self) -> bool:
        """Test Dilithium implementation"""
        if not self.is_available():
            return False
        
        try:
            return self.rust_module.test_dilithium()
        except Exception as e:
            print(f"Dilithium test failed: {e}")
            return False
    
    def create_dilithium3(self):
        """Create a new Dilithium3 instance"""
        if not self.is_available():
            raise RuntimeError("Rust PQC module not available")
        
        return self.rust_module.RealDilithium3()
    
    def create_kyber768(self):
        """Create a new Kyber768 instance"""
        if not self.is_available():
            raise RuntimeError("Rust PQC module not available")
        
        return self.rust_module.RealKyber768()

# Global instance
rust_pqc = RustPQCBridge()

def install_rust_pqc():
    """Install and build the Rust PQC module"""
    print("🔧 Installing Rust PQC module...")
    
    # Check if Rust is installed
    try:
        result = subprocess.run(['rustc', '--version'], 
                              capture_output=True, text=True, check=True)
        print(f"✅ Rust found: {result.stdout.strip()}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Rust not found. Please install Rust from https://rustup.rs/")
        return False
    
    # Install maturin if not available
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'maturin'], 
                      check=True)
        print("✅ Maturin installed")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install maturin: {e}")
        return False
    
    # Build and install the Rust module
    try:
        pqc_rust_dir = os.path.join(os.path.dirname(__file__), '..', 'pqc_rust')
        if os.path.exists(pqc_rust_dir):
            print(f"📁 Building Rust module in: {pqc_rust_dir}")
            subprocess.run(['maturin', 'develop'], 
                          cwd=pqc_rust_dir, check=True)
            print("✅ Rust PQC module built and installed!")
            
            # Reload the module
            global rust_pqc
            rust_pqc = RustPQCBridge()
            return True
        else:
            print(f"❌ pqc_rust directory not found: {pqc_rust_dir}")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to build Rust module: {e}")
        return False

if __name__ == "__main__":
    # Test the bridge
    print("🧪 Testing Rust PQC Bridge...")
    
    if rust_pqc.is_available():
        print("✅ Rust PQC is available!")
        info = rust_pqc.get_info()
        for k, v in info.items():
            print(f"   {k}: {v}")
        
        print("\n🧪 Testing Dilithium3...")
        if rust_pqc.test_dilithium():
            print("✅ Dilithium3 test passed!")
        else:
            print("❌ Dilithium3 test failed!")
    else:
        print("❌ Rust PQC not available")
        print("💡 Run install_rust_pqc() to set it up")

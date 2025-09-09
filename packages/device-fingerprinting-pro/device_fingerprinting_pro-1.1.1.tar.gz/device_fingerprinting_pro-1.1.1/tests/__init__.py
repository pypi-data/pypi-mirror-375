"""Test runner for all tests"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if __name__ == "__main__":
    import pytest
    
    # Run all tests with coverage
    exit_code = pytest.main([
        "tests/",
        "-v",
        "--tb=short",
        "-x"  # Stop on first failure for development
    ])
    
    sys.exit(exit_code)

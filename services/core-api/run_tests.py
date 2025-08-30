#!/usr/bin/env python3
"""
Test runner for the core API service
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Run tests for the core API service"""
    
    # Set environment variables for testing
    os.environ.setdefault("DATABASE_URL", "postgresql://test:test@localhost:5432/test_anzx")
    os.environ.setdefault("JWT_SECRET", "test-secret-key-for-testing-only")
    os.environ.setdefault("FIREBASE_CONFIG", "{}")
    
    # Change to the service directory
    service_dir = Path(__file__).parent
    os.chdir(service_dir)
    
    print("🧪 Running ANZx.ai Core API Tests")
    print("=" * 50)
    
    try:
        # Run pytest
        result = subprocess.run([
            sys.executable, "-m", "pytest",
            "tests/",
            "-v",
            "--tb=short",
            "--color=yes"
        ], check=True)
        
        print("\n✅ All tests passed!")
        return 0
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Tests failed with exit code: {e.returncode}")
        return e.returncode
    except Exception as e:
        print(f"\n💥 Error running tests: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
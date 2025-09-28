#!/usr/bin/env python3
"""
Test runner for cricket agent
Handles imports and runs tests with coverage
"""

import sys
import os
import subprocess

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def run_tests():
    """Run tests with coverage"""
    print("🏏 Running Cricket Agent Tests")
    print("=" * 50)
    
    # Run tests
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/test_normalize.py",
        "-v",
        "--cov=agent.tools.normalize",
        "--cov=models",
        "--cov-report=term-missing",
        "--cov-report=html:htmlcov"
    ]
    
    try:
        result = subprocess.run(cmd, cwd=project_root, capture_output=True, text=True)
        
        print("STDOUT:")
        print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        print(f"Exit code: {result.returncode}")
        
        if result.returncode == 0:
            print("\n✅ All tests passed!")
        else:
            print("\n❌ Some tests failed!")
            
        return result.returncode == 0
        
    except Exception as e:
        print(f"Error running tests: {e}")
        return False

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)

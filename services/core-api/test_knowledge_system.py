#!/usr/bin/env python3
"""
Quick test script for Knowledge Management System
Run this to verify the system is working correctly
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

async def main():
    """Run knowledge system tests"""
    print("🧪 Testing ANZx.ai Knowledge Management System")
    print("=" * 50)
    
    try:
        # Import test runner
        from tests.run_knowledge_tests import main as run_tests
        
        # Run the tests
        success = await run_tests()
        
        if success:
            print("\n" + "=" * 50)
            print("✅ Knowledge Management System Test: PASSED")
            print("🚀 System is ready for production!")
            return 0
        else:
            print("\n" + "=" * 50)
            print("❌ Knowledge Management System Test: FAILED")
            print("🔧 Please check the error messages above")
            return 1
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("🔧 Make sure all dependencies are installed")
        return 1
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
#!/usr/bin/env python3
"""
Run Synthetic Data Generation
Script to populate the cricket agent with synthetic data for testing
"""

import asyncio
import json
import logging
import sys
from pathlib import Path

# Add the parent directory to the path so we can import from the cricket-agent module
sys.path.append(str(Path(__file__).parent.parent))

from scripts.synthetic_data_generator import SyntheticCricketDataGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def main():
    """Main function to run synthetic data generation"""
    print("🏏 Starting Synthetic Cricket Data Generation")
    print("=" * 50)
    
    try:
        # Initialize generator
        generator = SyntheticCricketDataGenerator()
        
        # Generate and store synthetic data
        result = await generator.generate_and_store_synthetic_data()
        
        print("\n📊 Generation Results:")
        print("=" * 30)
        
        if result["status"] == "success":
            print("✅ Synthetic data generation completed successfully!")
            print(f"📈 Statistics:")
            for key, value in result["stats"].items():
                print(f"  {key}: {value}")
            
            print(f"\n📋 Generated Data:")
            for key, value in result["generated_data"].items():
                print(f"  {key}: {value}")
            
            print(f"\n🎯 Vector Store Status:")
            vector_stats = generator.vector_client.get_stats()
            for key, value in vector_stats.items():
                print(f"  {key}: {value}")
                
        else:
            print("❌ Synthetic data generation failed!")
            print(f"Error: {result.get('error', 'Unknown error')}")
            return 1
            
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1
    
    print("\n🎉 Synthetic data generation completed!")
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

#!/usr/bin/env python3
"""
Test Configuration for Synthetic Data Generation
Bypasses secret requirements for testing
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the path
sys.path.append(str(Path(__file__).parent.parent))

# Set test environment variables
os.environ.update({
    "APP_ENV": "test",
    "GCP_PROJECT": "virtual-stratum-473511-u5",
    "REGION": "australia-southeast1",
    "VERTEX_LOCATION": "australia-southeast1",
    "VERTEX_MODEL": "gemini-1.5-flash",
    "EMBED_MODEL": "text-embedding-005",
    "PLAYHQ_MODE": "public",
    "VECTOR_BACKEND": "vertex_rag",
    "SECRET_PLAYHQ_API_KEY": "test-api-key",
    "SECRET_IDS_BUNDLE": '{"tenant":"ca","org_id":"test-org","season_id":"test-season","grade_id":"test-grade","teams":[{"name":"Test Team","team_id":"test-team"}]}',
    "SECRET_INTERNAL_TOKEN": "test-internal-token"
})

# Now import and run the synthetic data generator
from scripts.synthetic_data_generator import SyntheticCricketDataGenerator
import asyncio
import json
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def main():
    """Main function to run synthetic data generation with test config"""
    print("🏏 Starting Synthetic Cricket Data Generation (Test Mode)")
    print("=" * 60)
    
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
        import traceback
        traceback.print_exc()
        return 1
    
    print("\n🎉 Synthetic data generation completed!")
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

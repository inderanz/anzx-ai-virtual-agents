#!/usr/bin/env python3
"""
Test Vector Store with Synthetic Data
Verify that the vector store is working with synthetic data
"""

import asyncio
import json
import logging
import sys
from pathlib import Path

# Add the parent directory to the path
sys.path.append(str(Path(__file__).parent.parent))

# Set test environment variables
import os
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

from agent.tools.vector_client import get_vector_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_vector_store():
    """Test vector store functionality"""
    print("🔍 Testing Vector Store with Synthetic Data")
    print("=" * 50)
    
    try:
        # Get vector client
        vector_client = get_vector_client()
        
        # Test queries
        test_queries = [
            "Which team is Harshvarshan in?",
            "Show me the ladder for Blue U10",
            "List fixtures for Caroline Springs Blue U10",
            "Who are the players for Caroline Springs White U10?"
        ]
        
        for query in test_queries:
            print(f"\n🔍 Query: {query}")
            print("-" * 40)
            
            # Query vector store
            results = vector_client.query(query, filters={}, k=3)
            print(f"📊 Results: {len(results)} documents found")
            
            for i, result in enumerate(results, 1):
                print(f"  {i}. {result}")
        
        # Get vector store stats
        stats = vector_client.get_stats()
        print(f"\n📈 Vector Store Stats:")
        print("-" * 30)
        for key, value in stats.items():
            print(f"  {key}: {value}")
            
        return True
        
    except Exception as e:
        print(f"❌ Vector store test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main function"""
    success = await test_vector_store()
    
    if success:
        print("\n✅ Vector store test completed successfully!")
        return 0
    else:
        print("\n❌ Vector store test failed!")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

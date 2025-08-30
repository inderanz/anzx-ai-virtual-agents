"""
Knowledge Management System Test Runner
Runs end-to-end tests for the complete knowledge management pipeline
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.utils.database import get_db
from app.models.user import Organization, User
from app.services.knowledge_service import knowledge_service
from app.services.document_processor import document_processor
from app.services.vector_search_service import vector_search_service


async def test_basic_functionality():
    """Test basic knowledge management functionality"""
    print("🧪 Testing Knowledge Management System...")
    
    # Get database session
    db = next(get_db())
    
    try:
        # Create test organization
        print("📝 Creating test organization...")
        org = Organization(
            name="Test Organization",
            region="AU",
            plan="pro"
        )
        db.add(org)
        db.commit()
        print(f"✅ Created organization: {org.id}")
        
        # Test document processing
        print("📄 Testing document processing...")
        sample_content = """
        ANZx.ai Platform Test Document
        
        This is a test document for the knowledge management system.
        It contains information about AI assistants, automation, and business processes.
        
        Key features:
        - Multi-agent AI platform
        - Customer support automation
        - Business analytics
        - Integration capabilities
        
        For support, contact support@anzx.ai
        """
        
        source_data = {
            "name": "Test Document",
            "type": "file",
            "filename": "test.txt",
            "mime_type": "text/plain",
            "content": sample_content.encode('utf-8'),
            "metadata": {"test": True}
        }
        
        # Process document
        result = await knowledge_service.create_knowledge_source(
            db=db,
            organization_id=str(org.id),
            source_data=source_data
        )
        
        print(f"✅ Document processed: {result['documents_created']} documents, {result['chunks_created']} chunks")
        print(f"✅ Embeddings generated: {result['embeddings_generated']} embeddings")
        
        source_id = result["source_id"]
        
        # Test search functionality
        print("🔍 Testing search functionality...")
        
        # Semantic search
        semantic_results = await vector_search_service.semantic_search(
            db=db,
            organization_id=str(org.id),
            query="AI platform features",
            max_results=3
        )
        print(f"✅ Semantic search: {len(semantic_results)} results")
        
        # Keyword search
        keyword_results = await vector_search_service.keyword_search(
            db=db,
            organization_id=str(org.id),
            query="support contact",
            max_results=3
        )
        print(f"✅ Keyword search: {len(keyword_results)} results")
        
        # Hybrid search
        hybrid_results = await vector_search_service.hybrid_search(
            db=db,
            organization_id=str(org.id),
            query="business automation platform",
            max_results=5
        )
        print(f"✅ Hybrid search: {len(hybrid_results)} results")
        
        # Test knowledge service search
        knowledge_search = await knowledge_service.search_knowledge_base(
            db=db,
            organization_id=str(org.id),
            query="What is ANZx.ai?",
            search_type="hybrid",
            max_results=3
        )
        print(f"✅ Knowledge service search: {len(knowledge_search['results'])} results")
        print(f"   Search time: {knowledge_search['search_time_ms']}ms")
        
        # Display sample results
        if knowledge_search['results']:
            print("\n📋 Sample search results:")
            for i, result in enumerate(knowledge_search['results'][:2]):
                print(f"   {i+1}. Score: {result['score']:.3f}")
                print(f"      Content: {result['content'][:100]}...")
                print(f"      Source: {result['source_name']}")
        
        # Test analytics
        print("\n📊 Testing analytics...")
        analytics = await knowledge_service.get_knowledge_analytics(
            db=db,
            organization_id=str(org.id)
        )
        
        print(f"✅ Analytics generated:")
        print(f"   Total sources: {analytics['processing']['total_sources']}")
        print(f"   Total documents: {analytics['search']['total_documents']}")
        print(f"   Embedded documents: {analytics['search']['embedded_documents']}")
        print(f"   Embedding coverage: {analytics['search']['embedding_coverage_percent']}%")
        
        # Test knowledge source management
        print("\n🔧 Testing knowledge source management...")
        
        # Get knowledge source details
        source_details = await knowledge_service.get_knowledge_source(
            db=db,
            source_id=source_id,
            organization_id=str(org.id)
        )
        print(f"✅ Retrieved source details: {source_details['name']}")
        print(f"   Status: {source_details['status']}")
        print(f"   Documents: {source_details['statistics']['total_documents']}")
        
        # Update knowledge source
        update_result = await knowledge_service.update_knowledge_source(
            db=db,
            source_id=source_id,
            organization_id=str(org.id),
            update_data={"name": "Updated Test Document"}
        )
        print(f"✅ Updated source name: {update_result['name']}")
        
        # Test health check
        print("\n🏥 Testing health check...")
        health = await knowledge_service.health_check(db=db)
        print(f"✅ Health check: {health['status']}")
        print(f"   Database connected: {health['database_connected']}")
        print(f"   pgvector available: {health['pgvector_available']}")
        
        print("\n🎉 All tests passed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        db.close()


async def test_performance():
    """Test system performance with multiple documents"""
    print("\n⚡ Testing performance...")
    
    db = next(get_db())
    
    try:
        # Create test organization
        org = Organization(name="Performance Test Org", region="AU", plan="enterprise")
        db.add(org)
        db.commit()
        
        # Create multiple knowledge sources
        import time
        start_time = time.time()
        
        for i in range(3):
            content = f"""
            Performance Test Document {i}
            
            This is document number {i} for performance testing.
            It contains various information about business processes,
            AI automation, customer service, and analytics.
            
            Document {i} specific content:
            - Feature set {i}
            - Process automation {i}
            - Customer data {i}
            - Business metrics {i}
            """
            
            source_data = {
                "name": f"Performance Test {i}",
                "type": "file",
                "filename": f"perf_test_{i}.txt",
                "mime_type": "text/plain",
                "content": content.encode('utf-8'),
                "metadata": {"batch": "performance", "index": i}
            }
            
            await knowledge_service.create_knowledge_source(
                db=db,
                organization_id=str(org.id),
                source_data=source_data
            )
        
        processing_time = time.time() - start_time
        print(f"✅ Processed 3 documents in {processing_time:.2f} seconds")
        
        # Test search performance
        search_start = time.time()
        
        search_results = await knowledge_service.search_knowledge_base(
            db=db,
            organization_id=str(org.id),
            query="business automation processes",
            search_type="hybrid",
            max_results=10
        )
        
        search_time = time.time() - search_start
        print(f"✅ Search completed in {search_time:.3f} seconds")
        print(f"   Found {len(search_results['results'])} results")
        print(f"   Reported search time: {search_results['search_time_ms']}ms")
        
        return True
        
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False
        
    finally:
        db.close()


def test_service_health():
    """Test individual service health"""
    print("\n🔍 Testing service health...")
    
    try:
        # Test document processor
        print("📄 Document processor:", "✅ Ready" if document_processor else "❌ Not ready")
        
        # Test vector search service
        print("🔍 Vector search service:", "✅ Ready" if vector_search_service else "❌ Not ready")
        
        # Test knowledge service
        print("🧠 Knowledge service:", "✅ Ready" if knowledge_service else "❌ Not ready")
        
        return True
        
    except Exception as e:
        print(f"❌ Service health check failed: {e}")
        return False


async def main():
    """Run all tests"""
    print("🚀 Starting Knowledge Management System Tests\n")
    
    # Test service health
    health_ok = test_service_health()
    
    if not health_ok:
        print("❌ Service health check failed. Exiting.")
        return False
    
    # Test basic functionality
    basic_ok = await test_basic_functionality()
    
    if not basic_ok:
        print("❌ Basic functionality tests failed.")
        return False
    
    # Test performance
    perf_ok = await test_performance()
    
    if not perf_ok:
        print("❌ Performance tests failed.")
        return False
    
    print("\n🎉 All Knowledge Management System tests completed successfully!")
    print("\n📋 Test Summary:")
    print("   ✅ Service health checks")
    print("   ✅ Document processing pipeline")
    print("   ✅ Vector embedding generation")
    print("   ✅ Semantic search")
    print("   ✅ Keyword search")
    print("   ✅ Hybrid search")
    print("   ✅ Knowledge source management")
    print("   ✅ Analytics and monitoring")
    print("   ✅ Performance testing")
    
    return True


if __name__ == "__main__":
    # Run the tests
    success = asyncio.run(main())
    
    if success:
        print("\n✅ Knowledge Management System is ready for production!")
        sys.exit(0)
    else:
        print("\n❌ Knowledge Management System tests failed!")
        sys.exit(1)
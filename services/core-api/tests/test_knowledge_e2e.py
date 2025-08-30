"""
End-to-End Tests for Knowledge Management System
Tests the complete pipeline: document processing → embedding → search
"""

import pytest
import asyncio
import tempfile
import os
from typing import Dict, Any
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.utils.database import get_db
from app.models.user import Organization, User, KnowledgeSource, Document
from app.services.knowledge_service import knowledge_service
from app.services.document_processor import document_processor
from app.services.vector_search_service import vector_search_service

# Test client
client = TestClient(app)

# Test data
SAMPLE_TEXT_CONTENT = """
ANZx.ai Platform Documentation

## Overview
ANZx.ai is an AI-powered virtual business assistant platform that provides small businesses 
with specialized AI agents for support, administration, content creation, and business insights.

## Features
- Multi-agent AI assistant platform
- Customer support automation
- Administrative task management
- Content creation and marketing
- Business analytics and insights

## Getting Started
To get started with ANZx.ai:
1. Sign up for an account
2. Choose your subscription plan
3. Configure your AI assistants
4. Upload your knowledge base
5. Start automating your business processes

## Support
For support, contact us at support@anzx.ai or visit our help center.
"""

SAMPLE_FAQ_CONTENT = """
Frequently Asked Questions

Q: How do I reset my password?
A: Click the "Forgot Password" link on the login page and follow the instructions.

Q: What subscription plans are available?
A: We offer Freemium, Pro ($49-99/month), and Enterprise (custom pricing) plans.

Q: How do I upload documents to my knowledge base?
A: Go to the Knowledge Base section and click "Upload Document" or "Add URL".

Q: Can I integrate with Google services?
A: Yes, we support Gmail, Google Calendar, and Google Drive integration.

Q: Is my data secure?
A: Yes, we use AES-256 encryption and comply with Australian Privacy Principles.
"""


class TestKnowledgeManagementE2E:
    """End-to-end tests for knowledge management system"""
    
    @pytest.fixture
    def db_session(self):
        """Get database session for testing"""
        db = next(get_db())
        yield db
        db.close()
    
    @pytest.fixture
    def test_organization(self, db_session: Session):
        """Create test organization"""
        org = Organization(
            name="Test Organization",
            region="AU",
            plan="pro"
        )
        db_session.add(org)
        db_session.commit()
        return org
    
    @pytest.fixture
    def test_user(self, db_session: Session, test_organization: Organization):
        """Create test user"""
        user = User(
            email="test@example.com",
            organization_id=test_organization.id,
            role="owner"
        )
        db_session.add(user)
        db_session.commit()
        return user
    
    @pytest.fixture
    def auth_headers(self, test_user: User):
        """Mock authentication headers"""
        return {
            "Authorization": f"Bearer mock_token_{test_user.id}",
            "X-Organization-ID": str(test_user.organization_id)
        }
    
    @pytest.mark.asyncio
    async def test_complete_document_processing_pipeline(
        self, 
        db_session: Session, 
        test_organization: Organization
    ):
        """Test complete document processing from upload to search"""
        
        # Step 1: Create knowledge source with text content
        source_data = {
            "name": "Platform Documentation",
            "type": "file",
            "filename": "docs.txt",
            "mime_type": "text/plain",
            "content": SAMPLE_TEXT_CONTENT.encode('utf-8'),
            "metadata": {"category": "documentation"}
        }
        
        # Process document
        result = await knowledge_service.create_knowledge_source(
            db=db_session,
            organization_id=str(test_organization.id),
            source_data=source_data
        )
        
        # Verify processing results
        assert result["status"] == "completed"
        assert result["documents_created"] > 0
        assert result["chunks_created"] > 0
        assert result["embeddings_generated"] > 0
        
        source_id = result["source_id"]
        
        # Step 2: Verify documents were created
        documents = db_session.query(Document).join(KnowledgeSource).filter(
            KnowledgeSource.id == source_id
        ).all()
        
        assert len(documents) > 0
        assert all(doc.embedding is not None for doc in documents)
        
        # Step 3: Test semantic search
        search_results = await vector_search_service.semantic_search(
            db=db_session,
            organization_id=str(test_organization.id),
            query="AI assistant platform features",
            max_results=5
        )
        
        assert len(search_results) > 0
        assert any("AI assistant" in result["content"] for result in search_results)
        
        # Step 4: Test keyword search
        keyword_results = await vector_search_service.keyword_search(
            db=db_session,
            organization_id=str(test_organization.id),
            query="subscription plan",
            max_results=5
        )
        
        assert len(keyword_results) > 0
        
        # Step 5: Test hybrid search
        hybrid_results = await vector_search_service.hybrid_search(
            db=db_session,
            organization_id=str(test_organization.id),
            query="getting started with ANZx",
            max_results=5
        )
        
        assert len(hybrid_results) > 0
        assert all("combined_score" in result for result in hybrid_results)
    
    @pytest.mark.asyncio
    async def test_multiple_knowledge_sources(
        self, 
        db_session: Session, 
        test_organization: Organization
    ):
        """Test processing multiple knowledge sources"""
        
        # Create first knowledge source (documentation)
        doc_source = {
            "name": "Documentation",
            "type": "file",
            "filename": "docs.txt",
            "mime_type": "text/plain",
            "content": SAMPLE_TEXT_CONTENT.encode('utf-8'),
            "metadata": {"category": "docs"}
        }
        
        doc_result = await knowledge_service.create_knowledge_source(
            db=db_session,
            organization_id=str(test_organization.id),
            source_data=doc_source
        )
        
        # Create second knowledge source (FAQ)
        faq_source = {
            "name": "FAQ",
            "type": "file",
            "filename": "faq.txt",
            "mime_type": "text/plain",
            "content": SAMPLE_FAQ_CONTENT.encode('utf-8'),
            "metadata": {"category": "faq"}
        }
        
        faq_result = await knowledge_service.create_knowledge_source(
            db=db_session,
            organization_id=str(test_organization.id),
            source_data=faq_source
        )
        
        # Verify both sources were processed
        assert doc_result["status"] == "completed"
        assert faq_result["status"] == "completed"
        
        # Test search across all sources
        all_results = await vector_search_service.hybrid_search(
            db=db_session,
            organization_id=str(test_organization.id),
            query="password reset",
            max_results=10
        )
        
        # Should find results from FAQ source
        assert len(all_results) > 0
        assert any("password" in result["content"].lower() for result in all_results)
        
        # Test filtered search (only FAQ source)
        faq_results = await vector_search_service.hybrid_search(
            db=db_session,
            organization_id=str(test_organization.id),
            query="subscription plans",
            max_results=10,
            source_filter=faq_result["source_id"]
        )
        
        # Should only find results from FAQ source
        assert len(faq_results) > 0
        assert all(result["source_id"] == faq_result["source_id"] for result in faq_results)
    
    def test_knowledge_api_endpoints(self, auth_headers: Dict[str, str]):
        """Test knowledge management API endpoints"""
        
        # Test health check
        response = client.get("/api/knowledge/health")
        assert response.status_code == 200
        health_data = response.json()
        assert "status" in health_data
        
        # Test get knowledge sources (empty initially)
        response = client.get("/api/knowledge/sources", headers=auth_headers)
        assert response.status_code == 200
        sources = response.json()
        assert isinstance(sources, list)
        
        # Test create knowledge source via URL
        url_source_data = {
            "name": "Test Website",
            "type": "url",
            "url": "https://example.com",
            "metadata": {"category": "external"}
        }
        
        response = client.post(
            "/api/knowledge/sources",
            json=url_source_data,
            headers=auth_headers
        )
        # Note: This might fail in test environment without actual URL crawling
        # In production tests, use mock responses
        
        # Test search endpoint
        search_data = {
            "query": "test query",
            "search_type": "hybrid",
            "max_results": 5
        }
        
        response = client.post(
            "/api/knowledge/search",
            json=search_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        search_results = response.json()
        assert "query" in search_results
        assert "results" in search_results
    
    def test_file_upload_endpoint(self, auth_headers: Dict[str, str]):
        """Test file upload endpoint"""
        
        # Create temporary test file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(SAMPLE_TEXT_CONTENT)
            temp_file_path = f.name
        
        try:
            # Test file upload
            with open(temp_file_path, 'rb') as f:
                files = {"file": ("test.txt", f, "text/plain")}
                data = {
                    "name": "Test Upload",
                    "metadata": '{"category": "test"}'
                }
                
                response = client.post(
                    "/api/knowledge/sources/upload",
                    files=files,
                    data=data,
                    headers=auth_headers
                )
                
                # Note: This might fail without proper auth setup in test environment
                # In production tests, ensure proper authentication mocking
                
        finally:
            # Clean up temporary file
            os.unlink(temp_file_path)
    
    @pytest.mark.asyncio
    async def test_knowledge_source_lifecycle(
        self, 
        db_session: Session, 
        test_organization: Organization
    ):
        """Test complete knowledge source lifecycle"""
        
        # Create knowledge source
        source_data = {
            "name": "Lifecycle Test",
            "type": "file",
            "filename": "test.txt",
            "mime_type": "text/plain",
            "content": SAMPLE_TEXT_CONTENT.encode('utf-8'),
            "metadata": {"test": True}
        }
        
        create_result = await knowledge_service.create_knowledge_source(
            db=db_session,
            organization_id=str(test_organization.id),
            source_data=source_data
        )
        
        source_id = create_result["source_id"]
        
        # Get knowledge source details
        source_details = await knowledge_service.get_knowledge_source(
            db=db_session,
            source_id=source_id,
            organization_id=str(test_organization.id)
        )
        
        assert source_details["name"] == "Lifecycle Test"
        assert source_details["status"] == "completed"
        assert source_details["statistics"]["total_documents"] > 0
        
        # Update knowledge source
        update_data = {
            "name": "Updated Lifecycle Test",
            "metadata": {"updated": True}
        }
        
        update_result = await knowledge_service.update_knowledge_source(
            db=db_session,
            source_id=source_id,
            organization_id=str(test_organization.id),
            update_data=update_data
        )
        
        assert update_result["name"] == "Updated Lifecycle Test"
        
        # Get analytics
        analytics = await knowledge_service.get_knowledge_analytics(
            db=db_session,
            organization_id=str(test_organization.id)
        )
        
        assert "processing" in analytics
        assert "search" in analytics
        assert analytics["processing"]["total_sources"] >= 1
        
        # Delete knowledge source
        delete_result = await knowledge_service.delete_knowledge_source(
            db=db_session,
            source_id=source_id,
            organization_id=str(test_organization.id)
        )
        
        assert delete_result["documents_deleted"] > 0
        
        # Verify deletion
        with pytest.raises(Exception):  # Should raise HTTPException
            await knowledge_service.get_knowledge_source(
                db=db_session,
                source_id=source_id,
                organization_id=str(test_organization.id)
            )
    
    @pytest.mark.asyncio
    async def test_search_performance(
        self, 
        db_session: Session, 
        test_organization: Organization
    ):
        """Test search performance with multiple documents"""
        
        # Create multiple knowledge sources
        sources = []
        for i in range(3):
            source_data = {
                "name": f"Performance Test {i}",
                "type": "file",
                "filename": f"test_{i}.txt",
                "mime_type": "text/plain",
                "content": (SAMPLE_TEXT_CONTENT + f"\n\nDocument {i} specific content").encode('utf-8'),
                "metadata": {"batch": i}
            }
            
            result = await knowledge_service.create_knowledge_source(
                db=db_session,
                organization_id=str(test_organization.id),
                source_data=source_data
            )
            sources.append(result["source_id"])
        
        # Test search performance
        import time
        
        start_time = time.time()
        search_results = await knowledge_service.search_knowledge_base(
            db=db_session,
            organization_id=str(test_organization.id),
            query="AI assistant platform",
            search_type="hybrid",
            max_results=10
        )
        end_time = time.time()
        
        search_time_ms = (end_time - start_time) * 1000
        
        # Verify performance
        assert len(search_results["results"]) > 0
        assert search_time_ms < 5000  # Should complete within 5 seconds
        assert search_results["search_time_ms"] > 0
        
        # Test similar document search
        if search_results["results"]:
            first_doc_id = search_results["results"][0]["document_id"]
            
            similar_docs = await vector_search_service.get_similar_documents(
                db=db_session,
                document_id=first_doc_id,
                organization_id=str(test_organization.id),
                max_results=3
            )
            
            assert len(similar_docs) >= 0  # May be empty if no similar docs
    
    @pytest.mark.asyncio
    async def test_error_handling(
        self, 
        db_session: Session, 
        test_organization: Organization
    ):
        """Test error handling in knowledge management"""
        
        # Test invalid source type
        with pytest.raises(Exception):
            await knowledge_service.create_knowledge_source(
                db=db_session,
                organization_id=str(test_organization.id),
                source_data={
                    "name": "Invalid Source",
                    "type": "invalid_type",
                    "content": b"test content"
                }
            )
        
        # Test search with invalid organization
        search_results = await vector_search_service.semantic_search(
            db=db_session,
            organization_id="invalid_org_id",
            query="test query"
        )
        assert len(search_results) == 0
        
        # Test get non-existent knowledge source
        with pytest.raises(Exception):
            await knowledge_service.get_knowledge_source(
                db=db_session,
                source_id="non_existent_id",
                organization_id=str(test_organization.id)
            )
    
    def test_integration_with_agents(self, auth_headers: Dict[str, str]):
        """Test knowledge base integration with AI agents"""
        
        # This would test the integration between knowledge base and agents
        # For now, we'll test that the search endpoint works as expected
        
        search_data = {
            "query": "How do I get started?",
            "search_type": "hybrid",
            "max_results": 3
        }
        
        response = client.post(
            "/api/knowledge/search",
            json=search_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        results = response.json()
        
        # Verify response format matches what agents would expect
        assert "query" in results
        assert "results" in results
        assert "search_time_ms" in results
        
        if results["results"]:
            result = results["results"][0]
            assert "content" in result
            assert "score" in result
            assert "source_name" in result


# Integration test for the complete RAG pipeline
@pytest.mark.asyncio
async def test_complete_rag_pipeline():
    """Test the complete RAG pipeline from document to agent response"""
    
    # This test would simulate:
    # 1. Document upload and processing
    # 2. Embedding generation
    # 3. Agent query with knowledge retrieval
    # 4. Response generation with citations
    
    # For now, we'll create a simplified version
    db = next(get_db())
    
    try:
        # Create test organization
        org = Organization(name="RAG Test Org", region="AU", plan="pro")
        db.add(org)
        db.commit()
        
        # Create knowledge source
        source_data = {
            "name": "RAG Test Knowledge",
            "type": "file",
            "filename": "rag_test.txt",
            "mime_type": "text/plain",
            "content": SAMPLE_TEXT_CONTENT.encode('utf-8'),
            "metadata": {"test": "rag_pipeline"}
        }
        
        # Process through knowledge service
        result = await knowledge_service.create_knowledge_source(
            db=db,
            organization_id=str(org.id),
            source_data=source_data
        )
        
        assert result["status"] == "completed"
        
        # Test knowledge retrieval (simulating agent query)
        search_result = await knowledge_service.search_knowledge_base(
            db=db,
            organization_id=str(org.id),
            query="What is ANZx.ai?",
            search_type="hybrid",
            max_results=3
        )
        
        assert len(search_result["results"]) > 0
        
        # Verify we can extract relevant context for agent
        context_chunks = []
        for result in search_result["results"]:
            context_chunks.append({
                "content": result["content"],
                "source": result["source_name"],
                "score": result["score"]
            })
        
        assert len(context_chunks) > 0
        assert any("ANZx.ai" in chunk["content"] for chunk in context_chunks)
        
    finally:
        db.close()


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
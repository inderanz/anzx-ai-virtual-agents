
import pytest
from unittest.mock import patch, AsyncMock

from fastapi.testclient import TestClient
from httpx import Response, HTTPStatusError, Request

from services.agent_orchestration.main import app

# Mark all tests in this file as asyncio
pytestmark = pytest.mark.asyncio

@pytest.fixture
def client():
    """Provides a FastAPI TestClient for making requests to the app."""
    return TestClient(app)

def test_health_check(client):
    """Tests the /health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "agent-orchestration"}

def test_root(client):
    """Tests the root / endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "ANZx.ai Agent Orchestration"

@patch('services.agent_orchestration.main.ChatVertexAI')
@patch('httpx.AsyncClient.post')
async def test_orchestrate_success(mock_httpx_post, mock_chat_vertex_ai, client):
    """Tests the /orchestrate endpoint on a successful run."""
    # Arrange
    mock_httpx_post.return_value = Response(
        200,
        json=[{"content": "This is a test context from the knowledge base."}]
    )

    mock_llm_instance = AsyncMock()
    mock_llm_instance.ainvoke.return_value.content = "This is a generated response from the LLM."
    mock_chat_vertex_ai.return_value = mock_llm_instance

    request_data = {"organization_id": "test-org", "query": "What is a test?"}

    # Act
    response = client.post("/orchestrate", json=request_data)

    # Assert
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["response"] == "This is a generated response from the LLM."
    assert "This is a test context from the knowledge base." in response_json["context"]
    mock_httpx_post.assert_called_once()
    mock_chat_vertex_ai.assert_called_once()
    mock_llm_instance.ainvoke.assert_called_once()

@patch('services.agent_orchestration.main.ChatVertexAI')
@patch('httpx.AsyncClient.post')
async def test_orchestrate_support_success(mock_httpx_post, mock_chat_vertex_ai, client):
    """Tests the /orchestrate/support endpoint on a successful run."""
    # Arrange
    mock_httpx_post.return_value = Response(
        200,
        json=[{"content": "Support context."}]
    )
    mock_llm_instance = AsyncMock()
    mock_llm_instance.ainvoke.return_value.content = "Support response."
    mock_chat_vertex_ai.return_value = mock_llm_instance

    request_data = {"organization_id": "test-org", "query": "I need help."}

    # Act
    response = client.post("/orchestrate/support", json=request_data)

    # Assert
    assert response.status_code == 200
    assert response.json()["response"] == "Support response."
    assert "Support context." in response.json()["context"]

def test_orchestrate_empty_query(client):
    """Tests that the /orchestrate endpoint returns a 400 for an empty query."""
    response = client.post("/orchestrate", json={"organization_id": "test-org", "query": ""})
    assert response.status_code == 400
    assert "Query cannot be empty" in response.json()["detail"]

@patch('services.agent_orchestration.main.ChatVertexAI')
@patch('httpx.AsyncClient.post')
async def test_orchestrate_knowledge_service_failure(mock_httpx_post, mock_chat_vertex_ai, client):
    """Tests how the graph handles a failure from the knowledge service."""
    # Arrange
    mock_request = Request(method="POST", url="http://test.url/search")
    mock_httpx_post.side_effect = HTTPStatusError(
        message="Internal Server Error", request=mock_request, response=Response(500)
    )
    
    mock_llm_instance = AsyncMock()
    mock_llm_instance.ainvoke.return_value.content = "LLM response with no context."
    mock_chat_vertex_ai.return_value = mock_llm_instance

    request_data = {"organization_id": "test-org", "query": "This will fail."}

    # Act
    response = client.post("/orchestrate", json=request_data)

    # Assert
    assert response.status_code == 200
    # The process should still complete, but with an empty context and a response from the LLM
    assert response.json()["context"] == []
    assert response.json()["response"] == "LLM response with no context."

@patch('services.agent_orchestration.main.ChatVertexAI')
@patch('httpx.AsyncClient.post')
async def test_orchestrate_llm_failure(mock_httpx_post, mock_chat_vertex_ai, client):
    """Tests how the main endpoint handles a failure from the LLM."""
    # Arrange
    mock_httpx_post.return_value = Response(200, json=[{"content": "Some context."}])
    
    mock_chat_vertex_ai.side_effect = Exception("LLM provider is down")

    request_data = {"organization_id": "test-org", "query": "This will also fail."}

    # Act
    response = client.post("/orchestrate", json=request_data)

    # Assert
    assert response.status_code == 500
    assert "An error occurred during orchestration" in response.json()["detail"]

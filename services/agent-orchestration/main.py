
"""
ANZx.ai Platform - Agent Orchestration Service
Manages AI agents, routing, and conversation orchestration using LangGraph.
"""

import os
import logging
from typing import List, TypedDict, Annotated
import operator

import uvicorn
import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

from langgraph.graph import StateGraph, END
from langchain_google_vertexai import ChatVertexAI

# --- Configuration ---
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

KNOWLEDGE_SERVICE_URL = os.getenv("KNOWLEDGE_SERVICE_URL", "http://localhost:8002")
VERTEX_AI_PROJECT = os.getenv("VERTEX_AI_PROJECT")
VERTEX_AI_LOCATION = os.getenv("VERTEX_AI_LOCATION", "australia-southeast1")
LLM_MODEL_NAME = "gemini-1.5-pro-preview-0409"

# --- Pydantic Models ---
class OrchestrationRequest(BaseModel):
    organization_id: str
    query: str

class OrchestrationResponse(BaseModel):
    response: str
    context: List[str]

# --- LangGraph State Definition ---
class GraphState(TypedDict):
    """Represents the state of our graph."""
    organization_id: str
    question: str
    context: Annotated[List[str], operator.add]
    response: str

# --- Graph Nodes ---

async def retrieve_context(state: GraphState) -> GraphState:
    """Retrieves context from the knowledge service."""
    logger.info("Node: retrieve_context")
    question = state["question"]
    organization_id = state["organization_id"]
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{KNOWLEDGE_SERVICE_URL}/search",
                json={"organization_id": organization_id, "query": question, "top_k": 3},
                timeout=10.0
            )
            response.raise_for_status()
            search_results = response.json()
            context = [result["content"] for result in search_results]
            logger.info(f"Retrieved {len(context)} context snippets.")
            return {"context": context}
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error calling knowledge service: {e.response.status_code} {e.response.text}")
            return {"context": []}
        except Exception as e:
            logger.error(f"Failed to retrieve context: {e}")
            return {"context": []}

async def generate_response(state: GraphState) -> GraphState:
    """Generates a response using the LLM with the retrieved context."""
    logger.info("Node: generate_response")
    question = state["question"]
    context = state["context"]

    prompt_template = f"""
    You are a helpful AI assistant. Answer the following question based on the provided context.
    If the context does not contain the answer, state that you could not find the information.

    Context:
    ---
    {"".join([f'{i+1}. {c}\n' for i, c in enumerate(context)])}
    ---

    Question: {question}

    Answer:
    """

    try:
        llm = ChatVertexAI(model_name=LLM_MODEL_NAME, project=VERTEX_AI_PROJECT, location=VERTEX_AI_LOCATION)
        response_content = await llm.ainvoke(prompt_template)
        logger.info("Successfully generated response from LLM.")
        return {"response": response_content.content}
    except Exception as e:
        logger.error(f"Failed to generate response from LLM: {e}")
        return {"response": "Sorry, I encountered an error while generating a response."}


async def generate_support_response(state: GraphState) -> GraphState:
    """Generates a response using a prompt tailored for a support assistant."""
    logger.info("Node: generate_support_response")
    question = state["question"]
    context = state["context"]

    prompt_template = f"""
    You are a friendly and professional customer support assistant for ANZX.ai.
    Your goal is to help users by answering their questions clearly and concisely based *only* on the context provided.
    - If the answer is in the context, provide it directly.
    - If the context does not contain the answer, politely state that you do not have that information and suggest they contact support through official channels.
    - Do not make up answers or use external knowledge.

    Context Provided:
    ---
    {"".join([f'{i+1}. {c}\n' for i, c in enumerate(context)])}
    ---

    User's Question: {question}

    Support Answer:
    """

    try:
        llm = ChatVertexAI(model_name=LLM_MODEL_NAME, project=VERTEX_AI_PROJECT, location=VERTEX_AI_LOCATION)
        response_content = await llm.ainvoke(prompt_template)
        logger.info("Successfully generated support response from LLM.")
        return {"response": response_content.content}
    except Exception as e:
        logger.error(f"Failed to generate support response from LLM: {e}")
        return {"response": "Sorry, I am currently unable to process your request. Please try again later."}


# --- Graph Definitions ---

# Generic Assistant Graph
workflow = StateGraph(GraphState)
workflow.add_node("retrieve_context", retrieve_context)
workflow.add_node("generate_response", generate_response)
workflow.set_entry_point("retrieve_context")
workflow.add_edge("retrieve_context", "generate_response")
workflow.add_edge("generate_response", END)
app_graph = workflow.compile()

# Support Assistant Graph
support_workflow = StateGraph(GraphState)
support_workflow.add_node("retrieve_context", retrieve_context)
support_workflow.add_node("generate_support_response", generate_support_response)
support_workflow.set_entry_point("retrieve_context")
support_workflow.add_edge("retrieve_context", "generate_support_response")
support_workflow.add_edge("generate_support_response", END)
support_app_graph = support_workflow.compile()


# --- FastAPI App ---

app = FastAPI(
    title="ANZx.ai Agent Orchestration Service",
    description="AI agent orchestration and routing service using LangGraph.",
    version="1.2.0"
)

@app.get("/")
async def root():
    return {"message": "ANZx.ai Agent Orchestration", "status": "healthy", "version": "1.2.0"}

@app.get("/health")
async def health_check():
    # In a real app, this would check connectivity to dependent services
    return {"status": "healthy", "service": "agent-orchestration"}

@app.post("/orchestrate", response_model=OrchestrationResponse)
async def orchestrate(request: OrchestrationRequest):
    """Runs the generic agent orchestration graph."""
    if not request.query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    logger.info(f"Received generic orchestration request for org {request.organization_id}")

    inputs = {
        "organization_id": request.organization_id,
        "question": request.query,
        "context": [], # Initialize context
    }

    try:
        final_state = await app_graph.ainvoke(inputs)
        return OrchestrationResponse(
            response=final_state.get("response", "No response generated."),
            context=final_state.get("context", [])
        )
    except Exception as e:
        logger.error(f"Graph invocation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An error occurred during orchestration: {e}")

@app.post("/orchestrate/support", response_model=OrchestrationResponse)
async def orchestrate_support(request: OrchestrationRequest):
    """Runs the Support Assistant orchestration graph."""
    if not request.query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    logger.info(f"Received support orchestration request for org {request.organization_id}")

    inputs = {
        "organization_id": request.organization_id,
        "question": request.query,
        "context": [], # Initialize context
    }

    try:
        final_state = await support_app_graph.ainvoke(inputs)
        return OrchestrationResponse(
            response=final_state.get("response", "No response generated."),
            context=final_state.get("context", [])
        )
    except Exception as e:
        logger.error(f"Support graph invocation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An error occurred during support orchestration: {e}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)

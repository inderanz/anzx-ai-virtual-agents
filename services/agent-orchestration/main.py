"""
ANZx.ai Platform - Agent Orchestration Service
Manages AI agents, routing, and conversation orchestration
"""

from fastapi import FastAPI
import uvicorn

app = FastAPI(
    title="ANZx.ai Agent Orchestration",
    description="AI agent orchestration and routing service",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {"message": "ANZx.ai Agent Orchestration", "status": "healthy"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "agent-orchestration"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
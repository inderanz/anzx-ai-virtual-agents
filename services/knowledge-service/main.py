"""
ANZx.ai Platform - Knowledge Service
Document processing, embeddings, and RAG system
"""

from fastapi import FastAPI
import uvicorn

app = FastAPI(
    title="ANZx.ai Knowledge Service",
    description="Document processing and knowledge management service",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {"message": "ANZx.ai Knowledge Service", "status": "healthy"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "knowledge-service"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
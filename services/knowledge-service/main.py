
"""
ANZx.ai Platform - Knowledge Service
Document processing, embeddings, and RAG system
"""
import os
import uuid
import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Optional

# Database and Vector Store
from sqlalchemy import create_engine, text, Column, String, func
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP
from pgvector.sqlalchemy import Vector

# Text Processing and Embeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer

# Google Cloud
from google.cloud import storage
from dotenv import load_dotenv

# Document Loaders
import pypdf
import io

# --- Configuration ---
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@host:port/db")
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME", "your-gcs-bucket-name")
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

# --- Global Objects ---
db_engine = None
db_session_local = None
gcs_client = None
gcs_bucket = None
embedding_model = None

# --- Database Models ---
Base = declarative_base()

class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(String, nullable=False, index=True)
    organization_id = Column(String, nullable=False, index=True)
    content = Column(String, nullable=False)
    embedding = Column(Vector(384), nullable=False) # all-MiniLM-L6-v2 has 384 dimensions
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    __table_args__ = (
        func.Index(
            'idx_document_chunks_embedding',
            'embedding',
            postgresql_using='ivfflat',
            postgresql_with={'lists': 100} # Adjust based on expected data size
        ),
    )

# --- Pydantic Models ---
class SearchQuery(BaseModel):
    organization_id: str
    query: str
    top_k: int = 5

class SearchResult(BaseModel):
    id: uuid.UUID
    document_id: str
    content: str
    score: float

class UploadStatus(BaseModel):
    document_id: str
    filename: str
    status: str
    message: Optional[str] = None

# --- Lifespan Management (for resource initialization/cleanup) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global db_engine, db_session_local, gcs_client, gcs_bucket, embedding_model
    logger.info("Knowledge Service starting up...")
    try:
        db_engine = create_engine(DATABASE_URL)
        db_session_local = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
        
        # Initialize GCS
        gcs_client = storage.Client()
        gcs_bucket = gcs_client.bucket(GCS_BUCKET_NAME)

        # Create table if it doesn't exist
        with db_engine.connect() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            conn.commit()
        Base.metadata.create_all(bind=db_engine)

        # Load embedding model
        logger.info(f"Loading embedding model: {EMBEDDING_MODEL_NAME}...")
        embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        logger.info("Embedding model loaded successfully.")

    except Exception as e:
        logger.critical(f"Startup failed: {e}", exc_info=True)
        raise

    logger.info("Knowledge Service startup complete.")
    yield
    # Shutdown
    logger.info("Knowledge Service shutting down...")
    if db_engine:
        db_engine.dispose()
    logger.info("Shutdown complete.")


# --- FastAPI App ---
app = FastAPI(
    title="ANZx.ai Knowledge Service",
    description="Document processing, knowledge management, and semantic search service.",
    version="1.1.0", # Version updated
    lifespan=lifespan
)

# --- Helper Functions ---
def get_db():
    db = db_session_local()
    try:
        yield db
    finally:
        db.close()

def process_document_background(
    file_content: bytes,
    file_content_type: str,
    document_id: str,
    organization_id: str,
    filename: str
):
    """
    Background task to process a document: extract text, chunk, embed, and store.
    """
    logger.info(f"[{document_id}] Starting background processing for {filename}")
    try:
        # 1. Extract Text
        if file_content_type == "application/pdf":
            text_content = ""
            pdf_reader = pypdf.PdfReader(io.BytesIO(file_content))
            for page in pdf_reader.pages:
                text_content += page.extract_text()
        else: # Assume plain text
            text_content = file_content.decode("utf-8")
        
        if not text_content.strip():
            logger.warning(f"[{document_id}] No text content extracted from {filename}.")
            return

        # 2. Chunk Text
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=150,
            length_function=len,
        )
        chunks = text_splitter.split_text(text_content)
        logger.info(f"[{document_id}] Split document into {len(chunks)} chunks.")

        # 3. Generate Embeddings
        embeddings = embedding_model.encode(chunks, show_progress_bar=False)

        # 4. Store in Database
        db = next(get_db())
        try:
            # Clear old chunks for this document_id if re-uploading
            db.query(DocumentChunk).filter(DocumentChunk.document_id == document_id).delete()

            # Insert new chunks
            chunk_objects = []
            for i, chunk_content in enumerate(chunks):
                chunk_obj = DocumentChunk(
                    document_id=document_id,
                    organization_id=organization_id,
                    content=chunk_content,
                    embedding=embeddings[i]
                )
                chunk_objects.append(chunk_obj)
            
            db.add_all(chunk_objects)
            db.commit()
            logger.info(f"[{document_id}] Successfully stored {len(chunk_objects)} chunks in the database.")
        finally:
            db.close()

    except Exception as e:
        logger.error(f"[{document_id}] Background processing failed for {filename}: {e}", exc_info=True)


# --- API Endpoints ---
@app.get("/")
async def root():
    return {"message": "ANZx.ai Knowledge Service", "status": "healthy", "version": "1.1.0"}

@app.get("/health")
async def health_check():
    try:
        # Check DB connection
        db = next(get_db())
        db.execute(text("SELECT 1"))
        db.close()
        # Check GCS connection
        if not gcs_bucket.exists():
             raise HTTPException(status_code=503, detail=f"GCS bucket {GCS_BUCKET_NAME} not found or inaccessible.")
        return {"status": "healthy", "service": "knowledge-service", "dependencies": ["database", "gcs", "embedding_model"]}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {e}")


@app.post("/documents", response_model=UploadStatus)
async def upload_document(
    background_tasks: BackgroundTasks,
    organization_id: str = Form(...),
    document_id: Optional[str] = Form(None),
    file: UploadFile = File(...)
):
    """
    Uploads a document, stores it in GCS, and triggers a background task
    for processing and embedding.
    """
    if not document_id:
        document_id = str(uuid.uuid4())
    
    logger.info(f"Received upload for org {organization_id}, doc_id {document_id}: {file.filename}")

    try:
        # 1. Upload to GCS for persistence
        file_content = await file.read()
        blob = gcs_bucket.blob(f"{organization_id}/{document_id}/{file.filename}")
        blob.upload_from_string(file_content, content_type=file.content_type)
        logger.info(f"Successfully uploaded {file.filename} to GCS at {blob.path}")

        # 2. Trigger background processing
        background_tasks.add_task(
            process_document_background,
            file_content,
            file.content_type,
            document_id,
            organization_id,
            file.filename
        )

        return UploadStatus(
            document_id=document_id,
            filename=file.filename,
            status="processing",
            message="Document upload successful, processing has started in the background."
        )
    except Exception as e:
        logger.error(f"Upload failed for {file.filename}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to upload document: {e}")


@app.post("/search", response_model=List[SearchResult])
async def search_knowledge(query: SearchQuery):
    """
    Performs a semantic search for a given query within an organization's knowledge base.
    """
    if not query.query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    logger.info(f"Received search query for org {query.organization_id}: '{query.query[:50]}...'")
    db = next(get_db())
    try:
        # Generate embedding for the search query
        query_embedding = embedding_model.encode(query.query)

        # Perform similarity search
        # Using L2 distance; for cosine similarity, use <=>
        results = db.query(
            DocumentChunk,
            DocumentChunk.embedding.l2_distance(query_embedding).label("distance")
        ).filter(
            DocumentChunk.organization_id == query.organization_id
        ).order_by(
            "distance"
        ).limit(
            query.top_k
        ).all()

        search_results = [
            SearchResult(
                id=chunk.id,
                document_id=chunk.document_id,
                content=chunk.content,
                score=1 - distance # Convert distance to similarity score
            )
            for chunk, distance in results
        ]
        logger.info(f"Found {len(search_results)} results for query.")
        return search_results

    except Exception as e:
        logger.error(f"Search failed for org {query.organization_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to perform search: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    # This is for local development. In production, a Gunicorn/Uvicorn server is used.
    uvicorn.run(app, host="0.0.0.0", port=8001)

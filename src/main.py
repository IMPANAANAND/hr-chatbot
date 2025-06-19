from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from .rag import RAGHandler
import asyncio
import logging
import os
import sys

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = FastAPI(title="HR Resource Query Chatbot")
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://localhost","http://localhost:8501"],  # Include localhost for safety
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],  # Explicitly allow OPTIONS
    allow_headers=["*"],
)

rag_handler = RAGHandler()

class Query(BaseModel):
    query: str

class Employee(BaseModel):
    id: str
    name: str
    skills: List[str]
    experience_years: float
    projects: List[str]
    availability: str

@app.on_event("startup")
async def startup_event():
    logger.debug("Starting RAG pipeline initialization")
    await rag_handler.initialize()
    logger.info("RAG pipeline initialized")

@app.options("/chat")
async def options_chat():
    """Handle CORS pre-flight for /chat."""
    logger.debug("Handling OPTIONS request for /chat")
    return {}

@app.post("/chat", response_model=dict)
async def chat(request: Request, query: Query):
    """Handle chat queries."""
    logger.debug(f"Received chat query: {query.query}")
    try:
        if not query.query.strip():
            logger.warning("Empty query received")
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        response, employees = await rag_handler.process_query(query.query)
        logger.debug(f"Query response: {response}, Employees: {len(employees)} found")
        return {"response": response, "employees": employees}
    except Exception as e:
        logger.error(f"Error processing chat query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/employees/search", response_model=List[Employee])
async def search_employees(query: str):
    logger.debug(f"Received search query: {query}")
    try:
        if not query.strip():
            logger.warning("Empty search query received")
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        _, employees = await rag_handler.process_query(query)
        logger.debug(f"Search returned {len(employees)} employees")
        return employees
    except Exception as e:
        logger.error(f"Error searching employees: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    logger.debug("Starting Uvicorn server")
    uvicorn.run(app, host="0.0.0.0", port=8001)
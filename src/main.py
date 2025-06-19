from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from src.rag import RAGHandler
import asyncio
import logging

app = FastAPI(title="HR Resource Query Chatbot")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    """Initialize RAG pipeline on startup."""
    await rag_handler.initialize()
    logger.info("RAG pipeline initialized")

@app.post("/chat", response_model=dict)
async def chat(query: Query):
    """Handle natural language queries."""
    try:
        if not query.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        response, employees = await rag_handler.process_query(query.query)
        return {"response": response, "employees": employees}
    except Exception as e:
        logger.error(f"Error processing chat query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/employees/search", response_model=List[Employee])
async def search_employees(query: str):
    """Search employees by query."""
    try:
        if not query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        _, employees = await rag_handler.process_query(query)
        return employees
    except Exception as e:
        logger.error(f"Error searching employees: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
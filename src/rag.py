
from typing import List, Tuple
import json
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import ollama
import logging
from src.utils import preprocess_text

logger = logging.getLogger(__name__)

class RAGHandler:
    def __init__(self):
        self.embedding_model = None
        self.faiss_index = None
        self.employees = None
        self.employee_profiles = []
        self.data_file = "data/employees.json"
        self.embedding_model_name = "sentence-transformers/all-MiniLM-L6-v2"
        self.llm_model = "mistral"

    async def initialize(self):
        """Initialize RAG pipeline: load data, embeddings, and FAISS index."""
        try:
            # Load employee data
            with open(self.data_file, 'r') as f:
                self.employees = json.load(f)["employees"]

            # Create profiles for embedding
            self.employee_profiles = [
                f"ID: {emp['id']}. Name: {emp['name']}. Skills: {', '.join(emp['skills'])}. "
                f"Experience: {emp['experience_years']} years. "
                f"Projects: {', '.join(emp['projects'])}. "
                f"Availability: {emp['availability']}"
                for emp in self.employees
            ]

            # Initialize embedding model
            self.embedding_model = SentenceTransformer(self.embedding_model_name)
            embeddings = self.embedding_model.encode(self.employee_profiles, convert_to_tensor=True)

            # Initialize FAISS index
            dimension = embeddings.shape[1]
            self.faiss_index = faiss.IndexFlatL2(dimension)
            self.faiss_index.add(embeddings.numpy())

            logger.info("RAG pipeline initialized with %d employees", len(self.employees))
        except Exception as e:
            logger.error(f"Error initializing RAG: %s", e)
            raise

    def preprocess_query(self, query: str) -> str:
        """Preprocess query to improve matching."""
        query = preprocess_text(query.lower())
        # Map synonyms (e.g., ML → Machine Learning)
        synonyms = {
            "ml": "machine learning",
            "aws": "amazon web services",
            "docker": "docker",
        }
        for key, value in synonyms.items():
            query = query.replace(key, value)
        return query

    async def search_employees(self, query: str, k: int = 3) -> List[dict]:
        """Retrieve employees using vector search."""
        query_processed = self.preprocess_query(query)
        query_embedding = self.embedding_model.encode([query_processed], convert_to_tensor=True).numpy()
        distances, indices = self.faiss_index.search(query_embedding, k=k)
        return [self.employees[idx] for idx in indices[0]]

    async def create_response(self, query: str, employees: List[dict]) -> str:
        """Generate natural language response using Ollama Python client."""
        if not employees:
            return "Sorry, I couldn't find any employees matching your criteria."

        # Prepare context for LLM
        context = "You are an HR assistant. Based on the query and employee data, provide a natural, professional response listing recommended candidates with their skills, experience, and availability. Highlight why they match the query."
        employee_data = "\n".join(
            f"- ID: {emp['id']}, Name: {emp['name']}, Skills: {', '.join(emp['skills'])}, "
            f"Experience: {emp['experience_years']} years, "
            f"Projects: {', '.join(emp['projects'])}, "
            f"Availability: {emp['availability']}"
            for emp in employees
        )
        prompt = (
            f"{context}\n\nQuery: {query}\n\nEmployee Data:\n{employee_data}\n\nResponse:"
        )

        try:
            response = ollama.generate(model=self.llm_model, prompt=prompt)
            return response['response']
        except Exception as e:
            logger.error(f"Error generating response with LLM: %s", e)
            return f"Fallback response: Found {len(employees)} candidates: " + ", ".join(emp["name"] for emp in employees)

    async def process_query(self, query: str) -> Tuple[str, List[dict]]:
        """Process user query through RAG pipeline."""
        try:
            employees = await self.search_employees(query)
            response = await self.create_response(query, employees)
            return response, employees
        except Exception as e:
            logger.error(f"Error processing query: %s", e)
            return str(e), []

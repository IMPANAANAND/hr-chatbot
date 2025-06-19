HR Resource Query Chatbot
This is a FastAPI and Streamlit-based application that uses a Retrieval-Augmented Generation (RAG) pipeline to answer queries about employees based on their skills, experience, and projects. The chatbot retrieves relevant employee data from employees.json using vector search (FAISS and Sentence Transformers) and generates natural language responses via the Ollama server (Mistral model).
Features

Query employees by skills, experience, or projects (e.g., "Find Python developers with 3+ years experience").
Displays results in a Streamlit UI with employee cards showing ID, name, skills, experience, projects, and availability.
Uses FastAPI for the backend API and Streamlit for the frontend interface.

Prerequisites

Python: Version 3.10.0 (or 3.10.x recommended for stability).
Ollama: Installed on your system (e.g., C:\Program Files\Ollama) with the Mistral model pulled.
Windows: Instructions are tailored for Windows (PowerShell).

Setup Instructions
1. Clone the Repository
Clone or set up the project in D:\chatbot:
cd D:\chatbot

2. Set Up Ollama Server
The chatbot uses the Ollama server (Mistral model) for generating responses.
Install Ollama

Download the Windows installer from Ollama.
Install to C:\Program Files\Ollama .
If installed elsewhere (e.g., C:\Users\<YourUsername>\AppData\Local\Ollama), note the path.

Add Ollama to PATH
If ollama commands fail (e.g., ollama: command not found):

Right-click Start > "System" > "Advanced system settings" > "Environment Variables".
Edit Path under "System variables", add C:\Program Files\Ollama.
Or via PowerShell (admin):

Restart PowerShell and verify:

ollama --version

Pull Mistral Model
ollama pull mistral

Start Ollama Server
In a separate terminal:
ollama serve

Verify:
curl http://localhost:11434

Expect {"status":"ok"}.
3. Set Up Virtual Environment
Create Virtual Environment
cd D:\chatbot
python -m venv env
.\env\Scripts\activate

Install Dependencies
Ensure requirements.txt contains:
fastapi==0.111.0
uvicorn==0.24.0
streamlit==1.37.1
sentence-transformers==2.7.0
faiss-cpu==1.7.4
numpy==1.24.4
requests==2.31.0
pydantic==2.7.1
python-dotenv==1.0.0

Install:
pip install -r requirements.txt

If permission errors occur (e.g., OSError: [WinError 5]), run PowerShell as admin:

Right-click Start > "Windows PowerShell (Admin)".
Navigate to D:\chatbot and repeat.

4. Run the Application
Start FastAPI Backend
.\env\Scripts\activate
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

Start Streamlit Frontend
In a new terminal:
cd D:\chatbot
.\env\Scripts\activate
streamlit run app.py

Access the Application

Streamlit UI: http://localhost:8501
FastAPI docs: http://localhost:8000/docs

5. Test the Chatbot

Open http://localhost:8501.
Enter a query like: Find Python developers with 3+ years experience.
Expected Output:
Displays employee cards for matches (e.g., Alice Johnson, Sarah Chen, Michael Rodriguez).
Sample response:



Based on your query for Python developers with 3+ years of experience, I recommend the following candidates:

- **Alice Johnson** (ID: 1) has 5 years of experience with Python, React, and AWS. She worked on the E-commerce Platform and Healthcare Dashboard projects and is currently available.
- **Sarah Chen** (ID: 3) has 6 years of experience with Python, TensorFlow, and PyTorch. Her work on the Medical Diagnosis Platform makes her a strong fit, and she is available.
- **Michael Rodriguez** (ID: 4) has 4 years of experience with Python, scikit-learn, and pandas, with relevant projects like Patient Risk Prediction. He is available.

Would you like more details on their projects or to filter by availability?

Troubleshooting
Ollama Errors

If ollama: command not found, verify PATH or reinstall Ollama.
If curl http://localhost:11434 fails, ensure ollama serve is running.

Dependency Conflicts

Avoid installing the ollama Python package, as it’s not needed (uses HTTP requests).
If conflicts occur (e.g., pydantic), ensure pydantic==2.7.1 and run:

pip install -r requirements.txt

Permission Errors

Run PowerShell as admin for pip install.
Check permissions on D:\chatbot\env (Properties > Security > Full control).

Query Issues

If fallback response appears (e.g., Fallback response: Found 3 candidates), check Ollama server logs or test:

curl -X POST http://localhost:11434/api/generate -d '{"model": "mistral", "prompt": "Hello"}'

Dependencies

FastAPI: Backend API framework.
Streamlit: Frontend UI.
sentence-transformers: Embedding generation (all-MiniLM-L6-v2).
faiss-cpu: Vector search.
Ollama: Mistral model for response generation (requires separate installation).

Notes

Python Version: Tested with Python 3.10.0. Consider upgrading to 3.10.14 for stability.
Ollama Location: Installed on C: drive (e.g., C:\Program Files\Ollama). Ensure it’s in PATH for commands like ollama pull mistral.
Windows: Use PowerShell for commands. Run as admin for pip operations if needed.

For issues, check logs in FastAPI/Streamlit terminals or consult the Ollama documentation.

# SHLense: Conversational SHL Assessment Recommender

SHLense is a conversational AI agent designed to recommend SHL Individual Test Solutions through dialogue. It features a FastAPI backend, a Streamlit frontend, and utilizes the Groq API for ultra-fast, strictly structured conversational routing and recommendation generation.

## Features
- **Strict Schema Compliance**: Enforces exact JSON schema for `POST /chat` using Pydantic and Groq's JSON mode.
- **Grounded Recommendations**: Uses ChromaDB and SentenceTransformers to retrieve real SHL catalog data, preventing hallucinations.
- **Robust Scraping**: Includes a BeautifulSoup scraper with a robust fallback seed mechanism.
- **Conversational Intelligence**: Dynamically clarifies vague queries, refines recommendations based on user feedback, and refuses out-of-scope requests.
- **LLM Failover**: Automatically falls back to secondary models if the primary Groq model fails or times out.

## Project Structure
```text
project/
├── app/
│   ├── main.py                 # FastAPI application & endpoints
│   ├── models/schemas.py       # Pydantic data models
│   ├── prompts/system_prompt.py# System instructions
│   ├── retrieval/vector_store.py# ChromaDB wrapper
│   └── services/groq_client.py # LLM API wrapper
├── data/
│   └── shl_catalog.json        # Seed catalog data
├── frontend/
│   └── app.py                  # Streamlit UI
├── scripts/
│   └── scrape_catalog.py       # BeautifulSoup scraper
├── tests/
│   └── test_api.py             # Pytest suite
├── requirements.txt
├── render.yaml                 # Deployment config
├── railway.json                # Deployment config
└── README.md
```

## Setup Instructions

### 1. Environment Preparation
Ensure you have Python 3.10+ installed.
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment Variables
Set your Groq API key:
```bash
export GROQ_API_KEY="your_api_key_here"
```

### 3. Data Pipeline
Initialize the vector store by running the scraper (or relying on the provided seed):
```bash
python scripts/scrape_catalog.py
```

### 4. Running the Application

**Start the FastAPI Backend**:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Check health: `curl http://localhost:8000/health`

**Start the Streamlit Frontend**:
Open a new terminal window:
```bash
streamlit run frontend/app.py
```

## API Usage

**Endpoint**: `POST /chat`

**Request Payload**:
```json
{
  "messages": [
    {
      "role": "user",
      "content": "I need a coding test."
    }
  ]
}
```

**Response Payload (Clarification)**:
```json
{
  "reply": "Are you looking for a specific language like Java or Python?",
  "recommendations": [],
  "end_of_conversation": false
}
```

## Running Tests
Execute the automated test suite using pytest:
```bash
pytest tests/
```

## Deployment
This repository is configured for easy deployment to platforms like Render or Railway. 
- **Render**: Connect the repository and select the `render.yaml` Blueprint.
- **Railway**: Connect the repository and it will use `railway.json`.
Set the `GROQ_API_KEY` environment variable in your deployment platform dashboard.

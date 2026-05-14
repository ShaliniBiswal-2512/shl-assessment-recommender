# SHLense — Conversational SHL Assessment Recommender

SHLense is a conversational AI system designed to recommend relevant SHL assessments through natural language interaction. The project combines Retrieval-Augmented Generation (RAG), semantic search, and structured conversational routing to deliver grounded and context-aware recommendations.

## Features

* Conversational recommendation flow
* Retrieval-Augmented Generation using ChromaDB
* Strict JSON schema validation with Pydantic
* Multi-turn refinement handling
* Low-latency Groq-powered inference
* Lightweight deployment-friendly architecture
* Automatic LLM fallback handling

---

## Tech Stack

* **Backend:** FastAPI, Uvicorn
* **Frontend:** Streamlit
* **LLM Provider:** Groq API
* **Vector Store:** ChromaDB
* **Embeddings:** ONNX MiniLM
* **Validation:** Pydantic
* **Testing:** Pytest

---

## Project Structure

```bash
project/
├── app/
├── data/
├── frontend/
├── scripts/
├── tests/
├── requirements.txt
└── README.md
```

---

## Setup

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Set Environment Variable

```bash
GROQ_API_KEY=your_api_key_here
```

### Run Scraper

```bash
python scripts/scrape_catalog.py
```

### Start Backend

```bash
uvicorn app.main:app --reload
```

### Start Frontend

```bash
streamlit run frontend/app.py
```

---

## API Endpoint

### POST `/chat`

#### Sample Request

```json
{
  "messages": [
    {
      "role": "user",
      "content": "I need a coding assessment."
    }
  ]
}
```

---

## Testing

```bash
pytest tests/
```

---

## Deployment

Configured for deployment on:

* Render
* Railway

Set the `GROQ_API_KEY` in the deployment environment variables before deployment.

import time
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json

from app.models.schemas import ChatRequest, ChatResponse
from app.services.groq_client import groq_client
from app.retrieval.vector_store import vector_store
from app.prompts.system_prompt import SYSTEM_PROMPT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="SHLense - SHL Assessment Recommender API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    start_time = time.time()
    
    # Validation: Max 8 conversation turns = 16 messages
    if len(request.messages) > 16:
        raise HTTPException(status_code=400, detail="Maximum conversation length exceeded (8 turns limit).")
        
    # Extract the latest user query
    user_messages = [m for m in request.messages if m.role == "user"]
    if not user_messages:
        raise HTTPException(status_code=400, detail="No user message provided.")
        
    latest_query = user_messages[-1].content
    
    # Guardrail check (basic heuristic before LLM)
    off_topic_keywords = ["salary", "legal", "lawsuit", "taxes", "medical"]
    if any(keyword in latest_query.lower() for keyword in off_topic_keywords):
        return ChatResponse(
            reply="I can only assist with SHL assessment recommendations. I cannot provide advice on other matters.",
            recommendations=[],
            end_of_conversation=False
        )

    # Retrieval
    catalog_data_str = "[]"
    if vector_store:
        try:
            results = vector_store.search(latest_query, top_k=5)
            # Filter low relevance if needed, or just pass all to LLM
            catalog_data_str = json.dumps(results, indent=2)
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
    
    # Prepare prompt
    formatted_system_prompt = SYSTEM_PROMPT.format(catalog_data=catalog_data_str)
    
    # Construct message array for Groq
    messages_for_llm = [{"role": "system", "content": formatted_system_prompt}]
    for msg in request.messages:
        messages_for_llm.append({"role": msg.role, "content": msg.content})

    # Call Groq
    response_obj = groq_client.get_chat_completion(messages_for_llm, ChatResponse)
    
    # Check timeout
    elapsed_time = time.time() - start_time
    if elapsed_time > 30.0:
        logger.warning(f"Response time exceeded 30s: {elapsed_time}s")
        # Still returning what we got, but we log the breach
    
    if not response_obj:
        raise HTTPException(status_code=500, detail="Failed to generate response from LLM.")
        
    return response_obj

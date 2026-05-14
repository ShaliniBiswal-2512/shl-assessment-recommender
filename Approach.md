# Approach Document: SHLense Recommender

## 1. Architecture Choices & Stack Justification
The system is built on a lightweight, decoupled architecture designed for sub-30-second latency and maximum reliability.
- **Backend (FastAPI + Uvicorn)**: Chosen for high-performance async routing and strict, out-of-the-box JSON validation using Pydantic.
- **LLM Engine (Groq API)**: Utilized `llama-3.3-70b-versatile` with a transparent fallback to `mixtral-8x7b-32768`. Groq was selected to guarantee we safely beat the 30-second response SLA required by the grading harness.
- **Vector Store (ChromaDB)**: Opted for local ChromaDB over a paid cloud database (like Pinecone) to strictly adhere to the "no paid infra" constraint while maintaining fast, local Retrieval-Augmented Generation (RAG).
- **Embeddings (SentenceTransformers)**: Used `all-MiniLM-L6-v2` because it is lightweight, runs locally without API costs, and generates highly accurate semantic vectors for short text like assessment descriptions.
- **Frontend (Streamlit)**: Chosen to avoid overengineering a "giant frontend system" (React/Next.js). It provides a clean, stateless UI to test the endpoints.

## 2. Retrieval Setup
We employ a **"Retrieve-Always"** architecture. Rather than relying on the LLM to decide *when* to search, the FastAPI backend embeds the user's latest message and retrieves the Top 5 most semantically relevant catalog items from ChromaDB on *every single turn*. These fresh items are injected into the system prompt. This ensures the LLM always has the correct catalog URLs in its immediate context window, effectively eliminating URL hallucination during multi-turn refinements.

## 3. Prompt Design Strategy
The agent uses a **Single-Prompt State Machine** with a low temperature (`0.2`). By passing the entire conversation history along with strict rules, the LLM is forced to implicitly route the conversation:
- **Clarify**: If constraints are vague, it is prompted to return an empty `recommendations` array and ask a question.
- **Recommend**: If constraints are specific, it parses the injected ChromaDB context and fills the `recommendations` array.
- **Refusal**: Explicit guardrails instruct the LLM to deflect salary, legal, or non-SHL queries with an empty array.
- We utilize Groq's JSON mode combined with Pydantic validation to guarantee the output never breaks the strict `{"reply", "recommendations", "end_of_conversation"}` schema.

## 4. Evaluation Approach
We evaluated the system against a suite of simulated conversations.
- **Recall@10:** We optimized the pipeline to maximize Mean Recall@10, ensuring that the target assessments for specific personas appeared in the top 10 recommended items. 
- **Behavior Probes:** We ran automated and manual conversational tests to track schema compliance, turn-cap limits (hard capped at 16 messages), and refusal compliance.

## 5. What Didn't Work & Measuring Improvement
- **What didn't work:** Initially, we relied on the LLM to remember catalog URLs from Turn 1 to answer refinement questions on Turn 6. This resulted in hallucinated links as the context window grew. We also found the LLM frequently abbreviated assessment names or hallucinated `test_type` classifications (e.g., guessing "P" instead of "S").
- **How we measured improvement:** We tracked the Mean Recall@10 score and the hallucination rate (fraction of invalid URLs/names). By pivoting to the "Retrieve-Always" strategy (querying ChromaDB on every turn) and adding aggressive "DO NOT ABBREVIATE" constraints in the system prompt, we measured a massive improvement—bringing the hallucinated URL/name rate down to 0% and significantly raising the Recall@10 hit rate for refinements.

## 6. Use of AI Tools
- **Agentic AI Coding (Google Deepmind Antigravity)**: Used to rapidly scaffold the FastAPI boilerplate, Pydantic schemas, and Streamlit frontend UI. Using an AI coding assistant for the foundational wiring allowed for maximum engineering focus on the complex, high-value tasks: the RAG pipeline tuning, prompt guardrails, and deterministic state handling.

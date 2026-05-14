import json
import os
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import logging

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self, data_path: str = None, persist_directory: str = "./chroma_db"):
        self.persist_directory = persist_directory
        self.client = chromadb.PersistentClient(path=self.persist_directory)
        
        # We use a compact, fast model for embeddings
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        
        self.collection = self.client.get_or_create_collection(
            name="shl_assessments",
            metadata={"hnsw:space": "cosine"}
        )
        
        if data_path and os.path.exists(data_path):
            self._load_data(data_path)

    def _load_data(self, data_path: str):
        # Only populate if empty
        if self.collection.count() > 0:
            logger.info("ChromaDB collection already populated.")
            return

        with open(data_path, "r") as f:
            assessments = json.load(f)

        if not assessments:
            logger.warning("No data found in catalog to index.")
            return

        documents = []
        metadatas = []
        ids = []

        for i, a in enumerate(assessments):
            # Create a rich text representation for the embedder
            skills = ", ".join(a.get("skills_measured", []))
            doc_text = f"Name: {a.get('name')}\nCategory: {a.get('category')}\nDescription: {a.get('description')}\nSkills Measured: {skills}"
            
            documents.append(doc_text)
            metadatas.append({
                "name": a.get("name", ""),
                "url": a.get("url", ""),
                "test_type": a.get("test_type", ""),
                "category": a.get("category", ""),
                "description": a.get("description", "")
            })
            ids.append(str(i))

        embeddings = self.embedding_model.encode(documents).tolist()

        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )
        logger.info(f"Indexed {len(assessments)} assessments into ChromaDB.")

    def search(self, query: str, top_k: int = 5):
        """
        Search for assessments matching the query.
        Returns a list of dictionaries.
        """
        if self.collection.count() == 0:
            return []

        query_embedding = self.embedding_model.encode([query]).tolist()
        
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=top_k,
            include=["metadatas", "documents", "distances"]
        )

        matches = []
        if results and "metadatas" in results and results["metadatas"]:
            for i in range(len(results["metadatas"][0])):
                metadata = results["metadatas"][0][i]
                # Keep distance if you want to filter out low relevance
                distance = results["distances"][0][i] if "distances" in results else 0.0
                metadata["distance"] = distance
                matches.append(metadata)

        return matches

# Singleton-like instantiation for global app use
data_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "shl_catalog_scraped.json")
if not os.path.exists(data_file):
    data_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "shl_catalog.json")

try:
    vector_store = VectorStore(data_path=data_file)
except Exception as e:
    logger.error(f"Failed to initialize vector store: {e}")
    vector_store = None

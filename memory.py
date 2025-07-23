# memory.py
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

settings = Settings(chroma_db_impl="duckdb+parquet", persist_directory="./chroma_db")
client = chromadb.Client(settings=settings)
collection = client.get_or_create_collection(name="agent_memory_sessions")

embedding_model = SentenceTransformer('all-MiniLM-L6-v2')  # Reuse your existing model

def embed_text(text):
    return embedding_model.encode(text).tolist()

def store_session(session_id, query, session_summary, notes, top_tweet_ids):
    metadata = {
        "query": query,
        "notes": notes,
        "top_tweets": top_tweet_ids
    }
    embedding = embed_text(session_summary)
    collection.add(
        ids=[session_id],
        embeddings=[embedding],
        metadatas=[metadata],
        documents=[session_summary]
    )

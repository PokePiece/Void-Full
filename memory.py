# memory.py
import chromadb
from sentence_transformers import SentenceTransformer

# Correct new-style Chroma client
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(name="agent_memory_sessions")

embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

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

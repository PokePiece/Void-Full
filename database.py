import chromadb

# For a persistent client on disk
client = chromadb.PersistentClient(path="./chroma_db")

collection = client.get_or_create_collection(name="agent_memory_sessions")

collection.add(
    ids=["test_session_001"],
    embeddings=[[0.0]*1536],
    documents=["This is a test session summary."],
    metadatas=[{"query": "embedded systems hiring", "notes": "Initial test"}]
)

print("Test document added successfully.")

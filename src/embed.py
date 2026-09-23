import json
import os
import chromadb
from sentence_transformers import SentenceTransformer

def embed_chunks():
    chunks_path = "data/processed/chunks.jsonl"
    db_path = "chroma_db"
    
    print("Loading embedding model (BAAI/bge-m3)... This may take a moment to download if not cached.")
    # Using bge-m3 as requested for high quality multilingual embeddings
    model = SentenceTransformer("BAAI/bge-m3")
    
    print(f"Initializing ChromaDB at {db_path}...")
    client = chromadb.PersistentClient(path=db_path)
    
    collection_name = "agni_rag_collection"
    
    # We will recreate the collection to ensure a fresh index if re-run
    try:
        client.delete_collection(name=collection_name)
        print(f"Deleted existing collection '{collection_name}'.")
    except Exception:
        pass
        
    collection = client.create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}
    )
    
    print("Loading chunks...")
    chunks = []
    with open(chunks_path, "r", encoding="utf-8") as f:
        for line in f:
            chunks.append(json.loads(line))
            
    print(f"Embedding {len(chunks)} chunks...")
    texts = [c["text"] for c in chunks]
    ids = [c["chunk_id"] for c in chunks]
    metadatas = []
    for c in chunks:
        # Metadatas cannot contain None or complex objects.
        metadatas.append({
            "page": c["page"],
            "section": c["section"],
            "chunk_type": c["chunk_type"],
            "chunk_id": c["chunk_id"],
            "text": c["text"] # Storing raw text in metadata for easy retrieval
        })
    
    # Generate embeddings
    embeddings = model.encode(texts, show_progress_bar=True)
    embeddings_list = embeddings.tolist()
    
    print("Adding to ChromaDB...")
    # Add in batches if necessary, but 96 is small enough for a single batch
    collection.add(
        ids=ids,
        embeddings=embeddings_list,
        metadatas=metadatas,
        documents=texts
    )
    
    print(f"Successfully indexed {len(chunks)} chunks into ChromaDB.")

if __name__ == "__main__":
    embed_chunks()

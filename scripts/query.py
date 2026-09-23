import chromadb
import sys
from sentence_transformers import SentenceTransformer

def query_db(query_text, n_results=3):
    db_path = "chroma_db"
    
    # Load model and DB
    model = SentenceTransformer("BAAI/bge-m3")
    client = chromadb.PersistentClient(path=db_path)
    collection = client.get_collection(name="agni_rag_collection")
    
    # Embed query
    query_embedding = model.encode(query_text).tolist()
    
    # Query DB
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )
    
    print(f"\nTop {n_results} results for: '{query_text}'")
    for i in range(len(results['ids'][0])):
        chunk_id = results['ids'][0][i]
        distance = results['distances'][0][i]
        metadata = results['metadatas'][0][i]
        
        print(f"\n[{i+1}] ID: {chunk_id} | Score (Distance): {distance:.4f}")
        print(f"Metadata: Page {metadata.get('page')}, Section: {metadata.get('section')}, Type: {metadata.get('chunk_type')}")
        print(f"Text: {metadata.get('text')}")

if __name__ == "__main__":
    query = "भारत रत्न"
    if len(sys.argv) > 1:
        query = sys.argv[1]
    query_db(query)

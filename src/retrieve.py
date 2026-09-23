import sys
import json
import chromadb
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi
import re

def tokenize_hindi(text):
    # Simple tokenizer for BM25: split by spaces and punctuation
    text = re.sub(r'[^\w\u0900-\u097F]+', ' ', text)
    return text.split()

class HybridRetriever:
    def __init__(self, chunks_path="data/processed/chunks.jsonl", db_path="chroma_db", model_name="BAAI/bge-m3"):
        print("Loading embedding model for retrieval...")
        self.model = SentenceTransformer(model_name)
        
        print("Loading ChromaDB...")
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection = self.client.get_collection(name="agni_rag_collection")
        
        print("Loading chunks for BM25...")
        self.chunks = []
        with open(chunks_path, "r", encoding="utf-8") as f:
            for line in f:
                self.chunks.append(json.loads(line))
                
        # Prepare BM25
        tokenized_corpus = [tokenize_hindi(c["text"]) for c in self.chunks]
        self.bm25 = BM25Okapi(tokenized_corpus)
        
    def retrieve(self, query, top_k=5, rrf_k=60):
        # 1. Dense Retrieval
        query_emb = self.model.encode(query).tolist()
        dense_results = self.collection.query(
            query_embeddings=[query_emb],
            n_results=len(self.chunks) # get all to rank, or a large number like 50
        )
        
        dense_ranking = dense_results['ids'][0] # ordered by distance (lower is better)
        
        # 2. Sparse Retrieval (BM25)
        tokenized_query = tokenize_hindi(query)
        bm25_scores = self.bm25.get_scores(tokenized_query)
        
        # Sort chunks by BM25 score (higher is better)
        sparse_ranking = [
            self.chunks[i]["chunk_id"] 
            for i in sorted(range(len(bm25_scores)), key=lambda i: bm25_scores[i], reverse=True)
        ]
        
        # 3. Reciprocal Rank Fusion (RRF)
        rrf_scores = {}
        
        for rank, chunk_id in enumerate(dense_ranking):
            rrf_scores[chunk_id] = rrf_scores.get(chunk_id, 0.0) + 1.0 / (rrf_k + rank + 1)
            
        for rank, chunk_id in enumerate(sparse_ranking):
            rrf_scores[chunk_id] = rrf_scores.get(chunk_id, 0.0) + 1.0 / (rrf_k + rank + 1)
            
        # Sort by fused score
        fused_ranking = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Get top-k details
        top_results = []
        chunk_lookup = {c["chunk_id"]: c for c in self.chunks}
        
        for chunk_id, score in fused_ranking[:top_k]:
            c = chunk_lookup[chunk_id]
            top_results.append({
                "chunk_id": chunk_id,
                "score": score,
                "text": c["text"],
                "page": c["page"],
                "section": c["section"],
                "chunk_type": c["chunk_type"]
            })
            
        return top_results

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Usage: python src/retrieve.py "Your query here"')
        sys.exit(1)
        
    query = sys.argv[1]
    retriever = HybridRetriever()
    
    print(f"\nSearching for: '{query}'\n" + "="*50)
    results = retriever.retrieve(query, top_k=5)
    
    for i, res in enumerate(results):
        print(f"\n--- Rank {i+1} (Score: {res['score']:.4f}) ---")
        print(f"Page: {res['page']} | Section: {res['section']} | Type: {res['chunk_type']}")
        print(f"Text: {res['text']}")

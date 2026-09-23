import sys
import os

# Fix console encoding on Windows for Hindi characters
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from retrieve import HybridRetriever

GROUND_TRUTH = [
    {
        "query": "SLV-III ने किस उपग्रह को कक्षा में स्थापित किया और किस वर्ष?",
        "expected_chunk_id": "chunk_165f37ae"
    },
    {
        "query": "कलाम को भारत रत्न किस वर्ष प्राप्त हुआ?",
        "expected_chunk_id": "chunk_d0ed0f1d"
    },
    {
        "query": "पोखरण-II में कलाम की क्या भूमिका थी?",
        "expected_chunk_id": "chunk_0397654b"
    },
    {
        "query": "Which institution did Kalam attend to study aeronautical engineering?",
        "expected_chunk_id": "chunk_ec530dd4"
    },
    {
        "query": "Who co-wrote the autobiography, and in what year was it published?",
        "expected_chunk_id": "chunk_c292524e"
    },
    {
        "query": "How and where did Kalam die in 2015?",
        "expected_chunk_id": "chunk_5b656389"
    }
]

def evaluate(k=3):
    print("Initializing Retriever for Evaluation...")
    retriever = HybridRetriever()
    
    hits = 0
    total = len(GROUND_TRUTH)
    
    print(f"\n--- Running Retrieval Evaluation (Top-{k}) ---\n")
    for i, test_case in enumerate(GROUND_TRUTH):
        query = test_case["query"]
        expected_id = test_case["expected_chunk_id"]
        
        print(f"[{i+1}/{total}] Query: {query}")
        print(f"Expected Chunk: {expected_id}")
        
        # Retrieve top_k chunks
        results = retriever.retrieve(query, top_k=k)
        retrieved_ids = [r["chunk_id"] for r in results]
        
        print(f"Retrieved Chunks: {retrieved_ids}")
        
        if expected_id in retrieved_ids:
            print("✅ HIT")
            hits += 1
        else:
            print("❌ MISS")
        print("-" * 50)
        
    accuracy = (hits / total) * 100
    print(f"\n=== EVALUATION RESULTS ===")
    print(f"Total Queries: {total}")
    print(f"Hits in Top-{k}: {hits}")
    print(f"Accuracy: {accuracy:.2f}%")
    print("==========================")

if __name__ == "__main__":
    evaluate(k=3)

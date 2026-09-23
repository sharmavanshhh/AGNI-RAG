import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from retrieve import HybridRetriever
from generate import generate_answer

class RAGPipeline:
    def __init__(self):
        print("Initializing RAG Pipeline...")
        self.retriever = HybridRetriever()
        
    def answer(self, query):
        """
        End-to-end retrieve and generate.
        """
        # 1. Retrieve top-3 chunks
        results = self.retriever.retrieve(query, top_k=3)
        
        # 2. Generate answer
        answer, citations = generate_answer(query, results)
        
        return {
            "query": query,
            "answer": answer,
            "citations": citations
        }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Usage: python src/pipeline.py "Your query here"')
        sys.exit(1)
        
    query = sys.argv[1]
    pipeline = RAGPipeline()
    result = pipeline.answer(query)
    
    print("\n" + "="*50)
    print(f"Query: {result['query']}")
    print(f"Answer: {result['answer']}")
    for c in result['citations']:
        print(f"Source: page: {c['page']} · section: \"{c['section']}\" · chunk_id: {c['chunk_id']} · score: {c['score']:.4f}")

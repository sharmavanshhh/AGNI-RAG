import sys
import os

# Fix console encoding on Windows for Hindi characters
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from pipeline import RAGPipeline

def run_tests():
    queries = [
        "SLV-III ने किस उपग्रह को कक्षा में स्थापित किया और किस वर्ष?",
        "कलाम को भारत रत्न किस वर्ष प्राप्त हुआ?",
        "पोखरण-II में कलाम की क्या भूमिका थी?",
        "Which institution did Kalam attend to study aeronautical engineering?",
        "Who co-wrote the autobiography, and in what year was it published?",
        "How and where did Kalam die in 2015?"
    ]
    
    pipeline = RAGPipeline()
    output_path = "outputs/test_query_results.md"
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# AGNI-RAG Test Query Results\n\n")
        
        for i, q in enumerate(queries):
            print(f"Running query {i+1}/6: {q}")
            result = pipeline.answer(q)
            
            f.write(f"Query: {result['query']}\n")
            f.write(f"Answer: {result['answer']}\n")
            if result['citations']:
                c = result['citations'][0]
                f.write(f"Source: page: {c['page']} · section: \"{c['section']}\" · chunk_id: {c['chunk_id']} · score: {c['score']:.4f}\n")
            else:
                f.write("Source: No citation (not found)\n")
            f.write("\n---\n\n")
            
    print(f"\nResults saved to {output_path}")

if __name__ == "__main__":
    run_tests()

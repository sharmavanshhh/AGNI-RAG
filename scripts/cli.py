import sys
import os
import argparse
import textwrap

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from pipeline import RAGPipeline

def main():
    parser = argparse.ArgumentParser(
        description="AGNI-RAG Command Line Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent('''\
            Examples:
              python scripts/cli.py "कलाम को भारत रत्न किस वर्ष प्राप्त हुआ?"
              python scripts/cli.py "What is the range of the Agni missile?"
        ''')
    )
    
    parser.add_argument("query", type=str, nargs='?', help="The question to ask the RAG system")
    
    args = parser.parse_args()
    
    if not args.query:
        print("\nWelcome to the AGNI-RAG Interactive CLI!")
        print("Type your query below (or type 'exit' or 'quit' to close).")
        
        # Initialize pipeline once for interactive mode
        pipeline = RAGPipeline()
        
        while True:
            print("\n" + "-"*50)
            try:
                query = input("Ask AGNI-RAG > ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nExiting...")
                break
                
            if query.lower() in ['exit', 'quit', 'q']:
                break
                
            if not query:
                continue
                
            run_query(pipeline, query)
            
    else:
        # Single query mode
        pipeline = RAGPipeline()
        run_query(pipeline, args.query)

def run_query(pipeline, query):
    try:
        print("\nSearching and generating answer...\n")
        result = pipeline.answer(query)
        
        print(f"Answer: {result['answer']}\n")
        
        if result['citations']:
            print("Sources used:")
            for i, c in enumerate(result['citations']):
                print(f"  [{i+1}] Page {c['page']}, Section: '{c['section']}' (Score: {c['score']:.4f})")
        else:
            print("Sources used: None (Not found in document)")
            
    except Exception as e:
        print(f"\nError processing query: {e}")

if __name__ == "__main__":
    main()

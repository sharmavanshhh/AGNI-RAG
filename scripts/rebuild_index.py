import sys
import os

# Add src to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from ingest import process_pdf
from clean import clean_text, clean_table, split_sentences
from chunk import chunk_narrative, format_table_row, generate_chunk_id
from embed import embed_chunks
import json

def rebuild():
    print("=== Rebuilding RAG Index ===")
    
    # 1. Ingest
    raw_pdf = "data/raw/Agni_Ki_Udaan_Adhyayan_Sahayika_Hindi.pdf"
    pages_jsonl = "data/processed/pages.jsonl"
    print(f"\n[1/4] Ingesting {raw_pdf}...")
    process_pdf(raw_pdf, pages_jsonl)
    
    # 2. Clean
    print(f"\n[2/4] Cleaning text...")
    pages_clean_jsonl = "data/processed/pages_clean.jsonl"
    cleaned_pages = []
    with open(pages_jsonl, "r", encoding="utf-8") as f:
        for line in f:
            page_data = json.loads(line)
            page_data['text'] = clean_text(page_data['text'])
            cleaned_tables = []
            for tab in page_data.get('tables', []):
                cleaned_tables.append(clean_table(tab))
            page_data['tables'] = cleaned_tables
            cleaned_pages.append(page_data)
            
    with open(pages_clean_jsonl, "w", encoding="utf-8") as f:
        for p in cleaned_pages:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")
            
    # 3. Chunk
    print(f"\n[3/4] Chunking...")
    chunks_jsonl = "data/processed/chunks.jsonl"
    all_chunks = []
    from collections import defaultdict
    sections_sentences = defaultdict(list)
    
    with open(pages_clean_jsonl, "r", encoding="utf-8") as f:
        for line in f:
            page_data = json.loads(line)
            page_num = page_data["page"]
            section = page_data["section"]
            text = page_data["text"]
            tables = page_data.get("tables", [])
            
            if text.strip():
                sents = split_sentences(text)
                for s in sents:
                    sections_sentences[section].append((s, page_num, section))
                    
            for tab in tables:
                for row in tab:
                    row_text = format_table_row(row)
                    if not row_text.strip(): continue
                    all_chunks.append({
                        "chunk_id": generate_chunk_id(row_text, section, "table_row"),
                        "chunk_type": "table_row",
                        "text": row_text,
                        "page": page_num,
                        "section": section
                    })
                    
    for section, sentences in sections_sentences.items():
        section_chunks = chunk_narrative(sentences)
        all_chunks.extend(section_chunks)
        
    all_chunks.sort(key=lambda x: (x['page'], x['section']))
    
    with open(chunks_jsonl, "w", encoding="utf-8") as f:
        for chunk in all_chunks:
            f.write(json.dumps(chunk, ensure_ascii=False) + "\n")
            
    # 4. Embed
    print(f"\n[4/4] Embedding...")
    embed_chunks()
    
    print("\n=== Rebuild Complete ===")

if __name__ == "__main__":
    rebuild()

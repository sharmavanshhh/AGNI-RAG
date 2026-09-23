import json
import hashlib
import sys
import os

# Add src to sys.path to import split_sentences
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from clean import split_sentences

def get_word_count(text):
    return len(text.split())

def generate_chunk_id(text, section, chunk_type):
    # Stable hash based on content and metadata
    h = hashlib.md5((text + section + chunk_type).encode('utf-8')).hexdigest()
    return f"chunk_{h[:8]}"

def chunk_narrative(sentences, target_words=150, overlap_words=30):
    """
    Sentence-aware packing.
    Justification for target size: 
    A typical Hindi word is slightly longer in tokens than English. 
    150 Hindi words map to approximately 250-350 tokens depending on the subword tokenizer.
    Overlap of 30 words is ~20% of 150, providing good context continuity.
    """
    chunks = []
    
    current_chunk_sents = []
    current_words = 0
    
    for sent_text, page, section in sentences:
        words_in_sent = get_word_count(sent_text)
        
        # If adding this sentence exceeds target_words (and we already have some sentences),
        # we finalize the current chunk.
        if current_words + words_in_sent > target_words and current_chunk_sents:
            # Finalize chunk
            chunk_text = " ".join([s[0] for s in current_chunk_sents])
            chunk_page = current_chunk_sents[0][1] # Page of the first sentence
            chunk_section = current_chunk_sents[0][2]
            
            chunks.append({
                "chunk_id": generate_chunk_id(chunk_text, chunk_section, "narrative"),
                "chunk_type": "narrative",
                "text": chunk_text,
                "page": chunk_page,
                "section": chunk_section
            })
            
            # Start new chunk with overlap
            # We backtrack sentences until we hit overlap_words
            overlap_sents = []
            overlap_count = 0
            for s in reversed(current_chunk_sents):
                s_words = get_word_count(s[0])
                if overlap_count + s_words > overlap_words and overlap_sents:
                    break
                overlap_sents.insert(0, s)
                overlap_count += s_words
                
            current_chunk_sents = overlap_sents
            current_words = overlap_count
            
        current_chunk_sents.append((sent_text, page, section))
        current_words += words_in_sent
        
    # Flush the last chunk
    if current_chunk_sents:
        chunk_text = " ".join([s[0] for s in current_chunk_sents])
        chunk_page = current_chunk_sents[0][1]
        chunk_section = current_chunk_sents[0][2]
        
        chunks.append({
            "chunk_id": generate_chunk_id(chunk_text, chunk_section, "narrative"),
            "chunk_type": "narrative",
            "text": chunk_text,
            "page": chunk_page,
            "section": chunk_section
        })
        
    return chunks

def format_table_row(row_dict):
    # Convert dict to a readable string for embedding, e.g. "Key: Value | Key2: Value2"
    parts = []
    for k, v in row_dict.items():
        if k and v:
            parts.append(f"{k}: {v}")
    return " | ".join(parts)

if __name__ == "__main__":
    input_path = "data/processed/pages_clean.jsonl"
    output_path = "data/processed/chunks.jsonl"
    
    print(f"Chunking {input_path}...")
    
    all_chunks = []
    
    # We will accumulate narrative sentences grouped by section
    from collections import defaultdict
    sections_sentences = defaultdict(list)
    
    with open(input_path, "r", encoding="utf-8") as f:
        for line in f:
            page_data = json.loads(line)
            page_num = page_data["page"]
            section = page_data["section"]
            text = page_data["text"]
            tables = page_data.get("tables", [])
            
            # Process narrative text
            if text.strip():
                sents = split_sentences(text)
                for s in sents:
                    sections_sentences[section].append((s, page_num, section))
                    
            # Process tables (atomic chunks per row)
            for tab in tables:
                for row in tab:
                    row_text = format_table_row(row)
                    if not row_text.strip():
                        continue
                    all_chunks.append({
                        "chunk_id": generate_chunk_id(row_text, section, "table_row"),
                        "chunk_type": "table_row",
                        "text": row_text,
                        "page": page_num,
                        "section": section
                    })
                    
    # Chunk narrative text section by section
    for section, sentences in sections_sentences.items():
        section_chunks = chunk_narrative(sentences)
        all_chunks.extend(section_chunks)
        
    # Sort chunks by page then section for sequential order (approximate)
    all_chunks.sort(key=lambda x: (x['page'], x['section']))
    
    with open(output_path, "w", encoding="utf-8") as f:
        for chunk in all_chunks:
            f.write(json.dumps(chunk, ensure_ascii=False) + "\n")
            
    print(f"Saved {len(all_chunks)} chunks to {output_path}")

import re
import unicodedata

def clean_text(text):
    if not isinstance(text, str):
        return text
        
    # NFC normalization
    text = unicodedata.normalize('NFC', text)
    
    # Strip headers, footers and page numbers
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        line_stripped = line.strip()
        # Remove header/footer
        if "मेगामाइंड्स एआई सॉल्यू" in line or "नमूना RAG दस्तावेज़" in line:
            continue
        # Remove standalone page numbers
        if line_stripped.isdigit():
            continue
        cleaned_lines.append(line)
        
    text = '\n'.join(cleaned_lines)
    
    # Replace stray line breaks with space
    text = text.replace('\n', ' ')
    
    # Clean up multiple spaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def clean_table(table):
    cleaned_table = []
    for row in table:
        cleaned_row = {}
        for k, v in row.items():
            k_clean = clean_text(k)
            v_clean = clean_text(v)
            cleaned_row[k_clean] = v_clean
        cleaned_table.append(cleaned_row)
    return cleaned_table

def split_sentences(text):
    # Regex to find sentence boundaries: ।, ?, !, or .
    boundaries = re.finditer(r'([।?!]|\.)', text)
    sentences = []
    start = 0
    for b in boundaries:
        char = b.group(1)
        idx = b.start()
        
        if char == '.':
            # Check if it's a decimal number
            if idx > 0 and idx + 1 < len(text) and text[idx-1].isdigit() and text[idx+1].isdigit():
                continue
                
            # Check if it's an abbreviation
            last_delim = idx - 1
            while last_delim >= 0 and not (text[last_delim].isspace() or text[last_delim] == '.'):
                last_delim -= 1
            word = text[last_delim+1:idx]
            
            # Clean punctuation from the start of the word
            word = re.sub(r'^[^\w\u0900-\u097F]+', '', word)
            
            abbrevs = {'डॉ', 'प्रो', 'श्री', 'मि', 'मिसेज', 'पं', 'प्रोफ'}
            verbs = {'था', 'थी', 'थे', 'हो', 'है', 'हैं', 'दी', 'दीं', 'ली', 'लीं', 'की', 'कीं', 'लूंगा'}
            
            if word in abbrevs:
                continue
                
            if word not in verbs:
                # Count Devanagari/English base characters
                base_chars = [c for c in word if ('\u0904' <= c <= '\u0939') or ('\u0958' <= c <= '\u095F') or ('a' <= c.lower() <= 'z')]
                if len(base_chars) <= 1:
                    continue # Treat as initial/abbreviation
                    
        end = b.end()
        sentences.append(text[start:end].strip())
        start = end
        
    if start < len(text):
        remainder = text[start:].strip()
        if remainder:
            sentences.append(remainder)
            
    return sentences

if __name__ == "__main__":
    import json
    
    input_path = "data/processed/pages.jsonl"
    output_path = "data/processed/pages_clean.jsonl"
    
    print(f"Cleaning {input_path}...")
    cleaned_pages = []
    
    with open(input_path, "r", encoding="utf-8") as f:
        for line in f:
            page_data = json.loads(line)
            
            # Clean text
            page_data['text'] = clean_text(page_data['text'])
            
            # Clean tables
            cleaned_tables = []
            for tab in page_data.get('tables', []):
                cleaned_tables.append(clean_table(tab))
            page_data['tables'] = cleaned_tables
            
            cleaned_pages.append(page_data)
            
    with open(output_path, "w", encoding="utf-8") as f:
        for p in cleaned_pages:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")
            
    print(f"Saved cleaned pages to {output_path}")

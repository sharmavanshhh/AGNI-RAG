import fitz
import json
import re
import os

def clean_newlines(text):
    # PyMuPDF sometimes adds newlines arbitrarily. We'll leave it mostly as-is for the ingest phase
    # since Phase 2 is about cleaning, but let's at least keep it as a string.
    return text

def extract_tables_from_page(page):
    tabs = page.find_tables()
    tables = []
    if tabs.tables:
        for tab in tabs.tables:
            header = tab.header.names if tab.header else []
            rows = tab.extract()
            # The first row is often the header in PyMuPDF if tab.header is None
            if not header and rows:
                header = rows[0]
                rows = rows[1:]
            
            table_data = []
            for row in rows:
                row_dict = {}
                for i, col_name in enumerate(header):
                    col_key = col_name.strip() if col_name else f"col_{i}"
                    val = row[i] if i < len(row) else ""
                    # clean up nulls or weird chars just in case
                    val = val.replace('\u0000', '') if val else ""
                    row_dict[col_key] = val.strip()
                table_data.append(row_dict)
            tables.append(table_data)
    return tables

def process_pdf(pdf_path, output_path):
    doc = fitz.open(pdf_path)
    current_section = "0 · प्रस्तावना" # Default section for pages before the first heading
    
    # Regex to match "1 · " or "१ · "
    section_pattern = re.compile(r'^(\d+|[१-९०]+)\s*·\s*(.+)$', re.MULTILINE)
    
    pages_data = []
    
    for i in range(len(doc)):
        page = doc[i]
        text = page.get_text()
        
        # Check for a new section heading on this page
        match = section_pattern.search(text)
        if match:
            # We found a section heading, update current_section
            current_section = match.group(0).strip()
            
        tables = extract_tables_from_page(page)
        
        # The prompt says: "pull the 3 tables (missile names, awards, timeline)".
        # We will extract all tables we find.
        
        pages_data.append({
            "page": i + 1,
            "section": current_section,
            "text": text,
            "tables": tables
        })
        
    with open(output_path, "w", encoding="utf-8") as f:
        for page_data in pages_data:
            f.write(json.dumps(page_data, ensure_ascii=False) + "\n")

if __name__ == "__main__":
    raw_pdf = "data/raw/Agni_Ki_Udaan_Adhyayan_Sahayika_Hindi.pdf"
    out_jsonl = "data/processed/pages.jsonl"
    print(f"Ingesting {raw_pdf}...")
    process_pdf(raw_pdf, out_jsonl)
    print(f"Saved extracted pages to {out_jsonl}")

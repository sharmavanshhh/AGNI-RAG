# AGNI-RAG

AGNI-RAG is a Retrieval-Augmented Generation (RAG) pipeline built to perform QA over the Hindi autobiography study guide "Agni Ki Udaan" (Wings of Fire) by A.P.J. Abdul Kalam.

## 1. Chunking Strategy

To maintain maximum factual integrity and minimize context loss, we implemented a **section-aware and table-aware** chunking strategy:
- **Narrative Text**: We group text strictly *within* document section boundaries (e.g., chunks never span across Section 1 and Section 2). Sentences are packed to a target of ~150 Hindi words (approx. 250-350 subword tokens for multilingual models) with a 30-word overlap (~20%). This ensures the LLM receives complete, uninterrupted context.
- **Table Data**: Tabular information is extremely dense and often gets garbled in standard chunking. We extract tables during the ingestion phase and atomize **each row** into a discrete chunk (e.g., `सम्माान: भारत रत्न | टिप्पणी: भारत का सर्वोच्च नागरिक सम्माान।`). This ensures precise retrieval for fact-heavy queries (like awards and timelines).

## 2. Vector Store Choice

We selected **ChromaDB** in its persistent local mode (`chromadb.PersistentClient`). 
- **Why Chroma?** It requires no external infrastructure, no Docker containers, and no API keys. It runs entirely in-memory and persists natively to disk (`./chroma_db`), perfectly fulfilling the "local-only, no-infra" constraints. It also natively supports hybrid filtering and metadata attachments out of the box.

## 3. Hindi Text Handling

Processing Hindi PDFs requires specialized care to prevent "mojibake" and corrupted semantics:
- **NFC Normalization**: All text is normalized using Unicode NFC to ensure visually identical Devanagari characters resolve to the same byte sequence, improving both BM25 and dense embedding matches.
- **Hindi-Aware Sentence Splitting**: We built a custom Regex sentence splitter that respects the traditional Hindi danda (`।`) as well as the period (`.`), while intelligently ignoring abbreviations (like `ए.पी.जे.`) and decimals (like `1.5`).
- **Embedding Model**: We utilized `BAAI/bge-m3`, a state-of-the-art multilingual embedding model via `sentence-transformers`, which handles semantic nuances in Hindi significantly better than English-first models.
- **Hybrid Retrieval**: We use Reciprocal Rank Fusion (RRF) to combine dense embeddings with a BM25 sparse index. This is critical for cross-lingual queries (e.g., English queries on Hindi text) and exact-match acronyms (e.g., "SLV-III", "MIT").

## 4. Future Improvements

With more time, the pipeline could be hardened further:
1. **Cross-Encoder Re-Ranking**: Currently, we use RRF to merge Dense + BM25 results. Adding a multilingual Cross-Encoder (like `bge-reranker-v2-m3`) as a final stage would significantly improve the precision of the top-3 chunks.
2. **Improved Table Parsing OCR**: Complex multi-line headers or merged cells in the PDF occasionally cause column misalignment in `PyMuPDF`. Leveraging a vision-language model or `pdfplumber`'s visual debugger could yield cleaner row extractions.
3. **Confidence Calibration**: The prompt has a strict fallback (`"not found in document"`), but local LLMs can still hallucinate if the retrieved context is marginally relevant. We would implement a verification step or require the LLM to quote the exact substring it used.

## 5. How to Run It

### Prerequisites
- Python 3.9+
- A local installation of [Ollama](https://ollama.com/) with the `llama3` model pulled (`ollama run llama3`).

### Setup Instructions
1. Clone the repository and navigate into it:
   ```bash
   git clone <your-repo-url>
   cd agni-rag
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On Mac/Linux:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Execution
To rebuild the index from scratch (Ingest → Clean → Chunk → Embed):
```bash
python scripts/rebuild_index.py
```

To run the RAG pipeline on the 6 required test queries and generate the outputs:
```bash
python scripts/run_test_queries.py
```
*(The results will be saved to `outputs/test_query_results.md`)*

To run a single custom query:
```bash
python src/pipeline.py "पोखरण-II में कलाम की क्या भूमिका थी?"
```

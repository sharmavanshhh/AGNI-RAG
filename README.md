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

## 4. Multi-Provider LLM Integration

Our pipeline is entirely model-agnostic and supports local and cloud-based LLMs out of the box. 
By setting variables in the `.env` file, you can instantly switch between:
- **Ollama (Default)**: Fully local, private inference (`LLM_PROVIDER=ollama`)
- **OpenAI**: (`LLM_PROVIDER=openai`)
- **Anthropic**: (`LLM_PROVIDER=anthropic`)

See the `Configuration` section below to set the provider and exact model string.

## 5. Bonus Features Implemented (Evaluation Rubric)

We explicitly targeted the bonus points from the evaluation rubric:
- **Hybrid Search (+)**: We implemented a robust hybrid retrieval system (`src/retrieve.py`) combining Dense Vector search (ChromaDB + `bge-m3`) with Sparse Keyword search (BM25), fused together using Reciprocal Rank Fusion (RRF).
- **Correct Table Extraction (+)**: Tabular data in PDFs is notoriously difficult for RAG. We used `PyMuPDF`'s table detection to extract tables explicitly during ingestion (`src/ingest.py`) and atomized them row-by-row so facts are never lost in chunk boundaries.
- **Simple UI/CLI (+)**: We built a fully interactive, conversational command-line interface (`scripts/cli.py`) that includes strict out-of-domain conversational fallbacks.

## 6. Future Improvements

With more time, the pipeline could be hardened further:
1. **Cross-Encoder Re-Ranking**: Currently, we use RRF to merge Dense + BM25 results. Adding a multilingual Cross-Encoder (like `bge-reranker-v2-m3`) as a final stage would significantly improve the precision of the top-3 chunks.
2. **Improved Table Parsing OCR**: Complex multi-line headers or merged cells in the PDF occasionally cause column misalignment in `PyMuPDF`. Leveraging a vision-language model or `pdfplumber`'s visual debugger could yield cleaner row extractions.
3. **Confidence Calibration**: The prompt has a strict fallback (`"not found in document"`), but local LLMs can still hallucinate if the retrieved context is marginally relevant. We would implement a verification step or require the LLM to quote the exact substring it used.

## 6. How to Run It

### Prerequisites
- Python 3.9+
- *(Optional)* A local installation of [Ollama](https://ollama.com/) if running locally.

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

### Configuration (Optional)
If you want to use OpenAI or Anthropic instead of the default local Ollama model, rename `.env.example` to `.env` and configure your keys and provider:
```env
LLM_PROVIDER=openai           # Options: ollama, openai, anthropic
LLM_MODEL=gpt-4o-mini         # e.g., llama3, gpt-4o, claude-3-haiku-20240307
OPENAI_API_KEY=sk-xxxx...
```

### Execution
To rebuild the index from scratch (Ingest → Clean → Chunk → Embed):
```bash
python scripts/rebuild_index.py
```
*(This will process the raw PDF and generate the persistent ChromaDB)*

To run the RAG pipeline on the 6 required test queries and generate the outputs:
```bash
python scripts/run_test_queries.py
```
*(The generated answers and citations are automatically saved to [outputs/test_query_results.md](outputs/test_query_results.md). You can view this file in the repository to see the final results!)*

To run a single custom query or enter Interactive Mode:
```bash
python scripts/cli.py "पोखरण-II में कलाम की क्या भूमिका थी?"
# Or for interactive mode:
python scripts/cli.py
```

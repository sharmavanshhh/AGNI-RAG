# AGNI-RAG

AGNI-RAG is a Retrieval-Augmented Generation (RAG) pipeline built to perform QA over the Hindi autobiography study guide "Agni Ki Udaan" (Wings of Fire) by A.P.J. Abdul Kalam.

## Project Structure

```
AGNI-RAG/
├── data/
│   ├── raw/                          # Source PDF
│   └── processed/                    # Generated JSONL files (gitignored)
├── src/
│   ├── ingest.py                     # PDF → pages + table extraction
│   ├── clean.py                      # Unicode NFC normalization & denoising
│   ├── chunk.py                      # Section-aware & table-aware chunking
│   ├── embed.py                      # BGE-M3 embeddings → ChromaDB
│   ├── retrieve.py                   # Hybrid retrieval (Dense + BM25 via RRF)
│   ├── generate.py                   # Multi-provider LLM generation
│   └── pipeline.py                   # End-to-end RAG orchestrator
├── scripts/
│   ├── rebuild_index.py              # One-command: Ingest → Clean → Chunk → Embed
│   ├── run_test_queries.py           # Run the 6 required test queries
│   ├── evaluate_retrieval.py         # Automated Top-K retrieval evaluation
│   ├── cli.py                        # Interactive conversational CLI
│   └── query.py                      # Single-query helper
├── outputs/                          # Pre-generated results (tracked in Git)
│   ├── test_query_results.md         # Answers & citations for 6 test queries
│   ├── evaluation_results.md         # Retrieval accuracy report (100% Top-3)
│   └── cli_demo.md                   # Recorded interactive CLI session
├── chroma_db/                        # Persistent vector store (gitignored)
├── .env.example                      # Environment template
├── requirements.txt                  # Python dependencies
└── README.md
```

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

## 5. Bonus Features Implemented

We explicitly targeted the bonus points from the evaluation rubric:
- **Hybrid Search (+)**: We implemented a robust hybrid retrieval system (`src/retrieve.py`) combining Dense Vector search (ChromaDB + `bge-m3`) with Sparse Keyword search (BM25), fused together using Reciprocal Rank Fusion (RRF).
- **Correct Table Extraction (+)**: Tabular data in PDFs is notoriously difficult for RAG. We used `PyMuPDF`'s table detection to extract tables explicitly during ingestion (`src/ingest.py`) and atomized them row-by-row so facts are never lost in chunk boundaries.
- **Retrieval Evaluation (+)**: We wrote a standalone evaluation script (`scripts/evaluate_retrieval.py`) that checks if the exact expected `chunk_id` for each test query is correctly pulled into the `Top-K` retrieved chunks. It currently achieves a **100% Top-3 Hit Rate** across all cross-lingual test cases. See [outputs/evaluation_results.md](outputs/evaluation_results.md).
- **Simple UI/CLI (+)**: We built a fully interactive, conversational command-line interface (`scripts/cli.py`) that includes strict out-of-domain fallbacks (e.g., asking about Virat Kohli returns: *"I can only answer questions related to Agni Ki Udaan."*). See [outputs/cli_demo.md](outputs/cli_demo.md).

## 6. Known Limitations

We believe in honest engineering — here is what the pipeline does **not** handle well:
1. **Single-Document Scope**: The pipeline is designed for a single PDF. Scaling to a multi-document corpus would require document-level metadata filtering and a more sophisticated chunking registry.
2. **Local LLM Hallucination**: While OpenAI/Anthropic models reliably respect our strict grounding prompt, smaller local models (e.g., `llama3:8b` via Ollama) occasionally paraphrase beyond the retrieved context. A cross-encoder verification step would mitigate this.
3. **Complex Table Layouts**: `PyMuPDF`'s table extraction works well for simple grids but can misalign columns in multi-line headers or merged cells. A vision-language model approach would yield cleaner extractions.
4. **No Caching**: Every query re-embeds the input. For production use, an embedding cache (keyed by query hash) would reduce latency.

## 7. Future Improvements

With more time, the pipeline could be hardened further:
1. **Cross-Encoder Re-Ranking**: Adding a multilingual Cross-Encoder (like `bge-reranker-v2-m3`) as a final re-ranking stage after RRF would significantly improve precision of the top-3 chunks.
2. **Confidence Calibration**: Require the LLM to quote the exact substring from the context it used to formulate its answer, enabling automated grounding verification.
3. **Streaming Responses**: For the CLI, stream tokens as they arrive from the LLM to improve perceived latency.

## 8. How to Run It

### Prerequisites
- Python 3.9+
- *(Optional)* A local installation of [Ollama](https://ollama.com/) if using local inference.

### Setup Instructions
1. Clone the repository and navigate into it:
   ```bash
   git clone https://github.com/sharmavanshhh/AGNI-RAG.git
   cd AGNI-RAG
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
If you want to use OpenAI or Anthropic instead of the default local Ollama model, copy `.env.example` to `.env` and configure your keys and provider:
```env
LLM_PROVIDER=openai           # Options: ollama, openai, anthropic
LLM_MODEL=gpt-4o-mini         # e.g., llama3, gpt-4o, claude-3-haiku-20240307
OPENAI_API_KEY=sk-xxxx...
```

### Execution

**Step 1: Build the index** (Ingest → Clean → Chunk → Embed):
```bash
python scripts/rebuild_index.py
```

**Step 2: Run the 6 required test queries:**
```bash
python scripts/run_test_queries.py
```
→ Results saved to [outputs/test_query_results.md](outputs/test_query_results.md)

**Step 3: Run the retrieval evaluation:**
```bash
python scripts/evaluate_retrieval.py
```
→ Results saved to [outputs/evaluation_results.md](outputs/evaluation_results.md)

**Step 4: Try the interactive CLI:**
```bash
python scripts/cli.py "पोखरण-II में कलाम की क्या भूमिका थी?"
# Or for interactive mode:
python scripts/cli.py
```
→ See a recorded session in [outputs/cli_demo.md](outputs/cli_demo.md)

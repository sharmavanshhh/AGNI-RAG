# AGNI-RAG — Repo Setup & Commit Workflow

A clean commit history is free evidence of "how you think" — one of the things
MegaMindz says they're evaluating. Treat each phase in `01-PHASE-PLAN.md` as one
(or a small handful of) commits, not one giant commit at the end.

## 1. Repo structure

```
agni-rag/
├── README.md
├── requirements.txt
├── .gitignore
├── .env.example
├── data/
│   ├── raw/
│   │   ├── Agni_Ki_Udaan_Adhyayan_Sahayika_Hindi.pdf
│   │   └── MegaMindz_RAG_Assignment_Instructions.pdf
│   └── processed/
│       ├── pages.jsonl
│       ├── pages_clean.jsonl
│       └── chunks.jsonl
├── src/
│   ├── __init__.py
│   ├── ingest.py
│   ├── clean.py
│   ├── chunk.py
│   ├── embed.py
│   ├── retrieve.py
│   ├── generate.py
│   └── pipeline.py
├── scripts/
│   ├── rebuild_index.py
│   ├── run_test_queries.py
│   ├── eval_retrieval.py       # bonus
│   └── cli.py                  # bonus
├── outputs/
│   └── test_query_results.md
├── chroma_db/                   # gitignored — local persistent vector store
└── tests/
    └── test_clean.py            # sentence splitter unit tests, etc.
```

## 2. `.gitignore` (minimum)

```
venv/
__pycache__/
*.pyc
.env
chroma_db/
.ipynb_checkpoints/
```

## 3. Branching

Solo project on a short deadline — **trunk-based is fine**, no need for feature
branches per phase. Work directly on `main`, but commit at every phase boundary
so `main` always reflects real, working progress. If you want a safety net, cut a
branch only if you're trying something risky (e.g. swapping embedding models) that
might not pan out.

## 4. Commit message convention

Use a short, consistent prefix per phase so the history reads like a table of
contents:

```
setup: initial repo skeleton, deps, gitignore
ingest: extract per-page text, section headings, and 3 tables
clean: NFC normalization + Hindi-aware sentence splitter
chunk: section- and table-aware chunking with metadata
embed: bge-m3 embeddings into persistent ChromaDB collection
retrieve: hybrid dense+BM25 retrieval with score fusion
generate: grounded answer generation with auto-citation
eval: retrieval hit-rate script using doc's own QA pairs (bonus)
cli: simple argparse CLI for ad-hoc queries (bonus)
docs: final README with chunking rationale, run instructions, limitations
```

One commit per completed phase is the target; it's fine to split a phase into 2–3
smaller commits if natural (e.g. "ingest: extract per-page text" then "ingest: add
table extraction" as two commits instead of one).

## 5. Suggested commit checkpoints (map to Phase Plan)

| After phase | Commit message | What must be true |
|---|---|---|
| 0 | `setup: initial repo skeleton, deps, gitignore` | `pip install -r requirements.txt` works |
| 1 | `ingest: extract pages, sections, and tables` | `pages.jsonl` exists and looks right |
| 2 | `clean: NFC normalization + Hindi sentence splitter` | `pages_clean.jsonl` has no mojibake |
| 3 | `chunk: section/table-aware chunking with metadata` | `chunks.jsonl` has full metadata per chunk |
| 4 | `embed: multilingual embeddings into ChromaDB` | manual query sanity check passes |
| 5 | `retrieve: hybrid dense+BM25 retrieval` | all 6 queries hit correct chunk in top-3 |
| 6 | `generate: grounded generation + auto-citation` | all 6 queries produce correct cited answers |
| 7 | `eval+cli: retrieval eval and CLI (bonus)` | hit-rate script runs; CLI answers ad-hoc queries |
| 8 | `docs: final README and submission polish` | fresh clone + README steps reproduces results |

Optionally tag the final commit:

```
git tag -a v1.0-submission -m "MegaMindz RAG assignment submission"
git push origin v1.0-submission
```

## 6. Practical git commands you'll actually run

```bash
# Phase 0
git init agni-rag
cd agni-rag
mkdir -p data/raw data/processed src scripts outputs tests
# copy in the two PDFs to data/raw/
git add .
git commit -m "setup: initial repo skeleton, deps, gitignore"

# after each subsequent phase, from repo root:
git add <changed files>
git commit -m "<phase prefix>: <short description>"

# at the very end
git tag -a v1.0-submission -m "MegaMindz RAG assignment submission"
git remote add origin <your-github-url>
git push -u origin main --tags
```

## 7. What NOT to do

- Don't commit the `chroma_db/` persistence directory (it's derived data, large,
  and regenerable from `chunks.jsonl` — regenerating it is itself proof the
  pipeline is reproducible).
- Don't commit API keys — use `.env` (gitignored) + `.env.example` (committed,
  with placeholder values) so the README can say "copy `.env.example` to `.env`
  and fill in your key."
- Don't squash everything into one commit at the end — the whole point of this
  workflow is that the history itself demonstrates phased, deliberate engineering.

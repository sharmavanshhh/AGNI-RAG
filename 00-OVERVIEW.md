# AGNI-RAG — Project Overview

## What this is

A Retrieval-Augmented Generation (RAG) pipeline built for the MegaMindz AI Solutions
internship screening assignment (Level 1). The system answers Hindi and English
questions about a single supplied Hindi-language document —
`Agni_Ki_Udaan_Adhyayan_Sahayika_Hindi.pdf` (a study guide on A.P.J. Abdul Kalam's
life, based on his autobiography *Wings of Fire*) — with every answer grounded in
retrieved chunks and traceable back to a page number, section heading, and chunk ID.

This is not a demo chatbot. It is a scored deliverable. Every design decision should
be made with the rubric in mind (see `03-OUTCOMES.md` for the full scoring map).

## The problem, restated plainly

1. We have one PDF, written in Hindi (Devanagari script), containing narrative prose
   plus three structured tables (missile program names, awards, timeline) and a
   glossary.
2. We must split it into retrievable chunks, embed those chunks with a
   multilingual model, and store them with metadata (page, section, chunk ID) in a
   vector DB.
3. Given a query in **either** Hindi or English, we must retrieve the right chunks
   — including when the query language doesn't match the document's language
   (cross-lingual retrieval, e.g. an English question must still find the Hindi
   paragraph that answers it).
4. We must generate an answer using only the retrieved context (not the LLM's own
   background knowledge of Kalam), and print that answer next to its citation.
5. We must do this for 6 required test queries (3 Hindi, 3 English), log the
   outputs, and explain our reasoning in a README.

## What "good" looks like here (in one paragraph)

A grader should be able to clone the repo, run one setup command and one run
command, and see all 6 answers print out correctly with correct page/section/chunk
citations — including the 3 English queries correctly pulling from Hindi source
text. The README should read like an engineer explaining trade-offs, not a tutorial
being copy-pasted. Nothing about the submission should look like the untouched
output of `pip install langchain && follow quickstart`.

## Architecture (text diagram)

```
Agni_Ki_Udaan_...pdf
        │
        ▼
 [1] INGEST  ──► extract text per page + detect the 20 numbered sections
        │         + pull the 3 tables (missile names, awards, timeline) as
        │         structured rows, not flattened prose
        ▼
 [2] CLEAN & NORMALIZE ──► Unicode NFC, strip PDF artifacts, fix broken
        │                   conjuncts, keep UTF-8 clean throughout
        ▼
 [3] CHUNK  ──► section-aware chunking, sentence-boundary aware (respects the
        │        Hindi danda "।", not just "."), overlap between chunks,
        │        each table row becomes its own atomic chunk
        ▼
 [4] EMBED & STORE ──► multilingual embedding model (bge-m3 or
        │               multilingual-e5-large) → ChromaDB, with metadata:
        │               {page, section, chunk_id, chunk_type, source_text}
        ▼
 [5] RETRIEVE ──► hybrid search: dense (embedding) + sparse (BM25) fused,
        │          top-k results, cross-lingual by construction (multilingual
        │          embedding space puts EN and HI queries near the same
        │          Hindi chunks)
        ▼
 [6] GENERATE ──► LLM prompted to answer ONLY from retrieved chunks, in the
        │          query's language, with an explicit "not found" fallback
        ▼
 [7] CITE & LOG ──► every answer auto-attaches page + section + chunk_id +
        │            score from the retrieved chunk's metadata
        ▼
 [8] EVALUATE (bonus) ──► run the doc's own §19 QA pairs through retrieval
                           only, measure hit-rate@k
```

## Tech stack (proposed, confirm before Phase 0)

| Layer | Choice | Why |
|---|---|---|
| Language | Python 3.11+ | required/preferred by assignment |
| PDF extraction | `pdfplumber` (+ `PyMuPDF`/`fitz` as fallback for layout-sensitive table pulls) | good text + table extraction, page-level access |
| Text cleaning | `unicodedata` (NFC), custom Hindi sentence splitter on `।` | correctness on Devanagari, explicitly graded |
| Chunking | custom section/table-aware chunker (no LangChain default splitter) | avoids "tutorial defaults", better metadata control |
| Embeddings | `BAAI/bge-m3` (or `intfloat/multilingual-e5-large` as fallback) via `sentence-transformers` | strong multilingual + Hindi retrieval, open-source, runs locally |
| Vector DB | ChromaDB (local, persistent) | required option, zero external infra |
| Sparse search | `rank_bm25` | cheap hybrid search bonus, fixes proper-noun/acronym misses |
| LLM (generation) | Claude API (or a local model like Qwen2.5 as a no-API-key fallback) | assignment explicitly allows either; graded on groundedness, not brand |
| CLI | `argparse` or `click` (bonus) | simple, no web frontend needed |
| Eval | small custom script using the doc's own §19 questions | bonus, ~30 min, high signal |

## Non-goals

- No web frontend / no React / no hosted UI. A CLI is optional bonus only.
- No fine-tuning of embedding or LLM models.
- No use of a proprietary/closed vector DB.
- No paraphrasing the source book's actual copyrighted narrative beyond what's
  already in the supplied study-guide PDF (it's already a derived summary, not the
  original book — we just chunk and cite it, we don't need to worry about
  reproducing the original *Wings of Fire* text).

## How this overview relates to the other files

- `01-PHASE-PLAN.md` — the detailed, phase-by-phase build plan (what to build, in
  what order, with acceptance criteria per phase).
- `02-REPO-WORKFLOW.md` — how to set up the Git repo and structure commits so the
  history itself shows disciplined, incremental engineering.
- `03-OUTCOMES.md` — the final deliverables checklist, mapped directly to
  MegaMindz's scoring rubric, plus the README outline.
- `CODEX_PROMPT.md` — the exact prompt to hand to your local Codex CLI to kick off
  the build.

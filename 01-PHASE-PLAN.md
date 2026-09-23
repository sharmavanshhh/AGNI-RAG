# AGNI-RAG — Phase-by-Phase Build Plan

Each phase below is designed to be completable in one sitting, end with a working
(if partial) state, and end with one Git commit. Do not start a phase until the
previous one's acceptance criteria are met — this keeps the repo history honest
and gives you a real fallback point if something breaks later.

Estimated total: 7–10 hours, matching the assignment's expected effort.

---

## Phase 0 — Repo & environment setup (~20 min)

**Objective:** a clean, reproducible skeleton exists before any RAG logic is written.

**Tasks:**
- Create the repo `agni-rag` (see `02-REPO-WORKFLOW.md` for exact structure).
- Add the two supplied PDFs into `data/raw/`.
- Set up a virtual environment, pin Python version.
- Create `requirements.txt` with initial deps (`pdfplumber`, `pymupdf`,
  `sentence-transformers`, `chromadb`, `rank-bm25`, `anthropic` or your chosen LLM
  client).
- Add `.gitignore` (venv, `__pycache__`, local Chroma persistence dir, `.env`).
- Write a stub `README.md` with just the title and a "work in progress" note.

**Acceptance criteria:** `pip install -r requirements.txt` succeeds in a fresh
venv; repo has the two PDFs committed under `data/raw/`; first commit made.

---

## Phase 1 — Ingestion: extract text + tables + page structure (~1.5 hr)

**Objective:** turn the PDF into a structured intermediate representation — not
just a text blob — that preserves page numbers, the 20 section headings, and the
3 tables as actual rows.

**Tasks:**
- Write `src/ingest.py`.
- Extract raw text per page (page number is critical metadata — capture it here,
  not later).
- Detect the 20 numbered section headings (they follow a consistent pattern in the
  doc, e.g. "१ · ..." / "1 ·") and use them to tag every page's text with a
  `section` label.
- Separately detect and extract the three tables (missile program names/meanings,
  awards & years, timeline) as structured `{row}` dicts, not flattened into
  prose — table extraction quality is explicitly a bonus criterion.
- Output an intermediate JSON/JSONL file, e.g. `data/processed/pages.jsonl`, where
  each record is `{page, section, text, tables: [...]}`.

**Acceptance criteria:** running `python src/ingest.py` produces
`data/processed/pages.jsonl` with all ~20 pages present, section labels populated
for every record, and the 3 tables extracted as separate structured entries you can
inspect and confirm are correct (spot-check the awards table years against the PDF
by eye).

---

## Phase 2 — Cleaning & normalization (~45 min)

**Objective:** make the Hindi text safe and consistent for both chunking and
embedding.

**Tasks:**
- Write `src/clean.py`.
- Apply Unicode NFC normalization to every text field (visually-identical
  Devanagari sequences must match).
- Strip PDF extraction artifacts (stray line breaks mid-word, repeated headers/
  footers like "मेगामाइंड्स एआई सॉल्यूशन्स", page-number strings bleeding into
  body text).
- Write and unit-test a Hindi-aware sentence splitter that treats `।` (danda) and
  `.` both as sentence boundaries, and does not break on numbers-with-periods
  (e.g. "1.5") or abbreviations.
- Re-save the cleaned version, e.g. `data/processed/pages_clean.jsonl`.

**Acceptance criteria:** a handful of manual spot checks show no mojibake, no
merged/garbled words at page boundaries, and the sentence splitter correctly
segments at least 3 sample paragraphs from the doc into sentences you'd agree with
by eye.

---

## Phase 3 — Chunking (~1 hr)

**Objective:** produce the final list of chunks with rich metadata, ready for
embedding. This is one of the two phases graders will scrutinize most (design
choices + Hindi handling).

**Tasks:**
- Write `src/chunk.py`.
- For narrative text: chunk **within** section boundaries (never span two
  sections in one chunk), using sentence-aware packing to a target size (start
  with ~250–350 tokens, ~15–20% overlap) — pick numbers you can justify, and note
  the justification in a comment/docstring for the README later.
- For tables: each row becomes its own atomic chunk (e.g. one chunk per award, one
  chunk per timeline entry, one chunk per missile), tagged `chunk_type: "table_row"`
  vs `chunk_type: "narrative"`.
- Assign every chunk a stable `chunk_id` (sequential int or hash), plus `page`,
  `section`, `chunk_type`.
- Output `data/processed/chunks.jsonl`.

**Acceptance criteria:** every chunk has non-empty `page`, `section`, `chunk_id`;
spot-check that the Bharat Ratna row and the SLV-III timeline row each ended up as
their own clean, complete chunk (not split mid-row) — these feed directly into 2
of the 6 required test queries.

---

## Phase 4 — Embedding & vector store (~1 hr)

**Objective:** get chunks into ChromaDB with a multilingual embedding model.

**Tasks:**
- Write `src/embed.py`.
- Load `BAAI/bge-m3` (or `multilingual-e5-large`) via `sentence-transformers`.
- Embed every chunk's text; store in a persistent local ChromaDB collection,
  attaching all metadata fields from Phase 3 (page, section, chunk_id, chunk_type)
  plus the raw chunk text.
- Add a small `scripts/rebuild_index.py` convenience entrypoint so re-indexing
  from scratch is one command.

**Acceptance criteria:** ChromaDB collection is persisted to disk; a quick sanity
query (e.g. `"भारत रत्न"`) returns the expected chunk in the top few results when
run manually.

---

## Phase 5 — Retrieval (hybrid) (~1 hr)

**Objective:** reliable retrieval for both Hindi and English queries, including
cross-lingual cases and proper-noun/acronym-heavy queries (SLV-III, IGMDP, MIT)
where pure dense retrieval is known to be weak.

**Tasks:**
- Write `src/retrieve.py`.
- Implement dense retrieval via ChromaDB (top-k, k≈5–8).
- Implement sparse retrieval via `rank_bm25` over the same chunk texts.
- Fuse the two rankings (simple reciprocal-rank fusion or weighted score
  combination — keep it simple and explainable).
- Return top-k fused results with their full metadata and score.

**Acceptance criteria:** manually run all 6 required queries (see
`03-OUTCOMES.md`) through retrieval only (no generation yet) and confirm the
correct chunk appears in the top-3 for each. If any query fails, this is the phase
to fix chunking/embedding/fusion weights before moving on — don't paper over a
retrieval miss with a clever prompt in Phase 6.

---

## Phase 6 — Generation & citation (~1 hr)

**Objective:** produce grounded, cited answers for each query.

**Tasks:**
- Write `src/generate.py`.
- Build a strict prompt template: the LLM receives only the retrieved chunk texts
  as context, is told to answer only from that context, to answer in the same
  language as the query (or note if it can't), and to say "not found in document"
  if the context doesn't support an answer.
- After generation, programmatically attach the citation (page, section,
  chunk_id, score) from the top retrieved chunk(s) that were actually used —
  metadata comes from the DB, never hand-typed.
- Write `src/pipeline.py` (or a `main.py`) that chains ingest→...→generate into a
  single callable `answer(query: str) -> {answer, citations}`.

**Acceptance criteria:** running the pipeline on all 6 required queries produces
answers matching the document's actual facts, each with a correctly formatted
citation line, in the exact `Query / Answer / Source` format from the assignment.

---

## Phase 7 — Logging, CLI (optional bonus), and eval (bonus) (~1–1.5 hr)

**Objective:** produce the required test-query log, and pick up bonus points
cheaply.

**Tasks:**
- Write `scripts/run_test_queries.py` that runs all 6 required queries (plus any
  extras you want to add) and writes `outputs/test_query_results.md` in the exact
  format the assignment shows.
- (Bonus, ~20 min) Add a tiny CLI (`scripts/cli.py` via `argparse`) — `python
  scripts/cli.py "your question"` → prints answer + citation.
- (Bonus, ~30 min) Write `scripts/eval_retrieval.py` using the doc's own §19
  bodh-prashn (comprehension questions) as a mini gold set: for each, check if the
  correct chunk is in top-k, report hit-rate@1/3/5.

**Acceptance criteria:** `outputs/test_query_results.md` exists and matches the
required format for all 6 queries; if built, eval script prints a hit-rate summary
you can quote in the README.

---

## Phase 8 — README & final polish (~45 min)

**Objective:** the README is itself a graded deliverable (5%) and is what a human
reads first — make it count.

**Tasks:**
- Write `README.md` covering exactly the 5 required sections (see
  `03-OUTCOMES.md` for the outline).
- Do one full clean-environment dry run of the README's own run instructions
  before submitting (catch any missing step).
- Final commit + tag `v1.0-submission`.

**Acceptance criteria:** a person with nothing but the repo and the README can
reproduce all 6 answers.

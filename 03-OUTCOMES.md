# AGNI-RAG — Outcomes, Deliverables & Scoring Map

## The 6 required test queries (must all pass)

| # | Query | Lang | Answerable from |
|---|---|---|---|
| 1 | SLV-III ने किस उपग्रह को कक्षा में स्थापित किया और किस वर्ष? | HI | §6 / timeline table |
| 2 | कलाम को भारत रत्न किस वर्ष प्राप्त हुआ? | HI | §14 awards table |
| 3 | पोखरण-II में कलाम की क्या भूमिका थी? | HI | §8 |
| 4 | Which institution did Kalam attend to study aeronautical engineering? | EN | §4 (MIT Chennai) |
| 5 | Who co-wrote the autobiography, and in what year was it published? | EN | §1 / §15 (Arun Tiwari, 1999) |
| 6 | How and where did Kalam die in 2015? | EN | §13 (Shillong, 27 July 2015) |

Required output format per query:
```
Query: <query text>
Answer: <grounded answer>
Source: page: <n> · section: "<heading>" · chunk_id: <id> · score: <float>
```

## Final deliverables checklist (maps to §10 of the assignment)

- [ ] Code runs end-to-end from a clean environment via README instructions only
- [ ] `requirements.txt` complete and accurate
- [ ] All 6 required queries answered, output logged in `outputs/test_query_results.md`
- [ ] Every answer has page + section + chunk_id citation, auto-generated from DB metadata
- [ ] `README.md` covers: chunking strategy & why, DB choice & why, Hindi handling, improvements, run steps
- [ ] No hardcoded secrets/API keys committed
- [ ] Repo is public and the link works

## Scoring rubric → what we're doing about each line

| Criterion | Weight | Our approach |
|---|---|---|
| It runs | 20 | One documented setup command + one run command; dry-run README before submitting |
| Retrieval quality (incl. cross-lingual) | 20 | Hybrid dense+BM25 retrieval; section/table-aware chunking so facts aren't split across chunks; multilingual embedding model handles EN→HI |
| Hindi handling | 15 | NFC normalization, Hindi-aware `।` sentence splitting, verified UTF-8 throughout, table text extracted readably |
| Answer quality | 10 | Strict "answer only from context" prompt with explicit not-found fallback |
| Citations & traceability | 10 | Metadata (page/section/chunk_id) stored at ingestion time, surfaced automatically at answer time — never hand-written |
| Design choices | 10 | Documented, justified chunk size/overlap; explained why ChromaDB; explained hybrid search choice — all in README |
| Code quality | 10 | Small single-purpose modules (`ingest.py`, `clean.py`, `chunk.py`, ...), no god-file, no over-engineering |
| README & communication | 5 | Follows the 5-part required outline exactly; honest limitations section |
| **Bonus (up to +10)** | — | Retrieval eval using doc's own §19 QA pairs; optional CLI; hybrid search (already counted above but also bonus-eligible); correct table extraction |

## README outline (write this last, in Phase 8)

1. **Chunking strategy** — chunk size/overlap chosen, why section-aware +
   table-row-atomic chunking was used instead of naive fixed-size splitting.
2. **Why ChromaDB (or Qdrant)** — reasoning for the DB choice given local-only,
   no-infra constraints.
3. **Hindi text handling** — NFC normalization, `।`-aware sentence splitting,
   choice of multilingual embedding model and why it was chosen over an
   English-only model.
4. **What you'd improve with more time** — be honest: e.g. re-ranking with a
   cross-encoder, better OCR-quality table parsing, a larger/held-out eval set,
   confidence calibration on the "not found" fallback.
5. **How to run it** — exact commands, from `git clone` to seeing the 6 answers
   print out. Test this yourself in a clean environment before submitting.

## Definition of done

You're done when: a stranger clones the repo, follows only the README, and within
a few minutes sees all 6 required queries answered correctly with properly
formatted citations — with no undocumented steps, no missing files, and no
secrets in the repo.

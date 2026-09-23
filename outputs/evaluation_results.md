# AGNI-RAG Retrieval Evaluation Results

Below is the automated retrieval evaluation verifying that our RRF (Reciprocal Rank Fusion) hybrid retriever successfully pulls the exact correct Ground-Truth `chunk_id` for both Hindi and English queries into the Top-3 results.

```text
Initializing Retriever for Evaluation...
Loading embedding model for retrieval...
Loading weights: 100%|██████████| 391/391 [00:00<00:00, 21918.03it/s]
Loading ChromaDB...
Loading chunks for BM25...

--- Running Retrieval Evaluation (Top-3) ---

[1/6] Query: SLV-III ने किस उपग्रह को कक्षा में स्थापित किया और किस वर्ष?
Expected Chunk: chunk_165f37ae
Retrieved Chunks: ['chunk_165f37ae', 'chunk_89d1b0c5', 'chunk_a438ec36']
✅ HIT
--------------------------------------------------
[2/6] Query: कलाम को भारत रत्न किस वर्ष प्राप्त हुआ?
Expected Chunk: chunk_d0ed0f1d
Retrieved Chunks: ['chunk_d0ed0f1d', 'chunk_671df86e', 'chunk_4a237f08']
✅ HIT
--------------------------------------------------
[3/6] Query: पोखरण-II में कलाम की क्या भूमिका थी?
Expected Chunk: chunk_0397654b
Retrieved Chunks: ['chunk_0397654b', 'chunk_34106b9c', 'chunk_ded2b72c']
✅ HIT
--------------------------------------------------
[4/6] Query: Which institution did Kalam attend to study aeronautical engineering?
Expected Chunk: chunk_ec530dd4
Retrieved Chunks: ['chunk_ec530dd4', 'chunk_0b3d12fc', 'chunk_6dfdf2d8']
✅ HIT
--------------------------------------------------
[5/6] Query: Who co-wrote the autobiography, and in what year was it published?
Expected Chunk: chunk_c292524e
Retrieved Chunks: ['chunk_c292524e', 'chunk_87cf381b', 'chunk_e08d0620']
✅ HIT
--------------------------------------------------
[6/6] Query: How and where did Kalam die in 2015?
Expected Chunk: chunk_5b656389
Retrieved Chunks: ['chunk_5b656389', 'chunk_d0ed0f1d', 'chunk_19e8cd26']
✅ HIT
--------------------------------------------------

=== EVALUATION RESULTS ===
Total Queries: 6
Hits in Top-3: 6
Accuracy: 100.00%
==========================
```

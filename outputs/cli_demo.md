# AGNI-RAG Interactive CLI Demo

We built an interactive CLI (`scripts/cli.py`) to allow real-time chat with the document. 
Below is a raw log demonstrating its bilingual capabilities and strict domain enforcement:

```text
(venv) PS E:\AGNI-RAG> python scripts/cli.py

Welcome to the AGNI-RAG Interactive CLI!
Type your query below (or type 'exit' or 'quit' to close).
Initializing RAG Pipeline...

--------------------------------------------------
Ask AGNI-RAG > कलाम को भारत रत्न किस वर्ष प्राप्त हुआ?

Searching and generating answer...

Answer: कलाम को भारत रत्न 1997 में प्राप्त हुआ।

Sources used:
  [1] Page 21, Section: '19 · विचार एवं बोध-प्रश्न' (Score: 0.0325)

--------------------------------------------------
Ask AGNI-RAG > Which institution did Kalam attend to study aeronautical engineering?

Searching and generating answer...

Answer: Kalam attended the Madras Institute of Technology (MIT) in Chennai to study aeronautical engineering.

Sources used:
  [1] Page 3, Section: '1 · ए.पी.जे. अब्दुुल कलाम कौन थे?' (Score: 0.0306)

--------------------------------------------------
Ask AGNI-RAG > Who is Virat Kohli ?

Searching and generating answer...

Answer: I can only answer questions related to Agni Ki Udaan.

Sources used: None (Not found in document)
```

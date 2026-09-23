# AGNI-RAG Test Query Results

Query: SLV-III ने किस उपग्रह को कक्षा में स्थापित किया और किस वर्ष?
Answer: SLV-III ने जुलाई 1980 में रोहिणी उपग्रह को कक्षा में स्थापित किया।
Source: page: 8 · section: "6 · इसरो के वर्ष और SLV-III" · chunk_id: chunk_165f37ae · score: 0.0323

---

Query: कलाम को भारत रत्न किस वर्ष प्राप्त हुआ?
Answer: कलाम को भारत रत्न 1997 में प्राप्त हुआ।
Source: page: 21 · section: "19 · विचार एवं बोध-प्रश्न" · chunk_id: chunk_d0ed0f1d · score: 0.0325

---

Query: पोखरण-II में कलाम की क्या भूमिका थी?
Answer: पोखरण-II में कलाम ने परमाणु ऊर्जा विभाग के वैज्ञानिकों के साथ मिलकर एक केंद्रीय संगठनात्मक भूमिका निभाई।
Source: page: 10 · section: "8 · पोखरण-II: 1998 के परमाणु परीक्षण" · chunk_id: chunk_0397654b · score: 0.0328

---

Query: Which institution did Kalam attend to study aeronautical engineering?
Answer: Kalam attended the Madras Institute of Technology (MIT) in Chennai to study aeronautical engineering.
Source: page: 3 · section: "1 · ए.पी.जे. अब्दुुल कलाम कौन थे?" · chunk_id: chunk_ec530dd4 · score: 0.0306

---

Query: Who co-wrote the autobiography, and in what year was it published?
Answer: The autobiography was co-written with scientist Arun Tiwari and was published in 1999.
Source: page: 1 · section: "0 · प्रस्तावना" · chunk_id: chunk_c292524e · score: 0.0323

---

Query: How and where did Kalam die in 2015?
Answer: Kalam died on 27 July 2015 in Shillong, Meghalaya, when he fell while giving a lecture at the Indian Institute of Management, Shillong, and passed away shortly after at the age of 83.
Source: page: 15 · section: "13 · अंतिम क्षण तक शिक्षक (2007–2015)" · chunk_id: chunk_5b656389 · score: 0.0323

---

## Extra Credit: Interactive CLI Demo

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

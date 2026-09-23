import requests
import json
import os

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")

PROMPT_TEMPLATE = """You are a strict, helpful AI assistant. You must answer the user's query ONLY using the information provided in the context below. 

Rules:
1. If the context does not contain the answer, you must output EXACTLY: "not found in document". Do not try to guess or use outside knowledge.
2. Answer in the same language as the query.
3. Be concise and accurate.

Context:
{context}

Query: {query}
Answer:"""

def generate_answer(query, retrieved_chunks):
    """
    Generate an answer using a local Ollama instance.
    """
    if not retrieved_chunks:
        return "not found in document", []
        
    context_parts = []
    for i, chunk in enumerate(retrieved_chunks):
        # We number the chunks so the LLM can see them as separate items
        context_parts.append(f"[Chunk {i+1}]\n{chunk['text']}")
        
    context_str = "\n\n".join(context_parts)
    prompt = PROMPT_TEMPLATE.format(context=context_str, query=query)
    
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.0
        }
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        answer = data.get("response", "").strip()
    except Exception as e:
        answer = f"Error calling Ollama API: {str(e)}"
        
    # Heuristic for citations: if the answer is not "not found in document", 
    # we just cite the top-1 chunk as requested by "programmatically attach the citation ... from the top retrieved chunk(s)"
    # A more advanced version would ask the LLM to output the chunk number it used.
    
    citations = []
    if "not found in document" not in answer.lower() and not answer.startswith("Error"):
        # Just use the top chunk as the primary source for simplicity in this baseline
        top_chunk = retrieved_chunks[0]
        citations.append({
            "page": top_chunk["page"],
            "section": top_chunk["section"],
            "chunk_id": top_chunk["chunk_id"],
            "score": top_chunk["score"]
        })
        
    return answer, citations

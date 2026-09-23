import requests
import json
import os
from dotenv import load_dotenv

# Load env variables if they exist
load_dotenv()

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama").lower()
LLM_MODEL = os.getenv("LLM_MODEL", "llama3")

# Optional keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")

PROMPT_TEMPLATE = """You are a strict, helpful AI assistant. You must answer the user's query ONLY using the information provided in the context below. 

Rules:
1. If the context does not contain the answer, you must output EXACTLY: "not found in document". Do not try to guess or use outside knowledge.
2. CRITICAL: You MUST answer in the EXACT SAME LANGUAGE as the user's query. If the query is in English, you must translate the information from the Hindi context and write your final answer in English. If the query is in Hindi, answer in Hindi.
3. Be concise and accurate.

Context:
{context}

Query: {query}
Answer:"""

def _generate_ollama(prompt):
    payload = {
        "model": LLM_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.0
        }
    }
    response = requests.post(OLLAMA_URL, json=payload, timeout=60)
    response.raise_for_status()
    data = response.json()
    return data.get("response", "").strip()

def _generate_openai(prompt):
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY environment variable is missing.")
        
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.0
    )
    return response.choices[0].message.content.strip()

def _generate_anthropic(prompt):
    if not ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY environment variable is missing.")
        
    from anthropic import Anthropic
    client = Anthropic(api_key=ANTHROPIC_API_KEY)
    
    response = client.messages.create(
        model=LLM_MODEL,
        max_tokens=1024,
        temperature=0.0,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return response.content[0].text.strip()

def generate_answer(query, retrieved_chunks):
    """
    Generate an answer using the configured LLM provider.
    """
    if not retrieved_chunks:
        return "not found in document", []
        
    context_parts = []
    for i, chunk in enumerate(retrieved_chunks):
        context_parts.append(f"[Chunk {i+1}]\n{chunk['text']}")
        
    context_str = "\n\n".join(context_parts)
    prompt = PROMPT_TEMPLATE.format(context=context_str, query=query)
    
    try:
        if LLM_PROVIDER == "openai":
            answer = _generate_openai(prompt)
        elif LLM_PROVIDER == "anthropic":
            answer = _generate_anthropic(prompt)
        else:
            answer = _generate_ollama(prompt)
    except Exception as e:
        answer = f"Error calling {LLM_PROVIDER} API: {str(e)}"
        
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

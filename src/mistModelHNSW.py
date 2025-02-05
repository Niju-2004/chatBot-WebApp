import os
import json
import logging
import sys
import hnswlib  # ✅ Use HNSW instead of FAISS
import requests
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv, dotenv_values 
from pathlib import Path

dotenv_path = Path('D:\Rag-Vector-DB\src\.env')
load_dotenv(dotenv_path=dotenv_path)

# Set up logging
logging.basicConfig(level=logging.INFO, filename="chatbot_errors.log", format="%(asctime)s - %(levelname)s - %(message)s")

# Mistral API key
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
MODEL = "open-mistral-7b"

# Mistral API URL
API_URL = "https://api.mistral.ai/v1/chat/completions"

# Load Sentence Transformer model
sentence_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def load_content():
    """Load content data from JSON."""
    try:
        with open(r"D:\Rag-Vector-DB\DB_Storage\DbHNSW\contentHNSW.json", 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error loading content JSON: {e}")
        return {}

def load_hnsw_index():
    """Load HNSW index file."""
    try:
        index = hnswlib.Index(space='cosine', dim=384)  # ✅ 384-dim embeddings
        index.load_index(r"D:\Rag-Vector-DB\DB_Storage\DbHNSW\vectors_hnswlib.bin")
        return index
    except Exception as e:
        logging.error(f"Error loading HNSW index: {e}")
        return None

def query_system(query, model, index, content, top_k=3):
    """Query the HNSW index and retrieve relevant content from content.json."""
    query_embedding = model.encode([query]).astype('float32')
    labels, distances = index.knn_query(query_embedding, k=top_k)

    logging.info(f"HNSW Search Results: Indices={labels}, Distances={distances}")

    relevant_contexts = []
    for label in labels[0]:
        content_key = str(label)
        if content_key in content:
            relevant_contexts.append(content[content_key])
        else:
            logging.warning(f"Content key {content_key} not found in content.json.")

    return relevant_contexts

def generate_response_with_mistral(query, relevant_contexts):
    """Generate a structured response using Mistral AI based on retrieved context."""
    try:
        if not relevant_contexts:
            return "I'm sorry, I couldn't find relevant information for your query."

        formatted_context = []
        for ctx in relevant_contexts:
            if isinstance(ctx, dict):
                disease = ctx.get('disease', 'Unknown')
                animal = ctx.get('animal', 'Unknown')
                symptoms = ctx.get('symptoms', 'No symptoms provided')
                ingredients = ctx.get('ingredients', 'No ingredients listed')
                treatment = ctx.get('treatment', 'No treatment available')

                formatted_context.append(
                    f"📌 **Disease:** {disease}\n"
                    f"🦠 **Affects:** {animal}\n"
                    f"⚠️ **Symptoms:** {symptoms}\n"
                    f"🧪 **Ingredients:** {ingredients}\n"
                    f"💊 **Treatment:** {treatment}\n"
                    "----------------------------"
                )
            else:
                formatted_context.append(f"📌 **Additional Context:** {ctx}")

        structured_content = "\n\n".join(formatted_context)

        prompt = (
            "You are an expert veterinary assistant helping farmers treat animal diseases using herbal and traditional remedies.\n\n"
            f"🔍 **User Query:** {query}\n\n"
            f"📜 **Retrieved Veterinary Knowledge:**\n{structured_content}\n\n"
            "✅ **Your Task:** Based on the retrieved information, provide a well-structured response that clearly explains:\n"
            "  - The disease name\n"
            "  - Affected animals\n"
            "  - Common symptoms\n"
            "  - Suggested herbal ingredients\n"
            "  - Treatment methods\n\n"
            "Use a structured format in your response."
        )

        HEADERS = {"Authorization": f"Bearer {MISTRAL_API_KEY}", "Content-Type": "application/json"}
        payload = {"model": MODEL, "messages": [{"role": "user", "content": prompt}], "temperature": 0.7}
        response = requests.post(API_URL, headers=HEADERS, json=payload)

        if response.status_code == 200:
            response_json = response.json()
            return response_json["choices"][0]["message"]["content"]
        else:
            return f"API Error {response.status_code}: {response.text}"

    except Exception as e:
        return f"Error generating response: {e}"

def main():
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        content = load_content()
        index = load_hnsw_index()
        relevant_contexts = query_system(query, sentence_model, index, content)
        print(generate_response_with_mistral(query, relevant_contexts))

if __name__ == "__main__":
    main()

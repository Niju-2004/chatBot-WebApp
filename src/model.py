import os
import json
import faiss
import numpy as np
import logging
import requests
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
from googletrans import Translator

# Configure logging
logging.basicConfig(level=logging.INFO)

# Get GEMINI API key from environment variable
GEMINI_API = os.getenv("GEMINI_API")
if not GEMINI_API:
    raise ValueError("GEMINI_API environment variable is not set. Please configure it in Render.")

genai.configure(api_key=GEMINI_API)

generation_config = {
    "temperature": 0.0,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048
}

model = genai.GenerativeModel("gemini-pro", generation_config=generation_config)

CONTENT_JSON_URL = "https://raw.githubusercontent.com/Niju-2004/faiss-index-storage/main/content.json"
FAISS_INDEX_URL = "https://raw.githubusercontent.com/Niju-2004/faiss-index-storage/main/vectors_faiss.index"

CONTENT_JSON_PATH = "content.json"
FAISS_INDEX_PATH = "vectors_faiss.index"

sentence_model = None
content = None
index = None
translator = Translator()

def download_file(url, local_path):
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(local_path, "wb") as f:
            f.write(response.content)
        logging.info(f"Downloaded {local_path}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error downloading {url}: {e}")
        raise

def initialize_system():
    global sentence_model, content, index
    try:
        download_file(CONTENT_JSON_URL, CONTENT_JSON_PATH)
        download_file(FAISS_INDEX_URL, FAISS_INDEX_PATH)
        
        sentence_model = SentenceTransformer("all-MiniLM-L6-v2")
        index = faiss.read_index(FAISS_INDEX_PATH)
        
        with open(CONTENT_JSON_PATH, "r", encoding="utf-8") as f:
            content = json.load(f)
        
        logging.info("System initialized successfully.")
    except Exception as e:
        logging.error(f"Error during system initialization: {e}")
        raise

def detect_language(text):
    try:
        return translator.detect(text).lang
    except Exception as e:
        logging.error(f"Language detection failed: {e}")
        return "en"

def translate_text(text, src_lang, dest_lang):
    try:
        return translator.translate(text, src=src_lang, dest=dest_lang).text
    except Exception as e:
        logging.error(f"Translation failed: {e}")
        return text

def query_system(user_query):
    try:
        query_lang = detect_language(user_query)
        if query_lang == "ta":
            user_query = translate_text(user_query, src_lang="ta", dest_lang="en")
        
        query_vector = np.array(sentence_model.encode([user_query], convert_to_tensor=False)).astype("float32")
        D, I = index.search(query_vector, k=3)
        relevant_info = get_relevant_info(I[0], content)
        
        response = generate_gemini_response(relevant_info)
        
        if query_lang == "ta":
            response = translate_text(response, src_lang="en", dest_lang="ta")
        
        return response, I, D, relevant_info
    except Exception as e:
        logging.error(f"Error processing query: {e}")
        return "An error occurred while processing your request.", [], [], []

def get_relevant_info(indices, content_data):
    results = []
    for idx in indices:
        str_idx = str(idx)
        if str_idx in content_data:
            entry = content_data[str_idx]
            results.append({
                'title': entry.get('disease', 'Unknown Disease'),
                'definition': "Not available",
                'symptoms': entry.get('symptoms', 'Not specified.').split(", "),
                'treatment': entry.get('treatment', 'Not specified.').split("\n"),
                'ingredients': entry.get('ingredients', 'Not specified.').split(", ")
            })
    return results

def generate_gemini_response(results):
    prompt = f"Provide a detailed explanation for the following veterinary conditions:\n{json.dumps(results, indent=2)}"
    try:
        response = model.generate_content(prompt)
        return response.text if response else "No response from Gemini."
    except Exception as e:
        logging.error(f"Error generating content with Gemini: {e}")
        return "Error generating response."

def format_bullet_points(items):
    return "\n".join([f"* {item.strip()}" for item in items if item.strip()]) if items else "Not specified."

initialize_system()

import os
import json
import faiss
import numpy as np
import logging
import asyncio
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
from googletrans import Translator
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)

# Load .env file
dotenv_path = r"D:\chatBot-WebApp\src\.env"  # Ensure raw string format for Windows paths
load_dotenv(dotenv_path=dotenv_path)

# Get GEMINI API key from environment
GEMINI_API = os.getenv("GEMINI_API")

# Ensure API key is set before configuring Gemini API
if not GEMINI_API:
    raise ValueError("Please set the GEMINI_API environment variable in your .env file.")

# Configure Gemini API
genai.configure(api_key=GEMINI_API)

# Generation settings
generation_config = {
    "temperature": 0.0,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048
}

# 2. Initialize the Model
model = genai.GenerativeModel("gemini-pro", generation_config=generation_config)

# File paths
FAISS_INDEX_PATH = r"D:\chatBot-WebApp\DB_Storage\vectors_faiss.index"
CONTENT_JSON_PATH = r"D:\chatBot-WebApp\DB_Storage\content.json"

# Load Sentence Transformer model
sentence_model = SentenceTransformer("all-MiniLM-L6-v2")

# Initialize Translator
translator = Translator()

async def detect_language(text):
    """Detect the language of the input text."""
    try:
        detection = await translator.detect(text)
        return detection.lang
    except Exception as e:
        logging.error(f"Language detection failed: {e}")
        return "en"  # Default to English on failure

async def translate_text(text, src_lang, dest_lang):
    """Translate text from source language to destination language."""
    try:
        translated = await translator.translate(text, src=src_lang, dest=dest_lang)  # Await the async translation
        return translated.text
    except Exception as e:
        logging.error(f"Translation failed: {e}")
        return text  # Return original text if translation fails

def initialize_system():
    """Initializes the system by loading necessary models and data."""
    sentence_model = SentenceTransformer("all-MiniLM-L6-v2")
    index = faiss.read_index(FAISS_INDEX_PATH)
    with open(CONTENT_JSON_PATH, "r", encoding="utf-8") as f:
        content = json.load(f)
    return sentence_model, content, index

async def query_system(user_query, sentence_model, index, content):
    """Process the user query, search FAISS, and generate response."""
    # Detect language of the query
    query_lang = await detect_language(user_query)
    
    # Translate query to English if it's in Tamil
    if query_lang == "ta":
        user_query = await translate_text(user_query, src_lang="ta", dest_lang="en")
    
    # Generate query embedding
    query_vector = np.array(sentence_model.encode([user_query], convert_to_tensor=False)).astype("float32")
    D, I = index.search(query_vector, k=3)  # Use `k` instead of `top_k`
    relevant_info = get_relevant_info(I[0], content)
    
    # Generate response using Gemini
    response = generate_gemini_response(relevant_info)
    
    # Translate response back to Tamil if the query was in Tamil
    if query_lang == "ta":
        response = await translate_text(response, src_lang="en", dest_lang="ta")
    
    return response, I, D, relevant_info

def get_relevant_info(indices, content_data):
    """Retrieve structured data from `content.json` based on FAISS indices."""
    results = []
    for idx in indices:
        str_idx = str(idx)
        if str_idx in content_data:
            results.append(content_data[str_idx])
    return results

def generate_gemini_response(results):
    """Generate response using Gemini AI."""
    prompt = f"Provide a detailed explanation for the following veterinary conditions:\n{json.dumps(results, indent=2)}"
    try:
        response = model.generate_content(prompt)  # Using the updated method
        return response.text if response else "No response from Gemini."
    except Exception as e:
        logging.error(f"Error generating content with Gemini: {str(e)}")
        return "Error generating response."

# This block will only run if model.py is executed directly (i.e., not imported by app.py)
if __name__ == "__main__":
    user_query = input("Enter your query: ")

    # Load FAISS index and content data
    sentence_model, content, index = initialize_system()

    # Process the query
    response, indices, distances, relevant_info = asyncio.run(query_system(user_query, sentence_model, index, content))

    # Print the FAISS index and distances, relevant content, and Gemini response
    print("\nFAISS Search Results:")
    print("Indices:", indices)
    print("Distances:", distances)

    print("\n🔍 **Search Results:**")
    for res in relevant_info:
        print(json.dumps(res, indent=2))

    print("\n🌿 **Veterinary Chatbot Response:**")
    print(response)

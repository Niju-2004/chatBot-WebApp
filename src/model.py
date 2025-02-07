import os
import json
import faiss
import numpy as np
import logging
import asyncio
import requests
from sentence_transformers import SentenceTransformer
import google.generativeai as genai

# Configure logging
logging.basicConfig(level=logging.INFO)

# Get GEMINI API key from Render's environment variable
GEMINI_API = os.getenv("GEMINI_API")

# Ensure API key is set
if not GEMINI_API:
    raise ValueError("GEMINI_API environment variable is not set. Please configure it in Render.")

# Configure Gemini API
genai.configure(api_key=GEMINI_API)

# Generation settings
generation_config = {
    "temperature": 0.0,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048
}

# Initialize Gemini model
model = genai.GenerativeModel("gemini-pro", generation_config=generation_config)

# GitHub Raw URLs for FAISS index and content
CONTENT_JSON_URL = "https://raw.githubusercontent.com/Niju-2004/faiss-index-storage/main/content.json"
FAISS_INDEX_URL = "https://raw.githubusercontent.com/Niju-2004/faiss-index-storage/main/vectors_faiss.index"

# Local Paths for downloaded files
CONTENT_JSON_PATH = "content.json"
FAISS_INDEX_PATH = "vectors_faiss.index"

def download_file(url, local_path):
    """Download a file from a URL and save it locally."""
    response = requests.get(url)
    if response.status_code == 200:
        with open(local_path, "wb") as f:
            f.write(response.content)
        logging.info(f"Downloaded {local_path}")
    else:
        raise Exception(f"Failed to download {url}")

def initialize_system():
    """Download required files and initialize the chatbot system."""
    try:
        download_file(CONTENT_JSON_URL, CONTENT_JSON_PATH)
        download_file(FAISS_INDEX_URL, FAISS_INDEX_PATH)

        # Load sentence transformer model
        sentence_model = SentenceTransformer("all-MiniLM-L6-v2")

        # Load FAISS index
        index = faiss.read_index(FAISS_INDEX_PATH)
        
        # Load content JSON
        with open(CONTENT_JSON_PATH, "r", encoding="utf-8") as f:
            content = json.load(f)
        
        return sentence_model, content, index
    except Exception as e:
        logging.error(f"Error during system initialization: {str(e)}")
        raise

async def query_system(user_query, sentence_model, index, content):
    """Process user query, search FAISS, and generate response."""
    try:
        query_vector = np.array(sentence_model.encode([user_query], convert_to_tensor=False)).astype("float32")
        D, I = index.search(query_vector, k=3)
        relevant_info = get_relevant_info(I[0], content)
        
        response = generate_gemini_response(relevant_info)
        
        return response, I, D, relevant_info
    except Exception as e:
        logging.error(f"Error during query processing: {str(e)}")
        raise

def get_relevant_info(indices, content_data):
    """Retrieve structured data from `content.json` based on FAISS indices."""
    try:
        results = []
        for idx in indices:
            str_idx = str(idx)
            if str_idx in content_data:
                results.append(content_data[str_idx])
        return results
    except Exception as e:
        logging.error(f"Error retrieving relevant info: {str(e)}")
        raise

def generate_gemini_response(results):
    """Generate response using Gemini AI."""
    try:
        prompt = f"Provide a detailed explanation for the following veterinary conditions:\n{json.dumps(results, indent=2)}"
        response = model.generate_content(prompt)
        return response.text if response else "No response from Gemini."
    except Exception as e:
        logging.error(f"Error generating content with Gemini: {str(e)}")
        return "Error generating response."

if __name__ == "__main__":
    try:
        user_query = input("Enter your query: ")

        # Download required files and initialize system
        sentence_model, content, index = initialize_system()

        # Process the query
        response, indices, distances, relevant_info = asyncio.run(query_system(user_query, sentence_model, index, content))

        # Print results
        print("\nFAISS Search Results:")
        print("Indices:", indices)
        print("Distances:", distances)

        print("\n🔍 **Search Results:**")
        for res in relevant_info:
            print(json.dumps(res, indent=2))

        print("\n🌿 **Veterinary Chatbot Response:**")
        print(response)

    except Exception as e:
        print(f"An error occurred: {str(e)}")

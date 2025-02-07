import os
import json
import faiss
import numpy as np
import logging
import aiohttp
import asyncio
from sentence_transformers import SentenceTransformer
import google.generativeai as genai

# Configure logging
logging.basicConfig(level=logging.INFO)

# Get GEMINI API key from Render's environment variable
GEMINI_API = os.getenv("GEMINI_API")

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

# Global variables for caching
sentence_model = None
content = None
index = None

async def download_file_async(url, local_path):
    """Download a file from a URL asynchronously and save it locally."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    with open(local_path, "wb") as f:
                        f.write(await response.read())
                    logging.info(f"Downloaded {local_path}")
                else:
                    raise Exception(f"Failed to download {url}")
    except Exception as e:
        logging.error(f"Error downloading file {url}: {str(e)}")
        raise

async def initialize_system():
    """Download required files and initialize the chatbot system."""
    global sentence_model, content, index
    try:
        await download_file_async(CONTENT_JSON_URL, CONTENT_JSON_PATH)
        await download_file_async(FAISS_INDEX_URL, FAISS_INDEX_PATH)

        sentence_model = SentenceTransformer("all-MiniLM-L6-v2")
        index = faiss.read_index(FAISS_INDEX_PATH)

        with open(CONTENT_JSON_PATH, "r", encoding="utf-8") as f:
            content = json.load(f)
        
        logging.info("System initialized successfully.")
    except Exception as e:
        logging.error(f"Error during system initialization: {str(e)}")
        raise

async def query_system(user_query):
    """Process user query, search FAISS, and generate a structured response."""
    try:
        query_vector = np.array(sentence_model.encode([user_query], convert_to_tensor=False)).astype("float32")
        D, I = index.search(query_vector, k=3)
        relevant_info = get_relevant_info(I[0], content)
        
        structured_response = format_response(relevant_info)
        return structured_response, I, D, relevant_info
    except Exception as e:
        logging.error(f"Error during query processing: {str(e)}")
        return f"Error: {str(e)}", [], [], []

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

def format_response(results):
    """Format the response into structured data with proper HTML formatting."""
    try:
        structured_output = []
        for result in results:
            formatted_text = f"""
            <b>{result.get('title', 'No Title')}</b><br><br>
            <b>Definition:</b> {result.get('definition', 'No Definition')}<br><br>
            <b>Symptoms:</b><br>
            {format_bullet_points(result.get('symptoms', []))}<br><br>
            <b>Treatment:</b><br>
            {format_bullet_points(result.get('treatment', []))}<br><br>
            <b>Ingredients:</b><br>
            {format_bullet_points(result.get('ingredients', []))}
            """
            structured_output.append(formatted_text)
        
        return "<br><br>".join(structured_output)
    except Exception as e:
        logging.error(f"Error formatting response: {str(e)}")
        return "Error formatting response."

def format_bullet_points(items):
    """Formats bullet points with '🟢' instead of '*'."""
    return "<br>".join([f"🟢 {item}" for item in items])
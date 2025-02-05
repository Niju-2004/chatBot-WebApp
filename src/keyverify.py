import os
from dotenv import load_dotenv

# Load .env file
dotenv_path = r"D:\Rag-Vector-DB\src\.env"
load_dotenv(dotenv_path=dotenv_path)

# Check if the API key is loaded correctly
GEMINI_API = os.getenv("GEMINI_API")
print("Loaded GEMINI_API_KEY:", GEMINI_API)  # Debugging step

if not GEMINI_API:
    raise ValueError("GEMINI_API_KEY is not loaded. Check .env file location or format.")

# Configure Gemini API
import google.generativeai as genai
genai.configure(api_key=GEMINI_API)

import os
import requests

# Set up API key
API_KEY = "5GnNzCryW9GDx7Zfbe04z5CovDlnl7Z3"
MODEL = "open-mistral-7b"  # Use the correct model name

# Mistral API URL
API_URL = "https://api.mistral.ai/v1/chat/completions"

# Define headers
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Define the request payload
payload = {
    "model": MODEL,
    "messages": [{"role": "user", "content": "What are the symptoms of Foot and Mouth Disease in cows?"}],
    "temperature": 0.7
}

try:
    # Send request to Mistral API
    response = requests.post(API_URL, headers=HEADERS, json=payload)

    # Check if response is successful
    if response.status_code == 200:
        response_json = response.json()
        if "choices" in response_json and response_json["choices"]:
            print("\n💬 Mistral API Response:")
            print(response_json["choices"][0]["message"]["content"])
        else:
            print("❌ No response received from Mistral API.")
    else:
        print(f"❌ API Error {response.status_code}: {response.text}")

except Exception as e:
    print(f"\n❌ Mistral API Error: {e}")

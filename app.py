from flask import Flask, render_template, request, jsonify
import model
import logging
import os
from datetime import datetime
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize Flask app
app = Flask(__name__)

# Configure rate limiting with in-memory storage (for development)
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    storage_uri="memory://",  # Use in-memory storage for rate limiting
    default_limits=["200 per day", "50 per hour"]
)

# Translation dictionary
translations = {
    'en': {
        'welcome_message': 'Welcome to the Veterinary Chatbot!',
        'chatbot_description': "I'm here to help answer your questions about veterinary care. Consult a veterinarian for an accurate diagnosis and proper treatment plan."
    },
    'ta': {
        'welcome_message': 'கால்நடை மருத்துவ அரட்டைப் பெட்டிக்கு வருக!',
        'chatbot_description': 'கால்நடை பராமரிப்பு பற்றிய உங்கள் கேள்விகளுக்கு பதிலளிக்க நான் இங்கே இருக்கிறேன். துல்லியமான நோயறிதல் மற்றும் சரியான சிகிச்சை திட்டத்திற்கு ஒரு கால்நடை மருத்தவரை அணுகவும்.'
    }
}

# Manually initialize the system when the app starts
model.initialize_system()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
@limiter.limit("5 per minute")
def ask():
    try:
        data = request.json
        user_query = data.get('query')
        
        if not user_query or len(user_query) > 500:
            return jsonify({'response': "Please enter a valid query (max 500 characters)."}), 400
        
        # Run the asynchronous query_system function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        response, _, _, _ = loop.run_until_complete(model.query_system(user_query))
        loop.close()
        
        return jsonify({'response': response})
    
    except Exception as e:
        error_message = f"Error processing query: {str(e)}"
        logging.error(error_message)
        return jsonify({'response': error_message}), 500

@app.route('/translations', methods=['GET'])
def get_translations():
    language = request.args.get('language')
    return jsonify(translations.get(language, {}))

if __name__ == '__main__':
    # Bind to the port specified by Render (default: 10000)
    port = int(os.getenv('PORT', 10000))
    # Increase timeout to 300 seconds (5 minutes)
    app.run(debug=False, host="0.0.0.0", port=port, threaded=True, timeout=300)
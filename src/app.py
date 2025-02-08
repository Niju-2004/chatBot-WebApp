from flask import Flask, render_template, request, jsonify
import model
import logging
import os
from datetime import datetime
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)

# Rate limiting
limiter = Limiter(app=app, key_func=get_remote_address)

logging.basicConfig(level=logging.INFO)

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

# Ensure the feedback file is in a writable directory
FEEDBACK_FILE_PATH = os.path.join(os.getenv('TEMP', '/tmp'), 'feedback.txt')

# Initialize the system before the first request
def initialize_system():
    """Initialize the system synchronously."""
    model.initialize_system()

# Manually initialize the system when the app starts
initialize_system()

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
            return jsonify({'response': "Invalid query!"}), 400
        
        response, indices, distances, relevant_info = model.query_system(user_query)
        return jsonify({'response': response})
    
    except Exception as e:
        logging.error(f"Error processing query: {e}")
        return jsonify({'response': f"An error occurred: {str(e)}"}), 500

@app.route('/feedback', methods=['POST'])
@limiter.limit("2 per minute")
def feedback():
    try:
        data = request.json
        feedback = data.get('feedback')
        if not feedback:
            return jsonify({'success': False, 'message': "No feedback provided!"}), 400
        
        current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(FEEDBACK_FILE_PATH, 'a') as f:
            f.write(f"{current_timestamp}: {feedback}\n")

        return jsonify({'success': True, 'message': "Feedback submitted successfully!"})
    except Exception as e:
        logging.error(f"Error processing feedback: {e}")
        return jsonify({'success': False, 'message': f"An error occurred: {str(e)}"}), 500

@app.route('/translations', methods=['GET'])
def get_translations():
    language = request.args.get('language')
    return jsonify(translations.get(language, {}))

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
document.addEventListener('DOMContentLoaded', () => {
    const messageContainer = document.getElementById('message-container');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const feedbackInput = document.getElementById('feedback-input');
    const feedbackButton = document.getElementById('feedback-button');
    const langToggleTa = document.getElementById('lang-toggle-ta');
    const langToggleEn = document.getElementById('lang-toggle-en');
    const chatHeaderTitle = document.getElementById('chat-header-title');
    const welcomeMessage = document.getElementById('welcome-message');
    const chatbotDescription = document.getElementById('chatbot-description');
    const loadingIndicator = document.getElementById('loading-indicator');

    let currentLanguage = 'en';

    // Translation data (same as in app.py)
    const translations = {
        "en": {
            "welcome_message": "Welcome to the Veterinary Chatbot!",
            "chatbot_description": "I'm here to help answer your questions about veterinary care. Consult a veterinarian for an accurate diagnosis and proper treatment plan."
        },
        "ta": {
            "welcome_message": "கால்நடை மருத்துவ அரட்டைப் பெட்டிக்கு வருக!",
            "chatbot_description": "கால்நடை பராமரிப்பு பற்றிய உங்கள் கேள்விகளுக்கு பதிலளிக்க நான் இங்கே இருக்கிறேன். துல்லியமான நோயறிதல் மற்றும் சரியான சிகிச்சை திட்டத்திற்கு ஒரு கால்நடை மருத்தவரை அணுகவும்."
        }
    };

    function displayMessage(message, isUser = false, isHTML = false) {
        const messageElement = document.createElement('div');
        messageElement.classList.add(isUser ? 'user-message' : 'bot-message');

        if (isHTML) {
            messageElement.innerHTML = message; // Use innerHTML for structured responses
        } else {
            messageElement.textContent = message;
        }

        messageContainer.appendChild(messageElement);
        messageContainer.scrollTop = messageContainer.scrollHeight;
    }

    function showLoadingIndicator() {
        loadingIndicator.style.display = 'block';
    }

    function hideLoadingIndicator() {
        loadingIndicator.style.display = 'none';
    }

    function handleTranslation(language) {
        chatHeaderTitle.textContent = translations[language].welcome_message;
        chatbotDescription.textContent = translations[language].chatbot_description;
    }

    // Ensure buttons switch languages correctly
    langToggleTa.addEventListener('click', () => {
        currentLanguage = 'ta';
        handleTranslation(currentLanguage);
    });

    langToggleEn.addEventListener('click', () => {
        currentLanguage = 'en';
        handleTranslation(currentLanguage);
    });

    sendButton.addEventListener('click', async () => {
        const query = userInput.value.trim();
        if (!query) return;

        displayMessage(query, true);
        userInput.value = '';
        showLoadingIndicator();

        try {
            const response = await fetch('/ask', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query })
            });

            const data = await response.json();
            if (data.response) {
                displayMessage(data.response, false, true); // Use formatted response with HTML
            } else {
                displayMessage("Sorry, I couldn't find an answer. Please try again.", false);
            }
        } catch (error) {
            console.error(error);
            displayMessage("Error: Unable to fetch response. Please try again later.", false);
        } finally {
            hideLoadingIndicator();
        }
    });

    feedbackButton.addEventListener('click', async () => {
        const feedbackText = feedbackInput.value.trim();
        if (!feedbackText) return;

        try {
            const response = await fetch('/feedback', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ feedback: feedbackText })
            });

            const data = await response.json();
            alert(data.message);
            if (data.success) feedbackInput.value = '';
        } catch (error) {
            console.error(error);
            alert("Error submitting feedback. Please try again later.");
        }
    });
});

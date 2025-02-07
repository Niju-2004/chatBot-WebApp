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

    let currentLanguage = localStorage.getItem('language') || 'en';

    // Translation data
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
        if (isHTML) messageElement.innerHTML = message;
        else messageElement.textContent = message;
        messageContainer.appendChild(messageElement);
        messageContainer.scrollTop = messageContainer.scrollHeight;
    }

    function showLoadingIndicator() {
        loadingIndicator.style.display = 'flex';
    }

    function hideLoadingIndicator() {
        loadingIndicator.style.display = 'none';
    }

    function handleTranslation(language) {
        currentLanguage = language;
        localStorage.setItem('language', language);
        chatHeaderTitle.textContent = translations[language].welcome_message;
        chatbotDescription.textContent = translations[language].chatbot_description;
    }

    // Language toggles
    langToggleTa.addEventListener('click', () => handleTranslation('ta'));
    langToggleEn.addEventListener('click', () => handleTranslation('en'));

    // Send button
    sendButton.addEventListener('click', async () => {
        const query = userInput.value.trim();
        if (!query || query.length > 500) {
            alert("Please enter a valid query (max 500 characters).");
            return;
        }

        displayMessage(query, true);
        userInput.value = '';
        showLoadingIndicator();

        try {
            const response = await fetch('/ask', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query })
            });

            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            const data = await response.json();
            displayMessage(data.response, false, true);
        } catch (error) {
            console.error(error);
            displayMessage("Error: Unable to fetch response. Please try again later.", false);
        } finally {
            hideLoadingIndicator();
        }
    });

    // Feedback button
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

    // Initialize language
    handleTranslation(currentLanguage);
});
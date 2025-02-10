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

    const translations = {
        "en": {
            "welcome_message": "Welcome to the Veterinary Chatbot!",
            "chatbot_description": "I'm here to help answer your questions about veterinary care. Consult a veterinarian for an accurate diagnosis and proper treatment plan."
        },
        "ta": {
            "welcome_message": "\u0b95\u0bbe\u0bb2\u0bcd\u0ba8\u0b9f\u0bc8 \u0bae\u0bb0\u0bc1\u0ba4\u0bcd\u0ba4\u0bc1\u0bb5 \u0b85\u0bb0\u0b9f\u0bcd\u0b9f\u0bc8\u0baa\u0bcd \u0baa\u0bc6\u0b9f\u0bcd\u0b9f\u0bbf\u0b95\u0bcd\u0b95\u0bc1 \u0bb5\u0bb0\u0bc1\u0b95!",
            "chatbot_description": "\u0b95\u0bbe\u0bb2\u0bcd\u0ba8\u0b9f\u0bc8 \u0baa\u0bb0\u0bbe\u0bae\u0bb0\u0bbf\u0baa\u0bcd\u0baa\u0bc1 \u0baa\u0b9f\u0bcd\u0b9f\u0bbf\u0baf \u0b89\u0b99\u0bcd\u0b95\u0bb3\u0bc1\u0b95\u0bcd\u0b95\u0bc1 \u0baa\u0bba\u0bc2\u0bb5\u0b95." 
        }
    };

    function displayMessage(message, isUser = false) {
        const messageElement = document.createElement('div');
        messageElement.classList.add(isUser ? 'user-message' : 'bot-message');
        messageElement.innerHTML = message.replace(/\n/g, '<br>');
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

    langToggleTa.addEventListener('click', () => handleTranslation('ta'));
    langToggleEn.addEventListener('click', () => handleTranslation('en'));

    sendButton.addEventListener('click', async () => {
        const query = userInput.value.trim();
        if (!query || query.length > 500) {
            displayMessage("⚠️ Please enter a valid query (max 500 characters).", false);
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

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            if (!data.response || data.response.trim() === "") {
                displayMessage("⚠️ No relevant information found. Try asking differently.", false);
            } else {
                displayMessage(data.response, false);
            }
        } catch (error) {
            console.error(error);
            displayMessage("❌ Error: Unable to fetch response. Please try again later.", false);
        } finally {
            hideLoadingIndicator();
        }
    });

    feedbackButton.addEventListener('click', async () => {
        const feedbackText = feedbackInput.value.trim();
        if (!feedbackText || feedbackText.length > 1000) {
            alert("⚠️ Please enter valid feedback (max 1000 characters).");
            return;
        }

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
            alert("❌ Error submitting feedback. Please try again later.");
        }
    });

    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendButton.click();
    });

    feedbackInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') feedbackButton.click();
    });

    handleTranslation(currentLanguage);
});
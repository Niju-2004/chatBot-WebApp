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

    const greetings = {
        "hello": "Hello! How can I assist you today?",
        "hi": "Hi! How can I assist you today?",
        "how are you": "I'm doing great, thank you for asking!"
    };

    function displayMessage(message, isUser = false) {
        const messageElement = document.createElement('div');
        messageElement.classList.add(isUser ? 'user-message' : 'bot-message');
        messageElement.textContent = message;
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
        const translation = translations[language];
        chatHeaderTitle.textContent = translation.welcome_message;
        chatbotDescription.textContent = translation.chatbot_description;
    }

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
                displayMessage(data.response, false);
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
            if (data.success) {
                alert(data.message);
                feedbackInput.value = '';
            } else {
                alert(data.message);
            }
        } catch (error) {
            console.error(error);
            alert("Error: Unable to submit feedback. Please try again later.");
        }
    });

});

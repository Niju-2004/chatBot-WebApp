document.addEventListener('DOMContentLoaded', () => {
    const messageContainer = document.getElementById('message-container');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const langToggleTa = document.getElementById('lang-toggle-ta');
    const langToggleEn = document.getElementById('lang-toggle-en');
    const chatHeaderTitle = document.getElementById('chat-header-title');
    const welcomeMessage = document.getElementById('welcome-message');
    const chatbotDescription = document.getElementById('chatbot-description');
    const loadingIndicator = document.getElementById('loading-indicator');
    const quickQuestions = document.querySelectorAll('.quick-question');

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

    /**
     * Display a message in the chat interface.
     * @param {string} message - The message to display.
     * @param {boolean} isUser - Whether the message is from the user.
     */
    function displayMessage(message, isUser = false) {
        const messageElement = document.createElement('div');
        messageElement.classList.add(isUser ? 'user-message' : 'bot-message');
        messageContainer.appendChild(messageElement);

        if (isUser) {
            // Display user message immediately
            messageElement.textContent = message;
        } else {
            // Display bot message with typing effect
            typeResponse(message, messageElement);
        }

        // Auto-scroll to the latest message
        messageContainer.scrollTop = messageContainer.scrollHeight;
    }

    /**
     * Type out the chatbot's response one character at a time.
     * @param {string} response - The chatbot's response.
     * @param {HTMLElement} messageElement - The message container element.
     */
    function typeResponse(response, messageElement) {
        let index = 0;
        const typingSpeed = 30; // Adjust typing speed (in milliseconds)

        function type() {
            if (index < response.length) {
                messageElement.textContent += response.charAt(index);
                index++;
                setTimeout(type, typingSpeed);
                messageContainer.scrollTop = messageContainer.scrollHeight; // Auto-scroll
            }
        }

        type(); // Start typing effect
    }

    /**
     * Show the loading indicator.
     */
    function showLoadingIndicator() {
        loadingIndicator.style.display = 'flex';
    }

    /**
     * Hide the loading indicator.
     */
    function hideLoadingIndicator() {
        loadingIndicator.style.display = 'none';
    }

    /**
     * Handle language translation updates.
     * @param {string} language - The language code ('en' or 'ta').
     */
    function handleTranslation(language) {
        currentLanguage = language;
        localStorage.setItem('language', language); // Save language preference
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
            displayMessage("⚠️ Please enter a valid query (max 500 characters).", false);
            return;
        }

        displayMessage(query, true); // Display user's query
        userInput.value = ''; // Clear input field
        showLoadingIndicator();

        try {
            const response = await fetch('/ask', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query })
            });

            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            const data = await response.json();

            if (!data.response || data.response.trim() === "") {
                displayMessage("⚠️ No relevant information found. Try asking differently.", false);
            } else {
                // Display the response with a typing effect
                displayMessage(data.response, false);
            }
        } catch (error) {
            console.error(error);
            displayMessage("❌ Error: Unable to fetch response. Please try again later.", false);
        } finally {
            hideLoadingIndicator();
        }
    });

    // Handle predefined query buttons
    quickQuestions.forEach(button => {
        button.addEventListener('click', () => {
            const query = button.getAttribute('data-question');
            userInput.value = query;
            sendButton.click();
        });
    });

    // Handle "Enter" key in user input
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendButton.click();
    });

    // Initialize language on page load
    handleTranslation(currentLanguage);
});
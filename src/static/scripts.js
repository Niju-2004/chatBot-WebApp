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

    /**
     * Display a message in the chat interface.
     * @param {string} message - The message to display.
     * @param {boolean} isUser - Whether the message is from the user.
     * @param {boolean} isHTML - Whether the message contains HTML.
     */
    function displayMessage(message, isUser = false, isHTML = false) {
        const messageElement = document.createElement('div');
        messageElement.classList.add(isUser ? 'user-message' : 'bot-message');

        if (isHTML) {
            messageElement.innerHTML = formatStructuredResponse(message);
        } else {
            messageElement.textContent = message;
        }

        messageContainer.appendChild(messageElement);
        messageContainer.scrollTop = messageContainer.scrollHeight; // Auto-scroll to the latest message
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
                displayMessage(data.response, false, true); // Display bot's response as formatted HTML
            }
        } catch (error) {
            console.error(error);
            displayMessage("❌ Error: Unable to fetch response. Please try again later.", false);
        } finally {
            hideLoadingIndicator();
        }
    });

    // Feedback button
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
            if (data.success) feedbackInput.value = ''; // Clear feedback input on success
        } catch (error) {
            console.error(error);
            alert("❌ Error submitting feedback. Please try again later.");
        }
    });

    /**
     * Format chatbot response to display structured data properly.
     * @param {string} text - The raw text response from the chatbot.
     * @returns {string} - Formatted HTML string.
     */
    function formatStructuredResponse(text) {
        // Split the text into paragraphs based on double newlines
        const paragraphs = text.split('\n\n');

        // Wrap each paragraph in <p> tags
        const formattedParagraphs = paragraphs.map(paragraph => {
            // Replace single newlines with <br> within the same paragraph
            const formattedParagraph = paragraph.replace(/\n/g, '<br>');

            // Handle bullet points (if any)
            if (formattedParagraph.startsWith('*')) {
                // Convert bullet points to <ul> and <li>
                const bulletPoints = formattedParagraph.split('<br>').map(line => {
                    if (line.startsWith('*')) {
                        return `<li>${line.slice(1).trim()}</li>`;
                    }
                    return line;
                }).join('');

                return `<ul>${bulletPoints}</ul>`;
            }

            // Wrap the paragraph in <p> tags
            return `<p>${formattedParagraph}</p>`;
        }).join('');

        return formattedParagraphs;
    }

    // Handle "Enter" key in user input
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendButton.click(); // Trigger send button click
        }
    });

    // Handle "Enter" key in feedback input
    feedbackInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            feedbackButton.click(); // Trigger feedback button click
        }
    });

    // Initialize language on page load
    handleTranslation(currentLanguage);
});
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

    let currentLanguage = 'en';

    const greetings = {
        "hello": "Hello! How can I assist you today?",
        "hi": "Hi there! How can I help you?",
        "good morning": "Good morning! How can I assist you today?",
        "good afternoon": "Good afternoon! How can I help you?",
        "good evening": "Good evening! How can I assist you today?",
        "good night": "Good night! If you have any more questions, feel free to ask tomorrow.",
        "thank you": "You're welcome! If you have any more questions, feel free to ask.",
        "thanks": "You're welcome! If you have any more questions, feel free to ask.",
        "ok": "Yes, I'm always here to assist you."
    };

    const tamilGreetings = {
        "வணக்கம்": "வணக்கம்! என்னால் எப்படி உதவ முடியும்?",
        "ஹலோ": "ஹலோ! நான் உங்களுக்கு எப்படி உதவ முடியும்?",
        "நலம்": "நலம்! நான் உங்களுக்கு எப்படி உதவ முடியும்?",
    };

    langToggleTa.addEventListener('click', () => {
        currentLanguage = 'ta';
        translateUITamil();
    });

    langToggleEn.addEventListener('click', () => {
        currentLanguage = 'en';
        translateUIEnglish();
    });

    function translateUITamil() {
        chatHeaderTitle.textContent = 'வேளாண் சாட்போட்';
        welcomeMessage.textContent = 'கால்நடை மருத்துவ அரட்டைப் பெட்டிக்கு வருக!';
        chatbotDescription.textContent = 'கால்நடை பராமரிப்பு பற்றிய உங்கள் கேள்விகளுக்கு பதிலளிக்க நான் இங்கே இருக்கிறேன். துல்லியமான நோயறிதல் மற்றும் சரியான சிகிச்சை திட்டத்திற்கு ஒரு கால்நடை மருத்துவரை அணுகவும்.';
        userInput.placeholder = 'உங்கள் கேள்வியை இங்கே எழுதவும்...';
        sendButton.textContent = 'அனுப்பு';
        feedbackInput.placeholder = 'உங்கள் கருத்துக்களை இங்கே எழுதவும்...';
        feedbackButton.textContent = 'சமர்ப்பிக்கவும்';
    }

    function translateUIEnglish() {
        chatHeaderTitle.textContent = 'Veterinary Chatbot';
        welcomeMessage.textContent = 'Welcome to the Veterinary Chatbot!';
        chatbotDescription.textContent = "I'm here to help answer your questions about veterinary care. Consult a veterinarian for an accurate diagnosis and proper treatment plan.";
        userInput.placeholder = 'Type your question here...';
        sendButton.textContent = 'Send';
        feedbackInput.placeholder = 'Enter your feedback here...';
        feedbackButton.textContent = 'Submit Feedback';
    }

    // Show loading indicator
    function showLoading() {
        const loading = document.getElementById('loading-indicator');
        loading.style.display = 'flex';
    }

    // Hide loading indicator
    function hideLoading() {
        const loading = document.getElementById('loading-indicator');
        loading.style.display = 'none';
    }

    sendButton.addEventListener('click', async () => {
        const userQuery = userInput.value.trim().toLowerCase();
        if (!userQuery) {
            alert('Please enter a query!');
            return;
        }

        const userQueryDiv = document.createElement('div');
        userQueryDiv.className = 'user-query';
        userQueryDiv.innerText = `User: ${userQuery}`;
        messageContainer.appendChild(userQueryDiv);

        let chatbotResponse;

        // Clear input and show loading
        userInput.value = '';
        showLoading();

        try {
            if (currentLanguage === 'ta') {
                if (tamilGreetings[userQuery]) {
                    chatbotResponse = tamilGreetings[userQuery];
                } else {
                    const response = await fetch('/ask', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ query: userQuery }),
                    });

                    const data = await response.json();
                    chatbotResponse = data.response.treatment;
                }
            } else {
                if (greetings[userQuery]) {
                    chatbotResponse = greetings[userQuery];
                } else {
                    const response = await fetch('/ask', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ query: userQuery }),
                    });

                    const data = await response.json();
                    chatbotResponse = data.response.treatment;
                }
            }

            const responseDiv = document.createElement('div');
            responseDiv.className = 'chatbot-response';
            responseDiv.innerHTML = chatbotResponse
                .replace(/\*\*(.*?)\*\*/g, '<b>$1</b>')
                .replace(/\n/g, '<br>');
            messageContainer.appendChild(responseDiv);
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to process your query. Please try again.');
        } finally {
            hideLoading();
        }
    });

    feedbackButton.addEventListener('click', async () => {
        const feedback = feedbackInput.value.trim();
        if (!feedback) {
            alert('Please enter your feedback!');
            return;
        }

        try {
            const response = await fetch('/feedback', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ feedback: feedback }),
            });

            const data = await response.json();
            if (data.success) {
                alert('Thank you for your feedback!');
                feedbackInput.value = '';
            } else {
                alert('Failed to submit feedback. Please try again.');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to submit feedback. Please try again.');
        }
    });

    // Keep header sticky
    window.addEventListener('scroll', () => {
        const header = document.querySelector('.chat-header');
        const scrollY = window.scrollY;

        if (scrollY > 100) {
            header.style.boxShadow = '0 4px 15px rgba(0, 0, 0, 0.1)';
        } else {
            header.style.boxShadow = 'none';
        }
    });
});

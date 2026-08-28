document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatMessages = document.getElementById('chat-messages');
    const sessionId = document.getElementById('session-id').value;
    const sendBtn = document.getElementById('send-btn');

    if (!chatForm) return;

    // Optional: Load history on load
    // fetchHistory();

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const message = userInput.value.trim();
        if (!message) return;

        // 1. Append User Message
        appendMessage('user', message);
        userInput.value = '';
        sendBtn.disabled = true;

        // 2. Append empty Bot Message wrapper
        const botMsgContent = appendMessage('bot', '<span class="typing">...</span>');

        // 3. Initiate SSE connection via POST using fetch
        try {
            const response = await fetch('/api/chat/stream', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: message,
                    session_id: sessionId
                })
            });

            if (!response.body) throw new Error("No readable stream available");

            const reader = response.body.getReader();
            const decoder = new TextDecoder('utf-8');
            let fullText = "";
            botMsgContent.innerHTML = ""; // clear typing

            let buffer = "";
            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n\n');
                
                // The last chunk might be incomplete (doesn't end with \n\n)
                buffer = lines.pop();
                
                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        const dataStr = line.substring(6);
                        if (dataStr === '[DONE]') {
                            break;
                        }
                        try {
                            const dataObj = JSON.parse(dataStr);
                            fullText += dataObj.content;
                            // Parse markdown and update UI
                            botMsgContent.innerHTML = marked.parse(fullText);
                            scrollToBottom();
                        } catch(err) {
                            console.error("Parse error", err, "on string:", dataStr);
                        }
                    }
                }
            }
        } catch (error) {
            console.error("Streaming error:", error);
            botMsgContent.innerHTML = "<em>Error connecting to the AI.</em>";
        } finally {
            sendBtn.disabled = false;
            userInput.focus();
        }
    });

    function appendMessage(role, contentHTML) {
        const div = document.createElement('div');
        div.className = `message ${role}-message`;
        
        const avatar = document.createElement('div');
        avatar.className = `avatar ${role}-avatar`;
        avatar.textContent = role === 'user' ? 'U' : 'AI';

        const content = document.createElement('div');
        content.className = 'message-content';
        content.innerHTML = role === 'user' ? contentHTML : contentHTML; // If user, just raw text. If bot, might be markdown.
        
        div.appendChild(avatar);
        div.appendChild(content);
        
        chatMessages.appendChild(div);
        scrollToBottom();
        return content;
    }

    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
});

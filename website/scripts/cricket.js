// Cricket Agent Chat Interface

class CricketChat {
    constructor() {
        this.chatInput = document.getElementById('chat-input');
        this.sendButton = document.getElementById('send-button');
        this.chatMessages = document.getElementById('chat-messages');
        this.suggestions = document.getElementById('chat-suggestions');
        
        this.cricketAgentUrl = 'http://localhost:8002'; // Default to local cricket-agent
        this.isLoading = false;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.loadCricketAgentUrl();
        console.log('🏏 Cricket Chat initialized');
    }
    
    setupEventListeners() {
        // Send button click
        this.sendButton.addEventListener('click', () => this.sendMessage());
        
        // Enter key press
        this.chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Input change for button state
        this.chatInput.addEventListener('input', () => {
            this.updateSendButton();
        });
        
        // Suggestion buttons
        this.suggestions.addEventListener('click', (e) => {
            if (e.target.classList.contains('suggestion-btn')) {
                const query = e.target.getAttribute('data-query');
                this.chatInput.value = query;
                this.updateSendButton();
                this.sendMessage();
            }
        });
        
        // Auto-resize input
        this.chatInput.addEventListener('input', () => {
            this.autoResizeInput();
        });
    }
    
    loadCricketAgentUrl() {
        // Try to get cricket agent URL from environment or use default
        const envUrl = window.CRICKET_AGENT_URL || process.env.CRICKET_AGENT_URL;
        if (envUrl) {
            this.cricketAgentUrl = envUrl;
        }
        
        // Check if we're in production and adjust URL accordingly
        if (window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
            this.cricketAgentUrl = 'https://cricket-agent-xxx.run.app'; // Replace with actual production URL
        }
        
        console.log('Cricket Agent URL:', this.cricketAgentUrl);
    }
    
    updateSendButton() {
        const hasText = this.chatInput.value.trim().length > 0;
        this.sendButton.disabled = !hasText || this.isLoading;
    }
    
    autoResizeInput() {
        this.chatInput.style.height = 'auto';
        this.chatInput.style.height = Math.min(this.chatInput.scrollHeight, 120) + 'px';
    }
    
    async sendMessage() {
        const message = this.chatInput.value.trim();
        if (!message || this.isLoading) return;
        
        // Add user message to chat
        this.addMessage(message, 'user');
        
        // Clear input and update button
        this.chatInput.value = '';
        this.updateSendButton();
        this.autoResizeInput();
        
        // Show typing indicator
        this.showTypingIndicator();
        
        // Send to cricket agent
        try {
            const response = await this.callCricketAgent(message);
            this.hideTypingIndicator();
            this.addMessage(response.answer, 'ai', response.meta);
        } catch (error) {
            this.hideTypingIndicator();
            this.addErrorMessage('Sorry, I encountered an error. Please try again.');
            console.error('Cricket agent error:', error);
        }
    }
    
    async callCricketAgent(message) {
        this.isLoading = true;
        this.updateSendButton();
        
        try {
            const response = await fetch(`${this.cricketAgentUrl}/v1/ask`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    text: message,
                    source: 'web',
                    team_hint: null
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            return data;
        } finally {
            this.isLoading = false;
            this.updateSendButton();
        }
    }
    
    addMessage(content, type, meta = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}-message`;
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerHTML = type === 'ai' ? '<span class="avatar-icon">🏏</span>' : '<span class="avatar-icon">👤</span>';
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        
        const messageText = document.createElement('div');
        messageText.className = 'message-text';
        messageText.innerHTML = this.formatMessage(content);
        
        const messageTime = document.createElement('div');
        messageTime.className = 'message-time';
        messageTime.textContent = this.getCurrentTime();
        
        messageContent.appendChild(messageText);
        messageContent.appendChild(messageTime);
        
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(messageContent);
        
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    addErrorMessage(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'message ai-message';
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerHTML = '<span class="avatar-icon">⚠️</span>';
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        
        const messageText = document.createElement('div');
        messageText.className = 'message-text error-message';
        messageText.textContent = message;
        
        const messageTime = document.createElement('div');
        messageTime.className = 'message-time';
        messageTime.textContent = this.getCurrentTime();
        
        messageContent.appendChild(messageText);
        messageContent.appendChild(messageTime);
        
        errorDiv.appendChild(avatar);
        errorDiv.appendChild(messageContent);
        
        this.chatMessages.appendChild(errorDiv);
        this.scrollToBottom();
    }
    
    showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message ai-message typing-indicator';
        typingDiv.id = 'typing-indicator';
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerHTML = '<span class="avatar-icon">🏏</span>';
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        
        const typingContent = document.createElement('div');
        typingContent.className = 'message-typing';
        typingContent.innerHTML = `
            <span>Cricket Assistant is typing</span>
            <div class="typing-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
        `;
        
        messageContent.appendChild(typingContent);
        
        typingDiv.appendChild(avatar);
        typingDiv.appendChild(messageContent);
        
        this.chatMessages.appendChild(typingDiv);
        this.scrollToBottom();
    }
    
    hideTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }
    
    formatMessage(content) {
        // Convert markdown-like formatting to HTML
        return content
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/\n/g, '<br>')
            .replace(/^• (.+)$/gm, '<li>$1</li>')
            .replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');
    }
    
    getCurrentTime() {
        return new Date().toLocaleTimeString([], { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
    }
    
    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
    
    // Public methods for testing
    getChatHistory() {
        const messages = this.chatMessages.querySelectorAll('.message');
        return Array.from(messages).map(msg => ({
            type: msg.classList.contains('user-message') ? 'user' : 'ai',
            content: msg.querySelector('.message-text').textContent,
            time: msg.querySelector('.message-time').textContent
        }));
    }
    
    clearChat() {
        this.chatMessages.innerHTML = '';
        this.addWelcomeMessage();
    }
    
    addWelcomeMessage() {
        this.addMessage(`
            Hello! I'm your cricket assistant for Caroline Springs Cricket Club. I can help you with:
            <ul>
                <li><strong>Player Information:</strong> "Which team is John Smith in?"</li>
                <li><strong>Player Stats:</strong> "How many runs did Jane Doe score last match?"</li>
                <li><strong>Fixtures:</strong> "List all fixtures for Caroline Springs Blue U10"</li>
                <li><strong>Ladder Position:</strong> "Where are Caroline Springs Blue U10 on the ladder?"</li>
                <li><strong>Next Match:</strong> "When is the next game for Caroline Springs White U10?"</li>
                <li><strong>Team Roster:</strong> "Who are the players for Caroline Springs Blue U10?"</li>
            </ul>
            What would you like to know?
        `, 'ai');
    }
}

// Initialize cricket chat when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize cricket chat
    window.cricketChat = new CricketChat();
    
    // Add keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + K to focus input
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            document.getElementById('chat-input').focus();
        }
        
        // Escape to clear input
        if (e.key === 'Escape') {
            document.getElementById('chat-input').value = '';
            document.getElementById('chat-input').blur();
        }
    });
    
    // Add connection status indicator
    checkCricketAgentConnection();
});

// Check cricket agent connection status
async function checkCricketAgentConnection() {
    try {
        const response = await fetch(`${window.cricketChat.cricketAgentUrl}/healthz`);
        if (response.ok) {
            console.log('✅ Cricket agent is online');
            updateConnectionStatus('online');
        } else {
            throw new Error('Health check failed');
        }
    } catch (error) {
        console.warn('⚠️ Cricket agent is offline:', error.message);
        updateConnectionStatus('offline');
    }
}

// Update connection status in UI
function updateConnectionStatus(status) {
    const statusIndicator = document.querySelector('.status-indicator');
    const statusText = document.querySelector('.chat-status span');
    
    if (statusIndicator && statusText) {
        statusIndicator.className = `status-indicator ${status}`;
        statusText.textContent = status === 'online' ? 'Online' : 'Offline';
    }
}

// Export for testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CricketChat;
}

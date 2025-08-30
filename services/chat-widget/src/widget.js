/**
 * ANZx.ai Chat Widget
 * Embeddable chat widget with WebSocket support
 */

class ANZxChatWidget {
    constructor(config = {}) {
        this.config = {
            apiUrl: config.apiUrl || 'wss://api.anzx.ai',
            theme: config.theme || 'light',
            position: config.position || 'bottom-right',
            organizationId: config.organizationId,
            ...config
        };
        
        this.isOpen = false;
        this.socket = null;
        this.messageQueue = [];
        
        this.init();
    }
    
    init() {
        this.createWidget();
        this.attachEventListeners();
        this.connectWebSocket();
    }
    
    createWidget() {
        // Create widget container
        this.container = document.createElement('div');
        this.container.id = 'anzx-chat-widget';
        this.container.className = `anzx-widget ${this.config.theme} ${this.config.position}`;
        
        // Create widget HTML structure
        this.container.innerHTML = `
            <div class="anzx-widget-button" id="anzx-widget-button">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M20 2H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h4l4 4 4-4h4c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z"/>
                </svg>
            </div>
            <div class="anzx-widget-chat" id="anzx-widget-chat" style="display: none;">
                <div class="anzx-widget-header">
                    <h3>ANZx.ai Assistant</h3>
                    <button class="anzx-widget-close" id="anzx-widget-close">×</button>
                </div>
                <div class="anzx-widget-messages" id="anzx-widget-messages"></div>
                <div class="anzx-widget-input">
                    <input type="text" id="anzx-widget-input" placeholder="Type your message...">
                    <button id="anzx-widget-send">Send</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(this.container);
        this.loadStyles();
    }
    
    loadStyles() {
        const styles = `
            .anzx-widget {
                position: fixed;
                z-index: 10000;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            }
            .anzx-widget.bottom-right {
                bottom: 20px;
                right: 20px;
            }
            .anzx-widget-button {
                width: 60px;
                height: 60px;
                border-radius: 50%;
                background: #007bff;
                color: white;
                display: flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                transition: all 0.3s ease;
            }
            .anzx-widget-button:hover {
                transform: scale(1.1);
            }
            .anzx-widget-chat {
                width: 350px;
                height: 500px;
                background: white;
                border-radius: 12px;
                box-shadow: 0 8px 32px rgba(0,0,0,0.12);
                display: flex;
                flex-direction: column;
                position: absolute;
                bottom: 70px;
                right: 0;
            }
            .anzx-widget-header {
                padding: 16px;
                background: #007bff;
                color: white;
                border-radius: 12px 12px 0 0;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .anzx-widget-messages {
                flex: 1;
                padding: 16px;
                overflow-y: auto;
            }
            .anzx-widget-input {
                padding: 16px;
                border-top: 1px solid #eee;
                display: flex;
                gap: 8px;
            }
            .anzx-widget-input input {
                flex: 1;
                padding: 8px 12px;
                border: 1px solid #ddd;
                border-radius: 20px;
                outline: none;
            }
            .anzx-widget-input button {
                padding: 8px 16px;
                background: #007bff;
                color: white;
                border: none;
                border-radius: 20px;
                cursor: pointer;
            }
        `;
        
        const styleSheet = document.createElement('style');
        styleSheet.textContent = styles;
        document.head.appendChild(styleSheet);
    }
    
    attachEventListeners() {
        const button = document.getElementById('anzx-widget-button');
        const close = document.getElementById('anzx-widget-close');
        const input = document.getElementById('anzx-widget-input');
        const send = document.getElementById('anzx-widget-send');
        
        button.addEventListener('click', () => this.toggleWidget());
        close.addEventListener('click', () => this.closeWidget());
        send.addEventListener('click', () => this.sendMessage());
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendMessage();
        });
    }
    
    toggleWidget() {
        this.isOpen = !this.isOpen;
        const chat = document.getElementById('anzx-widget-chat');
        chat.style.display = this.isOpen ? 'flex' : 'none';
    }
    
    closeWidget() {
        this.isOpen = false;
        const chat = document.getElementById('anzx-widget-chat');
        chat.style.display = 'none';
    }
    
    connectWebSocket() {
        try {
            this.socket = new WebSocket(`${this.config.apiUrl}/ws`);
            
            this.socket.onopen = () => {
                console.log('ANZx Chat Widget connected');
                this.processMessageQueue();
            };
            
            this.socket.onmessage = (event) => {
                const message = JSON.parse(event.data);
                this.displayMessage(message.content, 'assistant');
            };
            
            this.socket.onclose = () => {
                console.log('ANZx Chat Widget disconnected');
                // Implement reconnection logic
                setTimeout(() => this.connectWebSocket(), 5000);
            };
        } catch (error) {
            console.error('WebSocket connection failed:', error);
            // Fallback to HTTP polling
            this.setupHttpFallback();
        }
    }
    
    sendMessage() {
        const input = document.getElementById('anzx-widget-input');
        const message = input.value.trim();
        
        if (!message) return;
        
        this.displayMessage(message, 'user');
        input.value = '';
        
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify({
                type: 'message',
                content: message,
                organizationId: this.config.organizationId
            }));
        } else {
            this.messageQueue.push(message);
        }
    }
    
    displayMessage(content, sender) {
        const messages = document.getElementById('anzx-widget-messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        messageDiv.textContent = content;
        messages.appendChild(messageDiv);
        messages.scrollTop = messages.scrollHeight;
    }
    
    processMessageQueue() {
        while (this.messageQueue.length > 0) {
            const message = this.messageQueue.shift();
            this.socket.send(JSON.stringify({
                type: 'message',
                content: message,
                organizationId: this.config.organizationId
            }));
        }
    }
    
    setupHttpFallback() {
        // Implement HTTP polling as fallback
        console.log('Setting up HTTP fallback for chat widget');
    }
}

// Auto-initialize if config is provided
if (window.ANZxChatConfig) {
    window.anzxChat = new ANZxChatWidget(window.ANZxChatConfig);
}

// Export for manual initialization
window.ANZxChatWidget = ANZxChatWidget;
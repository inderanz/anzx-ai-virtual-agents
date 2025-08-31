/**
 * ANZx.ai Chat Widget
 * Embeddable chat widget with WebSocket support and HTTP fallback
 * Bundle size optimized for <12KB
 */

class ANZxChatWidget {
    constructor(config = {}) {
        this.config = {
            apiUrl: config.apiUrl || 'https://api.anzx.ai',
            wsUrl: config.wsUrl || 'wss://api.anzx.ai',
            widgetId: config.widgetId,
            apiKey: config.apiKey,
            theme: config.theme || 'light',
            position: config.position || 'bottom-right',
            primaryColor: config.primaryColor || '#007bff',
            welcomeMessage: config.welcomeMessage || 'Hi! How can I help you today?',
            placeholder: config.placeholder || 'Type your message...',
            maxMessageLength: config.maxMessageLength || 1000,
            enableFileUpload: config.enableFileUpload || false,
            showTypingIndicator: config.showTypingIndicator !== false,
            rateLimit: config.rateLimit || { messages: 10, windowMs: 60000 },
            ...config
        };
        
        this.state = {
            isOpen: false,
            isConnected: false,
            conversationId: this.generateId(),
            visitorId: this.getVisitorId(),
            messageQueue: [],
            lastMessageId: null,
            rateLimitExceeded: false,
            isTyping: false
        };
        
        this.socket = null;
        this.pollingInterval = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 3;
        
        this.init();
    }
    
    init() {
        this.validateConfig();
        this.createWidget();
        this.attachEventListeners();
        this.setupAccessibility();
        this.initializeConnection();
        this.trackEvent('widget_initialized');
    }
    
    validateConfig() {
        if (!this.config.widgetId || !this.config.apiKey) {
            throw new Error('ANZx Chat Widget: widgetId and apiKey are required');
        }
    }
    
    generateId() {
        return 'conv_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now();
    }
    
    getVisitorId() {
        let visitorId = localStorage.getItem('anzx_visitor_id');
        if (!visitorId) {
            visitorId = 'visitor_' + Math.random().toString(36).substr(2, 9);
            localStorage.setItem('anzx_visitor_id', visitorId);
        }
        return visitorId;
    }
    
    createWidget() {
        // Create widget container
        this.container = document.createElement('div');
        this.container.id = 'anzx-chat-widget';
        this.container.className = `anzx-widget ${this.config.theme} ${this.config.position}`;
        
        // Create widget HTML structure
        this.container.innerHTML = `
            <div class="anzx-widget-button" id="anzx-widget-button" role="button" tabindex="0" aria-label="Open chat support">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M20 2H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h4l4 4 4-4h4c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z"/>
                </svg>
            </div>
            <div class="anzx-widget-chat" id="anzx-widget-chat" role="dialog" aria-label="Chat support window" style="display: none;">
                <div class="anzx-widget-header">
                    <h3>ANZx.ai Assistant</h3>
                    <button class="anzx-widget-close" id="anzx-widget-close" aria-label="Close chat">×</button>
                </div>
                <div class="anzx-widget-messages" id="anzx-widget-messages" role="log" aria-live="polite"></div>
                <div class="anzx-widget-typing" id="anzx-widget-typing" style="display: none;">
                    <span>AI is typing</span>
                    <div class="anzx-typing-dots">
                        <div class="anzx-typing-dot"></div>
                        <div class="anzx-typing-dot"></div>
                        <div class="anzx-typing-dot"></div>
                    </div>
                </div>
                <div class="anzx-widget-input">
                    <textarea id="anzx-widget-input" placeholder="${this.config.placeholder}" rows="1" maxlength="${this.config.maxMessageLength}" aria-label="Type your message"></textarea>
                    <button id="anzx-widget-send" aria-label="Send message" disabled>
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
                        </svg>
                    </button>
                </div>
                <div class="anzx-widget-status" id="anzx-widget-status"></div>
            </div>
        `;
        
        document.body.appendChild(this.container);
        this.loadStyles();
        
        // Add welcome message
        setTimeout(() => {
            this.displayMessage(this.config.welcomeMessage, 'assistant');
        }, 500);
    }
    
    loadStyles() {
        const primaryColor = this.config.primaryColor;
        const styles = `
            .anzx-widget {
                position: fixed;
                z-index: 10000;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                font-size: 14px;
            }
            .anzx-widget.bottom-right { bottom: 20px; right: 20px; }
            .anzx-widget.bottom-left { bottom: 20px; left: 20px; }
            .anzx-widget.top-right { top: 20px; right: 20px; }
            .anzx-widget.top-left { top: 20px; left: 20px; }
            
            .anzx-widget-button {
                width: 60px; height: 60px; border-radius: 50%; background: ${primaryColor};
                color: white; display: flex; align-items: center; justify-content: center;
                cursor: pointer; box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                transition: all 0.3s ease; border: none; outline: none;
            }
            .anzx-widget-button:hover, .anzx-widget-button:focus { transform: scale(1.1); }
            
            .anzx-widget-chat {
                width: 350px; height: 500px; background: white; border-radius: 12px;
                box-shadow: 0 8px 32px rgba(0,0,0,0.12); display: flex; flex-direction: column;
                position: absolute; bottom: 70px; right: 0;
            }
            .anzx-widget.bottom-left .anzx-widget-chat, .anzx-widget.top-left .anzx-widget-chat { right: auto; left: 0; }
            .anzx-widget.top-right .anzx-widget-chat, .anzx-widget.top-left .anzx-widget-chat { bottom: auto; top: 70px; }
            
            .anzx-widget-header {
                padding: 16px; background: ${primaryColor}; color: white;
                border-radius: 12px 12px 0 0; display: flex; justify-content: space-between; align-items: center;
            }
            .anzx-widget-header h3 { margin: 0; font-size: 16px; font-weight: 600; }
            .anzx-widget-close {
                background: none; border: none; color: white; font-size: 20px;
                cursor: pointer; padding: 0; width: 24px; height: 24px;
                display: flex; align-items: center; justify-content: center; border-radius: 4px;
            }
            .anzx-widget-close:hover { background: rgba(255,255,255,0.1); }
            
            .anzx-widget-messages {
                flex: 1; padding: 16px; overflow-y: auto; display: flex; flex-direction: column; gap: 12px;
            }
            .anzx-message {
                max-width: 80%; padding: 12px 16px; border-radius: 18px; word-wrap: break-word; line-height: 1.4;
            }
            .anzx-message.user {
                background: ${primaryColor}; color: white; align-self: flex-end; margin-left: auto;
            }
            .anzx-message.assistant {
                background: #f1f3f5; color: #333; align-self: flex-start;
            }
            .anzx-message.system {
                background: #fff3cd; color: #856404; align-self: center; font-style: italic; font-size: 12px;
            }
            
            .anzx-widget-typing {
                padding: 8px 16px; display: flex; align-items: center; gap: 8px; color: #666; font-size: 12px; font-style: italic;
            }
            .anzx-typing-dots { display: flex; gap: 4px; }
            .anzx-typing-dot {
                width: 6px; height: 6px; border-radius: 50%; background: #666;
                animation: anzx-typing 1.4s infinite ease-in-out;
            }
            .anzx-typing-dot:nth-child(1) { animation-delay: -0.32s; }
            .anzx-typing-dot:nth-child(2) { animation-delay: -0.16s; }
            @keyframes anzx-typing {
                0%, 80%, 100% { transform: scale(0.8); opacity: 0.5; }
                40% { transform: scale(1); opacity: 1; }
            }
            
            .anzx-widget-input {
                padding: 16px; border-top: 1px solid #eee; display: flex; gap: 8px; align-items: flex-end;
            }
            .anzx-widget-input textarea {
                flex: 1; border: 1px solid #ddd; border-radius: 20px; padding: 10px 16px;
                outline: none; resize: none; font-family: inherit; font-size: 14px; line-height: 1.4;
                max-height: 100px; min-height: 40px;
            }
            .anzx-widget-input textarea:focus { border-color: ${primaryColor}; }
            .anzx-widget-input button {
                width: 40px; height: 40px; background: ${primaryColor}; color: white; border: none;
                border-radius: 50%; cursor: pointer; display: flex; align-items: center; justify-content: center;
                transition: all 0.2s ease;
            }
            .anzx-widget-input button:hover:not(:disabled) { background: ${primaryColor}dd; }
            .anzx-widget-input button:disabled { background: #ccc; cursor: not-allowed; }
            
            .anzx-widget-status {
                padding: 8px 16px; font-size: 12px; color: #666; border-top: 1px solid #eee;
                display: none;
            }
            .anzx-widget-status.error { color: #dc3545; background: #f8d7da; display: block; }
            .anzx-widget-status.success { color: #155724; background: #d4edda; display: block; }
            
            .anzx-citations {
                margin-top: 8px; font-size: 12px; color: #666;
            }
            .anzx-citation {
                display: inline-block; background: #e9ecef; padding: 2px 6px; border-radius: 4px;
                margin-right: 4px; text-decoration: none; color: #666;
            }
            
            @media (max-width: 480px) {
                .anzx-widget-chat { width: calc(100vw - 40px); height: calc(100vh - 100px); }
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
        button.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                this.toggleWidget();
            }
        });
        
        close.addEventListener('click', () => this.closeWidget());
        send.addEventListener('click', () => this.sendMessage());
        
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        input.addEventListener('input', () => this.handleInputChange());
        
        // Handle escape key to close widget
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.state.isOpen) {
                this.closeWidget();
            }
        });
    }
    
    setupAccessibility() {
        const chat = document.getElementById('anzx-widget-chat');
        chat.setAttribute('tabindex', '-1');
        
        // Focus management
        const focusableElements = 'button, input, textarea, [tabindex]:not([tabindex="-1"])';
        const firstFocusable = chat.querySelector(focusableElements);
        const focusableContent = chat.querySelectorAll(focusableElements);
        const lastFocusable = focusableContent[focusableContent.length - 1];
        
        chat.addEventListener('keydown', (e) => {
            if (e.key === 'Tab') {
                if (e.shiftKey) {
                    if (document.activeElement === firstFocusable) {
                        lastFocusable.focus();
                        e.preventDefault();
                    }
                } else {
                    if (document.activeElement === lastFocusable) {
                        firstFocusable.focus();
                        e.preventDefault();
                    }
                }
            }
        });
    }
    
    handleInputChange() {
        const input = document.getElementById('anzx-widget-input');
        const send = document.getElementById('anzx-widget-send');
        
        // Auto-resize textarea
        input.style.height = 'auto';
        input.style.height = Math.min(input.scrollHeight, 100) + 'px';
        
        // Enable/disable send button
        const hasText = input.value.trim().length > 0;
        const withinLimit = input.value.length <= this.config.maxMessageLength;
        send.disabled = !hasText || !withinLimit || this.state.rateLimitExceeded;
    }
    
    toggleWidget() {
        if (this.state.isOpen) {
            this.closeWidget();
        } else {
            this.openWidget();
        }
    }
    
    openWidget() {
        this.state.isOpen = true;
        const chat = document.getElementById('anzx-widget-chat');
        const button = document.getElementById('anzx-widget-button');
        
        chat.style.display = 'flex';
        button.style.display = 'none';
        
        // Focus on input
        setTimeout(() => {
            document.getElementById('anzx-widget-input').focus();
        }, 100);
        
        this.trackEvent('widget_opened');
    }
    
    closeWidget() {
        this.state.isOpen = false;
        const chat = document.getElementById('anzx-widget-chat');
        const button = document.getElementById('anzx-widget-button');
        
        chat.style.display = 'none';
        button.style.display = 'flex';
        
        this.trackEvent('widget_closed');
    }
    
    initializeConnection() {
        // Try WebSocket first, fallback to HTTP polling
        if ('WebSocket' in window) {
            this.connectWebSocket();
        } else {
            this.setupHttpFallback();
        }
    }
    
    connectWebSocket() {
        try {
            const wsUrl = this.config.wsUrl.replace('https://', 'wss://').replace('http://', 'ws://');
            this.socket = new WebSocket(`${wsUrl}/api/chat-widget/ws/${this.config.widgetId}`);
            
            this.socket.onopen = () => {
                console.log('ANZx Chat Widget connected');
                this.state.isConnected = true;
                this.reconnectAttempts = 0;
                
                // Send authentication
                this.socket.send(JSON.stringify({
                    type: 'auth',
                    widget_id: this.config.widgetId,
                    api_key: this.config.apiKey,
                    conversation_id: this.state.conversationId
                }));
                
                this.processMessageQueue();
            };
            
            this.socket.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleWebSocketMessage(data);
                } catch (error) {
                    console.error('WebSocket message parsing error:', error);
                }
            };
            
            this.socket.onclose = (event) => {
                console.log('ANZx Chat Widget disconnected:', event.code, event.reason);
                this.state.isConnected = false;
                this.socket = null;
                
                // Attempt reconnection or fallback
                if (this.reconnectAttempts < this.maxReconnectAttempts) {
                    this.reconnectAttempts++;
                    setTimeout(() => this.connectWebSocket(), 2000 * this.reconnectAttempts);
                } else {
                    console.log('WebSocket failed, falling back to polling');
                    this.setupHttpFallback();
                }
            };
            
            this.socket.onerror = (error) => {
                console.error('WebSocket error:', error);
            };
            
        } catch (error) {
            console.error('WebSocket connection failed:', error);
            this.setupHttpFallback();
        }
    }
    
    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'message':
                this.hideTypingIndicator();
                this.displayMessage(data.content, 'assistant', data.citations);
                break;
                
            case 'typing':
                if (data.typing) {
                    this.showTypingIndicator();
                } else {
                    this.hideTypingIndicator();
                }
                break;
                
            case 'error':
                this.hideTypingIndicator();
                this.showError(data.message || 'An error occurred');
                break;
                
            case 'auth_success':
                console.log('WebSocket authenticated');
                break;
                
            case 'auth_failed':
                console.error('WebSocket authentication failed');
                this.socket.close();
                break;
        }
    }
    
    async sendMessage() {
        const input = document.getElementById('anzx-widget-input');
        const message = input.value.trim();
        
        if (!message || message.length > this.config.maxMessageLength || this.state.rateLimitExceeded) {
            return;
        }
        
        // Clear input and disable send button
        input.value = '';
        input.style.height = 'auto';
        const send = document.getElementById('anzx-widget-send');
        send.disabled = true;
        
        // Add user message to UI
        this.displayMessage(message, 'user');
        
        // Show typing indicator
        this.showTypingIndicator();
        
        try {
            if (this.socket && this.socket.readyState === WebSocket.OPEN) {
                // Send via WebSocket
                this.socket.send(JSON.stringify({
                    type: 'message',
                    content: message,
                    conversation_id: this.state.conversationId,
                    visitor_info: this.getVisitorInfo()
                }));
            } else {
                // Send via HTTP API
                const response = await this.sendMessageHTTP(message);
                this.hideTypingIndicator();
                
                if (response.ai_response) {
                    this.displayMessage(
                        response.ai_response.content,
                        'assistant',
                        response.ai_response.citations
                    );
                }
            }
            
        } catch (error) {
            this.hideTypingIndicator();
            this.handleMessageError(error);
        }
        
        // Re-enable input
        this.handleInputChange();
    }
    
    async sendMessageHTTP(message) {
        const response = await fetch(`${this.config.apiUrl}/api/chat-widget/public/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Widget-ID': this.config.widgetId,
                'X-API-Key': this.config.apiKey,
                'Origin': window.location.origin
            },
            body: JSON.stringify({
                message: message,
                conversation_id: this.state.conversationId,
                visitor_info: this.getVisitorInfo()
            })
        });
        
        if (!response.ok) {
            if (response.status === 429) {
                this.state.rateLimitExceeded = true;
                setTimeout(() => {
                    this.state.rateLimitExceeded = false;
                }, 60000);
                throw new Error('Rate limit exceeded. Please wait a moment.');
            }
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        return await response.json();
    }
    
    handleMessageError(error) {
        if (error.message.includes('Rate limit')) {
            this.showError('Please wait a moment before sending another message.');
        } else if (error.message.includes('Domain not allowed')) {
            this.showError('This chat widget is not authorized for this domain.');
        } else {
            this.showError('Sorry, there was an error sending your message. Please try again.');
        }
        console.error('Chat error:', error);
    }
    
    getVisitorInfo() {
        return {
            visitor_id: this.state.visitorId,
            user_agent: navigator.userAgent,
            language: navigator.language,
            timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
            screen_resolution: `${screen.width}x${screen.height}`,
            page_url: window.location.href,
            page_title: document.title,
            referrer: document.referrer,
            timestamp: new Date().toISOString()
        };
    }
    
    displayMessage(content, sender, citations = null) {
        const messages = document.getElementById('anzx-widget-messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `anzx-message ${sender}`;
        messageDiv.textContent = content;
        
        // Add citations if provided
        if (citations && citations.length > 0) {
            const citationsDiv = document.createElement('div');
            citationsDiv.className = 'anzx-citations';
            citationsDiv.innerHTML = 'Sources: ' + citations.map((citation, index) => 
                `<span class="anzx-citation">${citation.source || `Source ${index + 1}`}</span>`
            ).join('');
            messageDiv.appendChild(citationsDiv);
        }
        
        messages.appendChild(messageDiv);
        messages.scrollTop = messages.scrollHeight;
    }
    
    showTypingIndicator() {
        if (this.state.isTyping || !this.config.showTypingIndicator) return;
        
        this.state.isTyping = true;
        const typingDiv = document.getElementById('anzx-widget-typing');
        typingDiv.style.display = 'flex';
        
        const messages = document.getElementById('anzx-widget-messages');
        messages.scrollTop = messages.scrollHeight;
    }
    
    hideTypingIndicator() {
        this.state.isTyping = false;
        const typingDiv = document.getElementById('anzx-widget-typing');
        typingDiv.style.display = 'none';
    }
    
    showError(message) {
        const status = document.getElementById('anzx-widget-status');
        status.className = 'anzx-widget-status error';
        status.textContent = message;
        
        // Hide error after 5 seconds
        setTimeout(() => {
            status.style.display = 'none';
            status.className = 'anzx-widget-status';
        }, 5000);
    }
    
    processMessageQueue() {
        while (this.state.messageQueue.length > 0) {
            const message = this.state.messageQueue.shift();
            this.socket.send(JSON.stringify({
                type: 'message',
                content: message,
                conversation_id: this.state.conversationId,
                visitor_info: this.getVisitorInfo()
            }));
        }
    }
    
    setupHttpFallback() {
        console.log('Setting up HTTP fallback for chat widget');
        
        if (this.pollingInterval) {
            clearInterval(this.pollingInterval);
        }
        
        // Poll every 2 seconds for new messages
        this.pollingInterval = setInterval(async () => {
            try {
                await this.pollForMessages();
            } catch (error) {
                console.error('Polling error:', error);
            }
        }, 2000);
    }
    
    async pollForMessages() {
        if (!this.state.conversationId) return;
        
        try {
            const response = await fetch(`${this.config.apiUrl}/api/chat-widget/public/messages/${this.state.conversationId}`, {
                headers: {
                    'X-Widget-ID': this.config.widgetId,
                    'X-API-Key': this.config.apiKey,
                    'X-Last-Message-ID': this.state.lastMessageId || ''
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                
                if (data.messages && data.messages.length > 0) {
                    data.messages.forEach(message => {
                        if (message.role === 'assistant') {
                            this.displayMessage(message.content, 'assistant', message.citations);
                            this.state.lastMessageId = message.id;
                        }
                    });
                }
            }
            
        } catch (error) {
            console.error('Polling failed:', error);
        }
    }
    
    trackEvent(eventName, properties = {}) {
        try {
            // Send analytics event
            if (typeof gtag !== 'undefined') {
                gtag('event', eventName, {
                    custom_map: { widget_id: this.config.widgetId },
                    ...properties
                });
            }
            
            // Custom analytics endpoint (fail silently)
            fetch(`${this.config.apiUrl}/api/chat-widget/analytics`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Widget-ID': this.config.widgetId
                },
                body: JSON.stringify({
                    event: eventName,
                    properties: {
                        ...properties,
                        timestamp: new Date().toISOString(),
                        user_agent: navigator.userAgent,
                        page_url: window.location.href
                    }
                })
            }).catch(() => {}); // Fail silently
            
        } catch (error) {
            // Fail silently for analytics
        }
    }
    
    // Public API methods
    destroy() {
        // Clean up WebSocket
        if (this.socket) {
            this.socket.close();
        }
        
        // Clean up polling
        if (this.pollingInterval) {
            clearInterval(this.pollingInterval);
        }
        
        // Remove widget from DOM
        if (this.container && this.container.parentNode) {
            this.container.parentNode.removeChild(this.container);
        }
        
        this.trackEvent('widget_destroyed');
    }
    
    getState() {
        return {
            isOpen: this.state.isOpen,
            isConnected: this.state.isConnected,
            conversationId: this.state.conversationId,
            visitorId: this.state.visitorId
        };
    }
}

// Auto-initialize if config is provided
if (window.ANZxChatConfig) {
    window.anzxChat = new ANZxChatWidget(window.ANZxChatConfig);
}

// Export for manual initialization
window.ANZxChatWidget = ANZxChatWidget;
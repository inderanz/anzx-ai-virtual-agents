/**
 * ChatWidget Component
 * Main UI component for the chat widget
 */

export class ChatWidget {
  constructor(config, callbacks) {
    this.config = config;
    this.callbacks = callbacks;
    this.isOpen = false;
    this.isMinimized = false;
    this.messages = [];
    
    // DOM elements
    this.container = null;
    this.widget = null;
    this.header = null;
    this.messagesContainer = null;
    this.inputContainer = null;
    this.messageInput = null;
    this.sendButton = null;
    this.toggleButton = null;
    this.typingIndicator = null;
    
    this.createWidget();
    this.attachEventListeners();
  }
  
  /**
   * Create the widget DOM structure
   */
  createWidget() {
    // Create container
    this.container = document.createElement('div');
    this.container.id = 'anzx-chat-widget';
    this.container.className = `anzx-widget-container ${this.config.position}`;
    this.container.setAttribute('role', 'dialog');
    this.container.setAttribute('aria-label', this.config.ariaLabel);
    this.container.setAttribute('aria-hidden', 'true');
    
    // Create toggle button (chat bubble)
    this.toggleButton = document.createElement('button');
    this.toggleButton.className = 'anzx-toggle-button';
    this.toggleButton.setAttribute('aria-label', 'Open chat');
    this.toggleButton.innerHTML = `
      <svg class="anzx-chat-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
      </svg>
      <svg class="anzx-close-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <line x1="18" y1="6" x2="6" y2="18"/>
        <line x1="6" y1="6" x2="18" y2="18"/>
      </svg>
    `;
    
    // Create main widget
    this.widget = document.createElement('div');
    this.widget.className = 'anzx-chat-widget';
    this.widget.innerHTML = `
      <div class="anzx-widget-header">
        <div class="anzx-header-content">
          <div class="anzx-header-avatar">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
              <circle cx="12" cy="7" r="4"/>
            </svg>
          </div>
          <div class="anzx-header-text">
            <div class="anzx-header-title">${this.config.title}</div>
            <div class="anzx-header-subtitle">${this.config.subtitle}</div>
          </div>
        </div>
        <div class="anzx-header-actions">
          <button class="anzx-minimize-button" aria-label="Minimize chat">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="5" y1="12" x2="19" y2="12"/>
            </svg>
          </button>
          <button class="anzx-close-button" aria-label="Close chat">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>
      </div>
      
      <div class="anzx-messages-container">
        <div class="anzx-messages" role="log" aria-live="polite" aria-label="Chat messages">
        </div>
        <div class="anzx-typing-indicator" style="display: none;">
          <div class="anzx-typing-dots">
            <span></span>
            <span></span>
            <span></span>
          </div>
          <span class="anzx-typing-text">AI is typing...</span>
        </div>
      </div>
      
      <div class="anzx-input-container">
        <div class="anzx-input-wrapper">
          <textarea 
            class="anzx-message-input" 
            placeholder="${this.config.placeholder}"
            rows="1"
            aria-label="Type your message"
            maxlength="2000"
          ></textarea>
          <button class="anzx-send-button" aria-label="Send message" disabled>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="22" y1="2" x2="11" y2="13"/>
              <polygon points="22,2 15,22 11,13 2,9 22,2"/>
            </svg>
          </button>
        </div>
        ${this.config.enableFileUpload ? `
          <div class="anzx-file-upload">
            <input type="file" id="anzx-file-input" accept=".pdf,.doc,.docx,.txt" style="display: none;">
            <button class="anzx-file-button" aria-label="Upload file">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                <polyline points="14,2 14,8 20,8"/>
                <line x1="16" y1="13" x2="8" y2="13"/>
                <line x1="16" y1="17" x2="8" y2="17"/>
                <polyline points="10,9 9,9 8,9"/>
              </svg>
            </button>
          </div>
        ` : ''}
      </div>
    `;
    
    // Append to container
    this.container.appendChild(this.toggleButton);
    this.container.appendChild(this.widget);
    
    // Append to body
    document.body.appendChild(this.container);
    
    // Get references to elements
    this.header = this.widget.querySelector('.anzx-widget-header');
    this.messagesContainer = this.widget.querySelector('.anzx-messages');
    this.inputContainer = this.widget.querySelector('.anzx-input-container');
    this.messageInput = this.widget.querySelector('.anzx-message-input');
    this.sendButton = this.widget.querySelector('.anzx-send-button');
    this.typingIndicator = this.widget.querySelector('.anzx-typing-indicator');
  }
  
  /**
   * Attach event listeners
   */
  attachEventListeners() {
    // Toggle button
    this.toggleButton.addEventListener('click', () => {
      if (this.isOpen) {
        this.callbacks.onClose();
      } else {
        this.callbacks.onOpen();
      }
    });
    
    // Close button
    const closeButton = this.widget.querySelector('.anzx-close-button');
    closeButton.addEventListener('click', () => {
      this.callbacks.onClose();
    });
    
    // Minimize button
    const minimizeButton = this.widget.querySelector('.anzx-minimize-button');
    minimizeButton.addEventListener('click', () => {
      this.callbacks.onMinimize();
    });
    
    // Message input
    this.messageInput.addEventListener('input', () => {
      this.handleInputChange();
      this.autoResize();
    });
    
    this.messageInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        this.sendMessage();
      }
    });
    
    // Send button
    this.sendButton.addEventListener('click', () => {
      this.sendMessage();
    });
    
    // File upload (if enabled)
    if (this.config.enableFileUpload) {
      const fileButton = this.widget.querySelector('.anzx-file-button');
      const fileInput = this.widget.querySelector('#anzx-file-input');
      
      fileButton.addEventListener('click', () => {
        fileInput.click();
      });
      
      fileInput.addEventListener('change', (e) => {
        this.handleFileUpload(e.target.files[0]);
      });
    }
    
    // Keyboard navigation
    this.container.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && this.isOpen) {
        this.callbacks.onClose();
      }
    });
    
    // Click outside to close (optional)
    document.addEventListener('click', (e) => {
      if (this.isOpen && !this.container.contains(e.target)) {
        // Don't close on outside click for better UX
        // this.callbacks.onClose();
      }
    });
  }
  
  /**
   * Open the widget
   */
  open() {
    this.isOpen = true;
    this.isMinimized = false;
    this.container.classList.add('anzx-open');
    this.container.setAttribute('aria-hidden', 'false');
    this.toggleButton.setAttribute('aria-label', 'Close chat');
    
    // Focus on input
    setTimeout(() => {
      this.messageInput.focus();
    }, 300);
    
    // Scroll to bottom
    this.scrollToBottom();
  }
  
  /**
   * Close the widget
   */
  close() {
    this.isOpen = false;
    this.isMinimized = false;
    this.container.classList.remove('anzx-open', 'anzx-minimized');
    this.container.setAttribute('aria-hidden', 'true');
    this.toggleButton.setAttribute('aria-label', 'Open chat');
  }
  
  /**
   * Minimize the widget
   */
  minimize() {
    this.isMinimized = true;
    this.container.classList.add('anzx-minimized');
  }
  
  /**
   * Add message to chat
   */
  addMessage(message, save = true) {
    const messageElement = this.createMessageElement(message);
    this.messagesContainer.appendChild(messageElement);
    
    if (save) {
      this.messages.push(message);
    }
    
    // Scroll to bottom
    this.scrollToBottom();
    
    // Announce to screen readers
    this.announceMessage(message);
  }
  
  /**
   * Create message DOM element
   */
  createMessageElement(message) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `anzx-message anzx-message-${message.role}`;
    
    if (message.isError) {
      messageDiv.classList.add('anzx-message-error');
    }
    
    const timestamp = new Date(message.timestamp).toLocaleTimeString([], {
      hour: '2-digit',
      minute: '2-digit'
    });
    
    messageDiv.innerHTML = `
      <div class="anzx-message-content">
        <div class="anzx-message-text">${this.formatMessageContent(message.content)}</div>
        ${message.citations ? this.createCitationsHTML(message.citations) : ''}
        <div class="anzx-message-time">${timestamp}</div>
      </div>
    `;
    
    return messageDiv;
  }
  
  /**
   * Format message content (handle markdown, links, etc.)
   */
  formatMessageContent(content) {
    // Basic formatting - in production, use a proper markdown parser
    return content
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/\n/g, '<br>')
      .replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>');
  }
  
  /**
   * Create citations HTML
   */
  createCitationsHTML(citations) {
    if (!citations || citations.length === 0) {
      return '';
    }
    
    const citationsList = citations.map((citation, index) => 
      `<li><a href="${citation.uri || '#'}" target="_blank" rel="noopener noreferrer">${citation.title || `Source ${index + 1}`}</a></li>`
    ).join('');
    
    return `
      <div class="anzx-message-citations">
        <details>
          <summary>Sources</summary>
          <ul>${citationsList}</ul>
        </details>
      </div>
    `;
  }
  
  /**
   * Send message
   */
  sendMessage() {
    const content = this.messageInput.value.trim();
    if (!content) return;
    
    this.callbacks.onSendMessage(content);
    this.messageInput.value = '';
    this.handleInputChange();
    this.autoResize();
  }
  
  /**
   * Handle input change
   */
  handleInputChange() {
    const hasContent = this.messageInput.value.trim().length > 0;
    this.sendButton.disabled = !hasContent;
    this.sendButton.classList.toggle('anzx-enabled', hasContent);
  }
  
  /**
   * Auto-resize textarea
   */
  autoResize() {
    this.messageInput.style.height = 'auto';
    const maxHeight = 120; // Max 5 lines approximately
    const newHeight = Math.min(this.messageInput.scrollHeight, maxHeight);
    this.messageInput.style.height = newHeight + 'px';
  }
  
  /**
   * Show typing indicator
   */
  showTypingIndicator() {
    this.typingIndicator.style.display = 'flex';
    this.scrollToBottom();
  }
  
  /**
   * Hide typing indicator
   */
  hideTypingIndicator() {
    this.typingIndicator.style.display = 'none';
  }
  
  /**
   * Scroll to bottom
   */
  scrollToBottom() {
    setTimeout(() => {
      const container = this.messagesContainer.parentElement;
      container.scrollTop = container.scrollHeight;
    }, 100);
  }
  
  /**
   * Announce message to screen readers
   */
  announceMessage(message) {
    if (message.role === 'assistant') {
      // Create temporary element for screen reader announcement
      const announcement = document.createElement('div');
      announcement.setAttribute('aria-live', 'polite');
      announcement.setAttribute('aria-atomic', 'true');
      announcement.className = 'anzx-sr-only';
      announcement.textContent = `Assistant: ${message.content}`;
      
      document.body.appendChild(announcement);
      
      setTimeout(() => {
        document.body.removeChild(announcement);
      }, 1000);
    }
  }
  
  /**
   * Handle file upload
   */
  handleFileUpload(file) {
    if (!file) return;
    
    // Validate file
    const maxSize = 10 * 1024 * 1024; // 10MB
    if (file.size > maxSize) {
      this.addMessage({
        role: 'system',
        content: 'File size too large. Please upload a file smaller than 10MB.',
        timestamp: new Date().toISOString(),
        isError: true
      });
      return;
    }
    
    // Add file message
    this.addMessage({
      role: 'user',
      content: `📎 Uploaded: ${file.name}`,
      timestamp: new Date().toISOString(),
      file: {
        name: file.name,
        size: file.size,
        type: file.type
      }
    });
    
    // TODO: Implement file upload to server
    this.callbacks.onSendMessage(`I've uploaded a file: ${file.name}`, { file });
  }
  
  /**
   * Clear all messages
   */
  clearMessages() {
    this.messagesContainer.innerHTML = '';
    this.messages = [];
  }
  
  /**
   * Update configuration
   */
  updateConfig(newConfig) {
    this.config = { ...this.config, ...newConfig };
    
    // Update UI elements
    const title = this.widget.querySelector('.anzx-header-title');
    const subtitle = this.widget.querySelector('.anzx-header-subtitle');
    
    if (title) title.textContent = this.config.title;
    if (subtitle) subtitle.textContent = this.config.subtitle;
    if (this.messageInput) this.messageInput.placeholder = this.config.placeholder;
  }
  
  /**
   * Destroy the widget
   */
  destroy() {
    if (this.container && this.container.parentNode) {
      this.container.parentNode.removeChild(this.container);
    }
  }
}
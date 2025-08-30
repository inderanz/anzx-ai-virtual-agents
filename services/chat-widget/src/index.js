/**
 * ANZx.ai Chat Widget
 * Embeddable chat widget for customer support and AI assistance
 * 
 * Features:
 * - Vanilla JavaScript (no dependencies)
 * - <12KB bundle size
 * - WebSocket with polling fallback
 * - Accessibility compliant
 * - Customizable themes
 * - Mobile responsive
 */

import './styles/widget.css';
import { ChatWidget } from './components/ChatWidget';
import { WebSocketManager } from './services/WebSocketManager';
import { APIClient } from './services/APIClient';
import { StorageManager } from './services/StorageManager';
import { ThemeManager } from './services/ThemeManager';

class ANZxWidget {
  constructor(config = {}) {
    this.config = {
      // Required configuration
      assistantId: config.assistantId || null,
      apiUrl: config.apiUrl || 'https://api.anzx.ai',
      
      // Widget appearance
      position: config.position || 'bottom-right',
      theme: config.theme || 'light',
      primaryColor: config.primaryColor || '#2563eb',
      
      // Behavior
      autoOpen: config.autoOpen || false,
      showWelcomeMessage: config.showWelcomeMessage !== false,
      enableFileUpload: config.enableFileUpload || false,
      enableTypingIndicator: config.enableTypingIndicator !== false,
      
      // Customization
      title: config.title || 'Chat with us',
      subtitle: config.subtitle || 'We\'re here to help',
      welcomeMessage: config.welcomeMessage || 'Hi! How can I help you today?',
      placeholder: config.placeholder || 'Type your message...',
      
      // Advanced
      enableWebSocket: config.enableWebSocket !== false,
      pollingInterval: config.pollingInterval || 3000,
      maxRetries: config.maxRetries || 3,
      
      // Callbacks
      onOpen: config.onOpen || null,
      onClose: config.onClose || null,
      onMessage: config.onMessage || null,
      onError: config.onError || null,
      
      // Accessibility
      ariaLabel: config.ariaLabel || 'Chat widget',
      
      // Development
      debug: config.debug || false,
      
      ...config
    };
    
    this.isInitialized = false;
    this.isOpen = false;
    this.conversationId = null;
    
    // Services
    this.apiClient = null;
    this.wsManager = null;
    this.storage = null;
    this.themeManager = null;
    this.chatWidget = null;
    
    // Initialize if assistant ID is provided
    if (this.config.assistantId) {
      this.init();
    } else {
      this.log('error', 'Assistant ID is required');
    }
  }
  
  /**
   * Initialize the widget
   */
  async init() {
    if (this.isInitialized) {
      this.log('warn', 'Widget already initialized');
      return;
    }
    
    try {
      this.log('info', 'Initializing ANZx Chat Widget', this.config);
      
      // Initialize services
      this.storage = new StorageManager();
      this.themeManager = new ThemeManager(this.config);
      this.apiClient = new APIClient(this.config);
      
      // Initialize WebSocket if enabled
      if (this.config.enableWebSocket) {
        this.wsManager = new WebSocketManager(this.config, this.apiClient);
        this.wsManager.on('message', this.handleWebSocketMessage.bind(this));
        this.wsManager.on('error', this.handleWebSocketError.bind(this));
      }
      
      // Create chat widget
      this.chatWidget = new ChatWidget(this.config, {
        onSendMessage: this.sendMessage.bind(this),
        onOpen: this.open.bind(this),
        onClose: this.close.bind(this),
        onMinimize: this.minimize.bind(this)
      });
      
      // Load conversation history
      await this.loadConversationHistory();
      
      // Apply theme
      this.themeManager.applyTheme();
      
      // Auto-open if configured
      if (this.config.autoOpen) {
        setTimeout(() => this.open(), 1000);
      }
      
      this.isInitialized = true;
      this.log('info', 'Widget initialized successfully');
      
    } catch (error) {
      this.log('error', 'Failed to initialize widget', error);
      this.handleError(error);
    }
  }
  
  /**
   * Open the chat widget
   */
  open() {
    if (!this.isInitialized) {
      this.log('warn', 'Widget not initialized');
      return;
    }
    
    this.isOpen = true;
    this.chatWidget.open();
    
    // Connect WebSocket
    if (this.wsManager) {
      this.wsManager.connect();
    }
    
    // Show welcome message
    if (this.config.showWelcomeMessage && !this.hasMessages()) {
      this.addMessage({
        role: 'assistant',
        content: this.config.welcomeMessage,
        timestamp: new Date().toISOString()
      });
    }
    
    // Callback
    if (this.config.onOpen) {
      this.config.onOpen();
    }
    
    this.log('info', 'Widget opened');
  }
  
  /**
   * Close the chat widget
   */
  close() {
    this.isOpen = false;
    this.chatWidget.close();
    
    // Disconnect WebSocket
    if (this.wsManager) {
      this.wsManager.disconnect();
    }
    
    // Callback
    if (this.config.onClose) {
      this.config.onClose();
    }
    
    this.log('info', 'Widget closed');
  }
  
  /**
   * Minimize the chat widget
   */
  minimize() {
    this.chatWidget.minimize();
    this.log('info', 'Widget minimized');
  }
  
  /**
   * Send a message
   */
  async sendMessage(content, options = {}) {
    if (!content || !content.trim()) {
      return;
    }
    
    const message = {
      role: 'user',
      content: content.trim(),
      timestamp: new Date().toISOString(),
      ...options
    };
    
    // Add user message to UI
    this.addMessage(message);
    
    // Show typing indicator
    if (this.config.enableTypingIndicator) {
      this.chatWidget.showTypingIndicator();
    }
    
    try {
      // Send via WebSocket if available, otherwise use HTTP
      if (this.wsManager && this.wsManager.isConnected()) {
        await this.wsManager.sendMessage(message);
      } else {
        await this.sendMessageHTTP(message);
      }
      
    } catch (error) {
      this.log('error', 'Failed to send message', error);
      this.handleError(error);
      
      // Add error message
      this.addMessage({
        role: 'system',
        content: 'Sorry, I\'m having trouble connecting. Please try again.',
        timestamp: new Date().toISOString(),
        isError: true
      });
    } finally {
      // Hide typing indicator
      if (this.config.enableTypingIndicator) {
        this.chatWidget.hideTypingIndicator();
      }
    }
  }
  
  /**
   * Send message via HTTP API
   */
  async sendMessageHTTP(message) {
    const response = await this.apiClient.sendMessage({
      assistantId: this.config.assistantId,
      conversationId: this.conversationId,
      message: message.content,
      channel: 'widget'
    });
    
    if (response.conversationId) {
      this.conversationId = response.conversationId;
      this.storage.setConversationId(this.conversationId);
    }
    
    // Add assistant response
    if (response.response) {
      this.addMessage({
        role: 'assistant',
        content: response.response,
        timestamp: new Date().toISOString(),
        messageId: response.messageId,
        citations: response.citations
      });
    }
  }
  
  /**
   * Handle WebSocket message
   */
  handleWebSocketMessage(data) {
    this.log('debug', 'WebSocket message received', data);
    
    if (data.type === 'message') {
      this.addMessage({
        role: 'assistant',
        content: data.content,
        timestamp: new Date().toISOString(),
        messageId: data.messageId,
        citations: data.citations
      });
    } else if (data.type === 'typing') {
      if (data.isTyping) {
        this.chatWidget.showTypingIndicator();
      } else {
        this.chatWidget.hideTypingIndicator();
      }
    } else if (data.type === 'error') {
      this.handleError(new Error(data.message));
    }
    
    // Update conversation ID
    if (data.conversationId) {
      this.conversationId = data.conversationId;
      this.storage.setConversationId(this.conversationId);
    }
  }
  
  /**
   * Handle WebSocket error
   */
  handleWebSocketError(error) {
    this.log('error', 'WebSocket error', error);
    // Fallback to HTTP polling if WebSocket fails
  }
  
  /**
   * Add message to chat
   */
  addMessage(message) {
    this.chatWidget.addMessage(message);
    this.storage.addMessage(message);
    
    // Callback
    if (this.config.onMessage) {
      this.config.onMessage(message);
    }
  }
  
  /**
   * Check if there are any messages
   */
  hasMessages() {
    return this.storage.getMessages().length > 0;
  }
  
  /**
   * Load conversation history
   */
  async loadConversationHistory() {
    try {
      // Get stored conversation ID
      this.conversationId = this.storage.getConversationId();
      
      // Load stored messages
      const messages = this.storage.getMessages();
      if (messages.length > 0) {
        messages.forEach(message => {
          this.chatWidget.addMessage(message, false); // Don't save again
        });
      }
      
      this.log('info', `Loaded ${messages.length} messages from history`);
      
    } catch (error) {
      this.log('error', 'Failed to load conversation history', error);
    }
  }
  
  /**
   * Clear conversation history
   */
  clearHistory() {
    this.storage.clearMessages();
    this.chatWidget.clearMessages();
    this.conversationId = null;
    this.storage.setConversationId(null);
    this.log('info', 'Conversation history cleared');
  }
  
  /**
   * Update widget configuration
   */
  updateConfig(newConfig) {
    this.config = { ...this.config, ...newConfig };
    
    // Update theme if changed
    if (newConfig.theme || newConfig.primaryColor) {
      this.themeManager.updateConfig(this.config);
      this.themeManager.applyTheme();
    }
    
    // Update chat widget
    if (this.chatWidget) {
      this.chatWidget.updateConfig(this.config);
    }
    
    this.log('info', 'Configuration updated', newConfig);
  }
  
  /**
   * Handle errors
   */
  handleError(error) {
    this.log('error', 'Widget error', error);
    
    if (this.config.onError) {
      this.config.onError(error);
    }
  }
  
  /**
   * Logging utility
   */
  log(level, message, data = null) {
    if (!this.config.debug && level === 'debug') {
      return;
    }
    
    const timestamp = new Date().toISOString();
    const logMessage = `[ANZx Widget ${timestamp}] ${message}`;
    
    if (data) {
      console[level](logMessage, data);
    } else {
      console[level](logMessage);
    }
  }
  
  /**
   * Destroy the widget
   */
  destroy() {
    if (this.wsManager) {
      this.wsManager.disconnect();
    }
    
    if (this.chatWidget) {
      this.chatWidget.destroy();
    }
    
    this.isInitialized = false;
    this.log('info', 'Widget destroyed');
  }
}

// Auto-initialize if config is provided in window
if (typeof window !== 'undefined') {
  // Check for global configuration
  if (window.anzxConfig) {
    window.anzxWidget = new ANZxWidget(window.anzxConfig);
  }
  
  // Expose constructor globally
  window.ANZxWidget = ANZxWidget;
}

export default ANZxWidget;
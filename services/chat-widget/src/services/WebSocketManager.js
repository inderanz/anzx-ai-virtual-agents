/**
 * WebSocket Manager
 * Handles real-time communication with fallback to polling
 */

export class WebSocketManager {
  constructor(config, apiClient) {
    this.config = config;
    this.apiClient = apiClient;
    this.ws = null;
    this.isConnected = false;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = this.config.maxRetries || 3;
    this.reconnectDelay = 1000;
    this.heartbeatInterval = null;
    this.messageQueue = [];
    this.eventListeners = {};
    
    // WebSocket URL
    this.wsUrl = this.config.apiUrl.replace('http', 'ws') + '/ws/chat';
  }
  
  /**
   * Connect to WebSocket
   */
  connect() {
    if (this.isConnected || this.ws) {
      return;
    }
    
    try {
      this.log('info', 'Connecting to WebSocket', this.wsUrl);
      
      this.ws = new WebSocket(this.wsUrl);
      
      this.ws.onopen = this.handleOpen.bind(this);
      this.ws.onmessage = this.handleMessage.bind(this);
      this.ws.onclose = this.handleClose.bind(this);
      this.ws.onerror = this.handleError.bind(this);
      
    } catch (error) {
      this.log('error', 'WebSocket connection failed', error);
      this.emit('error', error);
    }
  }
  
  /**
   * Disconnect from WebSocket
   */
  disconnect() {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
    
    if (this.ws) {
      this.ws.close(1000, 'Client disconnect');
      this.ws = null;
    }
    
    this.isConnected = false;
    this.reconnectAttempts = 0;
  }
  
  /**
   * Handle WebSocket open
   */
  handleOpen() {
    this.log('info', 'WebSocket connected');
    this.isConnected = true;
    this.reconnectAttempts = 0;
    
    // Send authentication
    this.send({
      type: 'auth',
      assistantId: this.config.assistantId,
      channel: 'widget'
    });
    
    // Start heartbeat
    this.startHeartbeat();
    
    // Send queued messages
    this.flushMessageQueue();
  }
  
  /**
   * Handle WebSocket message
   */
  handleMessage(event) {
    try {
      const data = JSON.parse(event.data);
      this.log('debug', 'WebSocket message received', data);
      
      if (data.type === 'pong') {
        // Heartbeat response
        return;
      }
      
      this.emit('message', data);
      
    } catch (error) {
      this.log('error', 'Failed to parse WebSocket message', error);
    }
  }
  
  /**
   * Handle WebSocket close
   */
  handleClose(event) {
    this.log('info', 'WebSocket disconnected', event.code, event.reason);
    this.isConnected = false;
    
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
    
    // Attempt reconnection if not intentional close
    if (event.code !== 1000 && this.reconnectAttempts < this.maxReconnectAttempts) {
      this.attemptReconnect();
    }
  }
  
  /**
   * Handle WebSocket error
   */
  handleError(error) {
    this.log('error', 'WebSocket error', error);
    this.emit('error', error);
  }
  
  /**
   * Attempt to reconnect
   */
  attemptReconnect() {
    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
    
    this.log('info', `Attempting reconnect ${this.reconnectAttempts}/${this.maxReconnectAttempts} in ${delay}ms`);
    
    setTimeout(() => {
      if (this.reconnectAttempts <= this.maxReconnectAttempts) {
        this.ws = null;
        this.connect();
      }
    }, delay);
  }
  
  /**
   * Send message via WebSocket
   */
  async sendMessage(message) {
    const payload = {
      type: 'message',
      assistantId: this.config.assistantId,
      content: message.content,
      timestamp: message.timestamp
    };
    
    if (this.isConnected) {
      this.send(payload);
    } else {
      // Queue message for when connection is restored
      this.messageQueue.push(payload);
      
      // Fallback to HTTP if WebSocket is not available
      this.log('warn', 'WebSocket not connected, falling back to HTTP');
      throw new Error('WebSocket not connected');
    }
  }
  
  /**
   * Send data via WebSocket
   */
  send(data) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    } else {
      this.log('warn', 'WebSocket not ready, queueing message');
      this.messageQueue.push(data);
    }
  }
  
  /**
   * Flush queued messages
   */
  flushMessageQueue() {
    while (this.messageQueue.length > 0) {
      const message = this.messageQueue.shift();
      this.send(message);
    }
  }
  
  /**
   * Start heartbeat to keep connection alive
   */
  startHeartbeat() {
    this.heartbeatInterval = setInterval(() => {
      if (this.isConnected) {
        this.send({ type: 'ping' });
      }
    }, 30000); // 30 seconds
  }
  
  /**
   * Check if WebSocket is connected
   */
  isConnected() {
    return this.isConnected && this.ws && this.ws.readyState === WebSocket.OPEN;
  }
  
  /**
   * Add event listener
   */
  on(event, callback) {
    if (!this.eventListeners[event]) {
      this.eventListeners[event] = [];
    }
    this.eventListeners[event].push(callback);
  }
  
  /**
   * Remove event listener
   */
  off(event, callback) {
    if (this.eventListeners[event]) {
      this.eventListeners[event] = this.eventListeners[event].filter(cb => cb !== callback);
    }
  }
  
  /**
   * Emit event
   */
  emit(event, data) {
    if (this.eventListeners[event]) {
      this.eventListeners[event].forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          this.log('error', 'Event listener error', error);
        }
      });
    }
  }
  
  /**
   * Logging utility
   */
  log(level, message, ...args) {
    if (this.config.debug || level === 'error') {
      console[level](`[WebSocket] ${message}`, ...args);
    }
  }
}
/**
 * API Client
 * Handles HTTP communication with the ANZx.ai API
 */

export class APIClient {
  constructor(config) {
    this.config = config;
    this.baseUrl = config.apiUrl;
    this.timeout = config.timeout || 30000;
  }
  
  /**
   * Send message to assistant
   */
  async sendMessage(data) {
    const response = await this.request('POST', '/api/chat', {
      assistant_id: data.assistantId,
      conversation_id: data.conversationId,
      message: data.message,
      channel: data.channel || 'widget',
      metadata: {
        user_agent: navigator.userAgent,
        timestamp: new Date().toISOString(),
        widget_version: '1.0.0'
      }
    });
    
    return response;
  }
  
  /**
   * Get conversation history
   */
  async getConversationHistory(conversationId) {
    const response = await this.request('GET', `/api/conversations/${conversationId}/messages`);
    return response;
  }
  
  /**
   * Upload file
   */
  async uploadFile(file, conversationId) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('conversation_id', conversationId);
    
    const response = await this.request('POST', '/api/files/upload', formData, {
      'Content-Type': undefined // Let browser set multipart boundary
    });
    
    return response;
  }
  
  /**
   * Get assistant info
   */
  async getAssistantInfo(assistantId) {
    const response = await this.request('GET', `/api/assistants/${assistantId}`);
    return response;
  }
  
  /**
   * Generic request method
   */
  async request(method, endpoint, data = null, customHeaders = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    
    const headers = {
      'Content-Type': 'application/json',
      'X-Widget-Version': '1.0.0',
      ...customHeaders
    };
    
    // Remove Content-Type for FormData
    if (data instanceof FormData) {
      delete headers['Content-Type'];
    }
    
    const options = {
      method,
      headers,
      timeout: this.timeout
    };
    
    if (data && method !== 'GET') {
      options.body = data instanceof FormData ? data : JSON.stringify(data);
    }
    
    try {
      this.log('debug', `${method} ${url}`, data);
      
      const response = await this.fetchWithTimeout(url, options);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new APIError(
          errorData.message || `HTTP ${response.status}`,
          response.status,
          errorData
        );
      }
      
      const result = await response.json();
      this.log('debug', `${method} ${url} response`, result);
      
      return result;
      
    } catch (error) {
      this.log('error', `API request failed: ${method} ${url}`, error);
      
      if (error instanceof APIError) {
        throw error;
      }
      
      // Network or other errors
      throw new APIError(
        error.message || 'Network error',
        0,
        { originalError: error }
      );
    }
  }
  
  /**
   * Fetch with timeout
   */
  async fetchWithTimeout(url, options) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);
    
    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);
      return response;
      
    } catch (error) {
      clearTimeout(timeoutId);
      
      if (error.name === 'AbortError') {
        throw new Error('Request timeout');
      }
      
      throw error;
    }
  }
  
  /**
   * Logging utility
   */
  log(level, message, ...args) {
    if (this.config.debug || level === 'error') {
      console[level](`[API] ${message}`, ...args);
    }
  }
}

/**
 * API Error class
 */
export class APIError extends Error {
  constructor(message, status, data = {}) {
    super(message);
    this.name = 'APIError';
    this.status = status;
    this.data = data;
  }
  
  get isNetworkError() {
    return this.status === 0;
  }
  
  get isServerError() {
    return this.status >= 500;
  }
  
  get isClientError() {
    return this.status >= 400 && this.status < 500;
  }
}
/**
 * Storage Manager
 * Handles local storage for conversation history and settings
 */

export class StorageManager {
  constructor() {
    this.storageKey = 'anzx-chat-widget';
    this.maxMessages = 100; // Limit stored messages
    this.maxAge = 7 * 24 * 60 * 60 * 1000; // 7 days in milliseconds
  }
  
  /**
   * Get conversation ID
   */
  getConversationId() {
    try {
      const data = this.getData();
      return data.conversationId || null;
    } catch (error) {
      console.warn('[Storage] Failed to get conversation ID', error);
      return null;
    }
  }
  
  /**
   * Set conversation ID
   */
  setConversationId(conversationId) {
    try {
      const data = this.getData();
      data.conversationId = conversationId;
      data.lastUpdated = Date.now();
      this.setData(data);
    } catch (error) {
      console.warn('[Storage] Failed to set conversation ID', error);
    }
  }
  
  /**
   * Get messages
   */
  getMessages() {
    try {
      const data = this.getData();
      
      // Filter out old messages
      const cutoff = Date.now() - this.maxAge;
      const messages = (data.messages || []).filter(message => {
        const messageTime = new Date(message.timestamp).getTime();
        return messageTime > cutoff;
      });
      
      return messages;
    } catch (error) {
      console.warn('[Storage] Failed to get messages', error);
      return [];
    }
  }
  
  /**
   * Add message
   */
  addMessage(message) {
    try {
      const data = this.getData();
      
      if (!data.messages) {
        data.messages = [];
      }
      
      // Add message
      data.messages.push({
        role: message.role,
        content: message.content,
        timestamp: message.timestamp,
        messageId: message.messageId,
        citations: message.citations,
        isError: message.isError
      });
      
      // Limit number of stored messages
      if (data.messages.length > this.maxMessages) {
        data.messages = data.messages.slice(-this.maxMessages);
      }
      
      data.lastUpdated = Date.now();
      this.setData(data);
      
    } catch (error) {
      console.warn('[Storage] Failed to add message', error);
    }
  }
  
  /**
   * Clear messages
   */
  clearMessages() {
    try {
      const data = this.getData();
      data.messages = [];
      data.lastUpdated = Date.now();
      this.setData(data);
    } catch (error) {
      console.warn('[Storage] Failed to clear messages', error);
    }
  }
  
  /**
   * Get widget settings
   */
  getSettings() {
    try {
      const data = this.getData();
      return data.settings || {};
    } catch (error) {
      console.warn('[Storage] Failed to get settings', error);
      return {};
    }
  }
  
  /**
   * Set widget settings
   */
  setSettings(settings) {
    try {
      const data = this.getData();
      data.settings = { ...data.settings, ...settings };
      data.lastUpdated = Date.now();
      this.setData(data);
    } catch (error) {
      console.warn('[Storage] Failed to set settings', error);
    }
  }
  
  /**
   * Get all data
   */
  getData() {
    try {
      if (!this.isStorageAvailable()) {
        return {};
      }
      
      const stored = localStorage.getItem(this.storageKey);
      if (!stored) {
        return {};
      }
      
      const data = JSON.parse(stored);
      
      // Check if data is too old
      if (data.lastUpdated && (Date.now() - data.lastUpdated) > this.maxAge) {
        this.clearData();
        return {};
      }
      
      return data;
      
    } catch (error) {
      console.warn('[Storage] Failed to get data', error);
      return {};
    }
  }
  
  /**
   * Set all data
   */
  setData(data) {
    try {
      if (!this.isStorageAvailable()) {
        return;
      }
      
      data.lastUpdated = Date.now();
      localStorage.setItem(this.storageKey, JSON.stringify(data));
      
    } catch (error) {
      console.warn('[Storage] Failed to set data', error);
      
      // If storage is full, try to clear old data
      if (error.name === 'QuotaExceededError') {
        this.clearOldData();
        try {
          localStorage.setItem(this.storageKey, JSON.stringify(data));
        } catch (retryError) {
          console.error('[Storage] Failed to set data after cleanup', retryError);
        }
      }
    }
  }
  
  /**
   * Clear all data
   */
  clearData() {
    try {
      if (this.isStorageAvailable()) {
        localStorage.removeItem(this.storageKey);
      }
    } catch (error) {
      console.warn('[Storage] Failed to clear data', error);
    }
  }
  
  /**
   * Clear old data to free up space
   */
  clearOldData() {
    try {
      const data = this.getData();
      
      // Keep only recent messages
      if (data.messages && data.messages.length > 20) {
        data.messages = data.messages.slice(-20);
      }
      
      // Remove old settings
      delete data.settings;
      
      this.setData(data);
      
    } catch (error) {
      console.warn('[Storage] Failed to clear old data', error);
    }
  }
  
  /**
   * Check if localStorage is available
   */
  isStorageAvailable() {
    try {
      const test = '__storage_test__';
      localStorage.setItem(test, test);
      localStorage.removeItem(test);
      return true;
    } catch (error) {
      return false;
    }
  }
  
  /**
   * Get storage usage info
   */
  getStorageInfo() {
    try {
      if (!this.isStorageAvailable()) {
        return { available: false };
      }
      
      const data = this.getData();
      const dataSize = JSON.stringify(data).length;
      
      return {
        available: true,
        dataSize,
        messageCount: (data.messages || []).length,
        conversationId: data.conversationId,
        lastUpdated: data.lastUpdated
      };
      
    } catch (error) {
      return { available: false, error: error.message };
    }
  }
}
/**
 * JSON Logger for Cricket Bridge
 * Structured logging with privacy protection and OpenTelemetry integration
 */

import winston from 'winston';
import { LoggerConfig } from './types';
import { metrics, trace } from '@opentelemetry/api';

class CricketLogger {
  private logger: winston.Logger;
  private messageCache: Set<string> = new Set();
  private readonly MAX_CACHE_SIZE = 1000;
  
  // Metrics tracking
  private messageCount = 0;
  private forwardCount = 0;
  private replyCount = 0;
  private errorCount = 0;
  private totalForwardMs = 0;
  private totalAgentLatencyMs = 0;
  
  // OpenTelemetry metrics
  private messageCounter: any;
  private forwardCounter: any;
  private replyCounter: any;
  private errorCounter: any;
  private forwardLatencyHistogram: any;
  private agentLatencyHistogram: any;

  constructor(config: LoggerConfig) {
    this.logger = winston.createLogger({
      level: config.level,
      format: winston.format.combine(
        winston.format.timestamp(),
        winston.format.errors({ stack: true }),
        winston.format.json()
      ),
      transports: [
        new winston.transports.Console({
          format: winston.format.combine(
            winston.format.colorize(),
            winston.format.simple()
          )
        })
      ]
    });
    
    // Setup OpenTelemetry metrics
    this.setupMetrics();
  }
  
  private setupMetrics() {
    try {
      const meter = metrics.getMeter('cricket-bridge');
      
      this.messageCounter = meter.createCounter('cricket_bridge_messages_total', {
        description: 'Total number of messages received'
      });
      
      this.forwardCounter = meter.createCounter('cricket_bridge_forwards_total', {
        description: 'Total number of messages forwarded to cricket agent'
      });
      
      this.replyCounter = meter.createCounter('cricket_bridge_replies_total', {
        description: 'Total number of replies sent'
      });
      
      this.errorCounter = meter.createCounter('cricket_bridge_errors_total', {
        description: 'Total number of errors'
      });
      
      this.forwardLatencyHistogram = meter.createHistogram('cricket_bridge_forward_duration_ms', {
        description: 'Duration of message forwarding in milliseconds'
      });
      
      this.agentLatencyHistogram = meter.createHistogram('cricket_bridge_agent_latency_ms', {
        description: 'Agent response latency in milliseconds'
      });
    } catch (error) {
      this.logger.warn('Failed to setup OpenTelemetry metrics', { error: error.message });
    }
  }

  /**
   * Log connection events
   */
  connect(jid?: string) {
    this.logger.info('whatsapp_connected', {
      event: 'connect',
      me: jid ? this.anonymizeJid(jid) : undefined,
      timestamp: new Date().toISOString()
    });
  }

  disconnect(reason?: string) {
    this.logger.info('whatsapp_disconnected', {
      event: 'disconnect',
      reason,
      timestamp: new Date().toISOString()
    });
  }

  /**
   * Log message received (without content)
   */
  messageReceived(chatId: string, sender: string, messageLength: number, isGroup: boolean) {
    this.messageCount++;
    
    // Record OpenTelemetry metrics
    try {
      this.messageCounter?.add(1, {
        chatType: isGroup ? 'group' : 'individual',
        source: 'whatsapp'
      });
    } catch (error) {
      // Ignore metrics errors
    }
    
    this.logger.info('message_received', {
      event: 'message_received',
      chatId: this.anonymizeJid(chatId),
      sender: this.anonymizeJid(sender),
      messageLength,
      isGroup,
      timestamp: new Date().toISOString()
    });
  }

  /**
   * Log message ignored (filtered out)
   */
  messageIgnored(chatId: string, reason: string) {
    this.logger.info('message_ignored', {
      event: 'message_ignored',
      chatId: this.anonymizeJid(chatId),
      reason,
      timestamp: new Date().toISOString()
    });
  }

  /**
   * Log message forwarded to cricket agent
   */
  messageForwarded(chatId: string, messageLength: number, forwardMs: number) {
    this.forwardCount++;
    this.totalForwardMs += forwardMs;
    
    // Record OpenTelemetry metrics
    try {
      this.forwardCounter?.add(1, {
        source: 'whatsapp',
        destination: 'cricket_agent'
      });
      this.forwardLatencyHistogram?.record(forwardMs, {
        operation: 'forward_message'
      });
    } catch (error) {
      // Ignore metrics errors
    }
    
    this.logger.info('message_forwarded', {
      event: 'message_forwarded',
      chatId: this.anonymizeJid(chatId),
      messageLength,
      forwardMs,
      timestamp: new Date().toISOString()
    });
  }

  /**
   * Log reply sent back to WhatsApp
   */
  replySent(chatId: string, replyLength: number, agentLatencyMs: number) {
    this.replyCount++;
    this.totalAgentLatencyMs += agentLatencyMs;
    
    // Record OpenTelemetry metrics
    try {
      this.replyCounter?.add(1, {
        source: 'cricket_agent',
        destination: 'whatsapp'
      });
      this.agentLatencyHistogram?.record(agentLatencyMs, {
        operation: 'agent_response'
      });
    } catch (error) {
      // Ignore metrics errors
    }
    
    this.logger.info('reply_sent', {
      event: 'reply_sent',
      chatId: this.anonymizeJid(chatId),
      replyLength,
      agentLatencyMs,
      timestamp: new Date().toISOString()
    });
  }

  /**
   * Log errors with context
   */
  error(message: string, error: Error, context?: Record<string, any>) {
    this.errorCount++;
    
    // Record OpenTelemetry metrics
    try {
      this.errorCounter?.add(1, {
        errorType: error.constructor.name,
        source: 'cricket_bridge'
      });
    } catch (metricsError) {
      // Ignore metrics errors
    }
    
    this.logger.error('error', {
      event: 'error',
      message,
      error: error.message,
      stack: error.stack,
      context,
      timestamp: new Date().toISOString()
    });
  }

  /**
   * Log rate limiting
   */
  rateLimited(chatId: string, limit: number, window: number) {
    this.logger.warn('rate_limited', {
      event: 'rate_limited',
      chatId: this.anonymizeJid(chatId),
      limit,
      window,
      timestamp: new Date().toISOString()
    });
  }

  /**
   * Log session operations
   */
  sessionLoaded(source: string) {
    this.logger.info('session_loaded', {
      event: 'session_loaded',
      source,
      timestamp: new Date().toISOString()
    });
  }

  sessionSaved(source: string) {
    this.logger.info('session_saved', {
      event: 'session_saved',
      source,
      timestamp: new Date().toISOString()
    });
  }

  /**
   * Log health checks
   */
  healthCheck(connected: boolean, me?: string) {
    this.logger.info('health_check', {
      event: 'health_check',
      connected,
      me: me ? this.anonymizeJid(me) : undefined,
      timestamp: new Date().toISOString()
    });
  }

  /**
   * Anonymize JID for privacy
   */
  private anonymizeJid(jid: string): string {
    if (!jid) return 'unknown';
    
    // For groups, keep the group identifier but anonymize the number
    if (jid.includes('@g.us')) {
      const parts = jid.split('@');
      const groupId = parts[0];
      const hash = this.simpleHash(groupId);
      return `${hash}@g.us`;
    }
    
    // For individual chats, anonymize the number
    const parts = jid.split('@');
    const number = parts[0];
    const hash = this.simpleHash(number);
    return `${hash}@s.whatsapp.net`;
  }

  /**
   * Simple hash function for anonymization
   */
  private simpleHash(str: string): string {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32-bit integer
    }
    return Math.abs(hash).toString(36).substring(0, 8);
  }

  /**
   * Check if message is duplicate (deduplication)
   */
  isDuplicate(messageId: string): boolean {
    if (this.messageCache.has(messageId)) {
      return true;
    }
    
    this.messageCache.add(messageId);
    
    // Clean up cache if it gets too large
    if (this.messageCache.size > this.MAX_CACHE_SIZE) {
      const entries = Array.from(this.messageCache);
      this.messageCache.clear();
      // Keep only the most recent half
      entries.slice(-this.MAX_CACHE_SIZE / 2).forEach(id => this.messageCache.add(id));
    }
    
    return false;
  }

  /**
   * Get comprehensive metrics
   */
  getMetrics() {
    const avgForwardMs = this.forwardCount > 0 ? this.totalForwardMs / this.forwardCount : 0;
    const avgAgentLatencyMs = this.replyCount > 0 ? this.totalAgentLatencyMs / this.replyCount : 0;
    
    return {
      messageCount: this.messageCount,
      forwardCount: this.forwardCount,
      replyCount: this.replyCount,
      errorCount: this.errorCount,
      avgForwardMs: Math.round(avgForwardMs * 100) / 100,
      avgAgentLatencyMs: Math.round(avgAgentLatencyMs * 100) / 100,
      totalForwardMs: this.totalForwardMs,
      totalAgentLatencyMs: this.totalAgentLatencyMs
    };
  }

  /**
   * Get the underlying winston logger for direct use
   */
  getWinstonLogger(): winston.Logger {
    return this.logger;
  }
}

export default CricketLogger;

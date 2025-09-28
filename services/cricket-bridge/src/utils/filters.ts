/**
 * Message filtering utilities
 * Handles group filtering, prefix/mention detection, and deduplication
 */

import { GroupFilter, RateLimitEntry } from '../types';
import CricketLogger from '../logger';

export class MessageFilters {
  private allowedGroups: Set<string>;
  private triggerPrefix: string;
  private mentionTrigger: boolean;
  private logger: CricketLogger;
  private rateLimitMap: Map<string, RateLimitEntry> = new Map();
  private messageCache: Set<string> = new Set();
  private readonly MAX_CACHE_SIZE = 1000;
  private readonly RATE_LIMIT_WINDOW = 2000; // 2 seconds
  private readonly RATE_LIMIT_BURST = 3; // 3 messages per window

  constructor(filter: GroupFilter, logger: CricketLogger) {
    this.allowedGroups = new Set(filter.allowedGroups || []);
    this.triggerPrefix = filter.triggerPrefix;
    this.mentionTrigger = filter.mentionTrigger;
    this.logger = logger;
  }

  /**
   * Check if message should be processed
   */
  shouldProcessMessage(
    chatId: string,
    messageText: string,
    isGroup: boolean,
    messageId: string,
    botJid?: string
  ): boolean {
    // Check for duplicates
    if (this.isDuplicate(messageId)) {
      this.logger.getWinstonLogger().debug('Duplicate message ignored', { messageId });
      return false;
    }

    // Check group filtering
    if (isGroup && this.allowedGroups.size > 0 && !this.allowedGroups.has(chatId)) {
      this.logger.messageIgnored(chatId, 'group_not_allowed');
      return false;
    }

    // Check rate limiting
    if (!this.checkRateLimit(chatId)) {
      this.logger.rateLimited(chatId, this.RATE_LIMIT_BURST, this.RATE_LIMIT_WINDOW);
      return false;
    }

    // Check trigger conditions
    if (!this.hasTrigger(messageText, isGroup, botJid)) {
      return false;
    }

    return true;
  }

  /**
   * Check if message has a valid trigger
   */
  private hasTrigger(messageText: string, isGroup: boolean, botJid?: string): boolean {
    const text = messageText.toLowerCase().trim();

    // Check for prefix trigger
    if (text.startsWith(this.triggerPrefix.toLowerCase())) {
      return true;
    }

    // Check for mention trigger in groups
    if (isGroup && this.mentionTrigger && botJid) {
      // Check if message mentions the bot
      const mentionPattern = new RegExp(`@${botJid.replace('@s.whatsapp.net', '')}`, 'i');
      if (mentionPattern.test(messageText)) {
        return true;
      }
    }

    return false;
  }

  /**
   * Clean message text by removing triggers
   */
  cleanMessage(messageText: string, botJid?: string): string {
    let cleanText = messageText.trim();

    // Remove prefix
    if (cleanText.toLowerCase().startsWith(this.triggerPrefix.toLowerCase())) {
      cleanText = cleanText.substring(this.triggerPrefix.length).trim();
    }

    // Remove mention
    if (botJid) {
      const mentionPattern = new RegExp(`@${botJid.replace('@s.whatsapp.net', '')}\\s*`, 'i');
      cleanText = cleanText.replace(mentionPattern, '').trim();
    }

    return cleanText;
  }

  /**
   * Check for duplicate messages
   */
  private isDuplicate(messageId: string): boolean {
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
   * Check rate limiting per group
   */
  private checkRateLimit(chatId: string): boolean {
    const now = Date.now();
    const entry = this.rateLimitMap.get(chatId);

    if (!entry) {
      this.rateLimitMap.set(chatId, {
        count: 1,
        resetTime: now + this.RATE_LIMIT_WINDOW
      });
      return true;
    }

    // Reset if window has passed
    if (now > entry.resetTime) {
      entry.count = 1;
      entry.resetTime = now + this.RATE_LIMIT_WINDOW;
      return true;
    }

    // Check if within limit
    if (entry.count < this.RATE_LIMIT_BURST) {
      entry.count++;
      return true;
    }

    return false;
  }

  /**
   * Get filter statistics
   */
  getStats(): {
    allowedGroups: number;
    messageCache: number;
    rateLimitEntries: number;
  } {
    return {
      allowedGroups: this.allowedGroups.size,
      messageCache: this.messageCache.size,
      rateLimitEntries: this.rateLimitMap.size
    };
  }

  /**
   * Clear caches (useful for testing)
   */
  clearCaches(): void {
    this.messageCache.clear();
    this.rateLimitMap.clear();
  }

  /**
   * Update allowed groups
   */
  updateAllowedGroups(groups: string[]): void {
    this.allowedGroups.clear();
    groups.forEach(group => this.allowedGroups.add(group));
  }

  /**
   * Check if group is allowed
   */
  isGroupAllowed(chatId: string): boolean {
    if (this.allowedGroups.size === 0) return true;
    return this.allowedGroups.has(chatId);
  }
}

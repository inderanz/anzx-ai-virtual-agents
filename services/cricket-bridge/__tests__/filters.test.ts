/**
 * Tests for message filters
 */

import { MessageFilters } from '../src/utils/filters';
import CricketLogger from '../src/logger';

describe('MessageFilters', () => {
  let filters: MessageFilters;
  let mockLogger: CricketLogger;

  beforeEach(() => {
    mockLogger = {
      getWinstonLogger: jest.fn().mockReturnValue({
        debug: jest.fn(),
        info: jest.fn(),
        warn: jest.fn(),
        error: jest.fn()
      }),
      messageIgnored: jest.fn(),
      rateLimited: jest.fn()
    } as any;

    filters = new MessageFilters(
      {
        allowedGroups: ['120363123456789012@g.us', '120363987654321098@g.us'],
        triggerPrefix: '!cscc',
        mentionTrigger: true
      },
      mockLogger
    );
  });

  describe('shouldProcessMessage', () => {
    it('should process message with valid trigger prefix', () => {
      const result = filters.shouldProcessMessage(
        '120363123456789012@g.us',
        '!cscc list fixtures',
        true,
        'msg123',
        'bot@s.whatsapp.net'
      );
      expect(result).toBe(true);
    });

    it('should process message with mention trigger', () => {
      const result = filters.shouldProcessMessage(
        '120363123456789012@g.us',
        '@bot list fixtures',
        true,
        'msg124',
        'bot@s.whatsapp.net'
      );
      expect(result).toBe(true);
    });

    it('should reject message without trigger', () => {
      const result = filters.shouldProcessMessage(
        '120363123456789012@g.us',
        'hello world',
        true,
        'msg125',
        'bot@s.whatsapp.net'
      );
      expect(result).toBe(false);
    });

    it('should reject message from non-allowed group', () => {
      const result = filters.shouldProcessMessage(
        '120363999999999999@g.us',
        '!cscc list fixtures',
        true,
        'msg126',
        'bot@s.whatsapp.net'
      );
      expect(result).toBe(false);
      expect(mockLogger.messageIgnored).toHaveBeenCalledWith(
        '120363999999999999@g.us',
        'group_not_allowed'
      );
    });

    it('should reject duplicate message', () => {
      const messageId = 'msg127';
      
      // First message should be processed
      const result1 = filters.shouldProcessMessage(
        '120363123456789012@g.us',
        '!cscc list fixtures',
        true,
        messageId,
        'bot@s.whatsapp.net'
      );
      expect(result1).toBe(true);

      // Second message with same ID should be rejected
      const result2 = filters.shouldProcessMessage(
        '120363123456789012@g.us',
        '!cscc list fixtures',
        true,
        messageId,
        'bot@s.whatsapp.net'
      );
      expect(result2).toBe(false);
    });

    it('should allow messages when no groups are specified', () => {
      const filtersNoGroups = new MessageFilters(
        {
          allowedGroups: [],
          triggerPrefix: '!cscc',
          mentionTrigger: true
        },
        mockLogger
      );

      const result = filtersNoGroups.shouldProcessMessage(
        '120363999999999999@g.us',
        '!cscc list fixtures',
        true,
        'msg128',
        'bot@s.whatsapp.net'
      );
      expect(result).toBe(true);
    });
  });

  describe('cleanMessage', () => {
    it('should remove trigger prefix', () => {
      const result = filters.cleanMessage('!cscc list fixtures', 'bot@s.whatsapp.net');
      expect(result).toBe('list fixtures');
    });

    it('should remove mention', () => {
      const result = filters.cleanMessage('@bot list fixtures', 'bot@s.whatsapp.net');
      expect(result).toBe('list fixtures');
    });

    it('should remove both prefix and mention', () => {
      const result = filters.cleanMessage('!cscc @bot list fixtures', 'bot@s.whatsapp.net');
      expect(result).toBe('list fixtures');
    });

    it('should handle case insensitive prefix', () => {
      const result = filters.cleanMessage('!CSCC list fixtures', 'bot@s.whatsapp.net');
      expect(result).toBe('list fixtures');
    });
  });

  describe('rate limiting', () => {
    it('should allow messages within rate limit', () => {
      const chatId = '120363123456789012@g.us';
      
      // Should allow first few messages
      for (let i = 0; i < 3; i++) {
        const result = filters.shouldProcessMessage(
          chatId,
          '!cscc test',
          true,
          `msg${i}`,
          'bot@s.whatsapp.net'
        );
        expect(result).toBe(true);
      }
    });

    it('should rate limit after burst limit', () => {
      const chatId = '120363123456789012@g.us';
      
      // Send messages up to burst limit
      for (let i = 0; i < 3; i++) {
        const result = filters.shouldProcessMessage(
          chatId,
          '!cscc test',
          true,
          `msg${i}`,
          'bot@s.whatsapp.net'
        );
        expect(result).toBe(true);
      }

      // Next message should be rate limited
      const result = filters.shouldProcessMessage(
        chatId,
        '!cscc test',
        true,
        'msg3',
        'bot@s.whatsapp.net'
      );
      expect(result).toBe(false);
      expect(mockLogger.rateLimited).toHaveBeenCalled();
    });
  });

  describe('getStats', () => {
    it('should return filter statistics', () => {
      const stats = filters.getStats();
      expect(stats).toHaveProperty('allowedGroups');
      expect(stats).toHaveProperty('messageCache');
      expect(stats).toHaveProperty('rateLimitEntries');
    });
  });

  describe('clearCaches', () => {
    it('should clear all caches', () => {
      // Add some data to caches
      filters.shouldProcessMessage(
        '120363123456789012@g.us',
        '!cscc test',
        true,
        'msg1',
        'bot@s.whatsapp.net'
      );

      const statsBefore = filters.getStats();
      expect(statsBefore.messageCache).toBeGreaterThan(0);

      filters.clearCaches();

      const statsAfter = filters.getStats();
      expect(statsAfter.messageCache).toBe(0);
      expect(statsAfter.rateLimitEntries).toBe(0);
    });
  });

  describe('updateAllowedGroups', () => {
    it('should update allowed groups', () => {
      const newGroups = ['120363111111111111@g.us', '120363222222222222@g.us'];
      filters.updateAllowedGroups(newGroups);

      // Should allow message from new group
      const result = filters.shouldProcessMessage(
        '120363111111111111@g.us',
        '!cscc test',
        true,
        'msg1',
        'bot@s.whatsapp.net'
      );
      expect(result).toBe(true);

      // Should reject message from old group
      const result2 = filters.shouldProcessMessage(
        '120363123456789012@g.us',
        '!cscc test',
        true,
        'msg2',
        'bot@s.whatsapp.net'
      );
      expect(result2).toBe(false);
    });
  });

  describe('isGroupAllowed', () => {
    it('should return true for allowed groups', () => {
      const result = filters.isGroupAllowed('120363123456789012@g.us');
      expect(result).toBe(true);
    });

    it('should return false for non-allowed groups', () => {
      const result = filters.isGroupAllowed('120363999999999999@g.us');
      expect(result).toBe(false);
    });

    it('should return true when no groups are specified', () => {
      const filtersNoGroups = new MessageFilters(
        {
          allowedGroups: [],
          triggerPrefix: '!cscc',
          mentionTrigger: true
        },
        mockLogger
      );

      const result = filtersNoGroups.isGroupAllowed('120363999999999999@g.us');
      expect(result).toBe(true);
    });
  });
});

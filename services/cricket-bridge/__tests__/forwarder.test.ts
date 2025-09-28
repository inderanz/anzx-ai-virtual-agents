/**
 * Tests for cricket forwarder
 */

import axios from 'axios';
import { CricketForwarder } from '../src/forwarder';
import CricketLogger from '../src/logger';

// Mock axios
jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('CricketForwarder', () => {
  let forwarder: CricketForwarder;
  let mockLogger: CricketLogger;
  let mockAxiosInstance: any;

  beforeEach(() => {
    mockLogger = {
      getWinstonLogger: jest.fn().mockReturnValue({
        info: jest.fn(),
        warn: jest.fn(),
        debug: jest.fn(),
        error: jest.fn()
      }),
      error: jest.fn()
    } as any;

    // Create a consistent mock axios instance
    mockAxiosInstance = {
      post: jest.fn(),
      get: jest.fn(),
      interceptors: {
        request: { use: jest.fn() },
        response: { use: jest.fn() }
      }
    };

    mockedAxios.create.mockReturnValue(mockAxiosInstance);

    forwarder = new CricketForwarder(
      'http://localhost:8002',
      'test-token',
      mockLogger
    );

    // Reset mocks
    jest.clearAllMocks();
  });

  describe('forwardMessage', () => {
    it('should forward message successfully', async () => {
      const mockResponse = {
        data: {
          answer: 'Test response',
          meta: {
            intent: 'fixtures_list',
            entities: { team_name: 'Test Team' },
            latency_ms: 100,
            request_id: 'req123',
            cache_hit: false,
            rag_hit: true
          }
        }
      };

      mockAxiosInstance.post.mockResolvedValue(mockResponse);

      const request = {
        text: 'list fixtures',
        source: 'whatsapp' as const,
        team_hint: 'team123'
      };

      const result = await forwarder.forwardMessage(request);

      expect(result).toEqual(mockResponse.data);
      expect(mockLogger.getWinstonLogger().info).toHaveBeenCalledWith(
        'Forwarding message to cricket agent',
        expect.objectContaining({
          textLength: request.text.length,
          source: request.source,
          teamHint: request.team_hint
        })
      );
    });

    it('should handle retry on server error', async () => {
      const mockResponse = {
        data: {
          answer: 'Test response',
          meta: { intent: 'fixtures_list', latency_ms: 100 }
        }
      };

      // First call fails, second succeeds
      mockAxiosInstance.post
        .mockRejectedValueOnce(new Error('Server error'))
        .mockResolvedValueOnce(mockResponse);

      const request = {
        text: 'list fixtures',
        source: 'whatsapp' as const
      };

      const result = await forwarder.forwardMessage(request);

      expect(result).toEqual(mockResponse.data);
      expect(mockAxiosInstance.post).toHaveBeenCalledTimes(2);
    });

    it('should not retry on client error', async () => {
      const error = new Error('Bad Request');
      (error as any).response = { status: 400 };
      mockAxiosInstance.post.mockRejectedValue(error);

      const request = {
        text: 'list fixtures',
        source: 'whatsapp' as const
      };

      await expect(forwarder.forwardMessage(request)).rejects.toThrow();
      expect(mockAxiosInstance.post).toHaveBeenCalledTimes(1);
    });

    it('should fail after max retries', async () => {
      mockAxiosInstance.post.mockRejectedValue(new Error('Server error'));

      const request = {
        text: 'list fixtures',
        source: 'whatsapp' as const
      };

      await expect(forwarder.forwardMessage(request)).rejects.toThrow('Server error');
      expect(mockAxiosInstance.post).toHaveBeenCalledTimes(3); // Max retries
    });

    it('should handle network timeout', async () => {
      mockAxiosInstance.post.mockRejectedValue(new Error('timeout'));

      const request = {
        text: 'list fixtures',
        source: 'whatsapp' as const
      };

      await expect(forwarder.forwardMessage(request)).rejects.toThrow();
      expect(mockLogger.error).toHaveBeenCalledWith(
        'Failed to forward message to cricket agent',
        expect.any(Error),
        expect.objectContaining({
          textLength: request.text.length
        })
      );
    });
  });

  describe('healthCheck', () => {
    it('should return true for healthy service', async () => {
      mockAxiosInstance.get.mockResolvedValue({ status: 200 });

      const result = await forwarder.healthCheck();

      expect(result).toBe(true);
      expect(mockAxiosInstance.get).toHaveBeenCalledWith('http://localhost:8002/healthz', {
        timeout: 5000
      });
    });

    it('should return false for unhealthy service', async () => {
      mockAxiosInstance.get.mockRejectedValue(new Error('Connection failed'));

      const result = await forwarder.healthCheck();

      expect(result).toBe(false);
      expect(mockLogger.error).toHaveBeenCalledWith(
        'Cricket agent health check failed',
        expect.any(Error)
      );
    });
  });

  describe('getCricketAgentStatus', () => {
    it('should return status data for healthy service', async () => {
      const mockStatus = {
        ok: true,
        connected: true,
        env: 'dev'
      };

      mockAxiosInstance.get.mockResolvedValue({ data: mockStatus });

      const result = await forwarder.getCricketAgentStatus();

      expect(result).toEqual(mockStatus);
    });

    it('should return null for failed status check', async () => {
      mockAxiosInstance.get.mockRejectedValue(new Error('Connection failed'));

      const result = await forwarder.getCricketAgentStatus();

      expect(result).toBeNull();
      expect(mockLogger.error).toHaveBeenCalledWith(
        'Failed to get cricket agent status',
        expect.any(Error)
      );
    });
  });

  // Note: Request configuration is tested implicitly through other tests
});
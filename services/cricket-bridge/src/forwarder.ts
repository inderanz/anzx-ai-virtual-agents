/**
 * HTTP client for forwarding messages to cricket-agent
 * Handles retries, backoff, and error handling
 */

import axios, { AxiosInstance, AxiosError } from 'axios';
import { CricketAgentRequest, CricketAgentResponse } from './types';
import CricketLogger from './logger';

export class CricketForwarder {
  private httpClient: AxiosInstance;
  private cricketAgentUrl: string;
  private relayToken: string;
  private logger: CricketLogger;
  private readonly MAX_RETRIES = 3;
  private readonly RETRY_DELAY = 1000; // 1 second base delay

  constructor(cricketAgentUrl: string, relayToken: string, logger: CricketLogger) {
    this.cricketAgentUrl = cricketAgentUrl;
    this.relayToken = relayToken;
    this.logger = logger;

    this.httpClient = axios.create({
      timeout: 30000, // 30 second timeout
      headers: {
        'Content-Type': 'application/json',
        'X-Relay-Token': this.relayToken
      }
    });

    // Add request/response interceptors for logging
    this.setupInterceptors();
  }

  /**
   * Forward message to cricket agent
   */
  async forwardMessage(request: CricketAgentRequest): Promise<CricketAgentResponse> {
    const startTime = Date.now();
    
    try {
      this.logger.getWinstonLogger().info('Forwarding message to cricket agent', {
        textLength: request.text.length,
        source: request.source,
        teamHint: request.team_hint
      });

      const response = await this.makeRequestWithRetry(request);
      const forwardMs = Date.now() - startTime;

      this.logger.getWinstonLogger().info('Cricket agent response received', {
        forwardMs,
        latency: response.meta?.latency_ms,
        intent: response.meta?.intent,
        cacheHit: response.meta?.cache_hit
      });

      return response;

    } catch (error) {
      const forwardMs = Date.now() - startTime;
      this.logger.error('Failed to forward message to cricket agent', error as Error, {
        forwardMs,
        textLength: request.text.length
      });
      throw error;
    }
  }

  /**
   * Make request with retry logic
   */
  private async makeRequestWithRetry(request: CricketAgentRequest): Promise<CricketAgentResponse> {
    let lastError: Error | null = null;

    for (let attempt = 1; attempt <= this.MAX_RETRIES; attempt++) {
      try {
        const response = await this.httpClient.post<CricketAgentResponse>(
          `${this.cricketAgentUrl}/v1/ask`,
          request
        );

        return response.data;

      } catch (error) {
        lastError = error as Error;
        
        // Don't retry on client errors (4xx)
        if (this.isClientError(error as AxiosError)) {
          this.logger.getWinstonLogger().warn('Client error, not retrying', {
            attempt,
            status: (error as AxiosError).response?.status,
            message: (error as AxiosError).message
          });
          break;
        }

        // Don't retry on last attempt
        if (attempt === this.MAX_RETRIES) {
          break;
        }

        // Calculate delay with exponential backoff
        const delay = this.RETRY_DELAY * Math.pow(2, attempt - 1);
        
        this.logger.getWinstonLogger().warn('Request failed, retrying', {
          attempt,
          delay,
          error: (error as AxiosError).message
        });

        await this.sleep(delay);
      }
    }

    throw lastError || new Error('All retry attempts failed');
  }

  /**
   * Check if error is a client error (4xx)
   */
  private isClientError(error: AxiosError): boolean {
    const status = error.response?.status;
    return status ? status >= 400 && status < 500 : false;
  }

  /**
   * Sleep utility
   */
  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Setup request/response interceptors
   */
  private setupInterceptors(): void {
    // Request interceptor
    this.httpClient.interceptors.request.use(
      (config) => {
        this.logger.getWinstonLogger().debug('HTTP request', {
          method: config.method,
          url: config.url,
          headers: this.sanitizeHeaders(config.headers)
        });
        return config;
      },
      (error) => {
        this.logger.error('HTTP request error', error);
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.httpClient.interceptors.response.use(
      (response) => {
        this.logger.getWinstonLogger().debug('HTTP response', {
          status: response.status,
          statusText: response.statusText,
          dataSize: JSON.stringify(response.data).length
        });
        return response;
      },
      (error) => {
        this.logger.error('HTTP response error', error, {
          status: error.response?.status,
          statusText: error.response?.statusText
        });
        return Promise.reject(error);
      }
    );
  }

  /**
   * Sanitize headers for logging (remove sensitive data)
   */
  private sanitizeHeaders(headers: any): any {
    const sanitized = { ...headers };
    if (sanitized['X-Relay-Token']) {
      sanitized['X-Relay-Token'] = '***';
    }
    return sanitized;
  }

  /**
   * Health check for cricket agent
   */
  async healthCheck(): Promise<boolean> {
    try {
      const response = await this.httpClient.get(`${this.cricketAgentUrl}/healthz`, {
        timeout: 5000
      });
      return response.status === 200;
    } catch (error) {
      this.logger.error('Cricket agent health check failed', error as Error);
      return false;
    }
  }

  /**
   * Get cricket agent status
   */
  async getCricketAgentStatus(): Promise<any> {
    try {
      const response = await this.httpClient.get(`${this.cricketAgentUrl}/healthz`);
      return response.data;
    } catch (error) {
      this.logger.error('Failed to get cricket agent status', error as Error);
      return null;
    }
  }
}

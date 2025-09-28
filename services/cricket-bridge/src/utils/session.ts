/**
 * Session persistence utilities
 * Supports GCS and Secret Manager for session storage
 */

import { Storage } from '@google-cloud/storage';
import { SecretManagerServiceClient } from '@google-cloud/secret-manager';
import { SessionData } from '../types';
import CricketLogger from '../logger';

export class SessionManager {
  private storage?: Storage;
  private secretManager?: SecretManagerServiceClient;
  private gcsBucket: string | undefined;
  private sessionSecretName: string | undefined;
  private logger: CricketLogger;

  constructor(
    logger: CricketLogger,
    gcsBucket?: string,
    sessionSecretName?: string
  ) {
    this.gcsBucket = gcsBucket;
    this.sessionSecretName = sessionSecretName;
    this.logger = logger;

    // Initialize GCS if bucket is provided
    if (gcsBucket) {
      try {
        this.storage = new Storage();
        this.logger.getWinstonLogger().info('GCS Storage initialized', { bucket: gcsBucket });
      } catch (error) {
        this.logger.error('Failed to initialize GCS Storage', error as Error);
      }
    }

    // Initialize Secret Manager if secret name is provided
    if (sessionSecretName) {
      try {
        this.secretManager = new SecretManagerServiceClient();
        this.logger.getWinstonLogger().info('Secret Manager initialized', { secretName: sessionSecretName });
      } catch (error) {
        this.logger.error('Failed to initialize Secret Manager', error as Error);
      }
    }
  }

  /**
   * Load session data from storage
   */
  async loadSession(): Promise<SessionData | null> {
    // Try GCS first
    if (this.storage && this.gcsBucket) {
      try {
        const sessionData = await this.loadFromGCS();
        if (sessionData) {
          this.logger.sessionLoaded('GCS');
          return sessionData;
        }
      } catch (error) {
        this.logger.error('Failed to load session from GCS', error as Error);
      }
    }

    // Try Secret Manager
    if (this.secretManager && this.sessionSecretName) {
      try {
        const sessionData = await this.loadFromSecretManager();
        if (sessionData) {
          this.logger.sessionLoaded('Secret Manager');
          return sessionData;
        }
      } catch (error) {
        this.logger.error('Failed to load session from Secret Manager', error as Error);
      }
    }

    this.logger.getWinstonLogger().warn('No session data found in any storage');
    return null;
  }

  /**
   * Save session data to storage
   */
  async saveSession(sessionData: SessionData): Promise<boolean> {
    let saved = false;

    // Save to GCS
    if (this.storage && this.gcsBucket) {
      try {
        await this.saveToGCS(sessionData);
        this.logger.sessionSaved('GCS');
        saved = true;
      } catch (error) {
        this.logger.error('Failed to save session to GCS', error as Error);
      }
    }

    // Save to Secret Manager
    if (this.secretManager && this.sessionSecretName) {
      try {
        await this.saveToSecretManager(sessionData);
        this.logger.sessionSaved('Secret Manager');
        saved = true;
      } catch (error) {
        this.logger.error('Failed to save session to Secret Manager', error as Error);
      }
    }

    return saved;
  }

  /**
   * Load session from GCS
   */
  private async loadFromGCS(): Promise<SessionData | null> {
    if (!this.storage || !this.gcsBucket) return null;

    try {
      const bucket = this.storage.bucket(this.gcsBucket);
      const file = bucket.file('whatsapp-session/session.json');
      
      const [exists] = await file.exists();
      if (!exists) return null;

      const [contents] = await file.download();
      const sessionData = JSON.parse(contents.toString());
      
      return sessionData;
    } catch (error) {
      this.logger.error('Failed to load session from GCS', error as Error);
      return null;
    }
  }

  /**
   * Save session to GCS
   */
  private async saveToGCS(sessionData: SessionData): Promise<void> {
    if (!this.storage || !this.gcsBucket) return;

    try {
      const bucket = this.storage.bucket(this.gcsBucket);
      const file = bucket.file('whatsapp-session/session.json');
      
      const jsonData = JSON.stringify(sessionData, null, 2);
      await file.save(jsonData, {
        metadata: {
          contentType: 'application/json',
          cacheControl: 'no-cache'
        }
      });
    } catch (error) {
      this.logger.error('Failed to save session to GCS', error as Error);
      throw error;
    }
  }

  /**
   * Load session from Secret Manager
   */
  private async loadFromSecretManager(): Promise<SessionData | null> {
    if (!this.secretManager || !this.sessionSecretName) return null;

    try {
      const [version] = await this.secretManager.accessSecretVersion({
        name: this.sessionSecretName
      });

      if (!version.payload?.data) return null;

      const sessionData = JSON.parse(version.payload.data.toString());
      return sessionData;
    } catch (error) {
      this.logger.error('Failed to load session from Secret Manager', error as Error);
      return null;
    }
  }

  /**
   * Save session to Secret Manager
   */
  private async saveToSecretManager(sessionData: SessionData): Promise<void> {
    if (!this.secretManager || !this.sessionSecretName) return;

    try {
      const jsonData = JSON.stringify(sessionData, null, 2);
      const secretName = this.sessionSecretName.replace('/versions/latest', '');

      await this.secretManager.addSecretVersion({
        parent: secretName,
        payload: {
          data: Buffer.from(jsonData, 'utf8')
        }
      });
    } catch (error) {
      this.logger.error('Failed to save session to Secret Manager', error as Error);
      throw error;
    }
  }

  /**
   * Check if session storage is available
   */
  isStorageAvailable(): boolean {
    return !!(this.storage || this.secretManager);
  }

  /**
   * Get storage type being used
   */
  getStorageType(): string {
    if (this.storage && this.gcsBucket) return 'GCS';
    if (this.secretManager && this.sessionSecretName) return 'Secret Manager';
    return 'None';
  }
}

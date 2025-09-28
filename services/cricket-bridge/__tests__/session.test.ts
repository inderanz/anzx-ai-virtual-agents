/**
 * Tests for session management
 */

import { Storage } from '@google-cloud/storage';
import { SecretManagerServiceClient } from '@google-cloud/secret-manager';
import { SessionManager } from '../src/utils/session';
import CricketLogger from '../src/logger';

// Mock Google Cloud services
jest.mock('@google-cloud/storage');
jest.mock('@google-cloud/secret-manager');

const MockedStorage = Storage as jest.MockedClass<typeof Storage>;
const MockedSecretManager = SecretManagerServiceClient as jest.MockedClass<typeof SecretManagerServiceClient>;

describe('SessionManager', () => {
  let sessionManager: SessionManager;
  let mockLogger: CricketLogger;
  let mockStorage: jest.Mocked<Storage>;
  let mockSecretManager: jest.Mocked<SecretManagerServiceClient>;

  beforeEach(() => {
    mockLogger = {
      getWinstonLogger: jest.fn().mockReturnValue({
        info: jest.fn(),
        warn: jest.fn(),
        error: jest.fn()
      }),
      error: jest.fn(),
      sessionLoaded: jest.fn(),
      sessionSaved: jest.fn()
    } as any;

    // Mock storage
    mockStorage = {
      bucket: jest.fn().mockReturnValue({
        file: jest.fn().mockReturnValue({
          exists: jest.fn(),
          download: jest.fn(),
          save: jest.fn()
        })
      })
    } as any;

    // Mock secret manager
    mockSecretManager = {
      accessSecretVersion: jest.fn(),
      addSecretVersion: jest.fn()
    } as any;

    MockedStorage.mockImplementation(() => mockStorage);
    MockedSecretManager.mockImplementation(() => mockSecretManager);
  });

  describe('GCS storage', () => {
    beforeEach(() => {
      sessionManager = new SessionManager(
        mockLogger,
        'test-bucket',
        undefined
      );
    });

    it('should load session from GCS successfully', async () => {
      const mockSessionData = {
        creds: { some: 'credentials' },
        keys: { some: 'keys' }
      };

      const mockFile = {
        exists: jest.fn().mockResolvedValue([true]),
        download: jest.fn().mockResolvedValue([Buffer.from(JSON.stringify(mockSessionData))])
      };

      mockStorage.bucket.mockReturnValue({
        file: jest.fn().mockReturnValue(mockFile)
      } as any);

      const result = await sessionManager.loadSession();

      expect(result).toEqual(mockSessionData);
      expect(mockLogger.sessionLoaded).toHaveBeenCalledWith('GCS');
    });

    it('should return null when GCS file does not exist', async () => {
      const mockFile = {
        exists: jest.fn().mockResolvedValue([false])
      };

      mockStorage.bucket.mockReturnValue({
        file: jest.fn().mockReturnValue(mockFile)
      } as any);

      const result = await sessionManager.loadSession();

      expect(result).toBeNull();
    });

    it('should save session to GCS successfully', async () => {
      const mockSessionData = {
        creds: { some: 'credentials' },
        keys: { some: 'keys' }
      };

      const mockFile = {
        save: jest.fn().mockResolvedValue(undefined)
      };

      mockStorage.bucket.mockReturnValue({
        file: jest.fn().mockReturnValue(mockFile)
      } as any);

      const result = await sessionManager.saveSession(mockSessionData);

      expect(result).toBe(true);
      expect(mockFile.save).toHaveBeenCalledWith(
        JSON.stringify(mockSessionData, null, 2),
        {
          metadata: {
            contentType: 'application/json',
            cacheControl: 'no-cache'
          }
        }
      );
      expect(mockLogger.sessionSaved).toHaveBeenCalledWith('GCS');
    });

    it('should handle GCS errors gracefully', async () => {
      const mockFile = {
        exists: jest.fn().mockRejectedValue(new Error('GCS error'))
      };

      mockStorage.bucket.mockReturnValue({
        file: jest.fn().mockReturnValue(mockFile)
      } as any);

      const result = await sessionManager.loadSession();

      expect(result).toBeNull();
      expect(mockLogger.error).toHaveBeenCalledWith(
        'Failed to load session from GCS',
        expect.any(Error)
      );
    });
  });

  describe('Secret Manager storage', () => {
    beforeEach(() => {
      sessionManager = new SessionManager(
        mockLogger,
        undefined,
        'projects/test/secrets/WHATSAPP_SESSION/versions/latest'
      );
    });

    it('should load session from Secret Manager successfully', async () => {
      const mockSessionData = {
        creds: { some: 'credentials' },
        keys: { some: 'keys' }
      };

      (mockSecretManager.accessSecretVersion as jest.Mock).mockResolvedValue([{
        payload: {
          data: Buffer.from(JSON.stringify(mockSessionData))
        }
      }]);

      const result = await sessionManager.loadSession();

      expect(result).toEqual(mockSessionData);
      expect(mockLogger.sessionLoaded).toHaveBeenCalledWith('Secret Manager');
    });

    it('should return null when Secret Manager has no data', async () => {
      (mockSecretManager.accessSecretVersion as jest.Mock).mockResolvedValue([{
        payload: {
          data: null
        }
      }]);

      const result = await sessionManager.loadSession();

      expect(result).toBeNull();
    });

    it('should save session to Secret Manager successfully', async () => {
      const mockSessionData = {
        creds: { some: 'credentials' },
        keys: { some: 'keys' }
      };

      (mockSecretManager.addSecretVersion as jest.Mock).mockResolvedValue(undefined);

      const result = await sessionManager.saveSession(mockSessionData);

      expect(result).toBe(true);
      expect(mockSecretManager.addSecretVersion).toHaveBeenCalledWith({
        parent: 'projects/test/secrets/WHATSAPP_SESSION',
        payload: {
          data: Buffer.from(JSON.stringify(mockSessionData, null, 2), 'utf8')
        }
      });
      expect(mockLogger.sessionSaved).toHaveBeenCalledWith('Secret Manager');
    });

    it('should handle Secret Manager errors gracefully', async () => {
      (mockSecretManager.accessSecretVersion as jest.Mock).mockRejectedValue(new Error('Secret Manager error'));

      const result = await sessionManager.loadSession();

      expect(result).toBeNull();
      expect(mockLogger.error).toHaveBeenCalledWith(
        'Failed to load session from Secret Manager',
        expect.any(Error)
      );
    });
  });

  describe('No storage configured', () => {
    beforeEach(() => {
      sessionManager = new SessionManager(
        mockLogger,
        undefined,
        undefined
      );
    });

    it('should return null when no storage is configured', async () => {
      const result = await sessionManager.loadSession();
      expect(result).toBeNull();
    });

    it('should return false when trying to save with no storage', async () => {
      const mockSessionData = { creds: {}, keys: {} };
      const result = await sessionManager.saveSession(mockSessionData);
      expect(result).toBe(false);
    });

    it('should report no storage available', () => {
      expect(sessionManager.isStorageAvailable()).toBe(false);
      expect(sessionManager.getStorageType()).toBe('None');
    });
  });

  describe('Both storages configured', () => {
    beforeEach(() => {
      sessionManager = new SessionManager(
        mockLogger,
        'test-bucket',
        'projects/test/secrets/WHATSAPP_SESSION/versions/latest'
      );
    });

    it('should try GCS first, then Secret Manager', async () => {
      const mockSessionData = { creds: {}, keys: {} };

      // GCS fails
      const mockGCSFile = {
        exists: jest.fn().mockRejectedValue(new Error('GCS error'))
      };

      // Secret Manager succeeds
      (mockSecretManager.accessSecretVersion as jest.Mock).mockResolvedValue([{
        payload: {
          data: Buffer.from(JSON.stringify(mockSessionData))
        }
      }]);

      mockStorage.bucket.mockReturnValue({
        file: jest.fn().mockReturnValue(mockGCSFile)
      } as any);

      const result = await sessionManager.loadSession();

      expect(result).toEqual(mockSessionData);
      expect(mockLogger.sessionLoaded).toHaveBeenCalledWith('Secret Manager');
    });

    it('should save to both storages', async () => {
      const mockSessionData = { creds: {}, keys: {} };

      const mockGCSFile = {
        save: jest.fn().mockResolvedValue(undefined)
      };

      mockStorage.bucket.mockReturnValue({
        file: jest.fn().mockReturnValue(mockGCSFile)
      } as any);

      (mockSecretManager.addSecretVersion as jest.Mock).mockResolvedValue(undefined);

      const result = await sessionManager.saveSession(mockSessionData);

      expect(result).toBe(true);
      expect(mockGCSFile.save).toHaveBeenCalled();
      expect(mockSecretManager.addSecretVersion).toHaveBeenCalled();
      expect(mockLogger.sessionSaved).toHaveBeenCalledWith('GCS');
      expect(mockLogger.sessionSaved).toHaveBeenCalledWith('Secret Manager');
    });

    it('should report GCS as storage type when both are configured', () => {
      expect(sessionManager.getStorageType()).toBe('GCS');
    });
  });

  describe('error handling', () => {
    it('should handle JSON parse errors', async () => {
      const mockFile = {
        exists: jest.fn().mockResolvedValue([true]),
        download: jest.fn().mockResolvedValue([Buffer.from('invalid json')])
      };

      mockStorage.bucket.mockReturnValue({
        file: jest.fn().mockReturnValue(mockFile)
      } as any);

      sessionManager = new SessionManager(mockLogger, 'test-bucket', undefined);

      const result = await sessionManager.loadSession();

      expect(result).toBeNull();
      expect(mockLogger.error).toHaveBeenCalledWith(
        'Failed to load session from GCS',
        expect.any(Error)
      );
    });
  });
});
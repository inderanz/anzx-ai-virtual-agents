/**
 * Jest setup file
 */

// Mock environment variables
process.env['NODE_ENV'] = 'test';
process.env['PORT'] = '8003';
process.env['CRICKET_AGENT_URL'] = 'http://localhost:8002';
process.env['TRIGGER_PREFIX'] = '!cscc';
process.env['RELAY_TOKEN'] = 'test-token';
process.env['LOG_LEVEL'] = 'error';

// Mock console methods to reduce noise in tests
global.console = {
  ...console,
  log: jest.fn(),
  debug: jest.fn(),
  info: jest.fn(),
  warn: jest.fn(),
  error: jest.fn()
};

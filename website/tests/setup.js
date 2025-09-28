/**
 * Jest setup for website tests
 */

// Mock global objects
global.console = {
  ...console,
  log: jest.fn(),
  debug: jest.fn(),
  info: jest.fn(),
  warn: jest.fn(),
  error: jest.fn()
};

// Mock fetch globally
global.fetch = jest.fn();

// Mock process.env
process.env = {
  ...process.env,
  NODE_ENV: 'test'
};

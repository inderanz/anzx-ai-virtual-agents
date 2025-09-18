/**
 * Global Setup for E2E Tests
 * Sets up test environment, database, and authentication
 */

const { chromium } = require('@playwright/test');
const { execSync } = require('child_process');

async function globalSetup() {
  console.log('Setting up E2E test environment...');
  
  // Set up test database
  try {
    execSync('python -m pytest --setup-only tests/integration/conftest.py', { 
      stdio: 'inherit',
      cwd: '../../'
    });
    console.log('✓ Test database setup complete');
  } catch (error) {
    console.error('Failed to setup test database:', error.message);
    throw error;
  }
  
  // Create test user and organization
  const browser = await chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();
  
  try {
    // Navigate to registration page
    await page.goto('/auth/register');
    
    // Register test user
    await page.fill('[data-testid="email-input"]', 'e2e-test@example.com');
    await page.fill('[data-testid="password-input"]', 'TestPassword123!');
    await page.fill('[data-testid="full-name-input"]', 'E2E Test User');
    await page.fill('[data-testid="organization-name-input"]', 'E2E Test Organization');
    await page.click('[data-testid="register-button"]');
    
    // Wait for registration success
    await page.waitForSelector('[data-testid="registration-success"]', { timeout: 10000 });
    
    // Store authentication state
    await context.storageState({ path: 'tests/auth-state.json' });
    
    console.log('✓ Test user and organization created');
  } catch (error) {
    console.error('Failed to create test user:', error.message);
    throw error;
  } finally {
    await browser.close();
  }
  
  // Set up test data
  try {
    execSync('python scripts/setup_e2e_test_data.py', { 
      stdio: 'inherit',
      cwd: '../../'
    });
    console.log('✓ Test data setup complete');
  } catch (error) {
    console.warn('Test data setup failed (non-critical):', error.message);
  }
  
  console.log('E2E test environment ready!');
}

module.exports = globalSetup;
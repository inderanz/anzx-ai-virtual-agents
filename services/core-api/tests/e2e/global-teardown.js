/**
 * Global Teardown for E2E Tests
 * Cleans up test environment and resources
 */

const { execSync } = require('child_process');
const fs = require('fs');

async function globalTeardown() {
  console.log('Cleaning up E2E test environment...');
  
  // Clean up test data
  try {
    execSync('python scripts/cleanup_e2e_test_data.py', { 
      stdio: 'inherit',
      cwd: '../../'
    });
    console.log('✓ Test data cleanup complete');
  } catch (error) {
    console.warn('Test data cleanup failed (non-critical):', error.message);
  }
  
  // Remove auth state file
  try {
    if (fs.existsSync('tests/auth-state.json')) {
      fs.unlinkSync('tests/auth-state.json');
      console.log('✓ Auth state file removed');
    }
  } catch (error) {
    console.warn('Failed to remove auth state file:', error.message);
  }
  
  // Clean up test database
  try {
    execSync('python -m pytest --teardown-only tests/integration/conftest.py', { 
      stdio: 'inherit',
      cwd: '../../'
    });
    console.log('✓ Test database cleanup complete');
  } catch (error) {
    console.warn('Test database cleanup failed:', error.message);
  }
  
  console.log('E2E test environment cleanup complete!');
}

module.exports = globalTeardown;
// ANZX AI Platform - Comprehensive Playwright Tests
const { test, expect } = require('@playwright/test');
const fs = require('fs');

// Load test environment
let testEnv = {};
if (fs.existsSync('test_environment.json')) {
  testEnv = JSON.parse(fs.readFileSync('test_environment.json', 'utf8'));
}

test.describe('ANZX AI Platform Tests', () => {
  
  test('Health Check', async ({ request }) => {
    const response = await request.get('/health');
    expect(response.status()).toBe(200);
    
    const data = await response.json();
    expect(data.status).toBe('healthy');
    expect(data.service).toBe('anzx-core-api');
  });
  
  test('API Documentation Access', async ({ page }) => {
    await page.goto('/docs');
    await expect(page.locator('title')).toContainText('ANZX AI Platform API');
  });
  
  test('Assistant Discovery', async ({ request }) => {
    const response = await request.get('/assistants');
    expect(response.status()).toBe(200);
    
    const data = await response.json();
    expect(data).toHaveProperty('assistants');
  });
  
  test('API with Authentication', async ({ request }) => {
    if (!testEnv.api_key) {
      test.skip('No API key available for testing');
    }
    
    const response = await request.get('/api/v1/agents/', {
      headers: {
        'Authorization': `Bearer ${testEnv.api_key}`
      }
    });
    
    // Should return 200 or 401/403 (not 500)
    expect([200, 401, 403]).toContain(response.status());
  });
  
});

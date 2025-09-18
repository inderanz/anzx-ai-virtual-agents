/**
 * User Journey End-to-End Tests
 * Tests complete user workflows from registration to conversation
 */

const { test, expect } = require('@playwright/test');

test.describe('Complete User Journey', () => {
  test.beforeEach(async ({ page }) => {
    // Use stored authentication state
    await page.goto('/');
  });

  test('User registration and onboarding flow', async ({ page }) => {
    // Navigate to registration
    await page.goto('/auth/register');
    
    // Fill registration form
    await page.fill('[data-testid="email-input"]', 'journey-test@example.com');
    await page.fill('[data-testid="password-input"]', 'TestPassword123!');
    await page.fill('[data-testid="full-name-input"]', 'Journey Test User');
    await page.fill('[data-testid="organization-name-input"]', 'Journey Test Org');
    
    // Submit registration
    await page.click('[data-testid="register-button"]');
    
    // Verify registration success
    await expect(page.locator('[data-testid="registration-success"]')).toBeVisible();
    
    // Complete onboarding
    await page.click('[data-testid="start-onboarding"]');
    
    // Step 1: Choose assistant types
    await page.check('[data-testid="assistant-support"]');
    await page.check('[data-testid="assistant-sales"]');
    await page.click('[data-testid="next-step"]');
    
    // Step 2: Configure integrations
    await page.click('[data-testid="skip-integrations"]');
    
    // Step 3: Complete setup
    await page.click('[data-testid="complete-setup"]');
    
    // Verify dashboard access
    await expect(page.locator('[data-testid="dashboard"]')).toBeVisible();
    await expect(page.locator('[data-testid="assistant-list"]')).toContainText('Support Assistant');
  });

  test('Assistant creation and configuration', async ({ page, context }) => {
    // Use authenticated state
    await context.addInitScript(() => {
      localStorage.setItem('auth-token', 'test-token');
    });
    
    await page.goto('/dashboard');
    
    // Navigate to assistant creation
    await page.click('[data-testid="create-assistant"]');
    
    // Fill assistant details
    await page.fill('[data-testid="assistant-name"]', 'Test Support Assistant');
    await page.selectOption('[data-testid="assistant-type"]', 'support');
    await page.fill('[data-testid="assistant-description"]', 'Test assistant for customer support');
    
    // Configure capabilities
    await page.check('[data-testid="capability-communication"]');
    await page.check('[data-testid="capability-technical"]');
    
    // Set up knowledge base
    await page.click('[data-testid="add-knowledge-source"]');
    await page.fill('[data-testid="knowledge-url"]', 'https://example.com/docs');
    await page.click('[data-testid="add-source"]');
    
    // Create assistant
    await page.click('[data-testid="create-assistant-submit"]');
    
    // Verify creation success
    await expect(page.locator('[data-testid="assistant-created"]')).toBeVisible();
    await expect(page.locator('[data-testid="assistant-list"]')).toContainText('Test Support Assistant');
    
    // Test assistant configuration
    await page.click('[data-testid="configure-assistant"]');
    await expect(page.locator('[data-testid="assistant-settings"]')).toBeVisible();
    
    // Update system prompt
    await page.fill('[data-testid="system-prompt"]', 'You are a helpful customer support assistant.');
    await page.click('[data-testid="save-settings"]');
    
    await expect(page.locator('[data-testid="settings-saved"]')).toBeVisible();
  });

  test('Knowledge base management workflow', async ({ page, context }) => {
    await context.addInitScript(() => {
      localStorage.setItem('auth-token', 'test-token');
    });
    
    await page.goto('/dashboard/knowledge');
    
    // Upload document
    const fileInput = page.locator('[data-testid="file-upload"]');
    await fileInput.setInputFiles({
      name: 'test-document.pdf',
      mimeType: 'application/pdf',
      buffer: Buffer.from('Test PDF content')
    });
    
    await page.click('[data-testid="upload-document"]');
    
    // Wait for processing
    await expect(page.locator('[data-testid="processing-status"]')).toContainText('Processing');
    await expect(page.locator('[data-testid="processing-complete"]')).toBeVisible({ timeout: 30000 });
    
    // Verify document in list
    await expect(page.locator('[data-testid="document-list"]')).toContainText('test-document.pdf');
    
    // Test knowledge search
    await page.fill('[data-testid="search-input"]', 'test query');
    await page.click('[data-testid="search-button"]');
    
    await expect(page.locator('[data-testid="search-results"]')).toBeVisible();
    
    // Add URL source
    await page.click('[data-testid="add-url-source"]');
    await page.fill('[data-testid="url-input"]', 'https://example.com/help');
    await page.click('[data-testid="crawl-url"]');
    
    await expect(page.locator('[data-testid="crawl-status"]')).toContainText('Crawling');
    await expect(page.locator('[data-testid="crawl-complete"]')).toBeVisible({ timeout: 60000 });
  });

  test('Complete conversation workflow', async ({ page, context }) => {
    await context.addInitScript(() => {
      localStorage.setItem('auth-token', 'test-token');
    });
    
    await page.goto('/dashboard/conversations');
    
    // Start new conversation
    await page.click('[data-testid="new-conversation"]');
    await page.selectOption('[data-testid="select-assistant"]', 'support');
    await page.click('[data-testid="start-conversation"]');
    
    // Send initial message
    await page.fill('[data-testid="message-input"]', 'Hello, I need help with my account');
    await page.click('[data-testid="send-message"]');
    
    // Wait for AI response
    await expect(page.locator('[data-testid="ai-response"]')).toBeVisible({ timeout: 10000 });
    await expect(page.locator('[data-testid="message-list"]')).toContainText('Hello, I need help');
    
    // Continue conversation
    await page.fill('[data-testid="message-input"]', 'I cannot log into my account');
    await page.click('[data-testid="send-message"]');
    
    await expect(page.locator('[data-testid="ai-response"]').nth(1)).toBeVisible({ timeout: 10000 });
    
    // Test escalation
    await page.fill('[data-testid="message-input"]', 'I want to speak to a human agent');
    await page.click('[data-testid="send-message"]');
    
    // Should trigger escalation
    await expect(page.locator('[data-testid="escalation-notice"]')).toBeVisible();
    await expect(page.locator('[data-testid="escalation-notice"]')).toContainText('human agent');
    
    // Test conversation history
    await page.click('[data-testid="conversation-history"]');
    await expect(page.locator('[data-testid="message-count"]')).toContainText('3 messages');
    
    // Export conversation
    await page.click('[data-testid="export-conversation"]');
    const downloadPromise = page.waitForEvent('download');
    await page.click('[data-testid="download-json"]');
    const download = await downloadPromise;
    expect(download.suggestedFilename()).toContain('.json');
  });

  test('Billing and subscription workflow', async ({ page, context }) => {
    await context.addInitScript(() => {
      localStorage.setItem('auth-token', 'test-token');
    });
    
    await page.goto('/dashboard/billing');
    
    // View current plan
    await expect(page.locator('[data-testid="current-plan"]')).toBeVisible();
    
    // Upgrade plan
    await page.click('[data-testid="upgrade-plan"]');
    await page.click('[data-testid="select-professional"]');
    
    // Enter payment details (test mode)
    await page.fill('[data-testid="card-number"]', '4242424242424242');
    await page.fill('[data-testid="card-expiry"]', '12/25');
    await page.fill('[data-testid="card-cvc"]', '123');
    await page.fill('[data-testid="cardholder-name"]', 'Test User');
    
    await page.click('[data-testid="confirm-upgrade"]');
    
    // Verify upgrade success
    await expect(page.locator('[data-testid="upgrade-success"]')).toBeVisible();
    await expect(page.locator('[data-testid="current-plan"]')).toContainText('Professional');
    
    // Check usage metrics
    await page.click('[data-testid="usage-tab"]');
    await expect(page.locator('[data-testid="api-requests"]')).toBeVisible();
    await expect(page.locator('[data-testid="tokens-used"]')).toBeVisible();
    
    // Download invoice
    await page.click('[data-testid="billing-history"]');
    await expect(page.locator('[data-testid="invoice-list"]')).toBeVisible();
    
    const downloadPromise = page.waitForEvent('download');
    await page.click('[data-testid="download-invoice"]');
    const download = await downloadPromise;
    expect(download.suggestedFilename()).toContain('.pdf');
  });

  test('Multi-channel conversation flow', async ({ page, context }) => {
    await context.addInitScript(() => {
      localStorage.setItem('auth-token', 'test-token');
    });
    
    // Test chat widget integration
    await page.goto('/dashboard/integrations');
    await page.click('[data-testid="chat-widget-setup"]');
    
    // Configure widget
    await page.fill('[data-testid="widget-title"]', 'Customer Support');
    await page.selectOption('[data-testid="widget-theme"]', 'blue');
    await page.click('[data-testid="save-widget-config"]');
    
    // Get embed code
    await page.click('[data-testid="get-embed-code"]');
    const embedCode = await page.locator('[data-testid="embed-code"]').textContent();
    expect(embedCode).toContain('<script');
    
    // Test email integration
    await page.click('[data-testid="email-integration"]');
    await page.fill('[data-testid="support-email"]', 'support@test.com');
    await page.click('[data-testid="connect-email"]');
    
    await expect(page.locator('[data-testid="email-connected"]')).toBeVisible();
    
    // Simulate incoming email
    await page.goto('/dashboard/conversations');
    await expect(page.locator('[data-testid="email-conversation"]')).toBeVisible({ timeout: 30000 });
    
    // Test cross-channel context
    await page.click('[data-testid="email-conversation"]');
    await expect(page.locator('[data-testid="channel-indicator"]')).toContainText('Email');
    
    // Reply to email
    await page.fill('[data-testid="message-input"]', 'Thank you for contacting us. How can I help?');
    await page.click('[data-testid="send-reply"]');
    
    await expect(page.locator('[data-testid="email-sent"]')).toBeVisible();
  });

  test('Performance and responsiveness', async ({ page, context }) => {
    await context.addInitScript(() => {
      localStorage.setItem('auth-token', 'test-token');
    });
    
    // Measure page load times
    const startTime = Date.now();
    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');
    const loadTime = Date.now() - startTime;
    
    expect(loadTime).toBeLessThan(3000); // Should load within 3 seconds
    
    // Test conversation response time
    await page.goto('/dashboard/conversations');
    await page.click('[data-testid="new-conversation"]');
    await page.selectOption('[data-testid="select-assistant"]', 'support');
    await page.click('[data-testid="start-conversation"]');
    
    const messageStartTime = Date.now();
    await page.fill('[data-testid="message-input"]', 'Test message for response time');
    await page.click('[data-testid="send-message"]');
    
    await expect(page.locator('[data-testid="ai-response"]')).toBeVisible();
    const responseTime = Date.now() - messageStartTime;
    
    expect(responseTime).toBeLessThan(5000); // Should respond within 5 seconds
    
    // Test concurrent conversations
    const conversations = [];
    for (let i = 0; i < 3; i++) {
      await page.click('[data-testid="new-conversation"]');
      await page.selectOption('[data-testid="select-assistant"]', 'support');
      await page.click('[data-testid="start-conversation"]');
      conversations.push(page.url());
    }
    
    // Verify all conversations are accessible
    for (const url of conversations) {
      await page.goto(url);
      await expect(page.locator('[data-testid="conversation-active"]')).toBeVisible();
    }
  });
});
/**
 * Chat Widget End-to-End Tests
 * Tests the embeddable chat widget functionality and real-time communication
 */

const { test, expect } = require('@playwright/test');

test.describe('Chat Widget Integration', () => {
  let widgetPage;
  let dashboardPage;

  test.beforeAll(async ({ browser }) => {
    // Create two contexts - one for the widget, one for the dashboard
    const widgetContext = await browser.newContext();
    const dashboardContext = await browser.newContext();
    
    widgetPage = await widgetContext.newPage();
    dashboardPage = await dashboardContext.newPage();
    
    // Set up authentication for dashboard
    await dashboardContext.addInitScript(() => {
      localStorage.setItem('auth-token', 'test-token');
    });
  });

  test('Widget embedding and initialization', async () => {
    // Create a test HTML page with the widget
    const widgetHTML = `
      <!DOCTYPE html>
      <html>
      <head>
        <title>Test Widget Page</title>
      </head>
      <body>
        <h1>Test Website</h1>
        <div id="anzx-chat-widget"></div>
        <script>
          window.anzxChatConfig = {
            organizationId: 'test-org-123',
            assistantId: 'test-assistant-123',
            theme: 'blue',
            position: 'bottom-right',
            title: 'Customer Support',
            subtitle: 'How can we help you today?'
          };
        </script>
        <script src="http://localhost:3000/widget.js"></script>
      </body>
      </html>
    `;
    
    // Navigate to the test page
    await widgetPage.setContent(widgetHTML);
    
    // Wait for widget to load
    await expect(widgetPage.locator('[data-testid="chat-widget"]')).toBeVisible({ timeout: 10000 });
    
    // Verify widget configuration
    await expect(widgetPage.locator('[data-testid="widget-title"]')).toContainText('Customer Support');
    await expect(widgetPage.locator('[data-testid="widget-subtitle"]')).toContainText('How can we help you today?');
    
    // Check widget positioning
    const widget = widgetPage.locator('[data-testid="chat-widget"]');
    const boundingBox = await widget.boundingBox();
    expect(boundingBox.x).toBeGreaterThan(window.innerWidth - 400); // Right side
    expect(boundingBox.y).toBeGreaterThan(window.innerHeight - 600); // Bottom
  });

  test('Widget theme customization', async () => {
    const themes = ['blue', 'green', 'purple', 'dark'];
    
    for (const theme of themes) {
      const widgetHTML = `
        <!DOCTYPE html>
        <html>
        <body>
          <div id="anzx-chat-widget"></div>
          <script>
            window.anzxChatConfig = {
              organizationId: 'test-org-123',
              assistantId: 'test-assistant-123',
              theme: '${theme}'
            };
          </script>
          <script src="http://localhost:3000/widget.js"></script>
        </body>
        </html>
      `;
      
      await widgetPage.setContent(widgetHTML);
      await expect(widgetPage.locator('[data-testid="chat-widget"]')).toBeVisible();
      
      // Check theme class is applied
      await expect(widgetPage.locator('[data-testid="chat-widget"]')).toHaveClass(new RegExp(`theme-${theme}`));
      
      // Verify theme colors
      const headerColor = await widgetPage.locator('[data-testid="widget-header"]').evaluate(
        el => getComputedStyle(el).backgroundColor
      );
      expect(headerColor).toBeTruthy();
    }
  });

  test('Real-time conversation flow', async () => {
    // Set up widget
    const widgetHTML = `
      <!DOCTYPE html>
      <html>
      <body>
        <div id="anzx-chat-widget"></div>
        <script>
          window.anzxChatConfig = {
            organizationId: 'test-org-123',
            assistantId: 'test-assistant-123',
            websocketUrl: 'ws://localhost:8000/ws'
          };
        </script>
        <script src="http://localhost:3000/widget.js"></script>
      </body>
      </html>
    `;
    
    await widgetPage.setContent(widgetHTML);
    await expect(widgetPage.locator('[data-testid="chat-widget"]')).toBeVisible();
    
    // Open widget
    await widgetPage.click('[data-testid="widget-toggle"]');
    await expect(widgetPage.locator('[data-testid="chat-interface"]')).toBeVisible();
    
    // Send message from widget
    await widgetPage.fill('[data-testid="message-input"]', 'Hello, I need help with my order');
    await widgetPage.click('[data-testid="send-button"]');
    
    // Verify message appears in widget
    await expect(widgetPage.locator('[data-testid="user-message"]')).toContainText('Hello, I need help with my order');
    
    // Wait for AI response
    await expect(widgetPage.locator('[data-testid="ai-message"]')).toBeVisible({ timeout: 10000 });
    
    // Verify typing indicator
    await widgetPage.fill('[data-testid="message-input"]', 'Can you help me track my order?');
    await expect(widgetPage.locator('[data-testid="typing-indicator"]')).toBeVisible();
    
    await widgetPage.click('[data-testid="send-button"]');
    await expect(widgetPage.locator('[data-testid="ai-message"]').nth(1)).toBeVisible({ timeout: 10000 });
  });

  test('WebSocket connection and fallback', async () => {
    // Test with WebSocket enabled
    let widgetHTML = `
      <!DOCTYPE html>
      <html>
      <body>
        <div id="anzx-chat-widget"></div>
        <script>
          window.anzxChatConfig = {
            organizationId: 'test-org-123',
            assistantId: 'test-assistant-123',
            websocketUrl: 'ws://localhost:8000/ws',
            fallbackToPolling: true
          };
        </script>
        <script src="http://localhost:3000/widget.js"></script>
      </body>
      </html>
    `;
    
    await widgetPage.setContent(widgetHTML);
    await expect(widgetPage.locator('[data-testid="chat-widget"]')).toBeVisible();
    
    // Check WebSocket connection status
    const wsStatus = await widgetPage.evaluate(() => {
      return window.anzxChat && window.anzxChat.connectionStatus;
    });
    expect(wsStatus).toBe('connected');
    
    // Test fallback to polling when WebSocket fails
    widgetHTML = `
      <!DOCTYPE html>
      <html>
      <body>
        <div id="anzx-chat-widget"></div>
        <script>
          window.anzxChatConfig = {
            organizationId: 'test-org-123',
            assistantId: 'test-assistant-123',
            websocketUrl: 'ws://invalid-url:9999/ws',
            fallbackToPolling: true,
            pollingInterval: 1000
          };
        </script>
        <script src="http://localhost:3000/widget.js"></script>
      </body>
      </html>
    `;
    
    await widgetPage.setContent(widgetHTML);
    await expect(widgetPage.locator('[data-testid="chat-widget"]')).toBeVisible();
    
    // Should fallback to polling
    await widgetPage.waitForTimeout(2000);
    const fallbackStatus = await widgetPage.evaluate(() => {
      return window.anzxChat && window.anzxChat.connectionMode;
    });
    expect(fallbackStatus).toBe('polling');
  });

  test('Widget accessibility compliance', async () => {
    const widgetHTML = `
      <!DOCTYPE html>
      <html>
      <body>
        <div id="anzx-chat-widget"></div>
        <script>
          window.anzxChatConfig = {
            organizationId: 'test-org-123',
            assistantId: 'test-assistant-123'
          };
        </script>
        <script src="http://localhost:3000/widget.js"></script>
      </body>
      </html>
    `;
    
    await widgetPage.setContent(widgetHTML);
    await expect(widgetPage.locator('[data-testid="chat-widget"]')).toBeVisible();
    
    // Check ARIA labels
    await expect(widgetPage.locator('[data-testid="widget-toggle"]')).toHaveAttribute('aria-label');
    await expect(widgetPage.locator('[data-testid="widget-toggle"]')).toHaveAttribute('role', 'button');
    
    // Open widget and check chat interface accessibility
    await widgetPage.click('[data-testid="widget-toggle"]');
    
    await expect(widgetPage.locator('[data-testid="message-input"]')).toHaveAttribute('aria-label');
    await expect(widgetPage.locator('[data-testid="send-button"]')).toHaveAttribute('aria-label');
    await expect(widgetPage.locator('[data-testid="chat-messages"]')).toHaveAttribute('role', 'log');
    
    // Test keyboard navigation
    await widgetPage.keyboard.press('Tab');
    await expect(widgetPage.locator('[data-testid="message-input"]')).toBeFocused();
    
    await widgetPage.keyboard.press('Tab');
    await expect(widgetPage.locator('[data-testid="send-button"]')).toBeFocused();
    
    // Test screen reader announcements
    await widgetPage.fill('[data-testid="message-input"]', 'Test message');
    await widgetPage.keyboard.press('Enter');
    
    await expect(widgetPage.locator('[aria-live="polite"]')).toBeVisible();
  });

  test('Cross-browser widget compatibility', async ({ browserName }) => {
    const widgetHTML = `
      <!DOCTYPE html>
      <html>
      <body>
        <div id="anzx-chat-widget"></div>
        <script>
          window.anzxChatConfig = {
            organizationId: 'test-org-123',
            assistantId: 'test-assistant-123'
          };
        </script>
        <script src="http://localhost:3000/widget.js"></script>
      </body>
      </html>
    `;
    
    await widgetPage.setContent(widgetHTML);
    
    // Widget should load in all browsers
    await expect(widgetPage.locator('[data-testid="chat-widget"]')).toBeVisible({ timeout: 15000 });
    
    // Test basic functionality
    await widgetPage.click('[data-testid="widget-toggle"]');
    await expect(widgetPage.locator('[data-testid="chat-interface"]')).toBeVisible();
    
    await widgetPage.fill('[data-testid="message-input"]', `Test from ${browserName}`);
    await widgetPage.click('[data-testid="send-button"]');
    
    await expect(widgetPage.locator('[data-testid="user-message"]')).toContainText(`Test from ${browserName}`);
    
    // Browser-specific tests
    if (browserName === 'webkit') {
      // Test Safari-specific features
      const supportsWebSocket = await widgetPage.evaluate(() => {
        return typeof WebSocket !== 'undefined';
      });
      expect(supportsWebSocket).toBe(true);
    }
    
    if (browserName === 'firefox') {
      // Test Firefox-specific features
      const supportsLocalStorage = await widgetPage.evaluate(() => {
        return typeof localStorage !== 'undefined';
      });
      expect(supportsLocalStorage).toBe(true);
    }
  });

  test('Widget performance and bundle size', async () => {
    // Monitor network requests
    const requests = [];
    widgetPage.on('request', request => {
      requests.push({
        url: request.url(),
        method: request.method(),
        resourceType: request.resourceType()
      });
    });
    
    const responses = [];
    widgetPage.on('response', response => {
      responses.push({
        url: response.url(),
        status: response.status(),
        size: response.headers()['content-length']
      });
    });
    
    const widgetHTML = `
      <!DOCTYPE html>
      <html>
      <body>
        <div id="anzx-chat-widget"></div>
        <script>
          window.anzxChatConfig = {
            organizationId: 'test-org-123',
            assistantId: 'test-assistant-123'
          };
        </script>
        <script src="http://localhost:3000/widget.js"></script>
      </body>
      </html>
    `;
    
    const startTime = Date.now();
    await widgetPage.setContent(widgetHTML);
    await expect(widgetPage.locator('[data-testid="chat-widget"]')).toBeVisible();
    const loadTime = Date.now() - startTime;
    
    // Widget should load quickly
    expect(loadTime).toBeLessThan(2000);
    
    // Check bundle size
    const widgetScript = responses.find(r => r.url.includes('widget.js'));
    if (widgetScript && widgetScript.size) {
      const sizeKB = parseInt(widgetScript.size) / 1024;
      expect(sizeKB).toBeLessThan(12); // Should be under 12KB as specified
    }
    
    // Check for unnecessary requests
    const jsRequests = requests.filter(r => r.resourceType === 'script');
    expect(jsRequests.length).toBeLessThanOrEqual(2); // Widget script + config
  });

  test('Widget error handling and recovery', async () => {
    // Test with invalid configuration
    let widgetHTML = `
      <!DOCTYPE html>
      <html>
      <body>
        <div id="anzx-chat-widget"></div>
        <script>
          window.anzxChatConfig = {
            organizationId: 'invalid-org',
            assistantId: 'invalid-assistant'
          };
        </script>
        <script src="http://localhost:3000/widget.js"></script>
      </body>
      </html>
    `;
    
    await widgetPage.setContent(widgetHTML);
    
    // Widget should still render with error state
    await expect(widgetPage.locator('[data-testid="chat-widget"]')).toBeVisible();
    await widgetPage.click('[data-testid="widget-toggle"]');
    
    await expect(widgetPage.locator('[data-testid="error-message"]')).toBeVisible();
    await expect(widgetPage.locator('[data-testid="error-message"]')).toContainText('configuration');
    
    // Test network error recovery
    widgetHTML = `
      <!DOCTYPE html>
      <html>
      <body>
        <div id="anzx-chat-widget"></div>
        <script>
          window.anzxChatConfig = {
            organizationId: 'test-org-123',
            assistantId: 'test-assistant-123',
            apiUrl: 'http://invalid-api-url:9999'
          };
        </script>
        <script src="http://localhost:3000/widget.js"></script>
      </body>
      </html>
    `;
    
    await widgetPage.setContent(widgetHTML);
    await expect(widgetPage.locator('[data-testid="chat-widget"]')).toBeVisible();
    
    await widgetPage.click('[data-testid="widget-toggle"]');
    await widgetPage.fill('[data-testid="message-input"]', 'Test message');
    await widgetPage.click('[data-testid="send-button"]');
    
    // Should show network error
    await expect(widgetPage.locator('[data-testid="network-error"]')).toBeVisible();
    await expect(widgetPage.locator('[data-testid="retry-button"]')).toBeVisible();
  });

  test('Widget customization and branding', async () => {
    const customConfig = {
      organizationId: 'test-org-123',
      assistantId: 'test-assistant-123',
      theme: 'custom',
      customCSS: `
        .chat-widget { border-radius: 20px; }
        .widget-header { background: linear-gradient(45deg, #ff6b6b, #4ecdc4); }
      `,
      branding: {
        logo: 'https://example.com/logo.png',
        companyName: 'Test Company',
        primaryColor: '#ff6b6b',
        secondaryColor: '#4ecdc4'
      },
      messages: {
        welcome: 'Welcome to Test Company support!',
        placeholder: 'Type your message here...',
        offline: 'We are currently offline. Please leave a message.'
      }
    };
    
    const widgetHTML = `
      <!DOCTYPE html>
      <html>
      <body>
        <div id="anzx-chat-widget"></div>
        <script>
          window.anzxChatConfig = ${JSON.stringify(customConfig)};
        </script>
        <script src="http://localhost:3000/widget.js"></script>
      </body>
      </html>
    `;
    
    await widgetPage.setContent(widgetHTML);
    await expect(widgetPage.locator('[data-testid="chat-widget"]')).toBeVisible();
    
    // Check custom branding
    await widgetPage.click('[data-testid="widget-toggle"]');
    
    await expect(widgetPage.locator('[data-testid="company-logo"]')).toHaveAttribute('src', customConfig.branding.logo);
    await expect(widgetPage.locator('[data-testid="welcome-message"]')).toContainText(customConfig.messages.welcome);
    await expect(widgetPage.locator('[data-testid="message-input"]')).toHaveAttribute('placeholder', customConfig.messages.placeholder);
    
    // Check custom colors
    const headerBg = await widgetPage.locator('[data-testid="widget-header"]').evaluate(
      el => getComputedStyle(el).background
    );
    expect(headerBg).toContain('linear-gradient');
  });
});
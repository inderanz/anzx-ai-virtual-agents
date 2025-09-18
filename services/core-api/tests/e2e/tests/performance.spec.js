/**
 * Performance End-to-End Tests
 * Tests response times, throughput, and system performance under load
 */

const { test, expect } = require('@playwright/test');

test.describe('Performance Testing', () => {
  test.beforeEach(async ({ page, context }) => {
    await context.addInitScript(() => {
      localStorage.setItem('auth-token', 'test-token');
    });
  });

  test('API response time benchmarks', async ({ page }) => {
    const endpoints = [
      { path: '/api/v1/health', expectedTime: 100 },
      { path: '/api/v1/auth/me', expectedTime: 200 },
      { path: '/api/v1/organizations', expectedTime: 300 },
      { path: '/api/v1/assistants', expectedTime: 500 }
    ];
    
    for (const endpoint of endpoints) {
      const startTime = Date.now();
      
      const response = await page.request.get(endpoint.path, {
        headers: { 'Authorization': 'Bearer test-token' }
      });
      
      const responseTime = Date.now() - startTime;
      
      expect(response.status()).toBeLessThan(400);
      expect(responseTime).toBeLessThan(endpoint.expectedTime);
      
      console.log(`${endpoint.path}: ${responseTime}ms (expected < ${endpoint.expectedTime}ms)`);
    }
  });

  test('Conversation response time under load', async ({ page }) => {
    await page.goto('/dashboard/conversations');
    
    // Create multiple conversations simultaneously
    const conversationPromises = [];
    const responseTimeTargets = [];
    
    for (let i = 0; i < 5; i++) {
      const promise = (async () => {
        await page.click('[data-testid="new-conversation"]');
        await page.selectOption('[data-testid="select-assistant"]', 'support');
        await page.click('[data-testid="start-conversation"]');
        
        const startTime = Date.now();
        await page.fill('[data-testid="message-input"]', `Performance test message ${i}`);
        await page.click('[data-testid="send-message"]');
        
        await expect(page.locator('[data-testid="ai-response"]')).toBeVisible({ timeout: 10000 });
        const responseTime = Date.now() - startTime;
        
        return responseTime;
      })();
      
      conversationPromises.push(promise);
    }
    
    const responseTimes = await Promise.all(conversationPromises);
    
    // All responses should be under 5 seconds
    responseTimes.forEach((time, index) => {
      expect(time).toBeLessThan(5000);
      console.log(`Conversation ${index + 1}: ${time}ms`);
    });
    
    // Average response time should be reasonable
    const averageTime = responseTimes.reduce((a, b) => a + b, 0) / responseTimes.length;
    expect(averageTime).toBeLessThan(3000);
    console.log(`Average response time: ${averageTime}ms`);
  });

  test('Page load performance', async ({ page }) => {
    const pages = [
      { path: '/dashboard', name: 'Dashboard' },
      { path: '/dashboard/conversations', name: 'Conversations' },
      { path: '/dashboard/assistants', name: 'Assistants' },
      { path: '/dashboard/knowledge', name: 'Knowledge Base' },
      { path: '/dashboard/analytics', name: 'Analytics' }
    ];
    
    for (const pageInfo of pages) {
      const startTime = Date.now();
      
      await page.goto(pageInfo.path);
      await page.waitForLoadState('networkidle');
      
      const loadTime = Date.now() - startTime;
      
      // Pages should load within 3 seconds
      expect(loadTime).toBeLessThan(3000);
      
      // Check for performance metrics
      const performanceMetrics = await page.evaluate(() => {
        const navigation = performance.getEntriesByType('navigation')[0];
        return {
          domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
          loadComplete: navigation.loadEventEnd - navigation.loadEventStart,
          firstPaint: performance.getEntriesByName('first-paint')[0]?.startTime || 0,
          firstContentfulPaint: performance.getEntriesByName('first-contentful-paint')[0]?.startTime || 0
        };
      });
      
      console.log(`${pageInfo.name} Performance:`, {
        totalLoad: loadTime,
        ...performanceMetrics
      });
      
      // First Contentful Paint should be under 1.5 seconds
      if (performanceMetrics.firstContentfulPaint > 0) {
        expect(performanceMetrics.firstContentfulPaint).toBeLessThan(1500);
      }
    }
  });

  test('Memory usage and leak detection', async ({ page }) => {
    await page.goto('/dashboard/conversations');
    
    // Get initial memory usage
    const initialMemory = await page.evaluate(() => {
      return performance.memory ? {
        usedJSHeapSize: performance.memory.usedJSHeapSize,
        totalJSHeapSize: performance.memory.totalJSHeapSize
      } : null;
    });
    
    if (!initialMemory) {
      console.log('Memory API not available, skipping memory tests');
      return;
    }
    
    // Simulate heavy usage
    for (let i = 0; i < 10; i++) {
      await page.click('[data-testid="new-conversation"]');
      await page.selectOption('[data-testid="select-assistant"]', 'support');
      await page.click('[data-testid="start-conversation"]');
      
      await page.fill('[data-testid="message-input"]', `Memory test message ${i}`);
      await page.click('[data-testid="send-message"]');
      
      await expect(page.locator('[data-testid="ai-response"]')).toBeVisible();
      
      // Close conversation
      await page.click('[data-testid="close-conversation"]');
    }
    
    // Force garbage collection if available
    await page.evaluate(() => {
      if (window.gc) {
        window.gc();
      }
    });
    
    // Wait a bit for cleanup
    await page.waitForTimeout(2000);
    
    const finalMemory = await page.evaluate(() => {
      return {
        usedJSHeapSize: performance.memory.usedJSHeapSize,
        totalJSHeapSize: performance.memory.totalJSHeapSize
      };
    });
    
    const memoryIncrease = finalMemory.usedJSHeapSize - initialMemory.usedJSHeapSize;
    const memoryIncreasePercent = (memoryIncrease / initialMemory.usedJSHeapSize) * 100;
    
    console.log('Memory Usage:', {
      initial: `${Math.round(initialMemory.usedJSHeapSize / 1024 / 1024)}MB`,
      final: `${Math.round(finalMemory.usedJSHeapSize / 1024 / 1024)}MB`,
      increase: `${Math.round(memoryIncrease / 1024 / 1024)}MB (${memoryIncreasePercent.toFixed(1)}%)`
    });
    
    // Memory increase should be reasonable (less than 50% increase)
    expect(memoryIncreasePercent).toBeLessThan(50);
  });

  test('Concurrent user simulation', async ({ browser }) => {
    const userCount = 3;
    const contexts = [];
    const pages = [];
    
    // Create multiple user contexts
    for (let i = 0; i < userCount; i++) {
      const context = await browser.newContext();
      await context.addInitScript(() => {
        localStorage.setItem('auth-token', `test-token-${i}`);
      });
      
      const page = await context.newPage();
      contexts.push(context);
      pages.push(page);
    }
    
    try {
      // Simulate concurrent user actions
      const userActions = pages.map(async (page, index) => {
        await page.goto('/dashboard/conversations');
        
        // Each user starts a conversation
        await page.click('[data-testid="new-conversation"]');
        await page.selectOption('[data-testid="select-assistant"]', 'support');
        await page.click('[data-testid="start-conversation"]');
        
        const startTime = Date.now();
        await page.fill('[data-testid="message-input"]', `Concurrent user ${index + 1} message`);
        await page.click('[data-testid="send-message"]');
        
        await expect(page.locator('[data-testid="ai-response"]')).toBeVisible({ timeout: 15000 });
        const responseTime = Date.now() - startTime;
        
        return { user: index + 1, responseTime };
      });
      
      const results = await Promise.all(userActions);
      
      // All users should get responses
      results.forEach(result => {
        expect(result.responseTime).toBeLessThan(10000); // 10 second timeout for concurrent load
        console.log(`User ${result.user}: ${result.responseTime}ms`);
      });
      
      const averageResponseTime = results.reduce((sum, r) => sum + r.responseTime, 0) / results.length;
      console.log(`Average concurrent response time: ${averageResponseTime}ms`);
      
      // Average should still be reasonable under concurrent load
      expect(averageResponseTime).toBeLessThan(7000);
      
    } finally {
      // Clean up contexts
      await Promise.all(contexts.map(context => context.close()));
    }
  });

  test('Database query performance', async ({ page }) => {
    await page.goto('/dashboard/analytics');
    
    // Test various data-heavy operations
    const operations = [
      { action: () => page.click('[data-testid="load-conversation-history"]'), name: 'Conversation History' },
      { action: () => page.click('[data-testid="load-usage-metrics"]'), name: 'Usage Metrics' },
      { action: () => page.click('[data-testid="load-assistant-performance"]'), name: 'Assistant Performance' },
      { action: () => page.click('[data-testid="export-analytics"]'), name: 'Export Analytics' }
    ];
    
    for (const operation of operations) {
      const startTime = Date.now();
      
      await operation.action();
      
      // Wait for data to load
      await expect(page.locator('[data-testid="data-loaded"]')).toBeVisible({ timeout: 10000 });
      
      const loadTime = Date.now() - startTime;
      
      console.log(`${operation.name}: ${loadTime}ms`);
      
      // Database operations should complete within 5 seconds
      expect(loadTime).toBeLessThan(5000);
    }
  });

  test('File upload performance', async ({ page }) => {
    await page.goto('/dashboard/knowledge');
    
    // Test different file sizes
    const fileSizes = [
      { size: 1024, name: '1KB file' },
      { size: 1024 * 100, name: '100KB file' },
      { size: 1024 * 1024, name: '1MB file' },
      { size: 1024 * 1024 * 5, name: '5MB file' }
    ];
    
    for (const fileInfo of fileSizes) {
      const fileContent = 'A'.repeat(fileInfo.size);
      
      const startTime = Date.now();
      
      await page.setInputFiles('[data-testid="file-upload"]', {
        name: `test-${fileInfo.name.replace(' ', '-')}.txt`,
        mimeType: 'text/plain',
        buffer: Buffer.from(fileContent)
      });
      
      await page.click('[data-testid="upload-document"]');
      
      // Wait for upload completion
      await expect(page.locator('[data-testid="upload-complete"]')).toBeVisible({ timeout: 30000 });
      
      const uploadTime = Date.now() - startTime;
      
      console.log(`${fileInfo.name} upload: ${uploadTime}ms`);
      
      // Upload time should be reasonable based on file size
      const expectedMaxTime = Math.max(2000, fileInfo.size / 1024); // 1ms per KB minimum 2s
      expect(uploadTime).toBeLessThan(expectedMaxTime);
    }
  });

  test('WebSocket connection performance', async ({ page }) => {
    await page.goto('/dashboard/conversations');
    
    // Monitor WebSocket messages
    const wsMessages = [];
    
    page.on('websocket', ws => {
      ws.on('framereceived', event => {
        wsMessages.push({
          type: 'received',
          payload: event.payload,
          timestamp: Date.now()
        });
      });
      
      ws.on('framesent', event => {
        wsMessages.push({
          type: 'sent',
          payload: event.payload,
          timestamp: Date.now()
        });
      });
    });
    
    // Start conversation with WebSocket
    await page.click('[data-testid="new-conversation"]');
    await page.selectOption('[data-testid="select-assistant"]', 'support');
    await page.click('[data-testid="start-conversation"]');
    
    const messageStartTime = Date.now();
    await page.fill('[data-testid="message-input"]', 'WebSocket performance test');
    await page.click('[data-testid="send-message"]');
    
    await expect(page.locator('[data-testid="ai-response"]')).toBeVisible();
    const messageEndTime = Date.now();
    
    const totalMessageTime = messageEndTime - messageStartTime;
    console.log(`WebSocket message round-trip: ${totalMessageTime}ms`);
    
    // WebSocket should be faster than HTTP polling
    expect(totalMessageTime).toBeLessThan(3000);
    
    // Check WebSocket message flow
    const sentMessages = wsMessages.filter(m => m.type === 'sent');
    const receivedMessages = wsMessages.filter(m => m.type === 'received');
    
    expect(sentMessages.length).toBeGreaterThan(0);
    expect(receivedMessages.length).toBeGreaterThan(0);
    
    // Calculate WebSocket latency
    if (sentMessages.length > 0 && receivedMessages.length > 0) {
      const latency = receivedMessages[0].timestamp - sentMessages[0].timestamp;
      console.log(`WebSocket latency: ${latency}ms`);
      expect(latency).toBeLessThan(1000);
    }
  });

  test('Resource usage monitoring', async ({ page }) => {
    await page.goto('/dashboard');
    
    // Monitor network requests
    const networkRequests = [];
    page.on('request', request => {
      networkRequests.push({
        url: request.url(),
        method: request.method(),
        resourceType: request.resourceType(),
        timestamp: Date.now()
      });
    });
    
    // Navigate through different sections
    const sections = [
      '/dashboard/conversations',
      '/dashboard/assistants',
      '/dashboard/knowledge',
      '/dashboard/analytics',
      '/dashboard/billing'
    ];
    
    for (const section of sections) {
      await page.goto(section);
      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(1000); // Allow for any delayed requests
    }
    
    // Analyze network usage
    const apiRequests = networkRequests.filter(r => r.url.includes('/api/'));
    const staticRequests = networkRequests.filter(r => 
      r.resourceType === 'stylesheet' || 
      r.resourceType === 'script' || 
      r.resourceType === 'image'
    );
    
    console.log('Network Usage:', {
      totalRequests: networkRequests.length,
      apiRequests: apiRequests.length,
      staticRequests: staticRequests.length
    });
    
    // Should not make excessive API requests
    expect(apiRequests.length).toBeLessThan(50);
    
    // Should cache static resources
    const duplicateStatic = staticRequests.filter((request, index, arr) => 
      arr.findIndex(r => r.url === request.url) !== index
    );
    expect(duplicateStatic.length).toBeLessThan(5); // Allow some duplicates but not many
  });
});
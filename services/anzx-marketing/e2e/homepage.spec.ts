import { test, expect } from '@playwright/test';

test.describe('Homepage', () => {
  test('should load homepage successfully', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle(/ANZX/);
  });

  test('should display hero section', async ({ page }) => {
    await page.goto('/');
    const hero = page.locator('h1').first();
    await expect(hero).toBeVisible();
  });

  test('should navigate to product pages', async ({ page }) => {
    await page.goto('/');
    
    // Click on AI Interviewer link
    await page.click('text=AI Interviewer');
    await expect(page).toHaveURL(/ai-interviewer/);
  });

  test('should switch language', async ({ page }) => {
    await page.goto('/');
    
    // Click language switcher
    const langSwitcher = page.locator('[data-testid="language-switcher"]');
    if (await langSwitcher.isVisible()) {
      await langSwitcher.click();
      await page.click('text=Hindi');
      await expect(page).toHaveURL(/\/hi\//);
    }
  });

  test('should be responsive on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');
    
    const hero = page.locator('h1').first();
    await expect(hero).toBeVisible();
  });
});

test.describe('Demo Request Flow', () => {
  test('should complete demo request', async ({ page }) => {
    await page.goto('/ai-interviewer');
    
    // Fill demo form
    await page.fill('[name="name"]', 'Test User');
    await page.fill('[name="email"]', 'test@example.com');
    await page.fill('[name="company"]', 'Test Company');
    
    // Submit form
    await page.click('button[type="submit"]');
    
    // Check for success message
    await expect(page.locator('text=/thank you|success/i')).toBeVisible({ timeout: 5000 });
  });
});

test.describe('Blog Navigation', () => {
  test('should navigate blog posts', async ({ page }) => {
    await page.goto('/blog');
    
    // Click on first blog post
    const firstPost = page.locator('article').first();
    await firstPost.click();
    
    // Should navigate to blog post
    await expect(page).toHaveURL(/\/blog\/.+/);
  });

  test('should filter blog by category', async ({ page }) => {
    await page.goto('/blog');
    
    // Click category filter
    const categoryFilter = page.locator('[data-testid="category-filter"]');
    if (await categoryFilter.isVisible()) {
      await categoryFilter.click();
      await page.click('text=AI Agents');
      
      // Should filter posts
      const posts = page.locator('article');
      await expect(posts.first()).toBeVisible();
    }
  });
});

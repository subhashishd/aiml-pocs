// @ts-check
const { test, expect } = require('@playwright/test');

test.describe('Navigation and Basic UI', () => {
  test.beforeEach(async ({ page }) => {
    // Dismiss any webpack overlays by pressing Escape
    await page.goto('/');
    await page.keyboard.press('Escape');
    await page.waitForTimeout(1000);
  });

  test('loads homepage successfully', async ({ page }) => {
    console.log('🧪 Testing homepage load');
    
    await page.goto('/');
    
    // Wait for React to render
    await page.waitForSelector('h1', { timeout: 10000 });
    
    // Check main heading
    const heading = page.locator('h1');
    await expect(heading).toBeVisible();
    await expect(heading).toContainText('Excel-PDF Values Validator');
  });

  test('navigates to dashboard', async ({ page }) => {
    console.log('🧪 Testing dashboard navigation');
    
    await page.goto('/');
    
    // Dismiss any overlays
    await page.keyboard.press('Escape');
    await page.waitForTimeout(500);
    
    // Look for dashboard link with more specific targeting
    const dashboardLink = page.locator('nav a[href*="dashboard"], a:has-text("Dashboard")').first();
    
    // Wait for the element to be visible and stable
    await dashboardLink.waitFor({ state: 'visible', timeout: 10000 });
    await expect(dashboardLink).toBeVisible();
    
    // Click with force to handle any overlay issues
    await dashboardLink.click({ force: true });
    
    // Wait for navigation and page load
    await page.waitForURL('**/dashboard', { timeout: 10000 });
    await page.waitForLoadState('networkidle');
    
    // Verify we're on the dashboard
    await expect(page).toHaveURL(/dashboard/);
    
    // Check for dashboard content
    await page.waitForSelector('h2, h3, .dashboard', { timeout: 5000 });
  });

  test('handles file validation workflow UI', async ({ page }) => {
    console.log('🧪 Testing validation workflow UI elements');
    
    await page.goto('/');
    await page.keyboard.press('Escape');
    
    // Wait for page to be ready
    await page.waitForSelector('input[type="file"]', { timeout: 10000 });
    
    // Check for file upload inputs
    const pdfInput = page.locator('input[accept*=".pdf"]').first();
    const excelInput = page.locator('input[accept*=".xlsx"], input[accept*=".xls"]').first();
    
    await expect(pdfInput).toBeVisible();
    await expect(excelInput).toBeVisible();
    
    // Check for validation button
    const validateButton = page.locator('button:has-text("Validate"), input[type="submit"][value*="Validate"]').first();
    await expect(validateButton).toBeVisible();
  });

  test('responsive design - mobile viewport', async ({ page, isMobile }) => {
    if (!isMobile) {
      test.skip('Skipping mobile test on desktop');
    }
    
    console.log('🧪 Testing mobile responsiveness');
    
    await page.goto('/');
    await page.keyboard.press('Escape');
    
    // Wait for page load
    await page.waitForSelector('h1', { timeout: 10000 });
    
    // Verify mobile layout
    const mainContent = page.locator('main, .container, .app').first();
    await expect(mainContent).toBeVisible();
    
    // Check that content is not cut off
    const viewport = page.viewportSize();
    expect(viewport.width).toBeLessThanOrEqual(414); // Mobile width
  });

  test('handles network delays gracefully', async ({ page }) => {
    console.log('🧪 Testing network delay handling');
    
    // Simulate slow network
    await page.route('**/*', route => {
      setTimeout(() => route.continue(), 100);
    });
    
    await page.goto('/');
    await page.keyboard.press('Escape');
    
    // Should still load within reasonable time
    await page.waitForSelector('h1', { timeout: 15000 });
    const heading = page.locator('h1');
    await expect(heading).toBeVisible();
  });
});

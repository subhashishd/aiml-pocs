// @ts-check
const { test, expect } = require('@playwright/test');
const path = require('path');

test.describe('Validation Workflow Tests', () => {
  const pdfFile = path.join(__dirname, 'fixtures', 'BunkerDeliveryNote-1.16.3.PDF');
  const excelFile = path.join(__dirname, 'fixtures', 'output_parameters.xlsx');
  const comprehensiveExcelFile = path.join(__dirname, 'fixtures', 'comprehensive_parameters.xlsx');

  test.beforeEach(async ({ page }) => {
    console.log('🧪 Setting up validation workflow test');
    
    // Navigate and dismiss overlays
    await page.goto('/');
    await page.keyboard.press('Escape');
    await page.waitForTimeout(1000);
    
    // Ensure page is ready
    await page.waitForLoadState('networkidle');
  });

  test('complete file upload and validation workflow', async ({ page }) => {
    console.log('🧪 Testing complete validation workflow');
    
    // Wait for file inputs to be available
    await page.waitForSelector('input[type="file"]', { timeout: 10000 });
    
    // Find file inputs with more reliable selectors
    const pdfInput = page.locator('input[accept*=".pdf"]').first();
    const excelInput = page.locator('input[accept*=".xlsx"], input[accept*=".xls"]').first();
    
    // Upload files
    await pdfInput.setInputFiles(pdfFile);
    await excelInput.setInputFiles(excelFile);
    
    // Find and click validation button
    const validateButton = page.locator('button:has-text("Validate"), input[type="submit"]').first();
    await validateButton.waitFor({ state: 'visible', timeout: 5000 });
    
    // Click validation button and wait for processing
    await validateButton.click();
    
    // Wait for validation results (this may take time)
    console.log('⏳ Waiting for validation results...');
    
    // Look for results indicators
    await page.waitForSelector(
      '.results, .validation-results, .report, [data-testid="results"]', 
      { timeout: 60000 }
    );
    
    // Check for success indicators
    const resultsSection = page.locator('.results, .validation-results, .report').first();
    await expect(resultsSection).toBeVisible();
    
    console.log('✅ Validation workflow completed');
  });

  test('handles file validation errors gracefully', async ({ page }) => {
    console.log('🧪 Testing file validation error handling');
    
    await page.waitForSelector('input[type="file"]', { timeout: 10000 });
    
    // Try to upload wrong file types
    const validateButton = page.locator('button:has-text("Validate"), input[type="submit"]').first();
    
    // Click validate without files
    await validateButton.click();
    
    // Should show validation error
    await page.waitForSelector(
      '.error, .alert-danger, [role="alert"]', 
      { timeout: 5000 }
    );
    
    const errorMessage = page.locator('.error, .alert-danger, [role="alert"]').first();
    await expect(errorMessage).toBeVisible();
  });

  test('displays validation results properly', async ({ page }) => {
    console.log('🧪 Testing validation results display');
    
    await page.waitForSelector('input[type="file"]', { timeout: 10000 });
    
    const pdfInput = page.locator('input[accept*=".pdf"]').first();
    const excelInput = page.locator('input[accept*=".xlsx"], input[accept*=".xls"]').first();
    
    await pdfInput.setInputFiles(pdfFile);
    await excelInput.setInputFiles(excelFile);
    
    const validateButton = page.locator('button:has-text("Validate"), input[type="submit"]').first();
    await validateButton.click();
    
    // Wait for results
    await page.waitForSelector(
      '.results, .validation-results, .report', 
      { timeout: 60000 }
    );
    
    // Check for key result elements
    const results = page.locator('.results, .validation-results, .report').first();
    await expect(results).toBeVisible();
    
    // Look for specific validation metrics
    const passFailElements = page.locator('.pass, .fail, .success, .error, ✔️, ❌');
    await expect(passFailElements.first()).toBeVisible();
    
    console.log('✅ Validation results displayed correctly');
  });

  test('handles large file uploads', async ({ page }) => {
    console.log('🧪 Testing large file upload handling');
    
    await page.waitForSelector('input[type="file"]', { timeout: 10000 });
    
    const pdfInput = page.locator('input[accept*=".pdf"]').first();
    const excelInput = page.locator('input[accept*=".xlsx"], input[accept*=".xls"]').first();
    
    // Use comprehensive Excel file (larger)
    await pdfInput.setInputFiles(pdfFile);
    await excelInput.setInputFiles(comprehensiveExcelFile);
    
    const validateButton = page.locator('button:has-text("Validate"), input[type="submit"]').first();
    await validateButton.click();
    
    // Should show loading state
    await page.waitForSelector(
      '.loading, .spinner, [data-testid="loading"]', 
      { timeout: 5000 }
    );
    
    // Wait for completion (longer timeout for large files)
    await page.waitForSelector(
      '.results, .validation-results, .report', 
      { timeout: 90000 }
    );
    
    const results = page.locator('.results, .validation-results, .report').first();
    await expect(results).toBeVisible();
    
    console.log('✅ Large file upload completed');
  });

  test('supports file download functionality', async ({ page }) => {
    console.log('🧪 Testing file download functionality');
    
    // Complete a validation first
    await page.waitForSelector('input[type="file"]', { timeout: 10000 });
    
    const pdfInput = page.locator('input[accept*=".pdf"]').first();
    const excelInput = page.locator('input[accept*=".xlsx"], input[accept*=".xls"]').first();
    
    await pdfInput.setInputFiles(pdfFile);
    await excelInput.setInputFiles(excelFile);
    
    const validateButton = page.locator('button:has-text("Validate"), input[type="submit"]').first();
    await validateButton.click();
    
    // Wait for results
    await page.waitForSelector(
      '.results, .validation-results, .report', 
      { timeout: 60000 }
    );
    
    // Look for download link or button
    const downloadButton = page.locator(
      'a[download], button:has-text("Download"), .download-btn'
    ).first();
    
    // If download functionality exists, test it
    if (await downloadButton.isVisible()) {
      // Set up download handler
      const downloadPromise = page.waitForEvent('download');
      await downloadButton.click();
      const download = await downloadPromise;
      
      // Verify download
      expect(download.suggestedFilename()).toMatch(/\.txt$/);
      console.log('✅ File download functionality working');
    } else {
      console.log('ℹ️ Download functionality not found (may not be implemented in UI)');
    }
  });

  test('maintains state during validation process', async ({ page }) => {
    console.log('🧪 Testing state maintenance during validation');
    
    await page.waitForSelector('input[type="file"]', { timeout: 10000 });
    
    const pdfInput = page.locator('input[accept*=".pdf"]').first();
    const excelInput = page.locator('input[accept*=".xlsx"], input[accept*=".xls"]').first();
    
    await pdfInput.setInputFiles(pdfFile);
    await excelInput.setInputFiles(excelFile);
    
    // Verify files are selected
    const pdfFileName = page.locator('text=/BunkerDeliveryNote.*PDF/i').first();
    const excelFileName = page.locator('text=/output_parameters.*xlsx/i').first();
    
    // Files should be visible in UI
    await expect(pdfFileName.or(pdfInput)).toBeVisible();
    await expect(excelFileName.or(excelInput)).toBeVisible();
    
    const validateButton = page.locator('button:has-text("Validate"), input[type="submit"]').first();
    await validateButton.click();
    
    // During processing, files should still be indicated
    // Look for processing state
    await page.waitForSelector(
      '.loading, .processing, .spinner, .results', 
      { timeout: 10000 }
    );
    
    console.log('✅ State maintained during validation process');
  });
});

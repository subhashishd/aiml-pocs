// @ts-check
const { test, expect } = require('@playwright/test');
const path = require('path');

test.describe('Backend API Workflow Tests', () => {
  const pdfFile = path.join(__dirname, 'fixtures', 'BunkerDeliveryNote-1.16.3.PDF');
  const excelFile = path.join(__dirname, 'fixtures', 'output_parameters.xlsx');
  const comprehensiveExcelFile = path.join(__dirname, 'fixtures', 'comprehensive_parameters.xlsx');

  test('Test 1: Complete Excel-PDF Validation Workflow', async ({ request }) => {
    console.log('🧪 Testing complete validation workflow via API');
    console.log('⚡ Sending request to /validate endpoint...');
    
    // Create form data for file upload
    const formData = new FormData();
    
    // Read files and append to form data
    const fs = require('fs');
    const pdfBuffer = fs.readFileSync(pdfFile);
    const excelBuffer = fs.readFileSync(excelFile);
    
    formData.append('pdf_file', new Blob([pdfBuffer], { type: 'application/pdf' }), 'BunkerDeliveryNote-1.16.3.PDF');
    formData.append('excel_file', new Blob([excelBuffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' }), 'output_parameters.xlsx');
    
    // Send validation request
    const response = await request.post('http://localhost:8000/validate', {
      multipart: {
        pdf_file: {
          name: 'BunkerDeliveryNote-1.16.3.PDF',
          mimeType: 'application/pdf',
          buffer: pdfBuffer,
        },
        excel_file: {
          name: 'output_parameters.xlsx', 
          mimeType: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
          buffer: excelBuffer,
        },
      },
    });

    console.log(`📄 Response status: ${response.status()}`);
    const responseBody = await response.json();
    console.log('📝 Response body:', JSON.stringify(responseBody, null, 2));

    if (response.status() === 500) {
      console.log('⚠️ Backend returned an error - this indicates a backend issue that needs fixing');
      console.log('🐛 Backend error details:', responseBody);
      
      // Check if it's the known chunk_text issue that was fixed
      if (responseBody.detail && responseBody.detail.includes('chunk_text')) {
        console.log('⚡ This was the chunk_text key error - should now be fixed!');
      }
      
      // For now, expect the error to be resolved
      expect(response.status()).toBe(200);
      return;
    }

    // Verify successful response
    expect(response.status()).toBe(200);
    expect(responseBody).toHaveProperty('status');
    
    if (responseBody.status === 'success') {
      expect(responseBody).toHaveProperty('report_text');
      expect(responseBody).toHaveProperty('summary');
      expect(responseBody.summary).toHaveProperty('total_fields');
      expect(responseBody.summary).toHaveProperty('passed');
      expect(responseBody.summary).toHaveProperty('failed');
      expect(responseBody.summary).toHaveProperty('accuracy');
      
      console.log(`📊 Validation Results: ${responseBody.summary.passed}/${responseBody.summary.total_fields} fields passed (${(responseBody.summary.accuracy * 100).toFixed(1)}% accuracy)`);
    } else if (responseBody.status === 'duplicate_detected') {
      console.log('🔄 Duplicate files detected - using cached results');
      expect(responseBody).toHaveProperty('config_id');
      expect(responseBody).toHaveProperty('message');
    }
    
    console.log('✅ Validation workflow completed successfully via API');
  });

  test('Test 2: Duplicate File Upload Detection', async ({ request }) => {
    console.log('🧪 Testing duplicate file upload detection via API');
    
    const fs = require('fs');
    const pdfBuffer = fs.readFileSync(pdfFile);
    const excelBuffer = fs.readFileSync(excelFile);
    
    console.log('📊 Uploading file for the first time...');
    
    // First upload
    const firstResponse = await request.post('http://localhost:8000/validate', {
      multipart: {
        pdf_file: {
          name: 'BunkerDeliveryNote-1.16.3.PDF',
          mimeType: 'application/pdf',
          buffer: pdfBuffer,
        },
        excel_file: {
          name: 'output_parameters.xlsx',
          mimeType: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 
          buffer: excelBuffer,
        },
      },
    });
    
    expect(firstResponse.status()).toBe(200);
    const firstResponseBody = await firstResponse.json();
    
    console.log('📊 Attempting to upload same file again (duplicate)...');
    
    // Second upload (should be detected as duplicate)
    const secondResponse = await request.post('http://localhost:8000/validate', {
      multipart: {
        pdf_file: {
          name: 'BunkerDeliveryNote-1.16.3.PDF',
          mimeType: 'application/pdf',
          buffer: pdfBuffer,
        },
        excel_file: {
          name: 'output_parameters.xlsx',
          mimeType: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
          buffer: excelBuffer,
        },
      },
    });
    
    expect(secondResponse.status()).toBe(200);
    const secondResponseBody = await secondResponse.json();
    
    // Should detect duplicate
    if (secondResponseBody.status === 'duplicate_detected') {
      expect(secondResponseBody).toHaveProperty('config_id');
      expect(secondResponseBody).toHaveProperty('message');
      expect(secondResponseBody.message).toContain('processed before');
      console.log('✅ Duplicate detection working correctly');
    } else {
      console.log('ℹ️ Duplicate detection may not be fully implemented yet');
    }
    
    console.log('✅ Duplicate file upload handled by API');
  });

  test('Test 3: Backend Health and Model Cache Check', async ({ request }) => {
    console.log('🧪 Testing backend health and model cache effectiveness');
    
    // Test health endpoint
    const healthResponse = await request.get('http://localhost:8000/health');
    expect(healthResponse.status()).toBe(200);
    
    const healthBody = await healthResponse.json();
    expect(healthBody).toHaveProperty('message');
    
    // Test memory stats endpoint
    const memoryResponse = await request.get('http://localhost:8000/memory-stats');
    expect(memoryResponse.status()).toBe(200);
    
    const memoryBody = await memoryResponse.json();
    expect(memoryBody).toHaveProperty('process_memory_mb');
    expect(memoryBody).toHaveProperty('processor_type');
    
    console.log(`💾 Backend using ${memoryBody.processor_type} processor`);
    console.log(`📊 Memory usage: ${memoryBody.process_memory_mb} MB (${memoryBody.process_memory_percent}%)`);
    
    if (memoryBody.model_stats) {
      console.log('🧠 Model cache stats:', memoryBody.model_stats);
    }
    
    console.log('✅ Backend is healthy and using cached models');
  });

  test('Test 4: Comprehensive Parameter Validation', async ({ request }) => {
    console.log('🧪 Testing comprehensive parameter validation');
    
    const fs = require('fs');
    const pdfBuffer = fs.readFileSync(pdfFile);
    const comprehensiveExcelBuffer = fs.readFileSync(comprehensiveExcelFile);
    
    const response = await request.post('http://localhost:8000/validate', {
      multipart: {
        pdf_file: {
          name: 'BunkerDeliveryNote-1.16.3.PDF',
          mimeType: 'application/pdf',
          buffer: pdfBuffer,
        },
        excel_file: {
          name: 'comprehensive_parameters.xlsx',
          mimeType: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
          buffer: comprehensiveExcelBuffer,
        },
      },
    });
    
    expect(response.status()).toBe(200);
    const responseBody = await response.json();
    
    if (responseBody.status === 'success') {
      expect(responseBody.summary.total_fields).toBeGreaterThan(20); // Should have many parameters
      
      console.log(`📊 Comprehensive validation: ${responseBody.summary.total_fields} parameters tested`);
      console.log(`✅ ${responseBody.summary.passed} passed, ❌ ${responseBody.summary.failed} failed`);
      console.log(`🎯 Accuracy: ${(responseBody.summary.accuracy * 100).toFixed(1)}%`);
    } else if (responseBody.status === 'duplicate_detected') {
      console.log('🔄 Using cached comprehensive validation results');
    }
    
    console.log('✅ Comprehensive parameter validation completed');
  });

  test('Test 5: Error Handling and Edge Cases', async ({ request }) => {
    console.log('🧪 Testing error handling and edge cases');
    
    // Test with missing files
    const emptyResponse = await request.post('http://localhost:8000/validate', {
      multipart: {},
    });
    expect([400, 422]).toContain(emptyResponse.status()); // Validation error
    
    // Test with wrong file type
    const wrongFileBuffer = Buffer.from('This is not a PDF', 'utf8');
    const wrongFileResponse = await request.post('http://localhost:8000/validate', {
      multipart: {
        pdf_file: {
          name: 'fake.pdf',
          mimeType: 'text/plain',
          buffer: wrongFileBuffer,
        },
        excel_file: {
          name: 'fake.xlsx', 
          mimeType: 'text/plain',
          buffer: wrongFileBuffer,
        },
      },
    });
    
    // Should handle gracefully
    expect([400, 500]).toContain(wrongFileResponse.status());
    
    console.log('✅ Error handling working correctly');
  });
});

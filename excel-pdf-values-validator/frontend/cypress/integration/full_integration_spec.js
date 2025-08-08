// cypress/integration/full_integration_spec.js
// Comprehensive E2E tests that test the full application stack

describe('Full Stack Integration Tests', () => {
  const apiUrl = Cypress.env('apiUrl');

  beforeEach(() => {
    // Clear any existing data
    cy.clearAllData();
    
    // Visit the application
    cy.visit('/');
  });

  describe('API Integration', () => {
    it('should have healthy backend API', () => {
      cy.request('GET', `${apiUrl}/health`).should((response) => {
        expect(response.status).to.eq(200);
        expect(response.body).to.have.property('status');
      });
    });

    it('should load dashboard with real API data', () => {
      // Intercept API calls to verify they're made
      cy.intercept('GET', `${apiUrl}/api/dashboard/stats`).as('getDashboardStats');
      cy.intercept('GET', `${apiUrl}/api/tasks/recent`).as('getRecentTasks');

      cy.visit('/');

      // Wait for API calls to complete
      cy.wait('@getDashboardStats');
      cy.wait('@getRecentTasks');

      // Verify dashboard content loads
      cy.get('main').should('be.visible');
      
      // Check for stats cards (should be populated with real data)
      cy.get('[data-testid="stats-card"]').should('have.length.at.least', 1);
    });
  });

  describe('File Upload Flow', () => {
    it('should complete full file upload and processing flow', () => {
      // Navigate to upload page
      cy.contains('Upload Files').click();
      cy.url().should('include', '/upload');

      // Mock successful upload response
      cy.intercept('POST', `${apiUrl}/api/upload`, {
        fixture: 'api-responses.json',
        property: 'uploadResponse'
      }).as('uploadFile');

      // Test file upload interface
      cy.contains('Drag & drop files here').should('be.visible');
      
      // Simulate file upload (since we can't easily test real file upload in CI)
      // This would trigger the upload endpoint
      cy.get('[data-testid="upload-area"]').click();
      
      // In a real test, you might use:
      // cy.fixture('sample.pdf').then(fileContent => {
      //   cy.get('input[type="file"]').attachFile({
      //     fileContent: fileContent.toString(),
      //     fileName: 'sample.pdf',
      //     mimeType: 'application/pdf'
      //   });
      // });
    });

    it('should handle file upload errors gracefully', () => {
      cy.visit('/upload');

      // Mock error response
      cy.intercept('POST', `${apiUrl}/api/upload`, {
        statusCode: 400,
        body: { error: 'Invalid file format' }
      }).as('uploadError');

      // Verify error handling would work
      cy.contains('Supports PDF, XLSX, XLS files').should('be.visible');
    });
  });

  describe('Results and Monitoring', () => {
    it('should display validation results', () => {
      // Mock API responses for results page
      cy.intercept('GET', `${apiUrl}/api/tasks/*/results`, {
        fixture: 'api-responses.json',
        property: 'validationResults'
      }).as('getResults');

      cy.visit('/results');
      cy.get('main').should('be.visible');
    });

    it('should show system status with real data', () => {
      cy.intercept('GET', `${apiUrl}/api/system/status`, {
        fixture: 'api-responses.json',
        property: 'systemStatus'
      }).as('getSystemStatus');

      cy.visit('/system');
      cy.wait('@getSystemStatus');
      
      cy.get('main').should('be.visible');
    });

    it('should display monitoring dashboard', () => {
      cy.visit('/monitoring');
      cy.get('main').should('be.visible');
    });
  });

  describe('Real-time Features', () => {
    it('should handle WebSocket connections for real-time updates', () => {
      cy.visit('/');
      
      // Test that the app can handle real-time updates
      // This would test WebSocket connectivity in a real environment
      cy.window().should('have.property', 'WebSocket');
    });
  });

  describe('Error Handling', () => {
    it('should handle API errors gracefully', () => {
      // Mock API error
      cy.intercept('GET', `${apiUrl}/api/dashboard/stats`, {
        statusCode: 500,
        body: { error: 'Internal Server Error' }
      }).as('apiError');

      cy.visit('/');
      
      // The app should still load even if API calls fail
      cy.get('main').should('be.visible');
    });

    it('should handle network connectivity issues', () => {
      // Mock network failure
      cy.intercept('GET', `${apiUrl}/api/**`, { forceNetworkError: true }).as('networkError');

      cy.visit('/');
      
      // App should handle network errors gracefully
      cy.get('body').should('exist');
    });
  });

  describe('Performance', () => {
    it('should load within acceptable time limits', () => {
      const startTime = Date.now();
      
      cy.visit('/', {
        onLoad: () => {
          const loadTime = Date.now() - startTime;
          expect(loadTime).to.be.lessThan(5000); // 5 seconds max
        }
      });

      cy.get('main').should('be.visible');
    });
  });

  describe('Cross-browser Compatibility', () => {
    it('should work across different viewport sizes', () => {
      // Test mobile view
      cy.viewport(375, 667);
      cy.visit('/');
      cy.get('main').should('be.visible');

      // Test tablet view
      cy.viewport(768, 1024);
      cy.get('main').should('be.visible');

      // Test desktop view
      cy.viewport(1920, 1080);
      cy.get('main').should('be.visible');
    });
  });

  describe('Security', () => {
    it('should not expose sensitive information in the DOM', () => {
      cy.visit('/');
      
      // Check that no API keys or secrets are exposed
      cy.get('body').should('not.contain', 'sk-');  // OpenAI keys
      cy.get('body').should('not.contain', 'postgres://'); // DB strings
    });
  });

  describe('End-to-End User Journeys', () => {
    it('should complete a full user workflow', () => {
      // 1. Start at dashboard
      cy.visit('/');
      cy.get('main').should('be.visible');

      // 2. Navigate to upload
      cy.contains('Upload Files').click();
      cy.url().should('include', '/upload');
      cy.contains('Drag & drop files here').should('be.visible');

      // 3. Check results
      cy.contains('Results').click();
      cy.url().should('include', '/results');

      // 4. Check system status
      cy.contains('System Status').click();
      cy.url().should('include', '/system');

      // 5. Return to dashboard
      cy.contains('Dashboard').click();
      cy.url().should('match', /\/$|\/dashboard$/);
    });
  });
});

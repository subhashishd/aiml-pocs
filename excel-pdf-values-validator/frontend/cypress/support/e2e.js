// cypress/support/e2e.js
// Load commands
import './commands';

// Alternatively you can use CommonJS syntax:
// require('./commands')

// Global configuration
Cypress.on('uncaught:exception', (err, runnable) => {
  // Returning false here prevents Cypress from failing the test
  // on uncaught exceptions from the application under test
  console.log('Uncaught exception:', err.message);
  return false;
});

// Add custom commands
Cypress.Commands.add('waitForAppLoad', () => {
  cy.get('body').should('exist');
  cy.get('[data-testid="app-loaded"]').should('exist', { timeout: 15000 });
});

Cypress.Commands.add('checkApiHealth', () => {
  const apiUrl = Cypress.env('apiUrl');
  cy.request('GET', `${apiUrl}/health`).should((response) => {
    expect(response.status).to.eq(200);
  });
});

// Wait for backend to be ready
beforeEach(() => {
  // Check API health before each test
  cy.checkApiHealth();
});

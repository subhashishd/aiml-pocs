// cypress/support/commands.js

// Custom command to upload files
Cypress.Commands.add('uploadFile', (fileName, fileType = '', selector = 'input[type="file"]') => {
  cy.fixture(fileName).then(fileContent => {
    cy.get(selector).then(subject => {
      const el = subject[0];
      const blob = new Blob([fileContent], { type: fileType });
      const file = new File([blob], fileName, { type: fileType });
      
      const dataTransfer = new DataTransfer();
      dataTransfer.items.add(file);
      
      el.files = dataTransfer.files;
      el.dispatchEvent(new Event('change', { bubbles: true }));
    });
  });
});

// Custom command to wait for API response
Cypress.Commands.add('waitForApiCall', (method, url, alias) => {
  cy.intercept(method, url).as(alias);
  cy.wait(`@${alias}`);
});

// Custom command to login (if authentication is needed)
Cypress.Commands.add('login', (email = 'test@example.com', password = 'password') => {
  const apiUrl = Cypress.env('apiUrl');
  
  cy.request({
    method: 'POST',
    url: `${apiUrl}/auth/login`,
    body: { email, password },
  }).then((response) => {
    window.localStorage.setItem('authToken', response.body.access_token);
  });
});

// Custom command to clear all data
Cypress.Commands.add('clearAllData', () => {
  cy.window().then((win) => {
    win.localStorage.clear();
    win.sessionStorage.clear();
  });
  
  // Clear cookies
  cy.clearCookies();
});

// Custom command for drag and drop
Cypress.Commands.add('dragAndDrop', (dragSelector, dropSelector) => {
  cy.get(dragSelector).trigger('mousedown', { which: 1 });
  cy.get(dropSelector).trigger('mousemove').trigger('mouseup');
});

// Custom command to check accessibility
Cypress.Commands.add('checkA11y', () => {
  cy.injectAxe();
  cy.checkA11y();
});

// Add command for network stubbing
Cypress.Commands.add('stubApiCall', (method, url, response, statusCode = 200) => {
  cy.intercept(method, url, {
    statusCode,
    body: response,
  });
});

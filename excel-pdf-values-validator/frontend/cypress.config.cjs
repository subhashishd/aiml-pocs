const { defineConfig } = require('cypress');

module.exports = defineConfig({
  e2e: {
    baseUrl: process.env.CYPRESS_baseUrl || 'http://localhost:3000',
    specPattern: 'cypress/integration/**/*.js',
    supportFile: 'cypress/support/e2e.js',
    viewportWidth: 1280,
    viewportHeight: 720,
    video: true,
    screenshotOnRunFailure: true,
    defaultCommandTimeout: 10000,
    requestTimeout: 15000,
    responseTimeout: 15000,
    env: {
      apiUrl: process.env.CYPRESS_apiUrl || 'http://localhost:8000',
    },
    retries: {
      runMode: 2,
      openMode: 0,
    },
  },
});


// @ts-check

async function globalTeardown() {
  console.log('🧹 Cleaning up after E2E tests...');
  
  // Any cleanup logic can go here
  // For now, just log completion
  
  console.log('✅ E2E test cleanup complete');
}

module.exports = globalTeardown;

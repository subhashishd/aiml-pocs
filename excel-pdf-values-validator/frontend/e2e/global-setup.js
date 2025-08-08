// @ts-check
const { chromium } = require('@playwright/test');
const { spawn, exec } = require('child_process');
const { promisify } = require('util');
const execAsync = promisify(exec);
const fs = require('fs');
const path = require('path');

async function globalSetup() {
  console.log('🚀 Starting E2E test setup...');
  
  // Check if test fixtures exist
  const fixturesDir = path.join(__dirname, 'fixtures');
  const requiredFixtures = [
    'output_parameters.xlsx',
    'BunkerDeliveryNote-1.16.3.PDF'
  ];

  if (!fs.existsSync(fixturesDir)) {
    fs.mkdirSync(fixturesDir, { recursive: true });
  }

  // Check and copy fixtures from main files directory if they don't exist
  for (const fixture of requiredFixtures) {
    const fixturePath = path.join(fixturesDir, fixture);
    const sourcePath = path.join(__dirname, '../../files', fixture);
    
    if (!fs.existsSync(fixturePath)) {
      if (fs.existsSync(sourcePath)) {
        fs.copyFileSync(sourcePath, fixturePath);
        console.log(`✅ Copied fixture: ${fixture}`);
      } else {
        console.warn(`⚠️ Warning: Test fixture ${fixture} not found in source`);
      }
    } else {
      console.log(`✅ Test fixture found: ${fixture}`);
    }
  }

  // Wait for services to be ready
  console.log('⏳ Waiting for services to start...');
  
  // Check frontend service
  let frontendReady = false;
  for (let i = 0; i < 30; i++) {
    try {
      const response = await fetch('http://localhost:3000');
      if (response.ok) {
        frontendReady = true;
        console.log('✅ Frontend service ready');
        break;
      }
    } catch (error) {
      // Service not ready yet
    }
    await new Promise(resolve => setTimeout(resolve, 2000));
  }

  if (!frontendReady) {
    throw new Error('❌ Frontend service failed to start');
  }

  // Check backend service  
  let backendReady = false;
  for (let i = 0; i < 30; i++) {
    try {
      const response = await fetch('http://localhost:8000/health');
      if (response.ok) {
        backendReady = true;
        console.log('✅ Backend service ready');
        break;
      }
    } catch (error) {
      // Service not ready yet
    }
    await new Promise(resolve => setTimeout(resolve, 2000));
  }

  if (!backendReady) {
    throw new Error('❌ Backend service failed to start');
  }

  console.log('🎉 E2E test setup complete!');
}

module.exports = globalSetup;

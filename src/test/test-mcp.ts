import fetch from 'node-fetch';
import { logger } from '../utils/logger';

async function testMCPServer() {
  const baseUrl = 'http://localhost:3000';
  const testFile = 'src/test/sample.ts';

  try {
    // Test 1: Health check
    logger.info('Testing health endpoint...');
    const healthResponse = await fetch(`${baseUrl}/health`);
    const healthResult = await healthResponse.json();
    logger.info('Health check result:', healthResult);

    // Test 2: Code complexity analysis
    logger.info('\nTesting code complexity analysis...');
    const complexityResponse = await fetch(`${baseUrl}/mcp`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        method: 'code-analyzer',
        params: {
          filePath: testFile,
          analysisType: 'complexity'
        }
      })
    });
    const complexityResult = await complexityResponse.json();
    logger.info('Complexity analysis result:', complexityResult);

    // Test 3: Dependencies analysis
    logger.info('\nTesting dependencies analysis...');
    const dependenciesResponse = await fetch(`${baseUrl}/mcp`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        method: 'code-analyzer',
        params: {
          filePath: testFile,
          analysisType: 'dependencies'
        }
      })
    });
    const dependenciesResult = await dependenciesResponse.json();
    logger.info('Dependencies analysis result:', dependenciesResult);

    // Test 4: Documentation analysis
    logger.info('\nTesting documentation analysis...');
    const documentationResponse = await fetch(`${baseUrl}/mcp`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        method: 'code-analyzer',
        params: {
          filePath: testFile,
          analysisType: 'documentation'
        }
      })
    });
    const documentationResult = await documentationResponse.json();
    logger.info('Documentation analysis result:', documentationResult);

    logger.info('\nAll tests completed successfully!');
  } catch (error) {
    logger.error('Error during testing:', error);
    process.exit(1);
  }
}

// Run the tests
testMCPServer(); 
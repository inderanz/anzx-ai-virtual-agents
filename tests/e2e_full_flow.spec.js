
const { test, expect } = require('@playwright/test');

// Base URLs for the services. In a real CI/CD, these would come from environment variables.
const CORE_API_URL = process.env.CORE_API_URL || 'http://127.0.0.1:8000';
const KNOWLEDGE_SERVICE_URL = process.env.KNOWLEDGE_SERVICE_URL || 'http://127.0.0.1:8002';

// Use a unique identifier for test resources to avoid collisions
const testRunId = `test-${Date.now()}`;
const orgId = `org-${testRunId}`;
const docId = `doc-${testRunId}`;
const knowledgeContent = 'The policy number for ANZX.ai is POL-12345.';
const userQuestion = 'What is the policy number?';

test.describe.configure({ mode: 'serial' }); // Run tests in this file in sequence

let apiContext;
let headers;
let supportAgentId;

test.beforeAll(async ({ playwright }) => {
  // Create a single API context for all tests to share cookies, etc.
  apiContext = await playwright.request.newContext({
    baseURL: CORE_API_URL,
  });

  // NOTE: In a real test suite, we would programmatically log in a test user
  // to get a valid auth token. For this test, we assume an auth mechanism
  // that provides a token, or that the API is running in a test mode where
  // auth is bypassed. We will use a placeholder API key header.
  headers = {
    'X-API-Key': 'placeholder-test-api-key',
    'Content-Type': 'application/json',
  };
});

test.afterAll(async () => {
  // Dispose the context once all tests are done.
  await apiContext.dispose();
});

test('Step 1: Create a new Support Agent', async () => {
  const response = await apiContext.post('/api/v1/agents',
  {
    headers: headers,
    data: {
        name: `E2E Support Agent ${testRunId}`,
        type: 'support',
        description: 'Agent for end-to-end testing',
        organization_id: orgId, // Assuming org exists or is created for the test
    }
  });

  expect(response.ok()).toBeTruthy();
  const agent = await response.json();
  expect(agent.id).toBeDefined();
  expect(agent.type).toBe('support');
  supportAgentId = agent.id;
  console.log(`Created support agent with ID: ${supportAgentId}`);
});

test('Step 2: Upload a document to the Knowledge Service', async ({ request }) => {
  // This test needs to call the knowledge service directly to seed the data.
  const formData = new FormData();
  formData.append('organization_id', orgId);
  formData.append('document_id', docId);
  formData.append('file', new Blob([knowledgeContent], { type: 'text/plain' }), 'policy.txt');

  const response = await request.post(`${KNOWLEDGE_SERVICE_URL}/documents`, {
    multipart: formData,
  });

  expect(response.ok()).toBeTruthy();
  const result = await response.json();
  expect(result.status).toBe('processing');
  console.log(`Document ${result.document_id} uploaded for processing.`);

  // Wait for a few seconds to allow for background processing.
  // In a real-world scenario, you might poll a status endpoint.
  await new Promise(resolve => setTimeout(resolve, 5000));
});

test('Step 3: Chat with the Support Agent and get a contextual answer', async () => {
  expect(supportAgentId).toBeDefined();

  const response = await apiContext.post(`/api/v1/agents/${supportAgentId}/chat`,
  {
    headers: headers,
    data: {
        message: userQuestion,
        organization_id: orgId,
    }
  });

  expect(response.ok()).toBeTruthy();
  const chatResponse = await response.json();

  console.log('Received AI response:', chatResponse.reply);
  console.log('Received citations:', chatResponse.citations);

  // Assert that the AI's reply contains the policy number from the document.
  expect(chatResponse.reply).toContain('POL-12345');

  // Assert that the context we uploaded was returned as a citation.
  expect(chatResponse.citations.length).toBeGreaterThan(0);
  expect(chatResponse.citations[0]).toContain('policy number');
});

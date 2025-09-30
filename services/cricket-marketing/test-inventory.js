// Test script to verify data-testid attributes
// Run this in browser console on https://anzx.ai/cricket

console.log('=== Cricket Page Inventory Test ===');

// Test 1: Check if all required data-testid attributes exist
const testIds = [
  'cricket-hero',
  'cricket-examples', 
  'cricket-features',
  'cricket-footer'
];

console.log('Testing data-testid attributes...');
testIds.forEach(testId => {
  const element = document.querySelector(`[data-testid="${testId}"]`);
  console.log(`${testId}: ${element ? '✅ Found' : '❌ Missing'}`);
});

// Test 2: Count total cricket testids
const allCricketTestIds = document.querySelectorAll('[data-testid^="cricket-"]');
console.log(`\nTotal cricket testids found: ${allCricketTestIds.length}`);

// Test 3: Verify no visual differences (manual check)
console.log('\nVisual check: Page should look identical to before adding testids');

// Test 4: List all sections with their H1/H2 headings
console.log('\n=== Section Analysis ===');

const heroSection = document.querySelector('[data-testid="cricket-hero"]');
if (heroSection) {
  const h1 = heroSection.querySelector('h1');
  console.log('Hero H1:', h1 ? h1.textContent : 'No H1 found');
}

const examplesSection = document.querySelector('[data-testid="cricket-examples"]');
if (examplesSection) {
  const h3 = examplesSection.querySelector('h3');
  console.log('Examples H3:', h3 ? h3.textContent : 'No H3 found');
}

const featuresSection = document.querySelector('[data-testid="cricket-features"]');
if (featuresSection) {
  const h2 = featuresSection.querySelector('h2');
  console.log('Features H2:', h2 ? h2.textContent : 'No H2 found');
}

console.log('\n=== Test Complete ===');

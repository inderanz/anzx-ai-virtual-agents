// Test script for feature cards and live demo functionality
// Run this in browser console on https://anzx.ai/cricket

console.log('=== Feature Cards & Live Demo Test ===');

// Test 1: Check if feature cards exist
const featureCards = document.querySelectorAll('.feature-card');
console.log(`Found ${featureCards.length} feature cards`);
console.assert(featureCards.length === 4, 'Acceptance: Should have exactly 4 feature cards');

// Test 2: Check for reveal animations
featureCards.forEach((card, index) => {
    const revealAttr = card.getAttribute('data-reveal');
    console.log(`Card ${index + 1} reveal attribute: ${revealAttr}`);
    console.assert(revealAttr === `${index + 1}`, `Acceptance: Card ${index + 1} should have data-reveal="${index + 1}"`);
});

// Test 3: Check for icons (Lucide icons)
const featureIcons = document.querySelectorAll('.feature-icon svg');
console.log(`Found ${featureIcons.length} feature icons with SVG elements`);
console.assert(featureIcons.length === 4, 'Acceptance: All 4 cards should have SVG icons');

// Test 4: Check for examples in each card
const featureExamples = document.querySelectorAll('.feature-examples');
console.log(`Found ${featureExamples.length} feature examples containers`);
console.assert(featureExamples.length === 4, 'Acceptance: All 4 cards should have examples containers');

featureExamples.forEach((container, index) => {
    const examples = container.querySelectorAll('.feature-example');
    console.log(`Card ${index + 1} has ${examples.length} examples`);
    console.assert(examples.length >= 1, `Acceptance: Card ${index + 1} should have at least 1 example`);
});

// Test 5: Check for live demo section
const liveDemoSection = document.querySelector('.live-demo-section');
console.log('Live demo section found:', !!liveDemoSection);
console.assert(!!liveDemoSection, 'Acceptance: Live demo section should be present');

if (liveDemoSection) {
    const demoTitle = liveDemoSection.querySelector('.live-demo-title');
    const demoDescription = liveDemoSection.querySelector('.live-demo-description');
    console.log('Demo title:', demoTitle?.textContent);
    console.log('Demo description:', demoDescription?.textContent);
    console.assert(!!demoTitle, 'Acceptance: Demo title should be present');
    console.assert(!!demoDescription, 'Acceptance: Demo description should be present');
}

// Test 6: Check for demo chips
const demoChips = document.querySelectorAll('.demo-chip');
console.log(`Found ${demoChips.length} demo chips`);
console.assert(demoChips.length === 3, 'Acceptance: Should have exactly 3 demo chips');

demoChips.forEach((chip, index) => {
    const ariaLabel = chip.getAttribute('aria-label');
    const icon = chip.querySelector('svg');
    console.log(`Chip ${index + 1} aria-label: ${ariaLabel}`);
    console.log(`Chip ${index + 1} has icon: ${!!icon}`);
    console.assert(!!ariaLabel, `Acceptance: Chip ${index + 1} should have aria-label`);
    console.assert(!!icon, `Acceptance: Chip ${index + 1} should have an icon`);
});

// Test 7: Test demo chip functionality
console.log('\n=== Testing Demo Chip Functionality ===');
const firstChip = demoChips[0];
if (firstChip) {
    console.log('Testing first demo chip click...');
    
    // Store original scrollIntoView
    const originalScrollIntoView = Element.prototype.scrollIntoView;
    let scrollCalled = false;
    
    Element.prototype.scrollIntoView = function() {
        scrollCalled = true;
        console.log('scrollIntoView called on:', this);
        return originalScrollIntoView.apply(this, arguments);
    };
    
    // Simulate click
    firstChip.click();
    
    // Check if scroll was called
    setTimeout(() => {
        console.log('Scroll called after chip click:', scrollCalled);
        console.assert(scrollCalled, 'Acceptance: Clicking demo chip should scroll to chat interface');
        
        // Restore original method
        Element.prototype.scrollIntoView = originalScrollIntoView;
    }, 100);
}

// Test 8: Check for CTA visibility
const demoCTA = document.querySelector('.demo-cta');
console.log('Demo CTA visible:', !!demoCTA);
console.log('Demo CTA should be hidden initially');

// Test 9: Test keyboard navigation
console.log('\n=== Testing Keyboard Navigation ===');
const focusableElements = document.querySelectorAll('.feature-card, .demo-chip, .demo-cta button');
console.log(`Found ${focusableElements.length} focusable elements`);

focusableElements.forEach((element, index) => {
    const tabIndex = element.getAttribute('tabindex');
    console.log(`Element ${index + 1} tabindex: ${tabIndex || 'default'}`);
});

// Test 10: Check for reduced motion support
console.log('\n=== Testing Reduced Motion Support ===');
const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
console.log('prefers-reduced-motion is active:', prefersReducedMotion);

if (prefersReducedMotion) {
    console.log('Expected: Animations should be disabled');
} else {
    console.log('Expected: Animations should be enabled');
}

// Test 11: Check for hover effects (desktop only)
console.log('\n=== Testing Hover Effects ===');
const isDesktop = window.innerWidth > 768;
console.log(`Screen width: ${window.innerWidth}px, is desktop: ${isDesktop}`);

if (isDesktop) {
    console.log('Expected: Hover effects should be enabled on desktop');
} else {
    console.log('Expected: Hover effects should be disabled on mobile');
}

// Test 12: Check for contrast (basic check)
console.log('\n=== Testing Contrast (Basic Check) ===');
const featureTitles = document.querySelectorAll('.feature-title');
const featureDescriptions = document.querySelectorAll('.feature-description');

featureTitles.forEach((title, index) => {
    const computedStyle = window.getComputedStyle(title);
    const color = computedStyle.color;
    console.log(`Feature title ${index + 1} color: ${color}`);
});

featureDescriptions.forEach((desc, index) => {
    const computedStyle = window.getComputedStyle(desc);
    const color = computedStyle.color;
    console.log(`Feature description ${index + 1} color: ${color}`);
});

// Test 13: Check for mobile responsiveness
console.log('\n=== Testing Mobile Responsiveness ===');
const featuresGrid = document.querySelector('.features-grid');
if (featuresGrid) {
    const computedStyle = window.getComputedStyle(featuresGrid);
    const gridTemplateColumns = computedStyle.gridTemplateColumns;
    console.log('Features grid columns:', gridTemplateColumns);
    
    if (window.innerWidth <= 768) {
        console.assert(gridTemplateColumns === '1fr', 'Acceptance: Mobile should use single column layout');
    } else {
        console.assert(gridTemplateColumns.includes('minmax'), 'Acceptance: Desktop should use responsive grid');
    }
}

// Test 14: Check for demo chip text content
console.log('\n=== Testing Demo Chip Content ===');
const expectedChipTexts = [
    'Fixtures for Blue U10 this week',
    'Ladder position for White U10',
    'Who scored most runs last match?'
];

demoChips.forEach((chip, index) => {
    const text = chip.textContent.trim();
    const expectedText = expectedChipTexts[index];
    console.log(`Chip ${index + 1} text: "${text}"`);
    console.log(`Expected: "${expectedText}"`);
    console.assert(text.includes(expectedText), `Acceptance: Chip ${index + 1} should contain expected text`);
});

// Test 15: Check for feature card content
console.log('\n=== Testing Feature Card Content ===');
const expectedCardTitles = [
    'Player Information',
    'Fixtures & Schedule',
    'Ladder Positions',
    'Player Statistics'
];

featureCards.forEach((card, index) => {
    const title = card.querySelector('.feature-title')?.textContent;
    const expectedTitle = expectedCardTitles[index];
    console.log(`Card ${index + 1} title: "${title}"`);
    console.log(`Expected: "${expectedTitle}"`);
    console.assert(title === expectedTitle, `Acceptance: Card ${index + 1} should have correct title`);
});

console.log('\n=== Test Complete ===');
console.log('Manual checks:');
console.log('1. Scroll to feature cards and observe staggered reveal animation');
console.log('2. Hover over cards on desktop to see lift/glow effects');
console.log('3. Click demo chips to test functionality');
console.log('4. Test keyboard navigation with Tab key');
console.log('5. Check mobile responsiveness by resizing window');
console.log('6. Verify contrast meets AA standards');
console.log('7. Test with reduced motion preference enabled');

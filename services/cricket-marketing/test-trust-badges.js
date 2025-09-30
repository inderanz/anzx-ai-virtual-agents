// Test script for trust badges functionality
// Run this in browser console on https://anzx.ai/cricket

console.log('=== Trust Badges Test ===');

// Test 1: Check if trust badges exist in hero section
const heroTrustBadges = document.querySelector('[data-testid="cricket-hero"] .trust-badges-hero');
if (heroTrustBadges) {
  console.log('✅ Hero trust badges found');
} else {
  console.log('❌ Hero trust badges not found');
}

// Test 2: Check if trust badges exist in footer
const footerTrustBadges = document.querySelector('[data-testid="cricket-footer"] .trust-badges-footer');
if (footerTrustBadges) {
  console.log('✅ Footer trust badges found');
} else {
  console.log('❌ Footer trust badges not found');
}

// Test 3: Check for all three required badges
const allTrustBadges = document.querySelectorAll('.trust-badge');
console.log(`Found ${allTrustBadges.length} trust badges`);

const expectedBadges = ['Australian Hosted', 'SOC 2 Compliant', 'Privacy Act Compliant'];
expectedBadges.forEach(badgeText => {
  const badge = Array.from(allTrustBadges).find(b => b.textContent.includes(badgeText));
  if (badge) {
    console.log(`✅ "${badgeText}" badge found`);
  } else {
    console.log(`❌ "${badgeText}" badge not found`);
  }
});

// Test 4: Check for icons
allTrustBadges.forEach((badge, index) => {
  const icon = badge.querySelector('.trust-badge-icon');
  const text = badge.querySelector('.trust-badge-text');
  console.log(`Badge ${index + 1}:`);
  console.log(`  - Icon: ${icon ? icon.textContent : 'No icon'}`);
  console.log(`  - Text: ${text ? text.textContent : 'No text'}`);
});

// Test 5: Check contrast and accessibility
console.log('\n=== Accessibility Check ===');
allTrustBadges.forEach((badge, index) => {
  const computedStyle = window.getComputedStyle(badge);
  const color = computedStyle.color;
  const backgroundColor = computedStyle.backgroundColor;
  
  console.log(`Badge ${index + 1}:`);
  console.log(`  - Color: ${color}`);
  console.log(`  - Background: ${backgroundColor}`);
  console.log(`  - Font size: ${computedStyle.fontSize}`);
  console.log(`  - Font weight: ${computedStyle.fontWeight}`);
});

// Test 6: Check hover states
console.log('\n=== Hover State Check ===');
const isPointerDevice = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
const isTouchDevice = window.matchMedia('(hover: none) and (pointer: coarse)').matches;

console.log(`Pointer device: ${isPointerDevice}`);
console.log(`Touch device: ${isTouchDevice}`);

if (isPointerDevice) {
  console.log('✅ Hover effects should be active on pointer devices');
} else if (isTouchDevice) {
  console.log('✅ No hover effects on touch devices (prevents tap highlights)');
}

// Test 7: Check grayscale filter
allTrustBadges.forEach((badge, index) => {
  const computedStyle = window.getComputedStyle(badge);
  const filter = computedStyle.filter;
  const opacity = computedStyle.opacity;
  
  console.log(`Badge ${index + 1} initial state:`);
  console.log(`  - Filter: ${filter}`);
  console.log(`  - Opacity: ${opacity}`);
  
  if (filter.includes('grayscale')) {
    console.log('✅ Grayscale filter applied (should be removed on hover)');
  }
});

// Test 8: Test hover functionality (simulate hover)
console.log('\n=== Hover Functionality Test ===');
if (isPointerDevice) {
  allTrustBadges.forEach((badge, index) => {
    console.log(`Testing hover on badge ${index + 1}...`);
    
    // Simulate hover
    badge.dispatchEvent(new Event('mouseenter'));
    
    // Check if hover styles are applied
    const computedStyle = window.getComputedStyle(badge);
    const filter = computedStyle.filter;
    const opacity = computedStyle.opacity;
    
    console.log(`  - Filter after hover: ${filter}`);
    console.log(`  - Opacity after hover: ${opacity}`);
    
    // Reset
    badge.dispatchEvent(new Event('mouseleave'));
  });
}

// Test 9: Check responsive design
console.log('\n=== Responsive Design Check ===');
const isMobile = window.innerWidth <= 768;
console.log(`Screen width: ${window.innerWidth}px`);
console.log(`Is mobile: ${isMobile}`);

if (isMobile) {
  const trustBadges = document.querySelector('.trust-badges');
  if (trustBadges) {
    const flexDirection = window.getComputedStyle(trustBadges).flexDirection;
    const gap = window.getComputedStyle(trustBadges).gap;
    console.log(`Trust badges flex-direction: ${flexDirection}`);
    console.log(`Trust badges gap: ${gap}`);
  }
}

// Test 10: Check consistency between hero and footer
console.log('\n=== Consistency Check ===');
const heroBadges = document.querySelectorAll('[data-testid="cricket-hero"] .trust-badge');
const footerBadges = document.querySelectorAll('[data-testid="cricket-footer"] .trust-badge');

console.log(`Hero badges: ${heroBadges.length}`);
console.log(`Footer badges: ${footerBadges.length}`);

if (heroBadges.length === footerBadges.length) {
  console.log('✅ Same number of badges in hero and footer');
} else {
  console.log('❌ Different number of badges in hero and footer');
}

// Check if badges have different styling
if (heroBadges.length > 0 && footerBadges.length > 0) {
  const heroStyle = window.getComputedStyle(heroBadges[0]);
  const footerStyle = window.getComputedStyle(footerBadges[0]);
  
  console.log('Hero badge background:', heroStyle.backgroundColor);
  console.log('Footer badge background:', footerStyle.backgroundColor);
  
  if (heroStyle.backgroundColor !== footerStyle.backgroundColor) {
    console.log('✅ Different styling for hero vs footer (as expected)');
  } else {
    console.log('⚠️ Same styling for hero and footer');
  }
}

console.log('\n=== Test Complete ===');
console.log('Manual checks:');
console.log('1. Look for trust badges under CTAs in hero section');
console.log('2. Look for trust badges in footer');
console.log('3. Hover over badges to see grayscale → color effect');
console.log('4. Check mobile responsiveness');
console.log('5. Verify AA contrast for text');

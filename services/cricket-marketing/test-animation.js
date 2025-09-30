// Test script for animated hero background
// Run this in browser console on https://anzx.ai/cricket

console.log('=== Cricket Hero Animation Test ===');

// Test 1: Check if animated background elements exist
const heroSection = document.querySelector('[data-testid="cricket-hero"]');
if (heroSection) {
  console.log('✅ Hero section found');
  
  // Check for ::before pseudo-element (animated background)
  const computedStyle = window.getComputedStyle(heroSection, '::before');
  const hasAnimation = computedStyle.animationName !== 'none';
  console.log('Animation name:', computedStyle.animationName);
  console.log('Animation duration:', computedStyle.animationDuration);
  console.log('Animation iteration:', computedStyle.animationIterationCount);
  
  if (hasAnimation) {
    console.log('✅ Animated background detected');
  } else {
    console.log('❌ No animation found');
  }
} else {
  console.log('❌ Hero section not found');
}

// Test 2: Check for prefers-reduced-motion support
const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
console.log('Prefers reduced motion:', prefersReducedMotion);

if (prefersReducedMotion) {
  console.log('✅ Reduced motion preference detected - animation should be disabled');
} else {
  console.log('✅ Full motion allowed - animation should be active');
}

// Test 3: Check CSS custom properties and gradients
const heroElement = document.querySelector('.cricket-header');
if (heroElement) {
  const computedStyle = window.getComputedStyle(heroElement);
  console.log('Background:', computedStyle.background);
  console.log('Position:', computedStyle.position);
  console.log('Overflow:', computedStyle.overflow);
}

// Test 4: Performance check
console.log('\n=== Performance Check ===');
const startTime = performance.now();

// Simulate a small task to check if animation affects performance
setTimeout(() => {
  const endTime = performance.now();
  const duration = endTime - startTime;
  console.log(`Task duration: ${duration.toFixed(2)}ms`);
  
  if (duration < 100) {
    console.log('✅ Performance looks good');
  } else {
    console.log('⚠️ Performance may be affected');
  }
}, 100);

// Test 5: Check for CLS (Cumulative Layout Shift)
console.log('\n=== Layout Stability Check ===');
const observer = new PerformanceObserver((list) => {
  for (const entry of list.getEntries()) {
    if (entry.entryType === 'layout-shift' && !entry.hadRecentInput) {
      console.log('Layout shift detected:', entry.value);
    }
  }
});

try {
  observer.observe({ entryTypes: ['layout-shift'] });
  console.log('✅ Layout shift monitoring active');
} catch (e) {
  console.log('⚠️ Layout shift monitoring not available');
}

console.log('\n=== Test Complete ===');
console.log('Manual check: Look for smooth rotating gradient in hero background');
console.log('Expected: Deep navy → teal gradient with subtle rotation over 20 seconds');

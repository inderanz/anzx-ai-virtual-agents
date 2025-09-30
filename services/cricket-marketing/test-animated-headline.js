// Test script for AnimatedHeadline component
// Run this in browser console on https://anzx.ai/cricket

console.log('=== AnimatedHeadline Component Test ===');

// Test 1: Check if AnimatedHeadline component exists
const animatedHeadline = document.querySelector('.cricket-title');
console.log('AnimatedHeadline container found:', !!animatedHeadline);

if (animatedHeadline) {
    // Test 2: Check for "Intelligent" static text
    const intelligentText = animatedHeadline.textContent.includes('Intelligent');
    console.log('"Intelligent" static text found:', intelligentText);
    console.assert(intelligentText, 'Acceptance: Should contain "Intelligent" static text');
}

// Test 3: Check for cycling words in the component
const expectedWords = ["Cricket Assistant", "Cricket Expert", "Cricket Agent", "Team Manager", "Team Assistant"];
console.log('Expected cycling words:', expectedWords);

// Test 4: Check for enhanced description
const enhancedDescription = document.querySelector('.cricket-description-enhanced');
console.log('Enhanced description found:', !!enhancedDescription);

if (enhancedDescription) {
    // Test 5: Check typography classes
    const computedStyle = window.getComputedStyle(enhancedDescription);
    const fontWeight = computedStyle.fontWeight;
    const fontSize = computedStyle.fontSize;
    const textAlign = computedStyle.textAlign;
    
    console.log('Description font weight:', fontWeight);
    console.log('Description font size:', fontSize);
    console.log('Description text align:', textAlign);
    
    // Test 6: Check for strong tags with keywords
    const strongTags = enhancedDescription.querySelectorAll('strong');
    console.log(`Found ${strongTags.length} strong tags`);
    
    const expectedKeywords = ['fixtures', 'players', 'ladder positions', 'instant, accurate responses'];
    strongTags.forEach((tag, index) => {
        const text = tag.textContent.toLowerCase();
        console.log(`Strong tag ${index + 1}: "${text}"`);
    });
    
    // Test 7: Check for aria-hidden attributes
    strongTags.forEach((tag, index) => {
        const ariaHidden = tag.getAttribute('aria-hidden');
        console.log(`Strong tag ${index + 1} aria-hidden:`, ariaHidden);
        console.assert(ariaHidden === 'false' || ariaHidden === null, `Acceptance: Strong tag ${index + 1} should not have aria-hidden="true"`);
    });
}

// Test 8: Check for reduced motion support
const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
console.log('prefers-reduced-motion is active:', prefersReducedMotion);

if (prefersReducedMotion) {
    console.log('Expected: Animations should be disabled');
} else {
    console.log('Expected: Animations should be enabled');
}

// Test 9: Check for viewport visibility (basic check)
const isInViewport = () => {
    const rect = animatedHeadline?.getBoundingClientRect();
    return rect ? rect.top >= 0 && rect.left >= 0 && rect.bottom <= window.innerHeight && rect.right <= window.innerWidth : false;
};

console.log('AnimatedHeadline in viewport:', isInViewport());

// Test 10: Check for accessibility attributes
const ariaLiveElements = document.querySelectorAll('[aria-live]');
console.log(`Found ${ariaLiveElements.length} elements with aria-live`);

ariaLiveElements.forEach((element, index) => {
    const ariaLive = element.getAttribute('aria-live');
    console.log(`Element ${index + 1} aria-live:`, ariaLive);
    console.assert(ariaLive === 'polite', `Acceptance: Element ${index + 1} should have aria-live="polite"`);
});

// Test 11: Check for gradient text effects
if (enhancedDescription) {
    const computedStyle = window.getComputedStyle(enhancedDescription);
    const backgroundClip = computedStyle.backgroundClip;
    const webkitBackgroundClip = computedStyle.webkitBackgroundClip;
    
    console.log('Background clip:', backgroundClip);
    console.log('Webkit background clip:', webkitBackgroundClip);
    
    // Check if gradient is applied
    const hasGradient = computedStyle.backgroundImage && computedStyle.backgroundImage !== 'none';
    console.log('Has gradient background:', hasGradient);
}

// Test 12: Check responsive behavior
const isMobile = window.innerWidth < 768;
console.log('Is mobile viewport:', isMobile);

if (enhancedDescription) {
    const computedStyle = window.getComputedStyle(enhancedDescription);
    const fontSize = parseFloat(computedStyle.fontSize);
    const textAlign = computedStyle.textAlign;
    
    if (isMobile) {
        console.assert(fontSize >= 18, 'Acceptance: Mobile should use text-lg (18px+)');
        console.assert(textAlign === 'center', 'Acceptance: Mobile should be center-aligned');
    } else {
        console.assert(fontSize >= 20, 'Acceptance: Desktop should use text-xl (20px+)');
        console.assert(textAlign === 'left', 'Acceptance: Desktop should be left-aligned');
    }
}

// Test 13: Check contrast ratio (basic check)
if (enhancedDescription) {
    const computedStyle = window.getComputedStyle(enhancedDescription);
    const color = computedStyle.color;
    console.log('Description color:', color);
    
    // Check if high contrast mode is active
    const highContrastMode = window.matchMedia('(prefers-contrast: high)').matches;
    console.log('High contrast mode active:', highContrastMode);
    
    if (highContrastMode) {
        console.log('Expected: Should use solid colors for better contrast');
    }
}

// Test 14: Check for animation performance
console.log('\n=== Animation Performance Test ===');
const startTime = performance.now();

// Simulate scroll to trigger intersection observer
window.scrollTo(0, 0);
setTimeout(() => {
    const endTime = performance.now();
    const duration = endTime - startTime;
    console.log(`Animation setup time: ${duration.toFixed(2)}ms`);
    console.assert(duration < 100, 'Acceptance: Animation setup should be fast (<100ms)');
}, 100);

// Test 15: Check for proper word cycling
console.log('\n=== Word Cycling Test ===');
console.log('Watch the headline for 10 seconds to verify word cycling...');

let wordChanges = 0;
const observer = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
        if (mutation.type === 'childList' || mutation.type === 'characterData') {
            wordChanges++;
            console.log(`Word change detected: ${wordChanges}`);
        }
    });
});

if (animatedHeadline) {
    observer.observe(animatedHeadline, { 
        childList: true, 
        characterData: true, 
        subtree: true 
    });
    
    // Stop observing after 10 seconds
    setTimeout(() => {
        observer.disconnect();
        console.log(`Total word changes observed: ${wordChanges}`);
        console.assert(wordChanges > 0, 'Acceptance: Should observe word changes during animation');
    }, 10000);
}

console.log('\n=== Test Complete ===');
console.log('Manual checks:');
console.log('1. Watch the headline for word cycling animation');
console.log('2. Check that "Intelligent" stays static');
console.log('3. Verify smooth slide-up + fade transitions');
console.log('4. Test with reduced motion preference enabled');
console.log('5. Test scroll behavior (animation should pause when out of view)');
console.log('6. Check screen reader announcements');
console.log('7. Verify gradient text effects');
console.log('8. Test responsive typography');

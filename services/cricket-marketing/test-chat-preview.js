// Test script for chat preview card functionality
// Run this in browser console on https://anzx.ai/cricket

console.log('=== Chat Preview Card Test ===');

// Test 1: Check if chat preview card exists
const chatPreviewCard = document.querySelector('.chat-preview-card');
if (chatPreviewCard) {
  console.log('✅ Chat preview card found');
} else {
  console.log('❌ Chat preview card not found');
}

// Test 2: Check for CTA buttons
const tryAgentBtn = document.querySelector('.chat-preview-cta.btn-primary');
const watchDemoBtn = document.querySelector('.chat-preview-cta.btn-secondary');

if (tryAgentBtn) {
  console.log('✅ "Try the Cricket Agent" button found');
  console.log('Button text:', tryAgentBtn.textContent.trim());
  console.log('Button aria-label:', tryAgentBtn.getAttribute('aria-label'));
} else {
  console.log('❌ "Try the Cricket Agent" button not found');
}

if (watchDemoBtn) {
  console.log('✅ "Watch 60-sec Demo" button found');
  console.log('Button text:', watchDemoBtn.textContent.trim());
  console.log('Button aria-label:', watchDemoBtn.getAttribute('aria-label'));
} else {
  console.log('❌ "Watch 60-sec Demo" button not found');
}

// Test 3: Check for chat messages
const messages = document.querySelectorAll('.chat-preview-messages .message');
console.log(`Found ${messages.length} chat messages`);

messages.forEach((message, index) => {
  const messageText = message.querySelector('.message-text');
  const messageTime = message.querySelector('.message-time');
  console.log(`Message ${index + 1}:`, messageText ? messageText.textContent : 'No text');
  console.log(`Time:`, messageTime ? messageTime.textContent : 'No time');
});

// Test 4: Check for typing animation
const typingDots = document.querySelectorAll('.typing-dots span');
if (typingDots.length > 0) {
  console.log(`✅ Typing animation found with ${typingDots.length} dots`);
} else {
  console.log('ℹ️ No typing animation currently visible');
}

// Test 5: Test button functionality
if (tryAgentBtn) {
  console.log('\n=== Testing "Try the Cricket Agent" button ===');
  tryAgentBtn.addEventListener('click', () => {
    console.log('✅ "Try the Cricket Agent" button clicked - should scroll to chat section');
  });
}

if (watchDemoBtn) {
  console.log('\n=== Testing "Watch 60-sec Demo" button ===');
  watchDemoBtn.addEventListener('click', () => {
    console.log('✅ "Watch 60-sec Demo" button clicked - should open demo modal');
  });
}

// Test 6: Check responsive design
const isMobile = window.innerWidth <= 768;
console.log(`\n=== Responsive Design Check ===`);
console.log(`Screen width: ${window.innerWidth}px`);
console.log(`Is mobile: ${isMobile}`);

if (isMobile) {
  const actions = document.querySelector('.chat-preview-actions');
  if (actions) {
    const flexDirection = window.getComputedStyle(actions).flexDirection;
    console.log(`Actions flex-direction: ${flexDirection}`);
    if (flexDirection === 'column') {
      console.log('✅ Mobile layout: buttons stacked vertically');
    } else {
      console.log('⚠️ Mobile layout: buttons may not be stacked');
    }
  }
}

// Test 7: Check accessibility
console.log('\n=== Accessibility Check ===');
const buttons = document.querySelectorAll('.chat-preview-cta');
buttons.forEach((button, index) => {
  const hasAriaLabel = button.hasAttribute('aria-label');
  const hasAccessibleName = button.textContent.trim() || button.getAttribute('aria-label');
  console.log(`Button ${index + 1}:`);
  console.log(`  - Has aria-label: ${hasAriaLabel}`);
  console.log(`  - Has accessible name: ${!!hasAccessibleName}`);
  console.log(`  - Focusable: ${button.tabIndex >= 0}`);
});

// Test 8: Check animations
console.log('\n=== Animation Check ===');
const card = document.querySelector('.chat-preview-card');
if (card) {
  const computedStyle = window.getComputedStyle(card);
  const animation = computedStyle.animation;
  console.log(`Card animation: ${animation}`);
  
  if (animation && animation !== 'none') {
    console.log('✅ Card has floating animation');
  } else {
    console.log('ℹ️ No card animation detected');
  }
}

console.log('\n=== Test Complete ===');
console.log('Manual checks:');
console.log('1. Look for animated chat preview card in hero section');
console.log('2. Verify chat messages appear and animate');
console.log('3. Test button clicks (Try Agent should scroll, Watch Demo should show alert)');
console.log('4. Check mobile responsiveness');

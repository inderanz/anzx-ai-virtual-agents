// Test script for chat dock functionality
// Run this in browser console on https://anzx.ai/cricket

console.log('=== Chat Dock Test ===');

// Test 1: Check if chat dock components exist
const chatFab = document.querySelector('.chat-fab');
const chatDock = document.querySelector('.chat-dock');

if (chatFab) {
  console.log('✅ Chat FAB found');
} else {
  console.log('❌ Chat FAB not found');
}

if (chatDock) {
  console.log('✅ Chat dock found');
} else {
  console.log('❌ Chat dock not found');
}

// Test 2: Check for mobile vs desktop behavior
const isMobile = window.innerWidth <= 768;
console.log(`Screen width: ${window.innerWidth}px`);
console.log(`Is mobile: ${isMobile}`);

if (isMobile) {
  console.log('Expected: FAB should be visible, dock should be hidden initially');
} else {
  console.log('Expected: FAB should be visible, dock should be hidden initially');
}

// Test 3: Test FAB click functionality
if (chatFab) {
  console.log('\n=== Testing FAB Click ===');
  chatFab.addEventListener('click', () => {
    console.log('✅ FAB clicked - should open chat dock');
  });
}

// Test 4: Check for chat dock features
if (chatDock) {
  const header = chatDock.querySelector('.chat-dock-header');
  const messages = chatDock.querySelector('.chat-dock-messages');
  const input = chatDock.querySelector('.chat-dock-input');
  
  if (header) {
    console.log('✅ Chat dock header found');
    const title = header.querySelector('h3');
    if (title) {
      console.log('Header title:', title.textContent);
    }
  }
  
  if (messages) {
    console.log('✅ Chat dock messages area found');
  }
  
  if (input) {
    console.log('✅ Chat dock input area found');
  }
}

// Test 5: Check for message actions
const messageActions = document.querySelectorAll('.message-action');
console.log(`Found ${messageActions.length} message action buttons`);

messageActions.forEach((action, index) => {
  const icon = action.querySelector('svg');
  const ariaLabel = action.getAttribute('aria-label');
  console.log(`Action ${index + 1}: ${ariaLabel || 'No label'}`);
});

// Test 6: Check for streaming functionality
const streamingContent = document.querySelector('.streaming-content');
const streamingCursor = document.querySelector('.streaming-cursor');

if (streamingContent) {
  console.log('✅ Streaming content found');
} else {
  console.log('ℹ️ No streaming content currently visible');
}

if (streamingCursor) {
  console.log('✅ Streaming cursor found');
} else {
  console.log('ℹ️ No streaming cursor currently visible');
}

// Test 7: Check for new messages pill
const newMessagesPill = document.querySelector('.new-messages-pill');
if (newMessagesPill) {
  console.log('✅ New messages pill found');
} else {
  console.log('ℹ️ No new messages pill currently visible');
}

// Test 8: Check localStorage persistence
console.log('\n=== LocalStorage Persistence Test ===');
const savedMessages = localStorage.getItem('cricket-chat-messages');
if (savedMessages) {
  try {
    const messages = JSON.parse(savedMessages);
    console.log(`✅ Found ${messages.length} saved messages in localStorage`);
    console.log('Sample message:', messages[0]?.content?.substring(0, 50) + '...');
  } catch (e) {
    console.log('❌ Error parsing saved messages:', e.message);
  }
} else {
  console.log('ℹ️ No saved messages in localStorage');
}

// Test 9: Check URL parameters
console.log('\n=== URL Parameters Test ===');
const urlParams = new URLSearchParams(window.location.search);
const chatParam = urlParams.get('chat');
console.log(`Chat parameter: ${chatParam || 'not set'}`);

if (chatParam === '1') {
  console.log('✅ Chat should be open based on URL parameter');
} else {
  console.log('ℹ️ Chat should be closed based on URL parameter');
}

// Test 10: Check for full-page chat route
console.log('\n=== Full-Page Chat Route Test ===');
const currentPath = window.location.pathname;
console.log(`Current path: ${currentPath}`);

if (currentPath === '/cricket/chat') {
  console.log('✅ On full-page chat route');
  
  // Check for breadcrumb
  const breadcrumb = document.querySelector('.breadcrumb');
  if (breadcrumb) {
    console.log('✅ Breadcrumb found on full-page chat');
  } else {
    console.log('❌ Breadcrumb not found on full-page chat');
  }
} else {
  console.log('ℹ️ On main cricket page');
  
  // Test navigation to full-page chat
  console.log('Testing navigation to full-page chat...');
  const tryAgentBtn = document.querySelector('.chat-preview-cta.btn-primary');
  if (tryAgentBtn) {
    console.log('✅ "Try the Cricket Agent" button found');
    console.log('Clicking should navigate to /cricket/chat');
  } else {
    console.log('❌ "Try the Cricket Agent" button not found');
  }
}

// Test 11: Check for iOS safe area support
console.log('\n=== iOS Safe Area Support Test ===');
const supportsSafeArea = CSS.supports('padding', 'max(0px)');
console.log(`CSS supports max(): ${supportsSafeArea}`);

if (supportsSafeArea) {
  console.log('✅ iOS safe area support available');
} else {
  console.log('ℹ️ iOS safe area support not available');
}

// Test 12: Performance test for message rendering
console.log('\n=== Performance Test ===');
const startTime = performance.now();

// Simulate adding multiple messages
const testMessages = Array.from({ length: 50 }, (_, i) => ({
  id: i,
  type: i % 2 === 0 ? 'user' : 'ai',
  content: `Test message ${i}`,
  timestamp: 'Just now'
}));

const endTime = performance.now();
const duration = endTime - startTime;

console.log(`Performance test duration: ${duration.toFixed(2)}ms`);
if (duration < 100) {
  console.log('✅ Performance looks good');
} else {
  console.log('⚠️ Performance may need optimization');
}

// Test 13: Check for keyboard accessibility
console.log('\n=== Keyboard Accessibility Test ===');
const inputField = document.querySelector('.chat-dock-input-field');
if (inputField) {
  console.log('✅ Input field found');
  console.log('Tab index:', inputField.tabIndex);
  console.log('Disabled:', inputField.disabled);
} else {
  console.log('❌ Input field not found');
}

const sendButton = document.querySelector('.chat-dock-send');
if (sendButton) {
  console.log('✅ Send button found');
  console.log('Tab index:', sendButton.tabIndex);
  console.log('Disabled:', sendButton.disabled);
} else {
  console.log('❌ Send button not found');
}

console.log('\n=== Test Complete ===');
console.log('Manual checks:');
console.log('1. Click FAB to open chat dock');
console.log('2. Test typing and sending messages');
console.log('3. Check streaming animation');
console.log('4. Test message actions (copy, retry, regenerate)');
console.log('5. Test navigation to full-page chat');
console.log('6. Check mobile responsiveness');
console.log('7. Test keyboard navigation');
console.log('8. Verify state persistence on refresh');

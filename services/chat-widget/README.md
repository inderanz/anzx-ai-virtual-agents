# ANZx.ai Chat Widget

A lightweight, embeddable chat widget for customer websites with real-time WebSocket communication and HTTP fallback.

## Features

- **Lightweight**: Bundle size under 12KB (gzipped)
- **Real-time Communication**: WebSocket with automatic fallback to HTTP polling
- **Customizable UI**: Multiple themes, colors, and positioning options
- **Accessibility Compliant**: WCAG 2.1 AA compliant with keyboard navigation
- **Mobile Responsive**: Works seamlessly on all device sizes
- **Rate Limiting**: Built-in protection against spam
- **Analytics**: Visitor tracking and conversation analytics
- **Secure**: Domain validation and API key authentication

## Quick Start

### 1. Embed Script (Recommended)

Add this script to your website's HTML:

```html
<!-- ANZx.ai Chat Widget -->
<script>
(function() {
    var script = document.createElement('script');
    script.src = 'https://cdn.anzx.ai/widget/chat-widget.js';
    script.async = true;
    script.onload = function() {
        new ANZxChatWidget({
            widgetId: 'your_widget_id',
            apiKey: 'your_api_key',
            theme: 'light',
            position: 'bottom-right'
        });
    };
    document.head.appendChild(script);
})();
</script>
<!-- End ANZx.ai Chat Widget -->
```

### 2. Manual Initialization

For more control over the initialization:

```html
<script src="https://cdn.anzx.ai/widget/chat-widget.js"></script>
<script>
const widget = new ANZxChatWidget({
    widgetId: 'your_widget_id',
    apiKey: 'your_api_key',
    apiUrl: 'https://api.anzx.ai',
    theme: 'light',
    position: 'bottom-right',
    primaryColor: '#007bff',
    welcomeMessage: 'Hi! How can I help you today?',
    placeholder: 'Type your message...',
    showTypingIndicator: true,
    maxMessageLength: 1000
});
</script>
```

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `widgetId` | string | **required** | Your widget ID from ANZx.ai dashboard |
| `apiKey` | string | **required** | Your widget API key |
| `apiUrl` | string | `'https://api.anzx.ai'` | API endpoint URL |
| `wsUrl` | string | `'wss://api.anzx.ai'` | WebSocket endpoint URL |
| `theme` | string | `'light'` | Theme: `'light'`, `'dark'`, or `'auto'` |
| `position` | string | `'bottom-right'` | Position: `'bottom-right'`, `'bottom-left'`, `'top-right'`, `'top-left'` |
| `primaryColor` | string | `'#007bff'` | Primary color (hex, rgb, or named color) |
| `welcomeMessage` | string | `'Hi! How can I help you today?'` | Initial greeting message |
| `placeholder` | string | `'Type your message...'` | Input field placeholder text |
| `maxMessageLength` | number | `1000` | Maximum message length |
| `showTypingIndicator` | boolean | `true` | Show typing indicator when AI is responding |
| `enableFileUpload` | boolean | `false` | Enable file upload functionality |

## API Methods

### Widget Control

```javascript
// Open the widget
widget.openWidget();

// Close the widget
widget.closeWidget();

// Toggle widget visibility
widget.toggleWidget();

// Send a message programmatically
widget.sendMessage('Hello from code!');

// Get widget state
const state = widget.getState();
console.log(state);
// Returns: { isOpen: boolean, isConnected: boolean, conversationId: string, visitorId: string }

// Destroy the widget
widget.destroy();
```

### Theme Management

```javascript
// Change theme
widget.setTheme('dark');

// Update configuration
widget.updateConfig({
    primaryColor: '#ff0000',
    welcomeMessage: 'Welcome to our support!'
});
```

## Events

The widget emits events that you can listen to:

```javascript
// Widget opened
widget.on('open', () => {
    console.log('Widget opened');
});

// Widget closed
widget.on('close', () => {
    console.log('Widget closed');
});

// Message sent
widget.on('message_sent', (message) => {
    console.log('Message sent:', message);
});

// Message received
widget.on('message_received', (message) => {
    console.log('Message received:', message);
});

// Connection status changed
widget.on('connection_changed', (isConnected) => {
    console.log('Connection status:', isConnected);
});

// Error occurred
widget.on('error', (error) => {
    console.error('Widget error:', error);
});
```

## Styling and Customization

### CSS Custom Properties

You can override widget styles using CSS custom properties:

```css
:root {
    --anzx-primary-color: #your-brand-color;
    --anzx-text-color: #333333;
    --anzx-background-color: #ffffff;
    --anzx-border-radius: 8px;
    --anzx-shadow: 0 4px 12px rgba(0,0,0,0.15);
}
```

### Custom CSS Classes

The widget uses these CSS classes that you can style:

- `.anzx-widget` - Main container
- `.anzx-widget-button` - Chat button
- `.anzx-widget-chat` - Chat window
- `.anzx-widget-header` - Header area
- `.anzx-widget-messages` - Messages container
- `.anzx-message.user` - User messages
- `.anzx-message.assistant` - AI messages
- `.anzx-widget-input` - Input area

## Browser Support

- Chrome 60+
- Firefox 55+
- Safari 12+
- Edge 79+
- Internet Explorer 11 (with polyfills)

## Security

### Domain Validation

Configure allowed domains in your ANZx.ai dashboard to prevent unauthorized usage:

```javascript
// Only works on configured domains
allowedDomains: [
    'https://yourdomain.com',
    'https://www.yourdomain.com',
    'https://*.yourdomain.com' // Wildcard support
]
```

### Rate Limiting

Built-in rate limiting prevents spam:
- Default: 10 messages per minute per visitor
- Configurable in widget settings

## Development

### Building from Source

```bash
# Install dependencies
npm install

# Development build with watch
npm run dev

# Production build
npm run build

# Run tests
npm test

# Check bundle size
npm run size-check

# Analyze bundle
npm run build:analyze
```

### Testing

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run specific test file
npm test widget.test.js
```

### Local Development

1. Start the development server:
```bash
npm run serve
```

2. Open the demo page:
```
http://localhost:8080/demo/
```

## Troubleshooting

### Common Issues

**Widget not appearing:**
- Check that `widgetId` and `apiKey` are correct
- Verify domain is allowed in widget settings
- Check browser console for errors

**WebSocket connection failing:**
- Widget automatically falls back to HTTP polling
- Check network connectivity and firewall settings
- Verify WebSocket URL is accessible

**Messages not sending:**
- Check rate limiting (default: 10 messages/minute)
- Verify API endpoint is reachable
- Check message length (default max: 1000 characters)

### Debug Mode

Enable debug logging:

```javascript
const widget = new ANZxChatWidget({
    widgetId: 'your_widget_id',
    apiKey: 'your_api_key',
    debug: true // Enable debug logging
});
```

### Performance Optimization

- Widget lazy loads to minimize initial page load impact
- Images in messages are lazy loaded
- Automatic cleanup of old messages to prevent memory leaks
- Efficient WebSocket connection management with heartbeat

## Support

- Documentation: https://docs.anzx.ai/chat-widget
- API Reference: https://api.anzx.ai/docs
- Support: support@anzx.ai
- GitHub Issues: https://github.com/anzx-ai/chat-widget/issues

## License

MIT License - see LICENSE file for details.
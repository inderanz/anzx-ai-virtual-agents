/**
 * ANZx Chat Widget Tests
 */

// Mock DOM methods
global.document = {
  createElement: jest.fn(() => ({
    id: '',
    className: '',
    innerHTML: '',
    style: {},
    setAttribute: jest.fn(),
    getAttribute: jest.fn(),
    addEventListener: jest.fn(),
    appendChild: jest.fn(),
    querySelector: jest.fn(),
    querySelectorAll: jest.fn(() => [])
  })),
  getElementById: jest.fn(),
  head: {
    appendChild: jest.fn()
  },
  body: {
    appendChild: jest.fn()
  },
  addEventListener: jest.fn()
};

global.window = {
  location: {
    href: 'https://example.com',
    origin: 'https://example.com'
  },
  localStorage: {
    getItem: jest.fn(),
    setItem: jest.fn()
  },
  WebSocket: jest.fn(),
  fetch: jest.fn()
};

global.navigator = {
  userAgent: 'test-agent',
  language: 'en-US'
};

global.screen = {
  width: 1920,
  height: 1080
};

global.Intl = {
  DateTimeFormat: () => ({
    resolvedOptions: () => ({ timeZone: 'UTC' })
  })
};

// Import the widget after mocking globals
const ANZxChatWidget = require('../widget.js');

describe('ANZxChatWidget', () => {
  let widget;
  
  beforeEach(() => {
    // Reset mocks
    jest.clearAllMocks();
    
    // Mock DOM elements
    const mockElement = {
      id: '',
      className: '',
      innerHTML: '',
      style: { display: 'none', height: 'auto' },
      value: '',
      disabled: false,
      setAttribute: jest.fn(),
      getAttribute: jest.fn(),
      addEventListener: jest.fn(),
      appendChild: jest.fn(),
      querySelector: jest.fn(),
      querySelectorAll: jest.fn(() => []),
      focus: jest.fn(),
      scrollHeight: 40,
      scrollTop: 0,
      parentNode: {
        removeChild: jest.fn()
      }
    };
    
    document.createElement.mockReturnValue(mockElement);
    document.getElementById.mockReturnValue(mockElement);
    document.body.appendChild.mockReturnValue(mockElement);
  });
  
  afterEach(() => {
    if (widget) {
      try {
        widget.destroy();
      } catch (e) {
        // Ignore cleanup errors in tests
      }
      widget = null;
    }
  });
  
  describe('Initialization', () => {
    test('should throw error without required config', () => {
      expect(() => {
        new ANZxChatWidget({});
      }).toThrow('ANZx Chat Widget: widgetId and apiKey are required');
    });
    
    test('should initialize with valid config', () => {
      expect(() => {
        widget = new ANZxChatWidget({
          widgetId: 'test_widget',
          apiKey: 'test_api_key'
        });
      }).not.toThrow();
    });
    
    test('should set default configuration values', () => {
      widget = new ANZxChatWidget({
        widgetId: 'test_widget',\n        apiKey: 'test_api_key'\n      });\n      \n      expect(widget.config.apiUrl).toBe('https://api.anzx.ai');\n      expect(widget.config.theme).toBe('light');\n      expect(widget.config.position).toBe('bottom-right');\n      expect(widget.config.primaryColor).toBe('#007bff');\n      expect(widget.config.maxMessageLength).toBe(1000);\n    });\n    \n    test('should override default config with provided values', () => {\n      widget = new ANZxChatWidget({\n        widgetId: 'test_widget',\n        apiKey: 'test_api_key',\n        theme: 'dark',\n        primaryColor: '#ff0000',\n        maxMessageLength: 500\n      });\n      \n      expect(widget.config.theme).toBe('dark');\n      expect(widget.config.primaryColor).toBe('#ff0000');\n      expect(widget.config.maxMessageLength).toBe(500);\n    });\n  });\n  \n  describe('State Management', () => {\n    beforeEach(() => {\n      widget = new ANZxChatWidget({\n        widgetId: 'test_widget',\n        apiKey: 'test_api_key'\n      });\n    });\n    \n    test('should initialize with correct default state', () => {\n      expect(widget.state.isOpen).toBe(false);\n      expect(widget.state.isConnected).toBe(false);\n      expect(widget.state.rateLimitExceeded).toBe(false);\n      expect(widget.state.isTyping).toBe(false);\n      expect(widget.state.conversationId).toBeDefined();\n      expect(widget.state.visitorId).toBeDefined();\n    });\n    \n    test('should generate unique conversation ID', () => {\n      const id1 = widget.generateId();\n      const id2 = widget.generateId();\n      \n      expect(id1).not.toBe(id2);\n      expect(id1).toMatch(/^conv_[a-z0-9]+_\\d+$/);\n    });\n    \n    test('should get or create visitor ID', () => {\n      const visitorId = widget.getVisitorId();\n      \n      expect(visitorId).toBeDefined();\n      expect(typeof visitorId).toBe('string');\n      expect(window.localStorage.setItem).toHaveBeenCalled();\n    });\n  });\n  \n  describe('Widget UI', () => {\n    beforeEach(() => {\n      widget = new ANZxChatWidget({\n        widgetId: 'test_widget',\n        apiKey: 'test_api_key'\n      });\n    });\n    \n    test('should create widget container', () => {\n      expect(document.createElement).toHaveBeenCalledWith('div');\n      expect(document.body.appendChild).toHaveBeenCalled();\n    });\n    \n    test('should apply correct CSS classes', () => {\n      const mockElement = document.createElement();\n      expect(mockElement.className).toContain('anzx-widget');\n    });\n    \n    test('should toggle widget visibility', () => {\n      const mockChat = { style: { display: 'none' } };\n      const mockButton = { style: { display: 'flex' } };\n      \n      document.getElementById\n        .mockReturnValueOnce(mockChat)\n        .mockReturnValueOnce(mockButton)\n        .mockReturnValueOnce({ focus: jest.fn() });\n      \n      widget.openWidget();\n      expect(widget.state.isOpen).toBe(true);\n      \n      widget.closeWidget();\n      expect(widget.state.isOpen).toBe(false);\n    });\n  });\n  \n  describe('Message Handling', () => {\n    beforeEach(() => {\n      widget = new ANZxChatWidget({\n        widgetId: 'test_widget',\n        apiKey: 'test_api_key'\n      });\n      \n      // Mock fetch for HTTP requests\n      global.fetch = jest.fn(() =>\n        Promise.resolve({\n          ok: true,\n          json: () => Promise.resolve({\n            ai_response: {\n              content: 'Test response',\n              citations: []\n            }\n          })\n        })\n      );\n    });\n    \n    test('should display messages correctly', () => {\n      const mockMessages = {\n        appendChild: jest.fn(),\n        scrollTop: 0,\n        scrollHeight: 100\n      };\n      \n      document.getElementById.mockReturnValue(mockMessages);\n      \n      widget.displayMessage('Hello', 'user');\n      \n      expect(mockMessages.appendChild).toHaveBeenCalled();\n      expect(mockMessages.scrollTop).toBe(100);\n    });\n    \n    test('should handle input changes', () => {\n      const mockInput = {\n        value: 'test message',\n        style: { height: 'auto' },\n        scrollHeight: 60\n      };\n      const mockSend = { disabled: false };\n      \n      document.getElementById\n        .mockReturnValueOnce(mockInput)\n        .mockReturnValueOnce(mockSend);\n      \n      widget.handleInputChange();\n      \n      expect(mockInput.style.height).toBe('60px');\n      expect(mockSend.disabled).toBe(false);\n    });\n    \n    test('should validate message length', () => {\n      const mockInput = {\n        value: 'a'.repeat(1001), // Exceeds default limit\n        style: { height: 'auto' },\n        scrollHeight: 60\n      };\n      const mockSend = { disabled: false };\n      \n      document.getElementById\n        .mockReturnValueOnce(mockInput)\n        .mockReturnValueOnce(mockSend);\n      \n      widget.handleInputChange();\n      \n      expect(mockSend.disabled).toBe(true);\n    });\n  });\n  \n  describe('WebSocket Connection', () => {\n    beforeEach(() => {\n      // Mock WebSocket\n      global.WebSocket = jest.fn(() => ({\n        send: jest.fn(),\n        close: jest.fn(),\n        readyState: 1, // OPEN\n        onopen: null,\n        onmessage: null,\n        onclose: null,\n        onerror: null\n      }));\n      \n      widget = new ANZxChatWidget({\n        widgetId: 'test_widget',\n        apiKey: 'test_api_key'\n      });\n    });\n    \n    test('should create WebSocket connection', () => {\n      widget.connectWebSocket();\n      \n      expect(WebSocket).toHaveBeenCalledWith(\n        expect.stringContaining('wss://api.anzx.ai/api/chat-widget/ws/test_widget')\n      );\n    });\n    \n    test('should handle WebSocket messages', () => {\n      const mockData = {\n        type: 'message',\n        content: 'Hello from AI',\n        citations: []\n      };\n      \n      widget.displayMessage = jest.fn();\n      widget.hideTypingIndicator = jest.fn();\n      \n      widget.handleWebSocketMessage(mockData);\n      \n      expect(widget.hideTypingIndicator).toHaveBeenCalled();\n      expect(widget.displayMessage).toHaveBeenCalledWith(\n        'Hello from AI',\n        'assistant',\n        []\n      );\n    });\n  });\n  \n  describe('Visitor Information', () => {\n    beforeEach(() => {\n      widget = new ANZxChatWidget({\n        widgetId: 'test_widget',\n        apiKey: 'test_api_key'\n      });\n    });\n    \n    test('should collect visitor information', () => {\n      const visitorInfo = widget.getVisitorInfo();\n      \n      expect(visitorInfo).toHaveProperty('visitor_id');\n      expect(visitorInfo).toHaveProperty('user_agent', 'test-agent');\n      expect(visitorInfo).toHaveProperty('language', 'en-US');\n      expect(visitorInfo).toHaveProperty('page_url', 'https://example.com');\n      expect(visitorInfo).toHaveProperty('timestamp');\n    });\n  });\n  \n  describe('Cleanup', () => {\n    beforeEach(() => {\n      widget = new ANZxChatWidget({\n        widgetId: 'test_widget',\n        apiKey: 'test_api_key'\n      });\n    });\n    \n    test('should clean up resources on destroy', () => {\n      const mockSocket = {\n        close: jest.fn()\n      };\n      const mockContainer = {\n        parentNode: {\n          removeChild: jest.fn()\n        }\n      };\n      \n      widget.socket = mockSocket;\n      widget.container = mockContainer;\n      widget.pollingInterval = setInterval(() => {}, 1000);\n      \n      widget.destroy();\n      \n      expect(mockSocket.close).toHaveBeenCalled();\n      expect(mockContainer.parentNode.removeChild).toHaveBeenCalledWith(mockContainer);\n    });\n  });\n});"
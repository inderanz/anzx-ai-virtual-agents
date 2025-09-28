# ANZx.ai Website

A simple static website with a cricket agent interface.

## Features

- **Home Page**: Main landing page with navigation
- **Cricket Agent**: Interactive chat interface for cricket queries
- **Responsive Design**: Works on desktop and mobile devices

## Local Development

### Prerequisites

- Node.js 16+ (for testing)
- Python 3 (for local server)

### Running Locally

1. **Start the development server:**
   ```bash
   npm run dev
   # or
   python3 -m http.server 8080
   ```

2. **Open your browser:**
   - Navigate to `http://localhost:8080`
   - Click on "Cricket Agent" to access the chat interface

### Testing

Run the test suite:
```bash
npm test
```

Run tests in watch mode:
```bash
npm run test:watch
```

### Linting

Check code style:
```bash
npm run lint
```

## Cricket Agent Interface

The cricket agent provides an interactive chat interface where users can ask questions about:

- **Fixtures**: "Show me the fixtures for Caroline Springs"
- **Ladder**: "What is the current ladder position?"
- **Player Stats**: "How many runs did John score?"
- **Next Match**: "When is the next game?"
- **Roster**: "Who is in the team?"

### Features

- Real-time chat interface
- Message history
- Suggestion buttons for common queries
- Responsive design
- Error handling

## File Structure

```
website/
├── index.html          # Main landing page
├── cricket.html        # Cricket agent interface
├── styles/
│   ├── main.css       # Main styles
│   └── cricket.css     # Cricket chat styles
├── scripts/
│   ├── main.js        # Main page scripts
│   └── cricket.js     # Cricket chat functionality
├── tests/
│   ├── setup.js       # Test setup
│   └── cricket.test.js # Cricket chat tests
├── package.json       # Dependencies and scripts
└── README.md          # This file
```

## Deployment

This is a static website that can be deployed to any static hosting service:

- **Google Cloud Storage**: Upload files to a GCS bucket with static website hosting
- **Netlify**: Connect to your Git repository for automatic deployments
- **Vercel**: Deploy with zero configuration
- **GitHub Pages**: Enable GitHub Pages in repository settings

## Configuration

The cricket agent interface connects to the cricket-agent service. Update the API endpoint in `scripts/cricket.js` if needed:

```javascript
const API_BASE_URL = 'http://localhost:8002'; // Update for production
```

## Browser Support

- Chrome 60+
- Firefox 60+
- Safari 12+
- Edge 79+

## Contributing

1. Make changes to HTML, CSS, or JavaScript files
2. Run tests: `npm test`
3. Test locally: `npm run dev`
4. Commit and push changes

## License

MIT License - see LICENSE file for details.
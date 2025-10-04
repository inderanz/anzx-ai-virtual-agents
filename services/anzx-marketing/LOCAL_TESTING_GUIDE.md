# Local Testing Guide for ANZX Marketing

## Prerequisites

- Node.js 18+ installed
- npm or yarn package manager

## Quick Start

### 1. Install Dependencies

```bash
cd services/anzx-marketing
npm install
```

### 2. Set Up Environment Variables

Create a `.env.local` file:

```bash
cp .env.local.example .env.local
```

Edit `.env.local` with your local configuration:

```env
# Core API (optional for static pages)
NEXT_PUBLIC_CORE_API_URL=http://localhost:8000

# Chat Widget (optional)
NEXT_PUBLIC_CHAT_WIDGET_URL=http://localhost:3001

# Analytics (optional for local dev)
NEXT_PUBLIC_GA_MEASUREMENT_ID=
NEXT_PUBLIC_CLARITY_PROJECT_ID=

# Google Cloud (optional for local dev)
NEXT_PUBLIC_GOOGLE_CLOUD_PROJECT=anzx-ai-platform
NEXT_PUBLIC_AGENT_SPACE_URL=https://agentspace.googleapis.com

# Site URL
NEXT_PUBLIC_SITE_URL=http://localhost:3000
```

### 3. Run Development Server

```bash
npm run dev
```

The site will be available at: **http://localhost:3000**

### 4. Test Different Pages

Open your browser and navigate to:

- **Homepage**: http://localhost:3000
- **English Homepage**: http://localhost:3000/en
- **Hindi Homepage**: http://localhost:3000/hi
- **AI Interviewer**: http://localhost:3000/en/ai-interviewer
- **Customer Service AI**: http://localhost:3000/en/customer-service-ai
- **AI Sales Agent**: http://localhost:3000/en/ai-sales-agent
- **Blog**: http://localhost:3000/en/blog
- **Integrations**: http://localhost:3000/en/integrations

### 5. Run Type Checking

```bash
npm run type-check
```

### 6. Run Tests

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage
```

### 7. Build for Production

```bash
npm run build
npm start
```

## Troubleshooting

### Issue: Module not found errors

**Solution**: Make sure all dependencies are installed:
```bash
rm -rf node_modules package-lock.json
npm install
```

### Issue: TypeScript errors

**Solution**: Run type checking to see specific errors:
```bash
npm run type-check
```

### Issue: Port 3000 already in use

**Solution**: Use a different port:
```bash
PORT=3001 npm run dev
```

### Issue: Missing environment variables

**Solution**: Create `.env.local` file with required variables (see step 2)

### Issue: i18n errors

**Solution**: Make sure message files exist:
```bash
ls messages/
# Should show: en.json  hi.json
```

## Testing Checklist

### ✅ Basic Functionality
- [ ] Homepage loads without errors
- [ ] Navigation works between pages
- [ ] Language switcher toggles between English and Hindi
- [ ] Images load correctly
- [ ] Forms render properly

### ✅ Responsive Design
- [ ] Mobile view (375px width)
- [ ] Tablet view (768px width)
- [ ] Desktop view (1920px width)

### ✅ Performance
- [ ] Page loads in < 3 seconds
- [ ] Images lazy load
- [ ] No console errors
- [ ] Smooth animations

### ✅ Accessibility
- [ ] Keyboard navigation works
- [ ] Screen reader compatible
- [ ] Proper heading hierarchy
- [ ] Alt text on images

## Development Tips

### Hot Reload

Next.js automatically reloads when you save files. If it doesn't:
1. Check the terminal for errors
2. Restart the dev server
3. Clear `.next` folder: `rm -rf .next`

### Debugging

Add console logs or use browser DevTools:
```typescript
console.log('Debug:', variable);
```

### Component Development

Test individual components in isolation:
```typescript
// Create a test page in app/[locale]/test/page.tsx
import { MyComponent } from '@/components/MyComponent';

export default function TestPage() {
  return <MyComponent />;
}
```

## Common Commands

```bash
# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Run linter
npm run lint

# Type check
npm run type-check

# Run tests
npm test

# Run tests with coverage
npm run test:coverage
```

## File Structure

```
services/anzx-marketing/
├── app/                    # Next.js App Router
│   ├── [locale]/          # Locale-based routing
│   │   ├── page.tsx       # Homepage
│   │   ├── blog/          # Blog pages
│   │   ├── ai-interviewer/
│   │   └── ...
│   └── globals.css        # Global styles
├── components/            # React components
│   ├── ui/               # UI components
│   ├── blog/             # Blog components
│   ├── analytics/        # Analytics components
│   └── ...
├── lib/                  # Utility libraries
│   ├── analytics/        # Analytics utilities
│   ├── google-cloud/     # Google Cloud integrations
│   └── ...
├── messages/             # i18n translations
│   ├── en.json          # English
│   └── hi.json          # Hindi
├── public/              # Static assets
│   ├── avatars/         # Agent avatars
│   ├── backgrounds/     # Background images
│   └── ...
├── content/             # MDX content
│   └── blog/           # Blog posts
├── __tests__/          # Test files
├── e2e/                # E2E tests
└── docs/               # Documentation
```

## Next Steps

1. ✅ Install dependencies
2. ✅ Set up environment variables
3. ✅ Run development server
4. ✅ Test in browser
5. ✅ Run type checking
6. ✅ Run tests
7. ✅ Build for production

## Support

If you encounter issues:
1. Check the terminal for error messages
2. Review the troubleshooting section above
3. Check the Next.js documentation: https://nextjs.org/docs
4. Check the next-intl documentation: https://next-intl-docs.vercel.app/

---

**Happy Testing! 🚀**

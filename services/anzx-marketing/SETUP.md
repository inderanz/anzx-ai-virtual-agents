# ANZX Marketing - Development Setup Guide

This guide will help you set up the ANZX Marketing website for local development.

## Prerequisites

- Node.js 18+ and npm
- Google Cloud SDK (gcloud CLI)
- Access to ANZX Google Cloud project
- Firebase project credentials (optional for auth features)

## Quick Start

1. **Run the setup script:**
   ```bash
   cd services/anzx-marketing
   chmod +x scripts/setup-dev.sh
   ./scripts/setup-dev.sh
   ```

2. **Configure environment variables:**
   ```bash
   cp .env.local.example .env.local
   # Edit .env.local with your configuration
   ```

3. **Start development server:**
   ```bash
   npm run dev
   ```

4. **Open in browser:**
   Navigate to [http://localhost:3000](http://localhost:3000)

## Detailed Setup

### 1. Install Dependencies

```bash
npm install
```

### 2. Environment Configuration

Create `.env.local` file with the following variables:

```bash
# Core API (required)
CORE_API_URL=http://localhost:8000

# Firebase (optional - for authentication)
FIREBASE_API_KEY=your_api_key
FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
FIREBASE_PROJECT_ID=your_project_id

# Analytics (optional - for development)
GA_MEASUREMENT_ID=G-XXXXXXXXXX
CLARITY_PROJECT_ID=your_clarity_id

# Google Cloud (required for agent features)
GOOGLE_CLOUD_PROJECT=anzx-ai-platform
```

### 3. Google Cloud Setup

#### Install gcloud CLI

**macOS:**
```bash
brew install google-cloud-sdk
```

**Other platforms:**
Follow instructions at: https://cloud.google.com/sdk/docs/install

#### Authenticate

```bash
# Login to Google Cloud
gcloud auth login

# Set up Application Default Credentials
gcloud auth application-default login

# Set the project
gcloud config set project anzx-ai-platform
```

#### Verify Setup

```bash
# Check current configuration
gcloud config list

# Test authentication
gcloud auth application-default print-access-token
```

### 4. Workload Identity Federation (Production)

For production deployment, we use Workload Identity Federation instead of service account keys.

See `lib/config/workload-identity.ts` for detailed setup instructions.

**Key benefits:**
- No service account keys to manage
- Automatic credential rotation
- Better security posture
- Simplified key management

### 5. Firebase Setup (Optional)

If you need authentication features:

1. Create a Firebase project at https://console.firebase.google.com
2. Enable Authentication with Email/Password
3. Get your Firebase configuration from Project Settings
4. Add credentials to `.env.local`

### 6. Core API Setup

The marketing website integrates with the core-api service:

```bash
# Start core-api (in separate terminal)
cd services/core-api
python -m uvicorn app.main:app --reload --port 8000
```

## Development Workflow

### Running the Development Server

```bash
npm run dev
```

The site will be available at http://localhost:3000

### Building for Production

```bash
npm run build
npm run start
```

### Running Tests

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage
```

### Linting and Type Checking

```bash
# Run ESLint
npm run lint

# Run TypeScript type checking
npm run type-check
```

## Project Structure

```
services/anzx-marketing/
├── app/                    # Next.js App Router pages
│   ├── layout.tsx         # Root layout
│   ├── page.tsx           # Homepage
│   └── globals.css        # Global styles
├── components/            # React components
│   ├── layout/           # Header, Footer, Navigation
│   ├── ui/               # Reusable UI components
│   └── ...
├── lib/                  # Utilities and libraries
│   ├── api/              # API clients
│   ├── config/           # Configuration
│   └── utils/            # Utility functions
├── messages/             # i18n translations
│   ├── en.json          # English
│   └── hi.json          # Hindi
├── public/              # Static assets
└── scripts/             # Setup and utility scripts
```

## Environment Variables Reference

### Required Variables

- `CORE_API_URL` - URL of the core-api service
- `GOOGLE_CLOUD_PROJECT` - Google Cloud project ID

### Optional Variables

- `FIREBASE_API_KEY` - Firebase API key (for auth)
- `FIREBASE_AUTH_DOMAIN` - Firebase auth domain
- `FIREBASE_PROJECT_ID` - Firebase project ID
- `GA_MEASUREMENT_ID` - Google Analytics measurement ID
- `CLARITY_PROJECT_ID` - Microsoft Clarity project ID
- `SENTRY_DSN` - Sentry error tracking DSN

### Feature Flags

- `NEXT_PUBLIC_ENABLE_ANALYTICS` - Enable/disable analytics (default: false in dev)
- `NEXT_PUBLIC_ENABLE_CHAT_WIDGET` - Enable/disable chat widget (default: true)
- `NEXT_PUBLIC_ENABLE_AGENT_DEMO` - Enable/disable agent demo (default: true)
- `NEXT_PUBLIC_DEBUG_MODE` - Enable debug logging (default: true in dev)

## Troubleshooting

### Port Already in Use

If port 3000 is already in use:
```bash
npm run dev -- -p 3001
```

### Google Cloud Authentication Issues

```bash
# Re-authenticate
gcloud auth application-default login

# Check current credentials
gcloud auth application-default print-access-token

# Revoke and re-authenticate
gcloud auth application-default revoke
gcloud auth application-default login
```

### Module Not Found Errors

```bash
# Clear Next.js cache
rm -rf .next

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

### TypeScript Errors

```bash
# Regenerate TypeScript types
npm run type-check
```

## Additional Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [Google Cloud Documentation](https://cloud.google.com/docs)
- [Firebase Documentation](https://firebase.google.com/docs)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)

## Getting Help

- Check the main README.md for project overview
- Review the design document in `.kiro/specs/anzx-marketing-website-enhancement/design.md`
- Contact the development team for access to Google Cloud resources

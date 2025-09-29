# Cricket Chatbot - Enterprise-Grade AI Assistant

## 🏏 Overview

The Cricket Chatbot is a production-ready, enterprise-grade AI assistant for Caroline Springs Cricket Club. It provides real-time cricket information through a modern, responsive web interface with professional UI/UX design.

## ✨ Features

- **🤖 AI-Powered Responses**: Connected to cricket-agent API for intelligent responses
- **🎨 Enterprise UI/UX**: Professional design with modern styling and responsive layout
- **📱 Mobile Responsive**: Optimized for all device sizes
- **⚡ Real-time Chat**: Interactive web-based cricket assistant
- **🔒 Production Ready**: Built with enterprise-grade security and performance

## 🛠️ Technical Stack

- **Frontend**: Next.js 14 (App Router), TypeScript
- **Styling**: Tailwind CSS, shadcn/ui components
- **Icons**: Lucide React
- **Deployment**: Cloudflare Pages
- **Custom Domain**: Cloudflare Worker proxy
- **CI/CD**: Google Cloud Build with Cloud Storage integration

## 🚀 Deployment

### Automated Deployment

The cricket chatbot uses a fully automated CI/CD pipeline with Cloud Storage integration:

```bash
# Deploy the cricket chatbot
gcloud builds submit --config=infrastructure/cloudbuild/pipelines/cricket-chatbot-deploy-fixed.yaml \
  --substitutions=_PROJECT_ID=virtual-stratum-473511-u5,_REGION=australia-southeast1
```

### Manual Deployment

For local development:

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

## 🌐 Access URLs

- **Custom Domain**: https://anzx.ai/cricket
- **Cloudflare Pages**: https://eeb79de4.anzx-cricket.pages.dev
- **API Integration**: Connected to cricket-agent service

## 🎯 Capabilities

The cricket chatbot can answer questions about:

- **Player Information**: "Which team is John Smith in?"
- **Player Stats**: "How many runs did Jane Doe score last match?"
- **Fixtures**: "List all fixtures for Caroline Springs Blue U10"
- **Ladder Position**: "Where are Caroline Springs Blue U10 on the ladder?"
- **Next Match**: "When is the next game for Caroline Springs White U10?"
- **Team Roster**: "Who are the players for Caroline Springs Blue U10?"

## 🏗️ Architecture

### Components

- **CricketChatEnterprise**: Main chat interface component
- **Header**: Navigation and branding
- **Footer**: Links and company information
- **Chat Interface**: Real-time messaging with AI responses

### Styling

- **Global CSS**: Enterprise-grade styling with CSS variables
- **Responsive Design**: Mobile-first approach
- **Professional Theme**: Blue-based color scheme
- **Accessibility**: WCAG 2.2 AA compliant

### API Integration

- **Cricket Agent**: Real-time connection to cricket-agent service
- **Error Handling**: Graceful fallbacks for API failures
- **Loading States**: User-friendly loading indicators

## 🔧 Configuration

### Environment Variables

- `CRICKET_AGENT_API_URL`: Cricket agent service URL
- `NEXT_PUBLIC_APP_URL`: Public application URL

### Secrets (Google Secret Manager)

- `CRICKET_CHATBOT_URL`: Automatically updated deployment URL
- `CLOUDFLARE_API_TOKEN`: Cloudflare API access
- `CLOUDFLARE_ACCOUNT_ID`: Cloudflare account ID
- `CLOUDFLARE_ZONE_ID`: DNS zone ID
- `CLOUDFLARE_WORKER_NAME`: Worker name
- `CLOUDFLARE_ROUTE_PATTERN`: Route pattern

## 📁 Project Structure

```
services/cricket-marketing/
├── app/
│   ├── globals.css          # Global styles with enterprise theming
│   ├── layout.tsx           # Root layout
│   └── page.tsx             # Main page
├── components/
│   ├── cricket-chat-enterprise.tsx  # Main chat component
│   ├── ui/                  # Reusable UI components
│   └── ...
├── lib/
│   ├── utils.ts             # Utility functions
│   └── seo.ts               # SEO helpers
├── public/                  # Static assets
├── package.json             # Dependencies
├── next.config.js           # Next.js configuration
├── tailwind.config.ts       # Tailwind configuration
└── README.md                # This file
```

## 🚀 CI/CD Pipeline

### Build Steps

1. **Build Next.js App**: Install dependencies and build static site
2. **Deploy to Cloudflare Pages**: Upload with URL capture
3. **Upload URL to Cloud Storage**: Store deployment URL for subsequent steps
4. **Update Secret Manager**: Update CRICKET_CHATBOT_URL secret
5. **Prepare Worker Config**: Generate wrangler.toml with latest URLs
6. **Deploy Cloudflare Worker**: Deploy worker with updated configuration
7. **Write State**: Record deployment information to GCS

### Key Features

- **Cloud Storage Integration**: URL capture and transfer between build steps
- **Automatic Secret Management**: CRICKET_CHATBOT_URL updated automatically
- **Automatic Worker Deployment**: Cloudflare Worker deployed with correct configuration
- **Zero Manual Intervention**: Complete end-to-end automation

## 🔍 Monitoring

### Health Checks

- **Custom Domain**: https://anzx.ai/cricket
- **Static Assets**: https://anzx.ai/_next/static/css/...
- **API Integration**: Real-time connection to cricket-agent

### Logs

- **Cloud Build**: [Console](https://console.cloud.google.com/cloud-build)
- **Cloudflare**: Worker logs and analytics
- **Application**: Browser console for client-side issues

## 🛠️ Development

### Local Development

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

### Testing

```bash
# Run tests
npm test

# Run linting
npm run lint

# Type checking
npm run type-check
```

## 📚 Documentation

- **API Documentation**: https://cricket-agent-aa5gcxefza-ts.a.run.app/docs
- **Deployment Guide**: See `docs/DEPLOYMENT_GUIDE.md`
- **Status**: See `docs/STATUS.md`

## 🤝 Contributing

1. Make changes to the codebase
2. Test locally with `npm run dev`
3. Build and test with `npm run build`
4. Deploy using the automated CI/CD pipeline

## 📞 Support

For technical issues:
- **Logs**: [Cloud Logging Console](https://console.cloud.google.com/logs)
- **Builds**: [Cloud Build Console](https://console.cloud.google.com/cloud-build)
- **Cloudflare**: Worker logs and analytics

---

**Status**: ✅ **PRODUCTION READY** - Fully automated deployment with enterprise-grade UI/UX
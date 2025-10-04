# ANZX Marketing Website

Marketing website for ANZX.ai built with Next.js 14.

## Getting Started

1. Install dependencies:
```bash
npm install
```

2. Copy environment variables:
```bash
cp .env.local.example .env.local
```

3. Run development server:
```bash
npm run dev
```

4. Open [http://localhost:3000](http://localhost:3000)

## Features

- Next.js 14 with App Router
- TypeScript
- Tailwind CSS
- Multi-language support (English + Hindi)
- MDX for blog content
- Google Cloud native integration
- Analytics (GA4, Clarity)

## Project Structure

```
services/anzx-marketing/
├── app/              # Next.js App Router
├── components/       # React components
├── lib/             # Utilities and API clients
├── messages/        # i18n translations
├── docs/            # Documentation
└── public/          # Static assets
```

## Documentation

- [Microsoft Clarity Setup Guide](./docs/CLARITY_SETUP.md) - Complete guide for Clarity integration
- [Clarity Quick Reference](./docs/CLARITY_QUICK_REFERENCE.md) - Quick reference for developers

## Analytics

This project includes:
- **Google Analytics 4**: Page views, events, conversions
- **Microsoft Clarity**: Session recordings, heatmaps, user behavior

See the [Clarity Setup Guide](./docs/CLARITY_SETUP.md) for configuration details.

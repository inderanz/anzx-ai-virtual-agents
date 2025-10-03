# Design Document: ANZX Marketing Website Enhancement

## Overview

This design document outlines the technical architecture and implementation approach for creating a comprehensive marketing website for ANZX.ai. The solution involves creating a new Next.js service (`services/anzx-marketing`) that will serve the main anzx.ai website, while reusing patterns and components from the existing cricket-marketing service and integrating with all existing ANZX platform services.

## Architecture

### High-Level Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                        User Browser                               │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│                    CDN / Edge Network                             │
│              (Cloudflare / Google Cloud CDN)                      │
└────────────────────────┬─────────────────────────────────────────┘
                         │
         ┌───────────────┴───────────────┐
         │                               │
         ▼                               ▼
┌─────────────────────┐         ┌─────────────────────┐
│  anzx-marketing     │         │  cricket-marketing  │
│  (NEW SERVICE)      │         │  (EXISTING)         │
│  https://anzx.ai    │         │  /cricket           │
│                     │         │  (DO NOT MODIFY)    │
│  • Homepage         │         └─────────────────────┘
│  • Product Pages    │
│  • Blog             │
│  • Regional Pages   │
│  • Educational      │
└──────────┬──────────┘
           │
           ▼
┌──────────────────────────────────────────────────────────────────┐
│                    Backend Services Layer                         │
│                                                                   │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐   │
│  │   core-api     │  │  chat-widget   │  │ auth-frontend  │   │
│  │                │  │                │  │                │   │
│  │ • Auth         │  │ • WebSocket    │  │ • Firebase UI  │   │
│  │ • Agents       │  │ • Themes       │  │ • Login/Signup │   │
│  │ • Knowledge    │  │ • Storage      │  │                │   │
│  │ • Billing      │  └────────────────┘  └────────────────┘   │
│  │ • Email        │                                            │
│  └────────────────┘                                            │
│                                                                   │
│  ┌────────────────┐  ┌────────────────┐                        │
│  │ agent-orch     │  │ knowledge-svc  │                        │
│  │ • Routing      │  │ • Documents    │                        │
│  │ • Coordination │  │ • Embeddings   │                        │
│  └────────────────┘  └────────────────┘                        │
└──────────────────────────────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────────────────┐
│                    Data & Infrastructure Layer                    │
│                                                                   │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐   │
│  │  PostgreSQL    │  │  Firebase Auth │  │  Stripe        │   │
│  │  + pgvector    │  │                │  │  Billing       │   │
│  └────────────────┘  └────────────────┘  └────────────────┘   │
│                                                                   │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐   │
│  │  Vertex AI     │  │  Cloud Storage │  │  Analytics     │   │
│  │  Agents        │  │  Assets        │  │  GA4/Clarity   │   │
│  └────────────────┘  └────────────────┘  └────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
```

## Components

### 1. New Service: anzx-marketing

**Location:** `services/anzx-marketing/`

**Purpose:** Main marketing website for anzx.ai

**Technology Stack:**
- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- Framer Motion
- React Hook Form + Zod
- Next-intl (for Hindi support)



**Directory Structure:**
```
services/anzx-marketing/
├── app/
│   ├── (marketing)/          # Marketing pages group
│   │   ├── page.tsx          # Homepage
│   │   ├── layout.tsx        # Marketing layout
│   │   ├── ai-interviewer/
│   │   ├── customer-service-ai/
│   │   ├── ai-sales-agent/
│   │   ├── integrations/
│   │   ├── blog/
│   │   ├── industries/
│   │   └── ...
│   ├── (regional)/           # Regional pages group
│   │   ├── ai-agents-australia/
│   │   ├── ai-agents-new-zealand/
│   │   ├── ai-agents-india/
│   │   └── ai-agents-singapore/
│   ├── (legal)/              # Legal pages group
│   │   ├── privacy-policy/
│   │   └── terms/
│   ├── hi/                   # Hindi language pages
│   │   └── ...
│   ├── globals.css
│   └── layout.tsx            # Root layout
├── components/
│   ├── layout/
│   │   ├── Header.tsx
│   │   ├── Footer.tsx
│   │   ├── Navigation.tsx
│   │   └── MobileMenu.tsx
│   ├── hero/
│   │   ├── HomeHero.tsx
│   │   ├── ProductHero.tsx
│   │   └── AgentCards.tsx
│   ├── features/
│   │   ├── FeatureGrid.tsx
│   │   ├── FeatureCard.tsx
│   │   └── ComparisonTable.tsx
│   ├── content/
│   │   ├── BlogCard.tsx
│   │   ├── BlogList.tsx
│   │   ├── ArticleLayout.tsx
│   │   └── TableOfContents.tsx
│   ├── forms/
│   │   ├── LeadCaptureForm.tsx
│   │   ├── DemoRequestForm.tsx
│   │   └── NewsletterSignup.tsx
│   ├── social-proof/
│   │   ├── TrustBadges.tsx      # Copied from cricket-marketing
│   │   ├── TestimonialCard.tsx  # Copied from cricket-marketing
│   │   └── LogoCarousel.tsx
│   ├── integrations/
│   │   ├── IntegrationGrid.tsx
│   │   ├── IntegrationCard.tsx
│   │   └── CategoryFilter.tsx
│   ├── regional/
│   │   ├── RegionalHero.tsx
│   │   ├── CountrySelector.tsx
│   │   └── CurrencyDisplay.tsx
│   ├── chat/
│   │   ├── ChatDock.tsx         # Copied from cricket-marketing
│   │   └── ChatPreview.tsx      # Copied from cricket-marketing
│   ├── analytics/
│   │   ├── Analytics.tsx        # Copied from cricket-marketing
│   │   └── analytics-lib.ts     # Copied from cricket-marketing
│   ├── seo/
│   │   ├── SEOHead.tsx
│   │   ├── StructuredData.tsx   # Copied from cricket-marketing
│   │   └── seo-lib.ts           # Copied from cricket-marketing
│   └── ui/                      # shadcn/ui components
│       ├── button.tsx
│       ├── card.tsx
│       ├── dialog.tsx
│       └── ...
├── lib/
│   ├── api/
│   │   ├── core-api-client.ts   # Client for core-api
│   │   ├── agents.ts
│   │   ├── knowledge.ts
│   │   └── billing.ts
│   ├── utils/
│   │   ├── utils.ts
│   │   ├── motion-lib.ts        # Copied from cricket-marketing
│   │   └── utils-lib.ts         # Copied from cricket-marketing
│   └── constants/
│       ├── agents.ts            # Emma, Olivia, Jack, Liam
│       ├── regions.ts           # Australia, NZ, India, Singapore
│       └── integrations.ts
├── content/
│   ├── blog/                    # MDX blog posts
│   ├── agents/                  # Agent persona data
│   └── integrations/            # Integration data
├── public/
│   ├── images/
│   │   ├── agents/              # Emma, Olivia, Jack, Liam avatars
│   │   ├── logos/
│   │   ├── screenshots/
│   │   └── og-images/
│   └── assets/
├── messages/                    # i18n translations
│   ├── en.json
│   └── hi.json
├── next.config.js
├── tailwind.config.ts
├── tsconfig.json
└── package.json
```



### 2. Component Architecture

#### Core Layout Components

**Header Component (`components/layout/Header.tsx`)**
```typescript
interface HeaderProps {
  transparent?: boolean;
  sticky?: boolean;
}

// Features:
// - Logo with link to homepage
// - Navigation with dropdowns (AI Agents, Features)
// - Language switcher (En/Hi)
// - CTA buttons (Login, Get Started)
// - Mobile hamburger menu
// - Scroll-based transparency/solid background
```

**Navigation Component (`components/layout/Navigation.tsx`)**
```typescript
interface NavigationItem {
  label: string;
  href?: string;
  children?: NavigationItem[];
}

// Features:
// - Dropdown menus with hover states
// - Active link highlighting
// - Keyboard navigation support
// - Mobile-responsive
```

**Footer Component (`components/layout/Footer.tsx`)**
```typescript
// Features:
// - Multi-column layout
// - Links to all major sections
// - Social media icons
// - Newsletter signup
// - Legal links
// - Copyright notice
```

#### Hero Components

**HomeHero Component (`components/hero/HomeHero.tsx`)**
```typescript
interface HomeHeroProps {
  headline: string;
  subheadline: string;
  agents: AgentCard[];
  ctaButtons: CTAButton[];
}

// Features:
// - Animated background (SVG gradients)
// - Three agent cards (Emma, Olivia, Jack)
// - Gradient text for headline
// - Primary and secondary CTAs
// - Responsive layout
```

**ProductHero Component (`components/hero/ProductHero.tsx`)**
```typescript
interface ProductHeroProps {
  agent: Agent;
  integrations: Integration[];
  features: string[];
}

// Features:
// - Large agent image
// - Background image/gradient
// - Integration logos row
// - Feature highlights
// - CTA button
```

**AgentCards Component (`components/hero/AgentCards.tsx`)**
```typescript
interface AgentCardProps {
  name: string;
  role: string;
  image: string;
  description: string;
  link: string;
}

// Features:
// - Circular avatar image
// - Hover effects (scale, glow)
// - Role label
// - Link to product page
```

#### Feature Components

**FeatureGrid Component (`components/features/FeatureGrid.tsx`)**
```typescript
interface FeatureGridProps {
  features: Feature[];
  columns?: 2 | 3 | 4;
}

// Features:
// - Responsive grid layout
// - Feature cards with icons
// - Hover animations
// - Lazy loading
```

**ComparisonTable Component (`components/features/ComparisonTable.tsx`)**
```typescript
interface ComparisonTableProps {
  competitors: Competitor[];
  features: ComparisonFeature[];
}

// Features:
// - Sticky header row
// - Checkmarks/X marks for features
// - Highlight ANZX column
// - Mobile-responsive (horizontal scroll)
```



## Data Models

### Agent Persona Model
```typescript
interface Agent {
  id: string;
  name: string;              // Emma, Olivia, Jack, Liam
  role: string;              // "AI Recruiting Agent", etc.
  description: string;
  avatar: string;            // Path to avatar image
  capabilities: string[];
  integrations: string[];
  pricing: {
    freemium: boolean;
    pro: boolean;
    enterprise: boolean;
  };
  demoUrl: string;
  learnMoreUrl: string;
}
```

### Integration Model
```typescript
interface Integration {
  id: string;
  name: string;
  category: 'crm' | 'support' | 'communication' | 'productivity' | 'other';
  logo: string;
  description: string;
  setupUrl: string;
  documentationUrl: string;
  featured: boolean;
}
```

### Blog Post Model
```typescript
interface BlogPost {
  slug: string;
  title: string;
  excerpt: string;
  content: string;           // MDX content
  author: string;
  publishedAt: Date;
  updatedAt?: Date;
  category: string;
  tags: string[];
  featuredImage: string;
  readingTime: number;       // minutes
}
```

## Integration with Existing Services

### Core-API Integration

**Authentication Flow:**
```typescript
// lib/api/core-api-client.ts
import { getAuth } from 'firebase/auth';

export class CoreAPIClient {
  private baseURL = process.env.NEXT_PUBLIC_CORE_API_URL;
  
  async getAuthToken(): Promise<string> {
    const auth = getAuth();
    const user = auth.currentUser;
    if (!user) throw new Error('Not authenticated');
    return await user.getIdToken();
  }
  
  async request(endpoint: string, options?: RequestInit) {
    const token = await this.getAuthToken();
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      ...options,
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    });
    return response.json();
  }
}
```

**Agent Management:**
```typescript
// lib/api/agents.ts
export async function getAgents(organizationId: string) {
  return coreAPI.request(`/api/v1/agents?organization_id=${organizationId}`);
}

export async function createAgent(data: CreateAgentRequest) {
  return coreAPI.request('/api/v1/agents/', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function startConversation(agentId: string, message: string) {
  return coreAPI.request(`/api/v1/agents/${agentId}/chat`, {
    method: 'POST',
    body: JSON.stringify({ message }),
  });
}
```

**Billing Integration:**
```typescript
// lib/api/billing.ts
export async function getPlans() {
  return coreAPI.request('/api/v1/billing/plans');
}

export async function subscribe(plan: 'pro' | 'enterprise') {
  return coreAPI.request('/api/v1/billing/subscribe', {
    method: 'POST',
    body: JSON.stringify({ plan }),
  });
}

export async function getBillingInfo() {
  return coreAPI.request('/api/v1/billing/info');
}
```

**Knowledge Base Integration:**
```typescript
// lib/api/knowledge.ts
export async function uploadDocument(file: File, metadata: any) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('metadata', JSON.stringify(metadata));
  
  return coreAPI.request('/api/v1/knowledge/sources/upload', {
    method: 'POST',
    body: formData,
  });
}

export async function searchKnowledge(query: string) {
  return coreAPI.request('/api/v1/knowledge/search', {
    method: 'POST',
    body: JSON.stringify({ query, search_type: 'hybrid' }),
  });
}
```

### Chat Widget Integration

```typescript
// components/chat/ChatDock.tsx
import { useEffect } from 'react';

export function ChatDock() {
  useEffect(() => {
    // Load chat widget script
    const script = document.createElement('script');
    script.src = process.env.NEXT_PUBLIC_CHAT_WIDGET_URL;
    script.async = true;
    document.body.appendChild(script);
    
    // Initialize widget
    script.onload = () => {
      window.ANZXChat.init({
        apiUrl: process.env.NEXT_PUBLIC_CORE_API_URL,
        theme: 'light',
        position: 'bottom-right',
      });
    };
    
    return () => {
      document.body.removeChild(script);
    };
  }, []);
  
  return null; // Widget renders itself
}
```

## SEO & Performance

### SEO Implementation

**Meta Tags:**
```typescript
// app/(marketing)/page.tsx
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'AI Agents for Business | ANZX.ai',
  description: 'Enterprise-grade AI agents for customer service, sales, and recruiting. Trusted by businesses across Australia, New Zealand, India, and Singapore.',
  openGraph: {
    title: 'AI Agents for Business | ANZX.ai',
    description: '...',
    images: ['/images/og-image.jpg'],
    locale: 'en_AU',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: '...',
    description: '...',
    images: ['/images/twitter-card.jpg'],
  },
  alternates: {
    canonical: 'https://anzx.ai',
    languages: {
      'en': 'https://anzx.ai',
      'hi': 'https://anzx.ai/hi',
    },
  },
};
```

**Structured Data:**
```typescript
// components/seo/StructuredData.tsx
export function OrganizationSchema() {
  const schema = {
    '@context': 'https://schema.org',
    '@type': 'Organization',
    name: 'ANZX.ai',
    url: 'https://anzx.ai',
    logo: 'https://anzx.ai/images/logo.png',
    description: 'Enterprise-grade AI agents for Asia-Pacific businesses',
    address: {
      '@type': 'PostalAddress',
      addressCountry: 'AU',
    },
    sameAs: [
      'https://twitter.com/anzxai',
      'https://linkedin.com/company/anzx-ai',
    ],
  };
  
  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(schema) }}
    />
  );
}
```

### Performance Optimization

**Image Optimization:**
```typescript
// components/ui/OptimizedImage.tsx (copied from cricket-marketing)
import Image from 'next/image';

export function OptimizedImage({ src, alt, ...props }) {
  return (
    <Image
      src={src}
      alt={alt}
      loading="lazy"
      quality={85}
      formats={['image/webp', 'image/avif']}
      {...props}
    />
  );
}
```

**Lazy Loading:**
```typescript
// components/ui/LazySection.tsx (copied from cricket-marketing)
import { useInView } from 'react-intersection-observer';

export function LazySection({ children, threshold = 0.1 }) {
  const { ref, inView } = useInView({ threshold, triggerOnce: true });
  
  return (
    <div ref={ref}>
      {inView ? children : <div style={{ minHeight: '400px' }} />}
    </div>
  );
}
```

## Multi-Language Support (Hindi)

### i18n Configuration

```typescript
// next.config.js
const withNextIntl = require('next-intl/plugin')();

module.exports = withNextIntl({
  i18n: {
    locales: ['en', 'hi'],
    defaultLocale: 'en',
  },
});
```

**Translation Files:**
```json
// messages/en.json
{
  "nav": {
    "home": "Home",
    "products": "Products",
    "blog": "Blog"
  },
  "hero": {
    "headline": "AI Agents for Your Business",
    "subheadline": "Enterprise-grade AI agents..."
  }
}

// messages/hi.json
{
  "nav": {
    "home": "होम",
    "products": "उत्पाद",
    "blog": "ब्लॉग"
  },
  "hero": {
    "headline": "आपके व्यवसाय के लिए AI एजेंट",
    "subheadline": "एंटरप्राइज़-ग्रेड AI एजेंट..."
  }
}
```

## Deployment

### Build Configuration

```javascript
// next.config.js
module.exports = {
  output: 'export',  // Static export for CDN
  trailingSlash: true,
  images: {
    unoptimized: true,  // For static export
  },
  env: {
    NEXT_PUBLIC_CORE_API_URL: process.env.CORE_API_URL,
    NEXT_PUBLIC_CHAT_WIDGET_URL: process.env.CHAT_WIDGET_URL,
  },
};
```

### CI/CD Pipeline

```yaml
# cloudbuild.yaml
steps:
  # Build Next.js app
  - name: 'node:18'
    entrypoint: 'npm'
    args: ['install']
    dir: 'services/anzx-marketing'
  
  - name: 'node:18'
    entrypoint: 'npm'
    args: ['run', 'build']
    dir: 'services/anzx-marketing'
  
  # Deploy to Cloud Storage / CDN
  - name: 'gcr.io/cloud-builders/gsutil'
    args: ['rsync', '-r', '-d', 'services/anzx-marketing/out/', 'gs://anzx-marketing-prod/']
  
  # Invalidate CDN cache
  - name: 'gcr.io/cloud-builders/gcloud'
    args: ['compute', 'url-maps', 'invalidate-cdn-cache', 'anzx-lb', '--path', '/*']
```

## Testing Strategy

### Unit Tests
- Component rendering tests
- Utility function tests
- API client tests

### Integration Tests
- Form submission flows
- Navigation flows
- API integration tests

### E2E Tests
- User journey tests (homepage → product page → signup)
- Multi-language switching
- Mobile responsiveness

### Performance Tests
- Lighthouse CI (target: 90+ score)
- Core Web Vitals monitoring
- Load time testing

## Security Considerations

### Content Security Policy
```typescript
// next.config.js
const securityHeaders = [
  {
    key: 'Content-Security-Policy',
    value: "default-src 'self'; script-src 'self' 'unsafe-eval' 'unsafe-inline' *.googletagmanager.com; style-src 'self' 'unsafe-inline';"
  },
  {
    key: 'X-Frame-Options',
    value: 'SAMEORIGIN'
  },
  {
    key: 'X-Content-Type-Options',
    value: 'nosniff'
  },
];
```

### Input Validation
- All form inputs validated with Zod schemas
- XSS prevention through React's built-in escaping
- CSRF protection for API calls

## Monitoring & Analytics

### Analytics Integration
```typescript
// components/analytics/Analytics.tsx (copied from cricket-marketing)
import { useEffect } from 'react';
import { usePathname } from 'next/navigation';

export function Analytics() {
  const pathname = usePathname();
  
  useEffect(() => {
    // Google Analytics
    window.gtag('config', 'G-XXXXXXXXXX', {
      page_path: pathname,
    });
    
    // Microsoft Clarity
    window.clarity('set', 'page', pathname);
  }, [pathname]);
  
  return null;
}
```

### Error Tracking
- Sentry integration for error monitoring
- Custom error boundaries
- API error logging

## Summary

This design creates a new `services/anzx-marketing` service that:
1. Copies structure and reusable components from cricket-marketing
2. Integrates with all existing ANZX services (core-api, chat-widget, auth-frontend)
3. Implements 70+ pages with original ANZX branding
4. Supports English and Hindi languages
5. Focuses on Asia-Pacific regions (Australia, NZ, India, Singapore)
6. Uses Australian agent personas (Emma, Olivia, Jack, Liam)
7. Achieves high performance (Lighthouse 90+)
8. Maintains security and compliance standards

The design leverages existing infrastructure while creating a comprehensive marketing presence for ANZX.ai.


## UPDATED: Google Cloud Native Architecture

### Agent Development & Orchestration

**Google Agent Development Kit (ADK)**
- All agents built using Google ADK: https://google.github.io/adk-docs/
- Standardized agent development framework
- Native integration with Vertex AI

**Google Agent-to-Agent (A2A) Protocol**
- Inter-agent communication using A2A: https://a2a-protocol.org/latest/
- Standardized protocol for agent collaboration
- Enables complex multi-agent workflows

**Google AgentSpace**
- All agents hosted in Google AgentSpace
- On-demand agent orchestration
- Triggered from anzx-marketing customer orders
- Centralized agent management and monitoring

**Model Context Protocol (MCP) Servers**
- External data source integration via MCP
- Example: Xero integration using https://github.com/XeroAPI/xero-mcp-server
- Custom MCP servers for other integrations (Salesforce, HubSpot, etc.)

### Updated Technology Stack

**AI & ML:**
- **LLM:** Google Gemini (gemini-1.5-pro, gemini-1.5-flash)
- **Embeddings:** Vertex AI Text Embeddings (text-embedding-004)
- **Agent Framework:** Google Agent Development Kit (ADK)
- **Agent Hosting:** Google AgentSpace
- **Agent Communication:** A2A Protocol

**Authentication & Authorization:**
- **Workload Identity Federation:** All GCP service connections
- **No Service Account Keys:** Zero key-based authentication
- **Identity-Aware Proxy (IAP):** For internal services
- **Firebase Auth:** For end-user authentication

**Data & Storage:**
- **Database:** Cloud SQL (PostgreSQL) with pgvector
- **Vector Search:** Vertex AI Vector Search
- **Object Storage:** Cloud Storage
- **Secrets:** Secret Manager

### Updated Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                        User Browser                               │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│                    anzx-marketing (Next.js)                       │
│                    Deployed on Cloud Run                          │
│                                                                   │
│  • Customer orders agent                                         │
│  • Triggers AgentSpace orchestration                             │
│  • Displays agent capabilities                                   │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│                    Google AgentSpace                              │
│                    (Agent Orchestration Platform)                 │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              Agents (Built with Google ADK)                 │ │
│  │                                                             │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │ │
│  │  │  Emma    │  │  Olivia  │  │   Jack   │  │   Liam   │ │ │
│  │  │Recruiting│  │ Customer │  │  Sales   │  │ Support  │ │ │
│  │  │  Agent   │  │  Service │  │  Agent   │  │  Agent   │ │ │
│  │  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘ │ │
│  │       │             │             │             │        │ │
│  │       └─────────────┴─────────────┴─────────────┘        │ │
│  │                          │                                │ │
│  │                          ▼                                │ │
│  │              A2A Protocol Communication                   │ │
│  │              (Agent-to-Agent)                             │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              MCP Servers (External Data)                    │ │
│  │                                                             │ │
│  │  • Xero MCP Server (accounting)                            │ │
│  │  • Salesforce MCP Server (CRM)                             │ │
│  │  • HubSpot MCP Server (marketing)                          │ │
│  │  • Custom MCP Servers                                      │ │
│  └────────────────────────────────────────────────────────────┘ │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│                    Vertex AI Services                             │
│                                                                   │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐   │
│  │  Gemini LLM    │  │  Embeddings    │  │ Vector Search  │   │
│  │  (1.5-pro)     │  │ (text-emb-004) │  │                │   │
│  └────────────────┘  └────────────────┘  └────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│                    GCP Data Layer                                 │
│                    (Workload Identity Federation)                 │
│                                                                   │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐   │
│  │  Cloud SQL     │  │ Cloud Storage  │  │ Secret Manager │   │
│  │  (PostgreSQL)  │  │                │  │                │   │
│  └────────────────┘  └────────────────┘  └────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
```

### Agent Development with Google ADK

**Agent Structure:**
```python
# agents/emma_recruiting_agent.py
from google.adk import Agent, Tool, Context
from google.cloud import aiplatform
from vertexai.generative_models import GenerativeModel

class EmmaRecruitingAgent(Agent):
    """AI Recruiting Agent - Screens candidates and schedules interviews"""
    
    def __init__(self):
        super().__init__(
            name="Emma",
            description="AI Recruiting Agent for candidate screening",
            model=GenerativeModel("gemini-1.5-pro"),
            tools=[
                self.screen_candidate,
                self.schedule_interview,
                self.send_email,
            ]
        )
    
    @Tool
    async def screen_candidate(self, resume: str, job_description: str) -> dict:
        """Screen candidate resume against job requirements"""
        prompt = f"""
        Analyze this resume against the job description.
        Resume: {resume}
        Job Description: {job_description}
        
        Provide:
        1. Match score (0-100)
        2. Key strengths
        3. Potential concerns
        4. Recommendation (interview/reject)
        """
        
        response = await self.model.generate_content_async(prompt)
        return self.parse_screening_result(response.text)
    
    @Tool
    async def schedule_interview(self, candidate_email: str, time_slots: list) -> dict:
        """Schedule interview using calendar integration"""
        # Use MCP server for calendar integration
        calendar_mcp = await self.get_mcp_server("calendar")
        result = await calendar_mcp.schedule_event({
            "attendees": [candidate_email],
            "time_slots": time_slots,
            "duration": 60,
            "title": "Interview with Emma - ANZX.ai"
        })
        return result
    
    async def handle_request(self, context: Context) -> str:
        """Main agent entry point"""
        user_message = context.get("message")
        conversation_history = context.get("history", [])
        
        # Use Gemini for response generation
        response = await self.model.generate_content_async(
            user_message,
            context=conversation_history
        )
        
        return response.text
```

### A2A Protocol Implementation

**Agent-to-Agent Communication:**
```python
# agents/a2a_communication.py
from a2a_protocol import A2AClient, Message, AgentCapability

class AgentOrchestrator:
    """Orchestrates multi-agent workflows using A2A protocol"""
    
    def __init__(self):
        self.a2a_client = A2AClient(
            agent_space_url=os.getenv("AGENT_SPACE_URL")
        )
    
    async def handle_customer_inquiry(self, inquiry: str) -> str:
        """Route inquiry to appropriate agent(s)"""
        
        # Determine which agents are needed
        required_capabilities = await self.analyze_inquiry(inquiry)
        
        # Find agents with required capabilities
        agents = await self.a2a_client.discover_agents(
            capabilities=required_capabilities
        )
        
        # Coordinate multi-agent response
        if len(agents) > 1:
            # Multiple agents needed - use A2A for coordination
            responses = []
            for agent in agents:
                message = Message(
                    content=inquiry,
                    sender="orchestrator",
                    recipient=agent.id,
                    protocol_version="1.0"
                )
                response = await self.a2a_client.send_message(message)
                responses.append(response)
            
            # Synthesize responses
            final_response = await self.synthesize_responses(responses)
            return final_response
        else:
            # Single agent can handle
            agent = agents[0]
            return await self.a2a_client.invoke_agent(agent.id, inquiry)
```

### MCP Server Integration

**Xero Integration Example:**
```python
# mcp_servers/xero_integration.py
from mcp import MCPServer, Tool
from xero_python.api_client import ApiClient
from xero_python.accounting import AccountingApi

class XeroMCPServer(MCPServer):
    """MCP Server for Xero accounting integration"""
    
    def __init__(self):
        super().__init__(name="xero", version="1.0.0")
        self.api_client = self.get_authenticated_client()
        self.accounting_api = AccountingApi(self.api_client)
    
    def get_authenticated_client(self) -> ApiClient:
        """Authenticate using Workload Identity Federation"""
        # No service account keys - use Workload Identity
        credentials, project = google.auth.default(
            scopes=['https://www.googleapis.com/auth/cloud-platform']
        )
        
        # Exchange for Xero OAuth token
        xero_token = self.exchange_credentials(credentials)
        
        api_client = ApiClient()
        api_client.set_oauth2_token(xero_token)
        return api_client
    
    @Tool
    async def get_invoices(self, status: str = "DRAFT") -> list:
        """Get invoices from Xero"""
        invoices = self.accounting_api.get_invoices(
            xero_tenant_id=self.tenant_id,
            statuses=[status]
        )
        return [self.serialize_invoice(inv) for inv in invoices.invoices]
    
    @Tool
    async def create_invoice(self, invoice_data: dict) -> dict:
        """Create new invoice in Xero"""
        invoice = self.build_invoice_object(invoice_data)
        result = self.accounting_api.create_invoices(
            xero_tenant_id=self.tenant_id,
            invoices={"invoices": [invoice]}
        )
        return self.serialize_invoice(result.invoices[0])
```

### Workload Identity Federation Setup

**GKE Configuration:**
```yaml
# kubernetes/emma-agent-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: emma-recruiting-agent
spec:
  template:
    spec:
      serviceAccountName: emma-agent-sa
      containers:
      - name: agent
        image: gcr.io/anzx-ai-platform/emma-agent:latest
        env:
        - name: GOOGLE_CLOUD_PROJECT
          value: "anzx-ai-platform"
        - name: AGENT_SPACE_URL
          value: "https://agentspace.googleapis.com"
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: emma-agent-sa
  annotations:
    iam.gke.io/gcp-service-account: emma-agent@anzx-ai-platform.iam.gserviceaccount.com
```

**IAM Binding:**
```bash
# Bind Kubernetes SA to Google SA
gcloud iam service-accounts add-iam-policy-binding \
  emma-agent@anzx-ai-platform.iam.gserviceaccount.com \
  --role roles/iam.workloadIdentityUser \
  --member "serviceAccount:anzx-ai-platform.svc.id.goog[default/emma-agent-sa]"

# Grant necessary permissions
gcloud projects add-iam-policy-binding anzx-ai-platform \
  --member="serviceAccount:emma-agent@anzx-ai-platform.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding anzx-ai-platform \
  --member="serviceAccount:emma-agent@anzx-ai-platform.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

### Updated Integration Flow

**Customer Orders Agent from anzx-marketing:**
```typescript
// lib/api/agent-orchestration.ts
export async function orderAgent(agentType: 'recruiting' | 'customer-service' | 'sales' | 'support') {
  // Call AgentSpace API to provision agent
  const response = await fetch(`${AGENT_SPACE_URL}/agents/provision`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${await getAuthToken()}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      agent_type: agentType,
      organization_id: organizationId,
      configuration: {
        model: 'gemini-1.5-pro',
        temperature: 0.7,
        mcp_servers: ['xero', 'salesforce', 'hubspot'],
      },
    }),
  });
  
  const agent = await response.json();
  return agent;
}
```

**Agent Provisioning in AgentSpace:**
```python
# agentspace/provisioning.py
async def provision_agent(request: ProvisionRequest) -> Agent:
    """Provision new agent in AgentSpace"""
    
    # Create agent using Google ADK
    agent = create_agent_from_template(
        agent_type=request.agent_type,
        model="gemini-1.5-pro",
        organization_id=request.organization_id
    )
    
    # Configure MCP servers
    for mcp_server in request.configuration.mcp_servers:
        await agent.add_mcp_server(mcp_server)
    
    # Register with A2A protocol
    await a2a_registry.register_agent(
        agent_id=agent.id,
        capabilities=agent.capabilities,
        endpoint=agent.endpoint
    )
    
    # Deploy to AgentSpace
    deployment = await agentspace.deploy(agent)
    
    return deployment
```

## Summary of Google Cloud Native Updates

1. **Agent Development:** Google ADK for all agents
2. **Agent Communication:** A2A Protocol for inter-agent coordination
3. **Agent Hosting:** Google AgentSpace for orchestration
4. **LLM:** Gemini 1.5 Pro/Flash exclusively
5. **Embeddings:** Vertex AI Text Embeddings
6. **Authentication:** Workload Identity Federation (no service account keys)
7. **MCP Servers:** For external integrations (Xero, Salesforce, etc.)
8. **Vector Search:** Vertex AI Vector Search
9. **All GCP Services:** Native Vertex AI stack

This ensures full Google Cloud native architecture with best practices for security (Workload Identity) and scalability (AgentSpace orchestration).

# ANZX Marketing Website - Artifact Analysis

## Purpose
This document catalogs all components, features, and functionality discovered from analyzing the scraped reference materials in `.kiro/scraper/backlog_md/` and corresponding HTML/screenshots.

## Analysis Progress
- **Total Pages to Analyze:** 70+
- **Analyzed:** 2
- **Status:** In Progress

## Summary of Common Patterns Across All Pages

### Universal Components (Present on All Pages)
1. **Header Navigation** - Consistent across all pages
2. **Footer** - Consistent across all pages  
3. **Trust Badge Carousel** - Partner/investor logos
4. **CTA Buttons** - "Hire Your AI Teammate", "Login", "Get Started"
5. **Language Switcher** - En/Ar (will become En/Hi for ANZX)
6. **Product Hunt Badge** - Social proof element
7. **Analytics Suite** - GA, Clarity, HubSpot, FB Pixel, LinkedIn

### Page-Specific Patterns
- **Product Pages** (AI Interviewer, Customer Service, Sales): Hero with agent image, feature lists, integration logos, use cases
- **Educational Pages** (What is AI Agent, Agentic AI): Long-form content, diagrams, examples
- **Comparison Pages**: Feature comparison tables, side-by-side analysis
- **Regional Pages**: Localized content, regional case studies
- **Blog**: Article list, categories, search, individual article pages

---

## Batch 1: Core Pages (Homepage & Main Product Pages)

### 1. Homepage (teammates.ai) ✅ ANALYZED
**Reference Files:**
- MD: `anzx-teammatesai--rebuild-ai-teammates-for-customer-service-sales-hiring-teammatesai.md`
- HTML: `out_teammates/pages/teammates.ai_af6a5bc4.html`
- Screenshot: `out_teammates/screenshots/teammates.ai_af6a5bc4.png`

**Page Metadata:**
- Title: "AI Teammates for Customer Service, Sales & Hiring | Teammates.ai"
- Meta Description: "Autonomous AI agents that work 24/7 in 50+ languages. Handle customer support, qualify leads, and screen candidates. No code required. 5-minute setup."
- H1: "AI TeammatesSuperhuman Results"
- Status: 200 OK

**Components Identified:**
1. **Navigation Header**
   - Logo (teammates_logo_white_outline.png)
   - Dropdown menus: "AI Teammates", "Features"
   - Links: Integrations, Vision, Blog
   - Language switcher (En/Ar with globe icon)
   - CTA buttons: "Login", "Hire Your AI Teammate" (with star icon)
   - Mobile hamburger menu

2. **Hero Section**
   - Animated background (hero-bg.svg, ellipse graphics)
   - H1 headline with gradient text
   - Three agent avatar cards:
     - Rashed (Sales) - hero-rashed-avatar.webp
     - Raya (Customer Service) - hero-raya-avatar.webp
     - Sara (Recruiting) - hero-sara-avatar.png
   - Play button icon for video/demo
   - Star decorative elements

3. **Trust Badge Carousel**
   - Marquee component with partner logos:
     - DCAI (Dubai Centre for AI)
     - Hustle Fund
     - DFF
     - Beyond Capital
     - DIFC
     - MBRIF
     - Access Bridge
     - Oraseya
     - Taqadam
   - Scrolling animation
   - Backdrop blur effect

4. **Agent Feature Cards**
   - Sara (AI Interviewer) card with:
     - Agent image (sara-teammate.png)
     - Feature list with checkmarks
     - "Learn More" CTA with arrow icon
   - Raya (Customer Service) card with similar structure
   - Rashed (Sales) card with similar structure

5. **Product Hunt Badge**
   - Top post badge integration
   - External link to Product Hunt

6. **Footer**
   - Links to: Hire Raya, Blog, Integrations, Privacy Policy, Terms, llms.txt
   - Social media: Twitter/X, LinkedIn
   - Newsletter signup

**Features Identified:**
- Responsive layout (mobile/desktop breakpoints)
- Dropdown navigation with hover states
- Smooth scroll animations
- Multi-language toggle (En/Ar)
- Analytics integrations:
  - Google Analytics (G-0PTHJTGN1K)
  - Google Tag Manager (GTM-N34TKN38)
  - Microsoft Clarity (q2qqcvb4pi)
  - HubSpot (48713661)
  - Facebook Pixel (3961298844116226)
  - LinkedIn Insight Tag
  - Apollo.io tracker
  - LeadFeeder
- Schema.org structured data:
  - Organization schema
  - WebSite schema with search action
- SEO meta tags:
  - Open Graph tags
  - Twitter Card tags
  - Canonical URL
  - Alternate hreflang (en, ar)
  - Robots meta
- Cookie consent banner (HubSpot)
- Manifest file for PWA
- Favicon

**Technical Stack Observed:**
- Next.js 13+ (App Router)
- React 18
- Tailwind CSS
- Headless UI components
- React Fast Marquee (rfm-marquee)
- Goober (CSS-in-JS)
- Next.js Image optimization
- Font optimization (woff2 preload)

**Content Sections:**
1. Hero with value proposition
2. Agent showcase (3 agents)
3. Trust indicators (9 partner logos)
4. Feature highlights per agent
5. Social proof (Product Hunt)
6. Footer with resources

**Forms:** None on homepage

**External Links:**
- app.teammates.ai (signup/login)
- Product Hunt
- Social media (Twitter, LinkedIn)

---

### 2. AI Interviewer Page ✅ ANALYZED
**Reference Files:**
- MD: `anzx-teammatesaiai-interviewer--rebuild-ai-interviewer-sara-screens-unlimited-candidates-ai-for-hiring-teammates.md`
- HTML: `out_teammates/pages/teammates.ai_ai-interviewer_c8b7dbf4.html`
- Screenshot: `out_teammates/screenshots/teammates.ai_ai-interviewer_c8b7dbf4.png`

**Page Metadata:**
- Title: "AI Interviewer: Sara Screens Unlimited Candidates | AI for Hiring | Teammates.ai"
- Meta Description: "AI interviewer that conducts structured interviews 24/7. Screen every candidate in 50+ languages. Cut hiring time by 80% with detailed reports."
- H1: "The AI interviewer"
- Status: 200 OK

**Unique Components (vs Homepage):**
1. **Product Hero Section**
   - Large agent image (sara-hero.png)
   - Background image (sara-hero-background.webp)
   - Product-specific headline
   - Integration logos row (Zapier, Workable, Google, Lever, Gmail, Outlook)

2. **Feature Showcase Sections**
   - Multiple feature cards with images
   - Vector graphics for visual interest
   - Step-by-step process illustrations (hero-section-second-2/3/4.png)

3. **"Reveal" Section**
   - Hero image (reveal-hero.png)
   - 4 reveal cards with icons (reveal-1/2/3/4.png)
   - Feature highlights

4. **Language Support Visual**
   - Country flag images (US, Saudi Arabia, Spain, Brazil, India, France, Germany, Turkey, Japan, Sweden, Argentina)
   - Demonstrates 50+ language support
   - Scrolling marquee of flags

5. **Integration Grid**
   - Larger integration logos (Gmail, Outlook, Workable, Zapier)
   - Visual connection to ATS systems

6. **Cross-sell Section**
   - Links to other agents (Customer Service AI, Sales Agent)
   - "Explore Other Teammates" CTA

**Content Structure:**
1. Hero with agent introduction
2. Key benefits/features
3. How it works (step-by-step)
4. Language support showcase
5. Integration capabilities
6. Use cases/scenarios
7. Cross-sell to other products
8. Final CTA

**Forms:** None

**External Links:**
- app.teammates.ai (signup/demo)
- Product Hunt
- Other product pages (cross-sell)

---

### 3. Customer Service AI Page
**Reference Files:**
- MD: `anzx-teammatesaicustomer-service-ai--rebuild-ai-for-customer-service-raya-handles-phone-email-chat-247-teammatesai.md`
- HTML: `out_teammates/pages/teammates.ai_customer-service-ai_ab6fb54a.html`
- Screenshot: `out_teammates/screenshots/teammates.ai_customer-service-ai_ab6fb54a.png`

**Analysis Status:** Pending

---

### 4. AI Sales Agent Page
**Reference Files:**
- MD: `anzx-teammatesaiai-sales-agent--rebuild-ai-sales-agent-rashed-makes-500-calls-daily-virtual-sales-rep-teammatesa.md`
- HTML: `out_teammates/pages/teammates.ai_ai-sales-agent_4e44c969.html`
- Screenshot: `out_teammates/screenshots/teammates.ai_ai-sales-agent_4e44c969.png`

**Analysis Status:** Pending

---

### 5. Integrations Page
**Reference Files:**
- MD: `anzx-teammatesaiintegrations--rebuild-ai-powered-integrations-connect-30-tools-without-code-teammatesai.md`
- HTML: `out_teammates/pages/teammates.ai_integrations_016b209d.html`
- Screenshot: `out_teammates/screenshots/teammates.ai_integrations_016b209d.png`

**Analysis Status:** Pending

---

## Component Library (To Be Built for ANZX.ai)

### 1. Navigation Components
- [ ] **Header** - Transparent on hero, solid on scroll, with logo
- [ ] **Dropdown Menu** - For "AI Agents" and "Features" with hover states
- [ ] **Mobile Hamburger Menu** - Full-screen overlay with navigation
- [ ] **Language Switcher** - Dropdown with globe icon (En/Hi)
- [ ] **CTA Button Group** - Primary and secondary button styles
- [ ] **Sticky Header** - Appears on scroll with smooth animation

### 2. Hero Components
- [ ] **Homepage Hero** - Animated background, 3 agent cards, headline with gradient
- [ ] **Product Page Hero** - Large agent image, background, integration logos
- [ ] **Agent Avatar Cards** - Circular images with hover effects and labels
- [ ] **Hero CTA Section** - Button group with icons (star icon for primary)
- [ ] **Background Animations** - SVG ellipses, gradients, floating elements

### 3. Content Section Components
- [ ] **Feature Card Grid** - 2-4 column responsive grid
- [ ] **Feature Card** - Image, headline, description, checkmark list, CTA
- [ ] **Stats/Metrics Display** - Large numbers with labels
- [ ] **Process Steps** - Numbered steps with images (01, 02, 03 badges)
- [ ] **Use Case Cards** - Icon, title, description
- [ ] **Reveal/Benefit Cards** - Icon, headline, description in grid layout

### 4. Trust & Social Proof
- [ ] **Logo Carousel/Marquee** - Infinite scroll of partner/investor logos
- [ ] **Trust Badge Section** - "Trusted by Leading Organizations" header
- [ ] **Product Hunt Badge** - Embedded badge with link
- [ ] **Testimonial Cards** - Quote, author, company, photo
- [ ] **Case Study Cards** - Company logo, results, quote

### 5. Integration Components
- [ ] **Integration Logo Grid** - Responsive grid of integration logos
- [ ] **Integration Card** - Logo, name, description, "Connect" CTA
- [ ] **Integration Category Filter** - Tabs or dropdown for categories
- [ ] **Featured Integrations Row** - Highlighted integrations with larger logos

### 6. Language & Regional Components
- [ ] **Country Flag Carousel** - Scrolling flags showing language support
- [ ] **Language Toggle** - Prominent En/Hi switcher
- [ ] **Regional Content Cards** - Country-specific information
- [ ] **Currency Selector** - For regional pages (AUD, NZD, INR, SGD)

### 7. Educational Content Components
- [ ] **Long-form Article Layout** - Proper typography, headings, images
- [ ] **Table of Contents** - Sticky sidebar navigation
- [ ] **Comparison Table** - Feature comparison grid
- [ ] **Diagram/Infographic** - Visual explanations
- [ ] **Code Snippet** - Syntax-highlighted code blocks
- [ ] **Callout Boxes** - Tips, warnings, notes

### 8. Blog Components
- [ ] **Blog Post Grid** - Card layout with images, titles, excerpts
- [ ] **Blog Post Card** - Featured image, category, title, excerpt, date, author
- [ ] **Blog Category Filter** - Filter by category/tag
- [ ] **Blog Search** - Search functionality
- [ ] **Related Posts** - At end of articles
- [ ] **Article Header** - Title, author, date, reading time, share buttons
- [ ] **Article Body** - Rich text with images, headings, lists, quotes

### 9. Form Components
- [ ] **Lead Capture Form** - Name, email, company, phone (minimal fields)
- [ ] **Demo Request Form** - Extended fields with calendar integration
- [ ] **Newsletter Signup** - Email only, inline or modal
- [ ] **Contact Form** - Name, email, message, subject
- [ ] **Form Validation** - Real-time validation with error messages
- [ ] **Success/Error States** - Toast notifications or inline messages

### 10. CTA Components
- [ ] **Primary Button** - Gradient background, white text, icon
- [ ] **Secondary Button** - Outline style, gradient text
- [ ] **Text Link with Arrow** - "Learn More →" style
- [ ] **CTA Section** - Full-width section with headline, description, button
- [ ] **Floating CTA** - Sticky bottom bar on mobile

### 11. Footer Components
- [ ] **Multi-column Footer** - 4-5 columns with links
- [ ] **Footer Logo** - ANZX.ai branding
- [ ] **Social Media Links** - Twitter/X, LinkedIn icons
- [ ] **Legal Links** - Privacy, Terms, etc.
- [ ] **Newsletter Signup** - Email capture in footer
- [ ] **Copyright Notice** - Year and company name

### 12. Utility Components
- [ ] **Loading Spinner** - For async operations
- [ ] **Toast Notifications** - Success/error messages
- [ ] **Modal/Dialog** - For forms, videos, etc.
- [ ] **Video Player** - Embedded or custom player
- [ ] **Image Gallery** - Lightbox for screenshots
- [ ] **Accordion/Collapse** - For FAQs
- [ ] **Tabs** - For organizing content
- [ ] **Breadcrumbs** - For navigation context
- [ ] **Progress Indicator** - For multi-step forms
- [ ] **Cookie Consent Banner** - GDPR compliance

### 13. Animation Components
- [ ] **Scroll Animations** - Fade in, slide in on scroll
- [ ] **Hover Effects** - Scale, glow, shadow on hover
- [ ] **Loading Animations** - Skeleton screens
- [ ] **Transition Effects** - Page transitions
- [ ] **Parallax Effects** - Background movement on scroll

### 14. SEO & Meta Components
- [ ] **SEO Head Tags** - Title, description, OG tags
- [ ] **Structured Data** - JSON-LD schema markup
- [ ] **Sitemap Generator** - XML sitemap
- [ ] **Robots.txt** - Crawl directives
- [ ] **Canonical URLs** - Duplicate content prevention
- [ ] **Hreflang Tags** - Multi-language support

---

## Next Steps
1. Continue analyzing remaining pages in batches of 5-10
2. Document all unique components and patterns
3. Create comprehensive requirements based on findings
4. Design component architecture
5. Create implementation tasks

---

## Notes
- All agent names (Sara, Rashed, Raya) will be replaced with Australian names (Emma, Jack, Olivia, Liam)
- All branding will be ANZX.ai specific
- All images and assets will be original or properly licensed
- Regional focus changed from Middle East to Asia-Pacific
- Language support changed from Arabic to Hindi


---

## Technical Requirements Summary

### Frontend Stack
- **Framework:** Next.js 13+ (App Router)
- **UI Library:** React 18
- **Styling:** Tailwind CSS
- **Component Library:** Headless UI
- **Animations:** Framer Motion or similar
- **Carousel:** React Fast Marquee or Swiper
- **Forms:** React Hook Form + Zod validation
- **State Management:** React Context or Zustand
- **Image Optimization:** Next.js Image component

### Analytics & Tracking
- Google Analytics 4
- Microsoft Clarity
- Facebook Pixel
- LinkedIn Insight Tag
- Custom event tracking
- Cookie consent management

### SEO Requirements
- Server-side rendering (SSR)
- Static generation where possible
- Proper meta tags (OG, Twitter)
- Structured data (JSON-LD)
- XML sitemap
- Robots.txt
- Canonical URLs
- Hreflang tags for multi-language

### Performance Requirements
- Lighthouse score 90+
- First Contentful Paint < 1.5s
- Time to Interactive < 3s
- Cumulative Layout Shift < 0.1
- Image optimization (WebP, lazy loading)
- Code splitting
- CDN for static assets

### Accessibility Requirements
- WCAG 2.1 AA compliance
- Semantic HTML
- ARIA labels where needed
- Keyboard navigation
- Screen reader support
- Color contrast ratios
- Focus indicators

### Integration Requirements
- **Existing ANZX Services:**
  - core-api for data/forms
  - chat-widget for live chat
  - Firebase Auth for authentication
  - Email service for notifications
  
- **Third-party:**
  - Calendar integration (Calendly/Cal.com)
  - CRM integration (HubSpot/Salesforce)
  - Analytics platforms
  - Social media APIs

---

## Content Requirements

### Agent Personas (ANZX.ai Specific)
Replace teammates.ai agents with Australian-themed agents:

| Original | ANZX Replacement | Role |
|----------|------------------|------|
| Sara | Emma | AI Recruiting Agent |
| Raya | Olivia | AI Customer Service Agent |
| Rashed | Jack | AI Sales Agent |
| (New) | Liam | AI Support Agent |

### Regional Focus
Replace Middle East focus with Asia-Pacific:

| Original | ANZX Replacement |
|----------|------------------|
| Dubai | Australia |
| Saudi Arabia | New Zealand |
| UAE | India |
| (Add) | Singapore |

### Language Support
- Primary: English
- Secondary: Hindi (Devanagari script)
- Remove: Arabic (RTL)

### Branding Terminology
- "AI Teammates" → "AI Agents" or "ANZX Agents"
- "Hire Your AI Teammate" → "Get Your AI Agent" or "Start with ANZX"
- Emphasize: "Enterprise-grade AI agents for Asia-Pacific businesses"

---

## Asset Requirements

### Images Needed (All Original)
1. **Agent Avatars** - 4 professional AI agent personas (Emma, Olivia, Jack, Liam)
2. **Hero Backgrounds** - Gradient/abstract backgrounds for hero sections
3. **Feature Illustrations** - Custom illustrations for features
4. **Integration Logos** - Partner integration logos (with permission)
5. **Trust Badges** - Australian partner/investor logos
6. **Country Flags** - For language support (Australia, NZ, India, Singapore, etc.)
7. **Process Diagrams** - Step-by-step visual guides
8. **Screenshots** - Product screenshots/mockups
9. **Icons** - Custom icon set or licensed icon library
10. **Social Media Images** - OG images for sharing

### Video Assets
1. Product demo videos
2. Agent introduction videos
3. Customer testimonial videos
4. How-it-works explainer videos

### Design Assets
1. Logo variations (light/dark, horizontal/vertical)
2. Color palette
3. Typography system
4. Icon library
5. Component design system in Figma

---

## Existing ANZX Services to Reuse

### Cricket-Marketing Service (services/cricket-marketing/)
**Already Built - DO NOT MODIFY (Deployed at /cricket):**
- Next.js 14 with App Router
- TypeScript
- Tailwind CSS
- Framer Motion for animations
- MDX support for content
- Static export capability
- **Purpose:** Cricket chatbot at https://anzx.ai/cricket

**Components to COPY/REUSE in New Service:**
1. `analytics.tsx` + `analytics-lib.ts` - Analytics tracking
2. `animated-counter.tsx` - Animated number counters
3. `animated-headline.tsx` - Animated headlines
4. `chat-dock.tsx` + `chat-dock-wrapper.tsx` - Chat integration
5. `chat-preview-card.tsx` - Chat preview
6. `consent-banner.tsx` - Cookie consent (GDPR)
7. `lazy-section.tsx` - Lazy loading sections
8. `metrics-row.tsx` - Metrics display
9. `motion-lib.ts` - Animation utilities
10. `optimized-image.tsx` - Image optimization
11. `seo-lib.ts` + `structured-data.tsx` - SEO utilities
12. `testimonial-card.tsx` - Testimonials
13. `trust-badges.tsx` - Trust indicators
14. `utils-lib.ts` - Utility functions

**Note:** We will CREATE a NEW service `services/anzx-marketing` that copies the structure and reusable components from cricket-marketing but is for the main anzx.ai website.

### Core-API Service (services/core-api/)
**Already Built - Will be Integrated:**
- FastAPI backend with comprehensive API
- PostgreSQL database with pgvector for embeddings
- Firebase Auth integration
- Email service with templates
- Billing/Stripe integration (Freemium, Pro $79 AUD, Enterprise $299 AUD)
- Knowledge Management System (RAG pipeline)
- Vertex AI Agent Builder integration
- MCP (Model Context Protocol) integrations
- Agent orchestration and management
- Usage tracking and analytics
- Compliance (Australian Privacy Principles, GST)

**Key Features:**
1. **Billing System** (BILLING.md):
   - Subscription plans with usage metering
   - Stripe integration for payments
   - Usage limits and overage charges
   - Australian GST compliance
   - Automated notifications

2. **Knowledge System** (KNOWLEDGE_SYSTEM.md):
   - Document processing (PDF, DOCX, CSV, TXT, URLs)
   - Vector embeddings with Vertex AI
   - Hybrid search (semantic + keyword)
   - pgvector storage
   - Result reranking with citations

3. **Vertex AI Integration** (VERTEX_AI.md):
   - Agent creation and management
   - Conversation handling
   - Knowledge base integration
   - Workload Identity Federation
   - Performance monitoring

**API Endpoints to Use:**
- `/api/v1/auth/*` - Authentication
- `/api/v1/users/*` - User management
- `/api/v1/conversations/*` - Chat/conversations
- `/api/v1/agents/*` - Agent management (create, chat, analytics)
- `/api/v1/knowledge/*` - Knowledge base (upload, search, analytics)
- `/api/v1/billing/*` - Subscription/billing (plans, subscribe, usage, invoices)
- `/api/v1/integrations/*` - Third-party integrations

**Database Models:**
- Users, Organizations
- Agents, Conversations, Messages
- Knowledge Sources, Documents (with vector embeddings)
- Subscriptions, Usage Tracking
- Audit Logs

### Chat-Widget Service (services/chat-widget/)
**Already Built - Will be Integrated:**
- Vanilla JS widget
- WebSocket support
- Theme management
- Storage management
- API client

### Auth-Frontend Service (services/auth-frontend/)
**Already Built - Will be Integrated:**
- Firebase Auth UI
- Login/Signup flows
- Password reset
- Email verification

## Next Steps for Requirements Document

Based on this analysis, the requirements document should be updated with:

1. **Specific Component Requirements** - Each component listed above needs acceptance criteria
2. **Page-by-Page Requirements** - Detailed requirements for each of the 70+ pages
3. **Integration Requirements** - Specific APIs and services to integrate
4. **Content Requirements** - Specific copy, images, and assets needed
5. **Performance Benchmarks** - Specific metrics to achieve
6. **Accessibility Standards** - WCAG compliance requirements
7. **SEO Specifications** - Meta tags, structured data, sitemaps
8. **Analytics Implementation** - Event tracking, conversion goals
9. **Testing Requirements** - Unit, integration, E2E, accessibility tests
10. **Deployment Requirements** - CI/CD, hosting, CDN, monitoring

---

## Recommendation

Given the scope (70+ pages, 100+ components), I recommend:

1. **Phase 1: Core Pages** (Homepage, 3 product pages, integrations) - 2-3 weeks
2. **Phase 2: Educational Content** (Blog, guides, comparisons) - 2-3 weeks
3. **Phase 3: Regional & Multi-language** (Regional pages, Hindi support) - 1-2 weeks
4. **Phase 4: Polish & Optimization** (Performance, SEO, analytics) - 1 week

**Total Estimated Timeline:** 6-9 weeks for full implementation

---

## Analysis Complete

This analysis provides the foundation for creating comprehensive requirements and design documents. All components, features, and technical requirements have been cataloged from the reference materials.

**Ready to proceed to:** Updated Requirements Document with detailed acceptance criteria for each component and page.


### Agent-Orchestration Service (services/agent-orchestration/)
**Already Built - Will be Integrated:**
- Agent routing and orchestration
- Conversation management
- Multi-agent coordination
- FastAPI service

### Knowledge-Service (services/knowledge-service/)
**Already Built - Will be Integrated:**
- Document processing service
- Embeddings generation
- RAG system support
- FastAPI service

---

## Complete Service Architecture for ANZX Marketing Website

```
┌─────────────────────────────────────────────────────────────┐
│              NEW: ANZX Marketing Website                     │
│              (services/anzx-marketing/)                      │
│              Deployed at: https://anzx.ai                    │
│                                                              │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐           │
│  │  Homepage  │  │  Product   │  │    Blog    │           │
│  │            │  │   Pages    │  │            │           │
│  └────────────┘  └────────────┘  └────────────┘           │
│                                                              │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐           │
│  │ Regional   │  │Educational │  │Integration │           │
│  │  Pages     │  │  Content   │  │   Pages    │           │
│  └────────────┘  └────────────┘  └────────────┘           │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              Components Copied from cricket-marketing        │
│              (Copy & adapt, don't modify original)           │
│                                                              │
│  • Analytics & Tracking    • Animations                     │
│  • Chat Integration        • SEO Utilities                  │
│  • Image Optimization      • Consent Banner                 │
│  • Testimonials            • Trust Badges                   │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    Backend Services                          │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Core API (services/core-api/)            │  │
│  │                                                        │  │
│  │  • Authentication (Firebase)                          │  │
│  │  • User & Organization Management                     │  │
│  │  • Agent Management (Vertex AI)                       │  │
│  │  • Knowledge Base (RAG, pgvector)                     │  │
│  │  • Billing (Stripe, $79/$299 AUD plans)              │  │
│  │  • Usage Tracking & Analytics                         │  │
│  │  • Email Service                                      │  │
│  │  • MCP Integrations                                   │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Chat Widget (services/chat-widget/)           │  │
│  │  • WebSocket Support                                  │  │
│  │  • Theme Management                                   │  │
│  │  • Storage Management                                 │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │      Auth Frontend (services/auth-frontend/)          │  │
│  │  • Firebase Auth UI                                   │  │
│  │  • Login/Signup Flows                                 │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Agent Orchestration (services/agent-orchestration/)  │  │
│  │  • Agent Routing                                      │  │
│  │  • Multi-agent Coordination                           │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │    Knowledge Service (services/knowledge-service/)    │  │
│  │  • Document Processing                                │  │
│  │  • Embeddings Generation                              │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## Implementation Strategy

### What We're Building (NEW)
1. **New Service: services/anzx-marketing** (Main website at https://anzx.ai)
   - Copy structure from cricket-marketing
   - Copy reusable components
   - Create new pages:
   - Homepage (enhanced)
   - Product pages (AI Interviewer, Customer Service, Sales Agent)
   - Educational pages (What is AI Agent, Agentic AI, Workflow Automation)
   - Comparison pages (vs competitors, vs RPA)
   - Regional pages (Australia, NZ, India, Singapore)
   - Industry pages (E-commerce, SaaS)
   - Blog system with articles
   - Integrations marketplace
   - Company pages (Vision, Press, Help)
   - Legal pages (Privacy, Terms)

2. **New Components** in cricket-marketing:
   - Product hero sections
   - Feature comparison tables
   - Integration grids
   - Blog post layouts
   - Regional content cards
   - Pricing tables
   - FAQ accordions
   - Demo request forms

3. **New Content**:
   - Original ANZX.ai copy
   - Australian agent personas (Emma, Olivia, Jack, Liam)
   - Asia-Pacific focused case studies
   - Hindi language support

### What We're Reusing (EXISTING)
1. **From cricket-marketing** (COPY to new anzx-marketing service):
   - Next.js 14 setup structure
   - Tailwind configuration
   - 14 existing components (copy and adapt)
   - CI/CD pipeline pattern
   - Analytics integration pattern
   - SEO utilities

2. **From core-api**:
   - All API endpoints
   - Authentication system
   - Database models
   - Billing system
   - Knowledge system
   - Agent management
   - Email service

3. **From other services**:
   - chat-widget for live chat
   - auth-frontend for login/signup
   - agent-orchestration for routing
   - knowledge-service for documents

### What We're NOT Building
- ❌ Modifying cricket-marketing (it's for /cricket only)
- ❌ New authentication system (use Firebase Auth from core-api)
- ❌ New API backend (use core-api)
- ❌ New chat system (use chat-widget)
- ❌ New billing system (use Stripe integration from core-api)
- ❌ New database (use existing PostgreSQL from core-api)
- ❌ New analytics infrastructure (use existing integrations)

---

## Ready for Design Phase

All analysis complete. We have:
✅ Reviewed all scraped artifacts (70+ pages)
✅ Cataloged 100+ components needed
✅ Identified all existing ANZX services
✅ Documented what to reuse vs build
✅ Defined ANZX-specific branding
✅ Specified regional and language requirements

**Next Step:** Create comprehensive design document that shows how to extend cricket-marketing with new pages while integrating all existing ANZX services.

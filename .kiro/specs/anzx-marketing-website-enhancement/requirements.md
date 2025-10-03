# Requirements Document

## Introduction

This specification outlines the requirements for enhancing the ANZX.ai platform by integrating a comprehensive marketing website with 70+ pages including product pages, blog content, educational resources, and multi-language support (English and Hindi). The features are inspired by competitive analysis from scraped reference materials (teammates.ai) but will be implemented with ANZX.ai branding, original content, and custom imagery to avoid any copyright issues. 

The implementation will leverage existing ANZX platform services and patterns (core-api, chat-widget, authentication, etc.) rather than building everything from scratch. All scraped HTML, screenshots, and HAR files will serve as reference for layout and functionality, but all content, images, and branding will be original ANZX.ai assets.

**Reference Materials Location:** `.kiro/scraper/backlog_md/` contains 70+ markdown specifications with links to HTML, screenshots, and HAR files for reference.

## Requirements

### Requirement 1: Marketing Website Foundation

**User Story:** As a potential customer, I want to visit anzx.ai and understand the platform's value proposition, so that I can decide if it meets my business needs.

#### Acceptance Criteria

1. WHEN a visitor lands on anzx.ai THEN the system SHALL display a responsive homepage with hero section, feature highlights, and clear call-to-action buttons
2. WHEN a visitor views the homepage THEN the system SHALL load within 3 seconds and achieve a Lighthouse performance score of 90+
3. WHEN a visitor navigates the site THEN the system SHALL provide consistent header and footer navigation across all pages
4. IF a visitor is on mobile THEN the system SHALL display a mobile-optimized layout with hamburger menu
5. WHEN a visitor clicks primary CTA buttons THEN the system SHALL direct them to appropriate signup/demo request flows

### Requirement 2: Product Feature Pages

**User Story:** As a business decision-maker, I want to explore specific AI agent capabilities (customer service, sales, hiring), so that I can understand how ANZX.ai solves my specific use case.

#### Acceptance Criteria

1. WHEN a visitor navigates to /customer-service-ai THEN the system SHALL display features, benefits, and use cases for AI customer service agents
2. WHEN a visitor navigates to /ai-sales-agent THEN the system SHALL display features for AI-powered sales automation with call capabilities
3. WHEN a visitor navigates to /ai-interviewer THEN the system SHALL display features for AI-powered candidate screening and hiring
4. WHEN a visitor views any product page THEN the system SHALL include demo videos or interactive elements showcasing the feature
5. WHEN a visitor scrolls through product pages THEN the system SHALL display social proof elements (testimonials, metrics, trust badges)
6. IF a visitor clicks "Get Started" on any product page THEN the system SHALL capture lead information and route to appropriate onboarding

### Requirement 3: Industry-Specific Landing Pages

**User Story:** As a business owner in a specific industry (e-commerce, SaaS), I want to see how ANZX.ai applies to my industry, so that I can understand relevant use cases.

#### Acceptance Criteria

1. WHEN a visitor navigates to /industries/ecommerce THEN the system SHALL display e-commerce-specific AI agent use cases and benefits
2. WHEN a visitor navigates to /industries/saas THEN the system SHALL display SaaS-specific AI agent use cases and benefits
3. WHEN a visitor views industry pages THEN the system SHALL include industry-specific metrics, case studies, and ROI calculators
4. WHEN a visitor is on an industry page THEN the system SHALL provide industry-specific CTAs and demo scenarios

### Requirement 4: Educational Content & Blog

**User Story:** As a professional researching AI agents, I want to read educational content about AI agents, automation, and best practices, so that I can make informed decisions.

#### Acceptance Criteria

1. WHEN a visitor navigates to /blog THEN the system SHALL display a paginated list of blog articles with categories and search
2. WHEN a visitor clicks on a blog article THEN the system SHALL display the full article with proper formatting, images, and related content suggestions
3. WHEN the system displays blog content THEN it SHALL include articles covering: AI agents fundamentals, customer service AI, workflow automation, AI vs RPA comparisons, and implementation guides
4. WHEN a visitor reads a blog article THEN the system SHALL track engagement metrics (time on page, scroll depth)
5. WHEN a visitor finishes an article THEN the system SHALL display related articles and conversion CTAs

### Requirement 5: Integrations Marketplace

**User Story:** As a potential customer, I want to see what tools and platforms ANZX.ai integrates with, so that I can ensure compatibility with my existing tech stack.

#### Acceptance Criteria

1. WHEN a visitor navigates to /integrations THEN the system SHALL display a grid of available integrations with logos and descriptions
2. WHEN a visitor filters integrations THEN the system SHALL allow filtering by category (CRM, Support, Communication, etc.)
3. WHEN a visitor clicks on an integration THEN the system SHALL display integration details, setup instructions, and use cases
4. WHEN the system displays integrations THEN it SHALL show at least 30+ integration options organized by category
5. WHEN a visitor views integrations THEN the system SHALL highlight native integrations vs API-based connections

### Requirement 6: Multi-Language Support (Hindi)

**User Story:** As a Hindi-speaking business owner in India, I want to view the ANZX.ai website in Hindi, so that I can understand the platform in my native language.

#### Acceptance Criteria

1. WHEN a visitor selects Hindi language THEN the system SHALL display all content in Hindi with proper Devanagari script rendering
2. WHEN the system detects a visitor from India THEN it SHALL suggest Hindi language option
3. WHEN a visitor views Hindi pages THEN the system SHALL maintain all functionality including forms, navigation, and CTAs
4. WHEN a visitor switches languages THEN the system SHALL preserve their current page context and navigation state
5. IF content is not available in Hindi THEN the system SHALL display English content with a language notice

### Requirement 7: Regional Landing Pages (Australia, New Zealand, India, Singapore)

**User Story:** As a business owner in the Asia-Pacific region, I want to see region-specific information about ANZX.ai, so that I understand local support, compliance, and use cases.

#### Acceptance Criteria

1. WHEN a visitor navigates to /ai-agents-australia THEN the system SHALL display Australia-specific content, case studies, and local contact information
2. WHEN a visitor navigates to /ai-agents-new-zealand THEN the system SHALL display New Zealand-specific content and compliance information
3. WHEN a visitor navigates to /ai-agents-india THEN the system SHALL display India-specific content and business use cases with Hindi language toggle
4. WHEN a visitor navigates to /ai-agents-singapore THEN the system SHALL display Singapore-specific content and regional business use cases
5. WHEN a visitor views regional pages THEN the system SHALL include local phone numbers, business hours, and currency options (AUD, NZD, INR, SGD)

### Requirement 8: Comparison & Educational Pages

**User Story:** As a buyer researching AI solutions, I want to compare ANZX.ai with alternatives and understand AI concepts, so that I can make an informed purchase decision.

#### Acceptance Criteria

1. WHEN a visitor navigates to comparison pages (e.g., /ai-agents-vs-rpa) THEN the system SHALL display objective comparisons with feature matrices
2. WHEN a visitor views /what-is-an-ai-agent THEN the system SHALL provide comprehensive educational content about AI agents
3. WHEN a visitor views /agentic-ai THEN the system SHALL explain agentic AI concepts with examples and use cases
4. WHEN a visitor views /workflow-automation THEN the system SHALL explain automation capabilities with visual diagrams
5. WHEN a visitor reads educational content THEN the system SHALL include conversion CTAs without being overly promotional

### Requirement 9: Legal & Trust Pages

**User Story:** As a compliance officer evaluating ANZX.ai, I want to review privacy policies, terms of service, and security information, so that I can ensure regulatory compliance.

#### Acceptance Criteria

1. WHEN a visitor navigates to /legal/privacy-policy THEN the system SHALL display comprehensive privacy policy with GDPR and data protection information
2. WHEN a visitor navigates to /legal/terms THEN the system SHALL display terms of service with clear usage rights and limitations
3. WHEN a visitor views legal pages THEN the system SHALL include last updated dates and version history
4. WHEN a visitor is on legal pages THEN the system SHALL provide downloadable PDF versions
5. WHEN the system collects user data THEN it SHALL comply with all stated privacy policies

### Requirement 10: Help Center & Documentation

**User Story:** As a current or potential customer, I want to access help documentation and FAQs, so that I can find answers to my questions quickly.

#### Acceptance Criteria

1. WHEN a visitor navigates to /help THEN the system SHALL display a searchable help center with categories
2. WHEN a visitor searches help content THEN the system SHALL return relevant articles ranked by relevance
3. WHEN a visitor views help articles THEN the system SHALL include step-by-step guides with screenshots
4. WHEN a visitor cannot find an answer THEN the system SHALL provide options to contact support or start a chat
5. WHEN the system displays help content THEN it SHALL track which articles are most viewed and helpful

### Requirement 11: Press & Media Center

**User Story:** As a journalist or investor, I want to access ANZX.ai press releases and media assets, so that I can write about or promote the company.

#### Acceptance Criteria

1. WHEN a visitor navigates to /press THEN the system SHALL display recent press releases in reverse chronological order
2. WHEN a visitor views the press page THEN the system SHALL provide downloadable media kit with logos, screenshots, and brand guidelines
3. WHEN a visitor clicks on a press release THEN the system SHALL display the full release with sharing options
4. WHEN the system displays press content THEN it SHALL include contact information for media inquiries
5. WHEN a visitor downloads media assets THEN the system SHALL track downloads for analytics

### Requirement 12: Vision & Company Pages

**User Story:** As a potential partner or employee, I want to understand ANZX.ai's vision and mission, so that I can align with the company's values.

#### Acceptance Criteria

1. WHEN a visitor navigates to /vision THEN the system SHALL display company vision, mission, and future roadmap
2. WHEN a visitor views the vision page THEN the system SHALL include founder story and company values
3. WHEN a visitor is on the vision page THEN the system SHALL provide career opportunities link and partnership inquiries
4. WHEN the system displays vision content THEN it SHALL include visual timeline or roadmap graphics
5. WHEN a visitor engages with vision content THEN the system SHALL provide newsletter signup for company updates

### Requirement 13: Conversion & Lead Capture

**User Story:** As a marketing manager, I want to capture qualified leads from the website, so that the sales team can follow up with potential customers.

#### Acceptance Criteria

1. WHEN a visitor clicks "Get Started" or "Book Demo" THEN the system SHALL display a lead capture form with minimal required fields
2. WHEN a visitor submits a lead form THEN the system SHALL validate inputs and store data in the CRM
3. WHEN a lead is captured THEN the system SHALL trigger automated email sequences and sales notifications
4. WHEN a visitor abandons a form THEN the system SHALL save partial data and enable retargeting
5. WHEN the system captures leads THEN it SHALL segment them by source, industry, and intent for proper routing

### Requirement 14: Analytics & Performance Tracking

**User Story:** As a product manager, I want to track user behavior and page performance, so that I can optimize conversion rates and user experience.

#### Acceptance Criteria

1. WHEN a visitor interacts with the website THEN the system SHALL track page views, clicks, and conversion events
2. WHEN a visitor completes a conversion action THEN the system SHALL attribute it to the correct source and campaign
3. WHEN the system tracks analytics THEN it SHALL respect user privacy preferences and cookie consent
4. WHEN an admin views analytics THEN the system SHALL provide dashboards showing traffic, conversions, and funnel metrics
5. WHEN the system detects performance issues THEN it SHALL alert the technical team and log errors

### Requirement 15: SEO & Content Optimization

**User Story:** As a content marketer, I want the website to rank well in search engines, so that we can attract organic traffic.

#### Acceptance Criteria

1. WHEN a search engine crawls the site THEN the system SHALL provide proper meta tags, structured data, and sitemaps
2. WHEN a page loads THEN the system SHALL implement proper heading hierarchy (H1, H2, H3) and semantic HTML
3. WHEN the system generates pages THEN it SHALL include Open Graph tags for social media sharing
4. WHEN a visitor shares a page THEN the system SHALL display proper preview images and descriptions
5. WHEN the system serves content THEN it SHALL implement canonical URLs to avoid duplicate content issues

### Requirement 16: Original Assets & Branding

**User Story:** As a legal/compliance officer, I want all website assets to be original or properly licensed, so that we avoid copyright infringement.

#### Acceptance Criteria

1. WHEN the system displays images THEN it SHALL use only original ANZX.ai branded images or properly licensed stock photos
2. WHEN the system uses icons or illustrations THEN it SHALL use custom-designed assets or open-source libraries
3. WHEN the system displays logos THEN it SHALL use only ANZX.ai branding and partner logos with permission
4. WHEN content is created THEN it SHALL be original writing or properly attributed quotes/references
5. WHEN the system is audited THEN it SHALL have documentation of all asset sources and licenses

### Requirement 17: Integration with Existing ANZX Services & Creation of New Marketing Service

**User Story:** As a developer, I want the marketing website to be a new service that reuses patterns from cricket-marketing and integrates with ANZX platform services, so that we maintain consistency, reuse code, and avoid duplication.

#### Acceptance Criteria

1. WHEN implementing the marketing website THEN the system SHALL create a NEW service `services/anzx-marketing` (cricket-marketing is for /cricket only and must not be modified)
2. WHEN building components THEN the system SHALL copy and adapt reusable components from `services/cricket-marketing/components/` to the new `services/anzx-marketing/components/`:
   - analytics.tsx, analytics-lib.ts (for tracking)
   - animated-counter.tsx, animated-headline.tsx (for animations)
   - chat-dock.tsx, chat-preview-card.tsx (for chat integration)
   - consent-banner.tsx (for GDPR compliance)
   - lazy-section.tsx (for performance)
   - metrics-row.tsx (for stats display)
   - motion-lib.ts (for animations)
   - optimized-image.tsx (for image optimization)
   - seo-lib.ts, structured-data.tsx (for SEO)
   - testimonial-card.tsx, trust-badges.tsx (for social proof)
   - utils-lib.ts (for utilities)
3. WHEN a visitor signs up THEN the system SHALL use existing authentication services (Firebase Auth via auth-frontend)
4. WHEN a visitor starts a chat THEN the system SHALL use the existing chat-widget service
5. WHEN a visitor submits a form THEN the system SHALL store data using existing core-api endpoints
6. WHEN the system sends emails THEN it SHALL use existing email service infrastructure from core-api
7. WHEN the system tracks analytics THEN it SHALL use the existing analytics components and integrate with observability services
8. WHEN deploying THEN the system SHALL use the existing CI/CD pipeline (cloudbuild.yaml) with modifications for new pages
9. WHEN styling components THEN the system SHALL extend the existing Tailwind configuration and global CSS
10. WHEN creating new components THEN the system SHALL follow the existing component patterns and file structure

### Requirement 18: Complete Page Inventory

**User Story:** As a content manager, I want a complete inventory of all pages that need to be created, so that I can track progress and ensure nothing is missed.

#### Acceptance Criteria

1. WHEN the system is complete THEN it SHALL include the following English pages:
   - Homepage (/)
   - Product Pages: /ai-interviewer, /customer-service-ai, /ai-sales-agent, /ai-employees, /ai-agent
   - Educational: /what-is-an-ai-agent, /agentic-ai, /workflow-automation
   - Comparisons: /11x-ai-vs-anzx-ai, /ai-agents-vs-automation, /ai-agents-vs-rpa, /ai-vs-rpa
   - Regional: /ai-agents-australia, /ai-agents-new-zealand, /ai-agents-india, /ai-agents-singapore
   - Features: /multilingual-chatbot, /integrations, /ai-agent-companies
   - Industries: /industries/ecommerce, /industries/saas
   - Company: /vision, /press, /help, /get-started
   - Legal: /legal/privacy-policy, /legal/terms
   - Blog: /blog (index), plus 10+ blog articles covering AI agents, customer service, recruitment, MCP, automation

2. WHEN the system is complete THEN it SHALL include Hindi versions of key pages at /hi/* paths (homepage, product pages, regional India page)

3. WHEN the system creates pages THEN each page SHALL reference the corresponding HTML/screenshot artifacts in `.kiro/scraper/out_teammates/` for layout inspiration

4. WHEN the system creates pages THEN it SHALL use original ANZX.ai content, not copied text from reference materials

5. WHEN the system tracks progress THEN it SHALL maintain a checklist mapping each markdown spec to its implementation status

### Requirement 19: Content Creation & Asset Generation

**User Story:** As a content creator, I want guidelines for creating original content and assets, so that we avoid copyright issues while maintaining quality.

#### Acceptance Criteria

1. WHEN creating page content THEN the system SHALL use reference screenshots for layout inspiration only, not content copying
2. WHEN creating images THEN the system SHALL use one of: custom ANZX.ai designs, properly licensed stock photos, or open-source illustrations
3. WHEN creating agent personas THEN the system SHALL create original ANZX.ai agent names and personalities (not "Sara", "Rashed", "Raya")
4. WHEN writing copy THEN the system SHALL create original value propositions highlighting ANZX.ai's unique features
5. WHEN creating blog content THEN the system SHALL write original articles on similar topics with ANZX.ai perspective and examples

### Requirement 21: ANZX.ai Branding & Terminology

**User Story:** As a brand manager, I want consistent ANZX.ai branding and terminology throughout the website, so that we establish a unique identity distinct from competitors.

#### Acceptance Criteria

1. WHEN referring to AI agents THEN the system SHALL use "AI Agents" or "ANZX Agents" terminology (NOT "AI Teammates")
2. WHEN creating agent personas THEN the system SHALL use Australian/New Zealand names such as: "Olivia" (customer service), "Jack" (sales), "Emma" (recruiting), "Liam" (support)
3. WHEN displaying agent personas THEN the system SHALL use original ANZX.ai character designs and avatars (no copied images)
4. WHEN writing value propositions THEN the system SHALL emphasize "AI Agents as your workforce" or "AI-powered business automation" (avoiding "teammates" terminology)
5. WHEN creating marketing copy THEN the system SHALL highlight ANZX.ai's unique positioning: enterprise-grade AI agents for Asia-Pacific businesses
6. WHEN naming features THEN the system SHALL use ANZX.ai-specific terminology that differentiates from competitors
7. WHEN displaying company information THEN the system SHALL emphasize Australian headquarters and Asia-Pacific focus

### Requirement 20: Performance & Scalability

**User Story:** As a site reliability engineer, I want the marketing website to handle high traffic loads, so that we don't lose potential customers during campaigns.

#### Acceptance Criteria

1. WHEN traffic spikes occur THEN the system SHALL handle at least 10,000 concurrent visitors without degradation
2. WHEN pages load THEN the system SHALL achieve First Contentful Paint (FCP) under 1.5 seconds
3. WHEN the system serves assets THEN it SHALL use CDN for static content and implement proper caching
4. WHEN the system scales THEN it SHALL use containerized deployment with auto-scaling capabilities
5. WHEN the system experiences errors THEN it SHALL implement graceful degradation and error boundaries

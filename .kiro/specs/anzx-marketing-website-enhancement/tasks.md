# Implementation Plan

This implementation plan breaks down the ANZX Marketing Website Enhancement into discrete, manageable tasks. Each task builds incrementally on previous work and references specific requirements from the requirements document.

## Task Execution Guidelines

- Execute tasks in order (dependencies are indicated)
- Mark tasks as complete using the checkbox syntax
- Each task should be testable and deployable independently where possible
- Reference requirements using format: _Requirements: X.Y_

---

## Phase 1: Project Setup & Foundation

- [x] 1. Create anzx-marketing service structure
  - Create `services/anzx-marketing/` directory
  - Copy Next.js 14 configuration from cricket-marketing
  - Set up TypeScript, Tailwind CSS, and ESLint
  - Configure package.json with dependencies
  - _Requirements: 17.1, 18.1_

- [x] 2. Set up development environment
  - Configure environment variables (.env.local, .env.production)
  - Set up Google Cloud project configuration
  - Configure Workload Identity Federation for local development
  - Set up Firebase Auth configuration
  - _Requirements: 17.3, 17.6_

- [x] 3. Copy reusable components from cricket-marketing
  - Copy analytics components (analytics.tsx, analytics-lib.ts)
  - Copy animation components (animated-counter.tsx, animated-headline.tsx, motion-lib.ts)
  - Copy SEO components (seo-lib.ts, structured-data.tsx)
  - Copy utility components (optimized-image.tsx, lazy-section.tsx, utils-lib.ts)
  - Copy chat components (chat-dock.tsx, chat-preview-card.tsx)
  - Copy social proof components (testimonial-card.tsx, trust-badges.tsx)
  - Copy consent banner component
  - Adapt components for ANZX branding
  - _Requirements: 17.2_

- [x] 4. Set up core-api client library
  - Create `lib/api/core-api-client.ts` with authentication
  - Implement agents API client (`lib/api/agents.ts`)
  - Implement billing API client (`lib/api/billing.ts`)
  - Implement knowledge API client (`lib/api/knowledge.ts`)
  - Add error handling and retry logic
  - _Requirements: 17.4, 17.5_

- [x] 5. Configure multi-language support (English + Hindi)
  - Install and configure next-intl
  - Create translation files (messages/en.json, messages/hi.json)
  - Set up language switcher component
  - Configure routing for /hi/* paths
  - Test Hindi (Devanagari) script rendering
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

---

## Phase 2: Core Layout & Navigation

- [x] 6. Create base layout components
  - Implement Header component with logo and navigation
  - Implement Footer component with links and newsletter signup
  - Implement Navigation component with dropdowns
  - Implement MobileMenu component
  - Add scroll-based header transparency/solid background
  - _Requirements: 1.3, 1.4_

- [x] 7. Implement language switcher
  - Create LanguageSwitcher component with globe icon
  - Add En/Hi toggle functionality
  - Preserve page context when switching languages
  - Style for both desktop and mobile
  - _Requirements: 6.1, 6.4_

- [x] 8. Create CTA button components
  - Implement PrimaryButton with gradient background
  - Implement SecondaryButton with outline style
  - Add icon support (star icon for primary)
  - Add hover and active states
  - _Requirements: 1.5_

- [x] 9. Set up routing structure
  - Configure app router for all page groups
  - Set up (marketing) route group
  - Set up (regional) route group
  - Set up (legal) route group
  - Set up /hi language routes
  - _Requirements: 18.1_

---

## Phase 3: Homepage Implementation

- [x] 10. Create homepage hero section
  - Implement HomeHero component with animated background
  - Create agent avatar cards (Emma, Olivia, Jack placeholders)
  - Add gradient text for headline
  - Implement primary and secondary CTAs
  - Add responsive layout (mobile/desktop)
  - _Requirements: 1.1, 1.2, 21.2, 21.3_

- [x] 11. Create agent persona data
  - Define Agent data model in `lib/constants/agents.ts`
  - Create Emma (Recruiting Agent) persona
  - Create Olivia (Customer Service Agent) persona
  - Create Jack (Sales Agent) persona
  - Create Liam (Support Agent) persona
  - _Requirements: 21.1, 21.2_

- [x] 12. Implement trust badge carousel
  - Create LogoCarousel component with marquee animation
  - Add Australian partner/investor logos (placeholders)
  - Implement infinite scroll animation
  - Add backdrop blur effect
  - _Requirements: 1.1, 16.2_

- [x] 13. Create feature highlights section
  - Implement FeatureGrid component
  - Create FeatureCard component with icons
  - Add hover animations
  - Implement lazy loading
  - _Requirements: 1.1_

- [x] 14. Add homepage SEO and meta tags
  - Implement SEO metadata for homepage
  - Add Open Graph tags
  - Add Twitter Card tags
  - Add structured data (Organization schema)
  - Add canonical URL and hreflang tags
  - _Requirements: 15.1, 15.2, 15.3, 15.4, 15.5_

---

## Phase 4: Product Pages

- [x] 15. Create product page layout template
  - Implement ProductHero component
  - Create feature showcase sections
  - Add integration logos display
  - Implement cross-sell section
  - _Requirements: 2.1, 2.2, 2.3_

- [x] 16. Build AI Interviewer (Emma) page
  - Create `/ai-interviewer/page.tsx`
  - Implement product hero with Emma avatar
  - Add feature list with checkmarks
  - Add integration logos (ATS systems)
  - Implement demo request CTA
  - _Requirements: 2.1, 2.4, 21.2_

- [x] 17. Build Customer Service AI (Olivia) page
  - Create `/customer-service-ai/page.tsx`
  - Implement product hero with Olivia avatar
  - Add 24/7 support features
  - Add multi-channel capabilities (phone, email, chat)
  - Implement demo request CTA
  - _Requirements: 2.2, 2.4, 21.2_

- [x] 18. Build AI Sales Agent (Jack) page
  - Create `/ai-sales-agent/page.tsx`
  - Implement product hero with Jack avatar
  - Add call automation features
  - Add lead qualification capabilities
  - Implement demo request CTA
  - _Requirements: 2.3, 2.4, 21.2_

- [x] 19. Create demo request form component
  - Implement DemoRequestForm with React Hook Form + Zod
  - Add form validation
  - Integrate with core-api for lead capture
  - Add success/error states
  - Implement email notification
  - _Requirements: 2.6, 13.1, 13.2, 13.3_

- [x] 20. Add product page SEO
  - Add meta tags for each product page
  - Implement Product schema structured data
  - Add breadcrumbs
  - Optimize images for product pages
  - _Requirements: 15.1, 15.2_

---

## Phase 5: Integrations Marketplace

- [x] 21. Create integrations data model
  - Define Integration model in `lib/constants/integrations.ts`
  - Add integration categories (CRM, Support, Communication, etc.)
  - Create integration data for 30+ tools
  - _Requirements: 5.1, 5.4_

- [x] 22. Build integrations page
  - Create `/integrations/page.tsx`
  - Implement IntegrationGrid component
  - Create IntegrationCard component
  - Add category filter
  - Implement search functionality
  - _Requirements: 5.1, 5.2, 5.3_

- [x] 23. Create individual integration pages
  - Create dynamic route `/integrations/[slug]/page.tsx`
  - Display integration details
  - Add setup instructions
  - Link to documentation
  - Add "Connect" CTA
  - _Requirements: 5.3_

- [x] 24. Implement MCP server integration UI
  - Add MCP server badges for integrations
  - Display Xero MCP server integration
  - Add setup guides for MCP servers
  - Link to MCP server documentation
  - _Requirements: 5.5_

---

## Phase 6: Blog System

- [x] 25. Set up MDX for blog content
  - Configure @next/mdx
  - Set up remark and rehype plugins
  - Create blog post template
  - Add syntax highlighting for code blocks
  - _Requirements: 4.2_

- [ ] 26. Create blog listing page
  - Create `/blog/page.tsx`
  - Implement BlogList component
  - Create BlogCard component
  - Add pagination
  - Implement category filter
  - Add search functionality
  - _Requirements: 4.1, 4.4_

- [ ] 27. Create blog post layout
  - Create `/blog/[slug]/page.tsx`
  - Implement ArticleLayout component
  - Add table of contents
  - Add reading time estimate
  - Add author and date display
  - Add social sharing buttons
  - _Requirements: 4.2, 4.5_

- [ ] 28. Write initial blog content
  - Create 10+ blog posts in MDX format
  - Topics: AI agents, customer service AI, workflow automation, AI vs RPA
  - Ensure original ANZX.ai perspective
  - Add proper meta tags and OG images
  - _Requirements: 4.3, 19.5_

- [ ] 29. Implement related posts feature
  - Add related posts algorithm
  - Display related posts at end of articles
  - Add conversion CTAs in articles
  - _Requirements: 4.5_

---

## Phase 7: Regional Pages

- [ ] 30. Create regional page template
  - Implement RegionalHero component
  - Add country-specific content sections
  - Create CurrencyDisplay component
  - Add local contact information display
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [ ] 31. Build Australia regional page
  - Create `/ai-agents-australia/page.tsx`
  - Add Australia-specific case studies
  - Display AUD currency
  - Add Australian business hours
  - Add local phone number
  - _Requirements: 7.1, 7.4_

- [ ] 32. Build New Zealand regional page
  - Create `/ai-agents-new-zealand/page.tsx`
  - Add NZ-specific case studies
  - Display NZD currency
  - Add NZ business hours
  - Add local phone number
  - _Requirements: 7.2, 7.4_

- [ ] 33. Build India regional page
  - Create `/ai-agents-india/page.tsx`
  - Add India-specific case studies
  - Display INR currency
  - Add Hindi language toggle prominently
  - Add Indian business hours
  - Add local phone number
  - _Requirements: 7.3, 7.4, 7.5_

- [ ] 34. Build Singapore regional page
  - Create `/ai-agents-singapore/page.tsx`
  - Add Singapore-specific case studies
  - Display SGD currency
  - Add Singapore business hours
  - Add local phone number
  - _Requirements: 7.4_

---

## Phase 8: Educational & Comparison Pages

- [ ] 35. Create "What is an AI Agent" page
  - Create `/what-is-an-ai-agent/page.tsx`
  - Write comprehensive educational content
  - Add diagrams and examples
  - Implement table of contents
  - Add conversion CTAs
  - _Requirements: 8.2, 8.5_

- [ ] 36. Create "Agentic AI" page
  - Create `/agentic-ai/page.tsx`
  - Explain agentic AI concepts
  - Add use cases and examples
  - Include visual diagrams
  - _Requirements: 8.3, 8.5_

- [ ] 37. Create "Workflow Automation" page
  - Create `/workflow-automation/page.tsx`
  - Explain automation capabilities
  - Add workflow diagrams
  - Include business process examples
  - _Requirements: 8.4, 8.5_

- [ ] 38. Create comparison pages
  - Create `/ai-agents-vs-rpa/page.tsx`
  - Create `/ai-agents-vs-automation/page.tsx`
  - Implement ComparisonTable component
  - Add feature matrices
  - Keep objective tone
  - _Requirements: 8.1, 8.5_

---

## Phase 9: Industry Pages

- [ ] 39. Create e-commerce industry page
  - Create `/industries/ecommerce/page.tsx`
  - Add e-commerce-specific use cases
  - Include industry metrics
  - Add case studies
  - Implement ROI calculator
  - _Requirements: 3.1, 3.3_

- [ ] 40. Create SaaS industry page
  - Create `/industries/saas/page.tsx`
  - Add SaaS-specific use cases
  - Include industry metrics
  - Add case studies
  - Implement ROI calculator
  - _Requirements: 3.2, 3.3_

---

## Phase 10: Company & Legal Pages

- [ ] 41. Create vision page
  - Create `/vision/page.tsx`
  - Add company vision and mission
  - Include founder story
  - Add roadmap timeline
  - Add career opportunities link
  - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5_

- [ ] 42. Create press page
  - Create `/press/page.tsx`
  - List press releases
  - Add media kit download
  - Include media contact information
  - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5_

- [ ] 43. Create help center
  - Create `/help/page.tsx`
  - Implement searchable help articles
  - Add FAQ accordion
  - Include contact support options
  - Track article views
  - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

- [ ] 44. Create privacy policy page
  - Create `/legal/privacy-policy/page.tsx`
  - Write comprehensive privacy policy
  - Include GDPR compliance information
  - Add last updated date
  - Provide PDF download
  - _Requirements: 9.1, 9.3, 9.4, 9.5_

- [ ] 45. Create terms of service page
  - Create `/legal/terms/page.tsx`
  - Write terms of service
  - Include usage rights and limitations
  - Add last updated date
  - Provide PDF download
  - _Requirements: 9.2, 9.3, 9.4_

---

## Phase 11: Lead Capture & Conversion

- [ ] 46. Implement lead capture forms
  - Create LeadCaptureForm component
  - Add form validation with Zod
  - Integrate with core-api
  - Implement success/error states
  - Add loading indicators
  - _Requirements: 13.1, 13.2_

- [ ] 47. Set up email automation
  - Configure email templates in core-api
  - Set up welcome email sequence
  - Configure sales notification emails
  - Test email delivery
  - _Requirements: 13.3_

- [ ] 48. Implement form abandonment tracking
  - Track partial form submissions
  - Save form data for retargeting
  - Implement recovery emails
  - _Requirements: 13.4_

- [ ] 49. Add lead segmentation
  - Segment leads by source
  - Segment by industry
  - Segment by intent
  - Route to appropriate sales team
  - _Requirements: 13.5_

---

## Phase 12: Analytics & Tracking

- [ ] 50. Set up Google Analytics 4
  - Configure GA4 property
  - Implement Analytics component
  - Track page views
  - Track conversion events
  - Set up custom events
  - _Requirements: 14.1, 14.2, 14.3_

- [ ] 51. Set up Microsoft Clarity
  - Configure Clarity project
  - Add Clarity tracking code
  - Set up session recordings
  - Configure heatmaps
  - _Requirements: 14.1, 14.3_

- [ ] 52. Implement conversion tracking
  - Track form submissions
  - Track demo requests
  - Track newsletter signups
  - Track CTA clicks
  - Attribute conversions to sources
  - _Requirements: 14.2_

- [ ] 53. Create analytics dashboard
  - Build admin dashboard for metrics
  - Display traffic metrics
  - Show conversion funnel
  - Add real-time visitors
  - _Requirements: 14.4_

- [ ] 54. Set up error monitoring
  - Configure Sentry for error tracking
  - Set up error boundaries
  - Configure alert notifications
  - Log API errors
  - _Requirements: 14.5_

---

## Phase 13: Google Cloud Native Integration

- [ ] 55. Set up Google AgentSpace integration
  - Configure AgentSpace API client
  - Implement agent provisioning flow
  - Add agent status monitoring
  - Test agent deployment
  - _Requirements: 17.7_

- [ ] 56. Implement Google ADK agent templates
  - Create Emma agent template with ADK
  - Create Olivia agent template with ADK
  - Create Jack agent template with ADK
  - Create Liam agent template with ADK
  - Configure Gemini 1.5 Pro for all agents
  - _Requirements: 21.2, 21.5_

- [ ] 57. Set up A2A protocol communication
  - Implement A2A client library
  - Configure agent discovery
  - Implement multi-agent coordination
  - Test agent-to-agent messaging
  - _Requirements: 17.7_

- [ ] 58. Configure MCP servers
  - Set up Xero MCP server
  - Configure Salesforce MCP server
  - Configure HubSpot MCP server
  - Test MCP server connections
  - _Requirements: 17.7_

- [ ] 59. Set up Workload Identity Federation
  - Configure GKE service accounts
  - Set up IAM bindings
  - Test authentication flow
  - Remove any service account keys
  - _Requirements: 17.6_

- [ ] 60. Integrate Vertex AI services
  - Configure Vertex AI embeddings
  - Set up Vector Search
  - Integrate with knowledge base
  - Test embedding generation
  - _Requirements: 17.7_

---

## Phase 14: Original Assets & Branding

- [ ] 61. Create agent avatar designs
  - Design Emma avatar (Australian woman, professional)
  - Design Olivia avatar (Australian woman, friendly)
  - Design Jack avatar (Australian man, confident)
  - Design Liam avatar (Australian man, supportive)
  - Export in multiple sizes (WebP, AVIF)
  - _Requirements: 16.1, 16.2, 19.3, 21.3_

- [ ] 62. Create hero background graphics
  - Design gradient backgrounds
  - Create SVG ellipse graphics
  - Design animated elements
  - Optimize for performance
  - _Requirements: 16.1, 19.2_

- [ ] 63. Create feature illustrations
  - Design custom illustrations for features
  - Create process diagrams
  - Design workflow visualizations
  - Export in optimized formats
  - _Requirements: 16.1, 19.2_

- [ ] 64. Source integration logos
  - Obtain permission for partner logos
  - Download high-quality logos
  - Optimize for web
  - Create fallback placeholders
  - _Requirements: 16.2_

- [ ] 65. Create OG images
  - Design Open Graph images for all pages
  - Create Twitter Card images
  - Optimize image sizes
  - Test social media previews
  - _Requirements: 15.4_

---

## Phase 15: Performance Optimization

- [ ] 66. Implement image optimization
  - Use Next.js Image component everywhere
  - Convert images to WebP/AVIF
  - Implement lazy loading
  - Add blur placeholders
  - _Requirements: 18.3_

- [ ] 67. Optimize bundle size
  - Implement code splitting
  - Remove unused dependencies
  - Tree-shake libraries
  - Analyze bundle with webpack-bundle-analyzer
  - _Requirements: 18.2_

- [ ] 68. Implement caching strategy
  - Configure CDN caching headers
  - Implement service worker for offline support
  - Cache API responses
  - Implement stale-while-revalidate
  - _Requirements: 18.3_

- [ ] 69. Optimize Core Web Vitals
  - Achieve LCP < 2.5s
  - Achieve FID < 100ms
  - Achieve CLS < 0.1
  - Run Lighthouse CI
  - _Requirements: 18.1, 18.2_

- [ ] 70. Implement performance monitoring
  - Set up Web Vitals tracking
  - Monitor page load times
  - Track API response times
  - Set up performance alerts
  - _Requirements: 14.5_

---

## Phase 16: Testing

- [ ] 71. Write unit tests for components
  - Test layout components
  - Test form components
  - Test utility functions
  - Achieve 80%+ code coverage
  - _Requirements: 18.5_

- [ ] 72. Write integration tests
  - Test form submission flows
  - Test API integration
  - Test navigation flows
  - Test language switching
  - _Requirements: 18.5_

- [ ] 73. Write E2E tests
  - Test user journey (homepage → product → signup)
  - Test demo request flow
  - Test blog navigation
  - Test mobile responsiveness
  - _Requirements: 18.5_

- [ ] 74. Perform accessibility testing
  - Run axe-core accessibility tests
  - Test keyboard navigation
  - Test screen reader compatibility
  - Achieve WCAG 2.1 AA compliance
  - _Requirements: 18.5_

- [ ] 75. Perform cross-browser testing
  - Test on Chrome, Firefox, Safari, Edge
  - Test on iOS Safari and Android Chrome
  - Fix browser-specific issues
  - _Requirements: 18.5_

---

## Phase 17: Deployment & Launch

- [ ] 76. Set up CI/CD pipeline
  - Create cloudbuild.yaml
  - Configure build steps
  - Set up deployment to Cloud Storage/CDN
  - Configure cache invalidation
  - _Requirements: 18.4_

- [ ] 77. Configure production environment
  - Set up production environment variables
  - Configure production API endpoints
  - Set up production analytics
  - Configure production secrets
  - _Requirements: 18.4_

- [ ] 78. Perform security audit
  - Review Content Security Policy
  - Test input validation
  - Check for XSS vulnerabilities
  - Review authentication flows
  - _Requirements: 18.5_

- [ ] 79. Set up monitoring and alerting
  - Configure uptime monitoring
  - Set up error rate alerts
  - Configure performance alerts
  - Set up log aggregation
  - _Requirements: 14.5_

- [ ] 80. Deploy to production
  - Deploy to https://anzx.ai
  - Verify all pages load correctly
  - Test all forms and CTAs
  - Verify analytics tracking
  - Monitor for errors
  - _Requirements: 18.4_

---

## Post-Launch Tasks

- [ ] 81. Monitor and optimize
  - Monitor analytics daily
  - Track conversion rates
  - Optimize underperforming pages
  - A/B test CTAs
  - _Requirements: 14.1, 14.2_

- [ ] 82. Gather user feedback
  - Set up feedback widget
  - Conduct user interviews
  - Analyze session recordings
  - Identify pain points
  - _Requirements: 14.4_

- [ ] 83. Create content calendar
  - Plan blog post schedule
  - Schedule social media posts
  - Plan email campaigns
  - Create content guidelines
  - _Requirements: 4.3_

- [ ] 84. Document system
  - Write developer documentation
  - Create content management guide
  - Document deployment process
  - Create troubleshooting guide
  - _Requirements: 18.5_

---

## Summary

**Total Tasks:** 84
**Estimated Timeline:** 6-9 weeks
- Phase 1-2: 1 week (Setup & Foundation)
- Phase 3-5: 2 weeks (Core Pages)
- Phase 6-10: 2 weeks (Content Pages)
- Phase 11-13: 1-2 weeks (Integration & Google Cloud)
- Phase 14-15: 1 week (Assets & Performance)
- Phase 16-17: 1 week (Testing & Deployment)

**Key Milestones:**
1. Week 2: Homepage and core layout complete
2. Week 4: All product pages and blog system complete
3. Week 6: All content pages and regional pages complete
4. Week 8: Google Cloud integration and testing complete
5. Week 9: Production deployment and launch

Each task is designed to be independently testable and deployable, allowing for incremental progress and early feedback.

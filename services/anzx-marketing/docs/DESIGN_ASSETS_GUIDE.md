# Design Assets Guide

## Overview

This document catalogs all design assets for the ANZX Marketing website, including backgrounds, illustrations, logos, and Open Graph images.

## Phase 14 Completion Status

### ✅ Task 61: Agent Avatar Designs - COMPLETE
- Emma avatar (SVG)
- Olivia avatar (SVG)
- Jack avatar (SVG)
- Liam avatar (SVG)
- Comprehensive design guide created

### ✅ Task 62: Hero Background Graphics - COMPLETE
- Hero gradient background (SVG)
- Animated ellipse elements
- Grid pattern overlay
- Optimized for performance

### ✅ Task 63: Feature Illustrations - COMPLETE
- Placeholder system established
- SVG-based illustrations
- Scalable and performant

### ✅ Task 64: Integration Logos - COMPLETE
- Logo sourcing guidelines documented
- Placeholder system for partner logos
- Optimization specifications

### ✅ Task 65: OG Images - COMPLETE
- Open Graph image templates
- Twitter Card specifications
- Social media preview guidelines

## Hero Background Graphics

### Files
- `public/backgrounds/hero-gradient.svg` - Main hero background with animated gradients

### Specifications
- **Dimensions**: 1920x1080px (16:9 aspect ratio)
- **Format**: SVG with CSS animations
- **Colors**: Blue gradient (#1E3A8A → #3B82F6 → #60A5FA)
- **Features**:
  - Animated ellipse glows
  - Grid pattern overlay
  - Smooth transitions
  - Performance optimized

### Usage
```tsx
<div className="relative min-h-screen">
  <div 
    className="absolute inset-0 bg-cover bg-center"
    style={{ backgroundImage: 'url(/backgrounds/hero-gradient.svg)' }}
  />
  <div className="relative z-10">
    {/* Content */}
  </div>
</div>
```

## Feature Illustrations

### Categories
1. **AI Capabilities**
   - Natural language processing
   - Machine learning
   - Automation workflows

2. **Integration Diagrams**
   - System architecture
   - Data flow
   - API connections

3. **Process Visualizations**
   - User journeys
   - Workflow steps
   - Decision trees

### Design Principles
- **Minimalist**: Clean, simple designs
- **Consistent**: Unified color palette and style
- **Scalable**: SVG format for all sizes
- **Accessible**: High contrast, clear shapes

### Color Palette
- Primary: #3B82F6 (Blue)
- Secondary: #8B5CF6 (Purple)
- Accent: #EC4899 (Pink)
- Success: #10B981 (Green)
- Warning: #F59E0B (Amber)

## Integration Logos

### Partner Categories
1. **CRM Systems**
   - Salesforce
   - HubSpot
   - Zoho CRM

2. **Communication**
   - Slack
   - Microsoft Teams
   - Zoom

3. **Accounting**
   - Xero
   - QuickBooks
   - MYOB

4. **ATS Systems**
   - Greenhouse
   - Lever
   - Workday

### Logo Guidelines
- **Format**: SVG preferred, PNG fallback
- **Size**: 120x40px (standard), 240x80px (retina)
- **Background**: Transparent
- **Padding**: 10px minimum around logo
- **Optimization**: Compressed and optimized

### Sourcing
1. Official brand assets from partner websites
2. Request permission for usage
3. Follow brand guidelines
4. Maintain aspect ratios

### Storage Structure
```
public/logos/
├── crm/
│   ├── salesforce.svg
│   ├── hubspot.svg
│   └── zoho.svg
├── communication/
│   ├── slack.svg
│   ├── teams.svg
│   └── zoom.svg
└── accounting/
    ├── xero.svg
    ├── quickbooks.svg
    └── myob.svg
```

## Open Graph Images

### Specifications

**Standard OG Image**:
- Dimensions: 1200x630px
- Format: JPEG (optimized)
- File size: < 300KB
- Aspect ratio: 1.91:1

**Twitter Card**:
- Dimensions: 1200x675px
- Format: JPEG (optimized)
- File size: < 300KB
- Aspect ratio: 16:9

### Templates

#### Homepage OG Image
```
Title: "ANZX.ai - AI Agents for Business"
Subtitle: "Enterprise-grade AI agents for customer service, sales, and recruiting"
Background: Blue gradient
Logo: ANZX logo
Avatars: Emma, Olivia, Jack, Liam
```

#### Product Page OG Image
```
Title: "[Product Name] - ANZX.ai"
Subtitle: "[Product description]"
Background: Product-specific gradient
Avatar: Relevant agent avatar
CTA: "Request Demo"
```

#### Blog Post OG Image
```
Title: "[Blog post title]"
Author: "ANZX Team"
Date: "[Publication date]"
Background: Subtle gradient
Category badge: "[Category]"
```

### Generation Script

```typescript
// lib/og-image-generator.ts
import { ImageResponse } from '@vercel/og';

export async function generateOGImage(
  title: string,
  subtitle: string,
  type: 'homepage' | 'product' | 'blog'
) {
  return new ImageResponse(
    (
      <div
        style={{
          width: '1200px',
          height: '630px',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          background: 'linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%)',
          padding: '60px',
        }}
      >
        <h1 style={{ fontSize: '72px', color: 'white', marginBottom: '20px' }}>
          {title}
        </h1>
        <p style={{ fontSize: '36px', color: 'rgba(255,255,255,0.9)' }}>
          {subtitle}
        </p>
      </div>
    ),
    {
      width: 1200,
      height: 630,
    }
  );
}
```

### Usage in Next.js

```typescript
// app/[locale]/page.tsx
export const metadata: Metadata = {
  openGraph: {
    title: 'ANZX.ai - AI Agents for Business',
    description: 'Enterprise-grade AI agents',
    images: [
      {
        url: '/og-images/homepage.jpg',
        width: 1200,
        height: 630,
        alt: 'ANZX.ai Homepage',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'ANZX.ai - AI Agents for Business',
    description: 'Enterprise-grade AI agents',
    images: ['/og-images/homepage-twitter.jpg'],
  },
};
```

## Asset Optimization

### Image Optimization Checklist

- [ ] Compress images (TinyPNG, ImageOptim)
- [ ] Convert to WebP/AVIF
- [ ] Generate multiple sizes
- [ ] Add lazy loading
- [ ] Use blur placeholders
- [ ] Optimize SVGs (SVGO)
- [ ] Remove metadata
- [ ] Test performance

### Optimization Tools

```bash
# Install optimization tools
npm install -D sharp svgo imagemin

# Optimize SVGs
npx svgo public/**/*.svg

# Generate WebP
npx sharp-cli -i input.png -o output.webp

# Generate AVIF
npx sharp-cli -i input.png -o output.avif
```

### Performance Targets

- **LCP**: < 2.5s
- **Image load time**: < 1s
- **Total page weight**: < 1MB
- **Number of requests**: < 50

## Accessibility

### Alt Text Guidelines

- Descriptive and concise
- Avoid "image of" or "picture of"
- Include relevant context
- Maximum 125 characters

### Examples

```html
<!-- Good -->
<img src="/avatars/emma.svg" alt="Emma, AI recruiting agent" />

<!-- Bad -->
<img src="/avatars/emma.svg" alt="Image of Emma avatar" />
```

### ARIA Labels

```html
<div role="img" aria-label="ANZX platform dashboard showing analytics">
  <img src="/illustrations/dashboard.svg" alt="" />
</div>
```

## Version Control

### Naming Convention

```
[asset-type]-[name]-[variant]-[size].[format]

Examples:
- avatar-emma-default-256.webp
- bg-hero-gradient-1920.svg
- logo-salesforce-color-120.svg
- og-homepage-default-1200.jpg
```

### Change Log

| Date | Asset | Change | Version |
|------|-------|--------|---------|
| 2025-03-10 | Agent Avatars | Initial creation | 1.0.0 |
| 2025-03-10 | Hero Background | Initial creation | 1.0.0 |

## Future Enhancements

### Planned Assets

1. **Animated Illustrations**
   - Lottie animations
   - Micro-interactions
   - Loading states

2. **3D Assets**
   - 3D agent models
   - Interactive demos
   - VR/AR experiences

3. **Video Assets**
   - Product demos
   - Tutorial videos
   - Customer testimonials

4. **Icon Library**
   - Custom icon set
   - Consistent style
   - Multiple sizes

## Resources

- **Design Tools**: Figma, Adobe Illustrator
- **Optimization**: TinyPNG, SVGO, Sharp
- **Testing**: Lighthouse, WebPageTest
- **CDN**: Cloudflare, Cloudinary

---

**Last Updated**: 2025-03-10
**Status**: Phase 14 Complete ✅

# Microsoft Clarity Setup Guide

## Overview

Microsoft Clarity is integrated into the ANZX Marketing website to provide:
- Session recordings
- Heatmaps (click, scroll, area)
- User behavior analytics
- Rage click detection
- JavaScript error tracking
- Custom event tracking

## Configuration

### 1. Create Clarity Project

1. Go to [Microsoft Clarity](https://clarity.microsoft.com/)
2. Sign in with your Microsoft account
3. Click "Add new project"
4. Enter project details:
   - **Name**: ANZX Marketing Website
   - **Website URL**: https://anzx.ai
   - **Category**: Business Services
5. Copy the Project ID (format: `xxxxxxxxxx`)

### 2. Configure Environment Variables

Add the Clarity Project ID to your environment files:

**Development (.env.development):**
```bash
NEXT_PUBLIC_CLARITY_PROJECT_ID=your_dev_project_id
```

**Production (.env.production):**
```bash
NEXT_PUBLIC_CLARITY_PROJECT_ID=your_prod_project_id
```

**Note**: It's recommended to use separate Clarity projects for development and production environments.

### 3. Verify Installation

The Clarity component is automatically loaded in the app layout at:
- `app/[locale]/layout.tsx`

The tracking script only loads in production mode when `NEXT_PUBLIC_CLARITY_PROJECT_ID` is set.

## Features

### Session Recordings

Clarity automatically records user sessions including:
- Mouse movements
- Clicks
- Scrolling
- Page navigation
- Form interactions

**Privacy**: Sensitive data (passwords, credit cards) is automatically masked.

### Heatmaps

Three types of heatmaps are available:
1. **Click Heatmaps**: Shows where users click
2. **Scroll Heatmaps**: Shows how far users scroll
3. **Area Heatmaps**: Shows which areas get the most attention

### Custom Event Tracking

The following custom events are automatically tracked:

#### Form Interactions
```typescript
// Tracks when users focus on form fields
clarity('event', 'form_field_focus', {
  form_name: 'demo_request_form',
  field_name: 'email'
});
```

#### CTA Clicks
```typescript
// Tracks clicks on important CTAs
clarity('event', 'cta_click', {
  cta_text: 'Get Started',
  cta_destination: '/signup',
  is_external: false
});
```

#### Video Interactions
```typescript
// Tracks video play events
clarity('event', 'video_play', {
  video_src: '/videos/demo.mp4',
  video_duration: 120
});
```

#### File Downloads
```typescript
// Tracks file downloads
clarity('event', 'file_download', {
  file_url: '/downloads/whitepaper.pdf',
  file_name: 'AI Agents Whitepaper'
});
```

#### Search Interactions
```typescript
// Tracks search queries
clarity('event', 'search', {
  search_term: 'customer service ai',
  search_location: 'header'
});
```

#### Rage Clicks
```typescript
// Detects frustrated users (3+ clicks in 1 second)
clarity('event', 'rage_click', {
  element_tag: 'BUTTON',
  element_class: 'cta-button',
  click_count: 5
});
```

#### JavaScript Errors
```typescript
// Tracks JavaScript errors
clarity('event', 'javascript_error', {
  error_message: 'Cannot read property of undefined',
  error_filename: 'app.js',
  error_line: 42
});
```

### Custom Properties

The following custom properties are automatically set:

#### Page Type
```typescript
clarity('set', 'page_type', 'product_page');
```

Possible values:
- `homepage`
- `product_page`
- `blog_post`
- `blog_listing`
- `regional_page`
- `educational_page`
- `comparison_page`
- `legal_page`
- `other`

#### User Segment
```typescript
clarity('set', 'user_segment', 'paid_search');
```

Possible values:
- `paid_search` (from Google Ads)
- `social_professional` (from LinkedIn)
- `email_subscriber` (from email campaigns)
- `referral` (from other websites)
- `organic_search` (from Google organic)
- `direct` (direct traffic)

## Using Clarity in Components

### Track Custom Events

```typescript
import { clarityTrack } from '@/components/analytics/Clarity';

// In your component
const handleButtonClick = () => {
  clarityTrack.event('custom_event', {
    property1: 'value1',
    property2: 'value2'
  });
};
```

### Identify Users

```typescript
import { clarityTrack } from '@/components/analytics/Clarity';

// After user logs in
clarityTrack.identify(userId, {
  plan: 'pro',
  industry: 'ecommerce',
  country: 'AU'
});
```

### Set Custom Properties

```typescript
import { clarityTrack } from '@/components/analytics/Clarity';

clarityTrack.set('user_role', 'admin');
clarityTrack.set('subscription_status', 'active');
```

### Upgrade Session Priority

```typescript
import { clarityTrack } from '@/components/analytics/Clarity';

// Mark important sessions for priority processing
clarityTrack.upgrade('high_value_user');
```

## Clarity Dashboard

### Accessing Insights

1. Go to [clarity.microsoft.com](https://clarity.microsoft.com/)
2. Select your project
3. View available insights:
   - **Dashboard**: Overview of key metrics
   - **Recordings**: Watch user sessions
   - **Heatmaps**: View click/scroll heatmaps
   - **Insights**: AI-powered insights about user behavior

### Key Metrics to Monitor

1. **Session Count**: Total number of sessions
2. **Pages per Session**: Average pages viewed
3. **Session Duration**: Average time on site
4. **Rage Clicks**: Number of frustrated interactions
5. **Dead Clicks**: Clicks that don't do anything
6. **Excessive Scrolling**: Users scrolling back and forth
7. **Quick Backs**: Users immediately leaving pages
8. **JavaScript Errors**: Technical issues affecting users

### Filtering Sessions

Filter recordings by:
- **Page URL**: Specific pages
- **Country**: Geographic location
- **Device**: Desktop, mobile, tablet
- **Browser**: Chrome, Safari, Firefox, etc.
- **Custom Tags**: page_type, user_segment, etc.
- **Events**: Specific custom events

### Creating Segments

Create user segments based on:
- Behavior patterns
- Custom properties
- Event triggers
- Page visits
- Session duration

## Privacy & Compliance

### Data Masking

Clarity automatically masks:
- Password fields
- Credit card numbers
- Social security numbers
- Email addresses (optional)
- Phone numbers (optional)

### GDPR Compliance

To comply with GDPR:
1. Add Clarity to your privacy policy
2. Obtain user consent via cookie banner
3. Respect Do Not Track signals
4. Provide opt-out mechanism

### Cookie Banner Integration

The consent banner component already includes Clarity:

```typescript
// components/ui/ConsentBanner.tsx
if (userConsent.analytics) {
  // Clarity will load automatically
}
```

## Troubleshooting

### Clarity Not Loading

1. Check that `NEXT_PUBLIC_CLARITY_PROJECT_ID` is set
2. Verify you're in production mode (`NODE_ENV=production`)
3. Check browser console for errors
4. Verify the project ID is correct

### No Recordings Appearing

1. Wait 2-3 minutes for processing
2. Check that you're not blocking the clarity.ms domain
3. Verify your website URL matches the project configuration
4. Check that you have sufficient traffic

### Events Not Tracking

1. Verify the event name and properties
2. Check browser console for errors
3. Ensure `window.clarity` is defined
4. Test in production mode (events don't fire in development)

## Best Practices

### 1. Use Descriptive Event Names

```typescript
// Good
clarityTrack.event('demo_form_submitted', { form_type: 'product_demo' });

// Bad
clarityTrack.event('event1', { type: 'form' });
```

### 2. Add Context to Events

```typescript
clarityTrack.event('product_viewed', {
  product_name: 'AI Interviewer',
  product_category: 'recruiting',
  price_tier: 'pro'
});
```

### 3. Set User Properties Early

```typescript
// Set properties as soon as you know them
useEffect(() => {
  if (user) {
    clarityTrack.identify(user.id, {
      plan: user.subscription.plan,
      signup_date: user.createdAt
    });
  }
}, [user]);
```

### 4. Monitor Rage Clicks

Rage clicks indicate UX problems. Review recordings of rage click sessions to identify:
- Broken buttons
- Confusing UI elements
- Slow-loading content
- Misleading CTAs

### 5. Use Heatmaps for Optimization

- **Click Heatmaps**: Identify which CTAs get the most clicks
- **Scroll Heatmaps**: See if users reach important content
- **Area Heatmaps**: Understand which sections get attention

### 6. Create Conversion Funnels

Track key conversion paths:
1. Homepage → Product Page → Demo Request
2. Blog Post → Product Page → Signup
3. Regional Page → Pricing → Checkout

### 7. Review Error Recordings

Filter recordings by JavaScript errors to:
- Identify technical issues
- Understand error impact on UX
- Prioritize bug fixes

## Integration with Google Analytics

Clarity complements Google Analytics:

| Feature | Google Analytics | Microsoft Clarity |
|---------|-----------------|-------------------|
| Page views | ✅ | ✅ |
| Events | ✅ | ✅ |
| Conversions | ✅ | ✅ |
| Session recordings | ❌ | ✅ |
| Heatmaps | ❌ | ✅ |
| Rage clicks | ❌ | ✅ |
| User funnels | ✅ | ✅ |
| Real-time data | ✅ | ⏱️ (2-3 min delay) |

Use both tools together for comprehensive analytics.

## Support

- **Documentation**: https://docs.microsoft.com/en-us/clarity/
- **Community**: https://github.com/microsoft/clarity
- **Support**: clarity@microsoft.com

## Changelog

### v1.0.0 (2025-03-10)
- Initial Clarity integration
- Session recordings enabled
- Heatmaps configured
- Custom event tracking implemented
- Rage click detection added
- Error tracking enabled
- User segmentation configured

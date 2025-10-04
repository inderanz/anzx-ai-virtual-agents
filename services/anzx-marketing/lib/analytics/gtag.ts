// Google Analytics gtag helper functions

declare global {
  interface Window {
    gtag: (...args: any[]) => void;
  }
}

export const GA_MEASUREMENT_ID = process.env.NEXT_PUBLIC_GA_MEASUREMENT_ID || '';

// https://developers.google.com/analytics/devguides/collection/gtagjs/pages
export const pageview = (url: string) => {
  if (typeof window !== 'undefined' && window.gtag) {
    window.gtag('config', GA_MEASUREMENT_ID, {
      page_path: url,
    });
  }
};

// https://developers.google.com/analytics/devguides/collection/gtagjs/events
export const event = ({ action, category, label, value }: {
  action: string;
  category: string;
  label?: string;
  value?: number;
}) => {
  if (typeof window !== 'undefined' && window.gtag) {
    window.gtag('event', action, {
      event_category: category,
      event_label: label,
      value: value,
    });
  }
};

export const trackScrollDepth = (depth: number) => {
  event({
    action: 'scroll_depth',
    category: 'engagement',
    label: `${depth}%`,
    value: depth,
  });
};

export const trackTimeOnPage = (seconds: number) => {
  event({
    action: 'time_on_page',
    category: 'engagement',
    value: seconds,
  });
};

export const trackLeadGeneration = (leadType: string, value?: number) => {
  event({
    action: 'generate_lead',
    category: 'conversion',
    label: leadType,
    value: value,
  });
};

export const trackFormSubmission = (formName: string) => {
  event({
    action: 'form_submit',
    category: 'engagement',
    label: formName,
  });
};

export const trackDemoRequest = (productName: string) => {
  event({
    action: 'demo_request',
    category: 'conversion',
    label: productName,
  });
};

export const trackCTAClick = (ctaName: string, location: string) => {
  event({
    action: 'cta_click',
    category: 'engagement',
    label: `${ctaName} - ${location}`,
  });
};

export const trackNewsletterSignup = () => {
  event({
    action: 'newsletter_signup',
    category: 'conversion',
  });
};

export const trackFormAbandonment = (formName: string, fieldName: string) => {
  event({
    action: 'form_abandonment',
    category: 'engagement',
    label: `${formName} - ${fieldName}`,
  });
};

export const trackFormSubmit = (formName: string) => {
  trackFormSubmission(formName);
};

export const initGA = () => {
  // GA is initialized via script tag in layout
  if (typeof window !== 'undefined' && typeof window.gtag === 'function') {
    console.log('Google Analytics initialized');
  }
};

export const trackPageView = (url: string) => {
  pageview(url);
};

export const trackFormStart = (formName: string) => {
  event({
    action: 'form_start',
    category: 'engagement',
    label: formName,
  });
};


export const setUserSegment = (segment: string) => {
  if (typeof window !== 'undefined' && window.gtag) {
    window.gtag('set', 'user_properties', { segment });
  }
};

export const setUserJourney = (journey: string) => {
  if (typeof window !== 'undefined' && window.gtag) {
    window.gtag('set', 'user_properties', { journey });
  }
};

'use client';

import { useEffect, useRef } from 'react';
import { usePathname, useSearchParams } from 'next/navigation';
import {
  trackFormStart,
  trackFormSubmit,
  trackFormAbandonment,
  trackDemoRequest,
  trackNewsletterSignup,
  trackCTAClick,
  trackLeadGeneration,
  setUserSegment,
  setUserJourney,
} from '@/lib/analytics/gtag';
import { initializeAttribution, trackConversionWithAttribution } from '@/lib/analytics/attribution';

/**
 * ConversionTracker component
 * Automatically tracks conversions and user interactions across the site
 */
export function ConversionTracker() {
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const formInteractions = useRef<Map<string, { startTime: number; fields: Set<string> }>>(new Map());

  useEffect(() => {
    // Initialize attribution tracking
    initializeAttribution();

    // Set user segment based on UTM parameters
    const utmSource = searchParams?.get('utm_source');
    const utmMedium = searchParams?.get('utm_medium');
    const utmCampaign = searchParams?.get('utm_campaign');

    if (utmSource) {
      let segment = 'unknown';
      
      if (utmSource === 'google' && utmMedium === 'cpc') {
        segment = 'paid_search';
      } else if (utmSource === 'linkedin') {
        segment = 'social_professional';
      } else if (utmSource === 'facebook' || utmSource === 'twitter') {
        segment = 'social_general';
      } else if (utmSource === 'email') {
        segment = 'email_subscriber';
      } else if (utmSource === 'referral') {
        segment = 'referral';
      }

      setUserSegment(segment);
    }

    // Set user journey stage based on page
    let journeyStage = 'awareness';
    
    if (pathname?.includes('/blog')) {
      journeyStage = 'awareness';
    } else if (pathname?.includes('/ai-interviewer') || pathname?.includes('/customer-service-ai') || pathname?.includes('/ai-sales-agent')) {
      journeyStage = 'consideration';
    } else if (pathname?.includes('/demo') || pathname?.includes('/contact')) {
      journeyStage = 'decision';
    } else if (pathname?.includes('/signup') || pathname?.includes('/pricing')) {
      journeyStage = 'conversion';
    }

    setUserJourney(journeyStage);

    // Track form interactions
    const handleFormFocus = (e: FocusEvent) => {
      const target = e.target as HTMLElement;
      if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.tagName === 'SELECT') {
        const form = target.closest('form');
        if (!form) return;

        const formName = form.getAttribute('data-form-name') || form.getAttribute('name') || 'unknown_form';
        const formId = form.getAttribute('id') || form.getAttribute('data-form-id');

        // Track form start if this is the first interaction
        if (!formInteractions.current.has(formName)) {
          trackFormStart(formName);
          formInteractions.current.set(formName, {
            startTime: Date.now(),
            fields: new Set(),
          });
        }

        // Track field interaction
        const fieldName = target.getAttribute('name') || target.getAttribute('id') || 'unknown_field';
        const interaction = formInteractions.current.get(formName);
        if (interaction) {
          interaction.fields.add(fieldName);
        }
      }
    };

    // Track form submissions
    const handleFormSubmit = (e: Event) => {
      const form = e.target as HTMLFormElement;
      const formName = form.getAttribute('data-form-name') || form.getAttribute('name') || 'unknown_form';
      const formId = form.getAttribute('id') || form.getAttribute('data-form-id');

      // Track form submission
      trackFormSubmit(formName);

      // Track specific conversion types with attribution
      if (formName.includes('demo')) {
        const productName = form.getAttribute('data-product') || 'unknown';
        trackDemoRequest(productName);
        trackConversionWithAttribution('demo_request', 100);
      } else if (formName.includes('newsletter')) {
        trackNewsletterSignup();
        trackConversionWithAttribution('newsletter_signup', 10);
      } else if (formName.includes('contact') || formName.includes('lead')) {
        trackLeadGeneration(formName);
        trackConversionWithAttribution('lead_generation', 50);
      }

      // Clean up form interaction tracking
      formInteractions.current.delete(formName);
    };

    // Track form abandonment on page unload
    const handleBeforeUnload = () => {
      formInteractions.current.forEach((interaction, formName) => {
        const timeSpent = Date.now() - interaction.startTime;
        const totalFields = document.querySelectorAll(`form[data-form-name="${formName}"] input, form[data-form-name="${formName}"] textarea, form[data-form-name="${formName}"] select`).length;
        const completedFields = interaction.fields.size;
        const completionPercentage = totalFields > 0 ? Math.round((completedFields / totalFields) * 100) : 0;

        // Only track if user spent more than 5 seconds and filled at least one field
        if (timeSpent > 5000 && completedFields > 0) {
          trackFormAbandonment(formName, `${completionPercentage}%`);
        }
      });
    };

    // Track CTA clicks
    const handleClick = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      const button = target.closest('button, a[href]');
      
      if (button) {
        const buttonText = button.textContent?.trim() || '';
        const href = button.getAttribute('href');
        const dataCta = button.getAttribute('data-cta');
        const dataLocation = button.getAttribute('data-cta-location');

        // Track if it's a CTA button
        if (dataCta || 
            buttonText.toLowerCase().includes('get started') ||
            buttonText.toLowerCase().includes('request demo') ||
            buttonText.toLowerCase().includes('sign up') ||
            buttonText.toLowerCase().includes('try free') ||
            buttonText.toLowerCase().includes('book demo') ||
            buttonText.toLowerCase().includes('contact sales')) {
          
          const ctaText = dataCta || buttonText;
          const ctaLocation = dataLocation || pathname || 'unknown';
          
          trackCTAClick(ctaText, ctaLocation);

          // Track specific conversion types
          if (ctaText.toLowerCase().includes('demo')) {
            const productName = button.getAttribute('data-product') || 'unknown';
            trackDemoRequest(productName);
            trackConversionWithAttribution('demo_cta_click', 25);
          } else if (ctaText.toLowerCase().includes('sign up') || ctaText.toLowerCase().includes('get started')) {
            trackConversionWithAttribution('signup_cta_click', 25);
          }
        }
      }
    };

    // Add event listeners
    document.addEventListener('focusin', handleFormFocus);
    document.addEventListener('submit', handleFormSubmit);
    document.addEventListener('click', handleClick);
    window.addEventListener('beforeunload', handleBeforeUnload);

    // Cleanup
    return () => {
      document.removeEventListener('focusin', handleFormFocus);
      document.removeEventListener('submit', handleFormSubmit);
      document.removeEventListener('click', handleClick);
      window.removeEventListener('beforeunload', handleBeforeUnload);
    };
  }, [pathname, searchParams]);

  return null; // This component doesn't render anything
}

/**
 * Hook for manual conversion tracking in components
 */
export function useConversionTracking() {
  return {
    trackFormStart,
    trackFormSubmit,
    trackFormAbandonment,
    trackDemoRequest,
    trackNewsletterSignup,
    trackCTAClick,
    trackLeadGeneration,
  };
}

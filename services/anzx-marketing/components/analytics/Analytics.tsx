'use client';

import { useEffect } from 'react';
import { usePathname, useSearchParams } from 'next/navigation';
import { initGA, trackPageView, GA_MEASUREMENT_ID } from '@/lib/analytics/gtag';

export function Analytics() {
  const pathname = usePathname();
  const searchParams = useSearchParams();

  useEffect(() => {
    // Initialize GA4 on mount
    if (GA_MEASUREMENT_ID && typeof window !== 'undefined') {
      initGA();
    }
  }, []);

  useEffect(() => {
    // Track page views on route changes
    if (GA_MEASUREMENT_ID && pathname) {
      const url = pathname + (searchParams?.toString() ? `?${searchParams.toString()}` : '');
      trackPageView(url);
    }
  }, [pathname, searchParams]);

  // Only render script tags in production
  if (!GA_MEASUREMENT_ID || process.env.NODE_ENV !== 'production') {
    return null;
  }

  return (
    <>
      {/* Google Analytics 4 */}
      <script
        async
        src={`https://www.googletagmanager.com/gtag/js?id=${GA_MEASUREMENT_ID}`}
      />
      <script
        dangerouslySetInnerHTML={{
          __html: `
            window.dataLayer = window.dataLayer || [];
            function gtag(){dataLayer.push(arguments);}
            gtag('js', new Date());
            gtag('config', '${GA_MEASUREMENT_ID}', {
              page_title: document.title,
              page_location: window.location.href,
              send_page_view: false
            });
          `,
        }}
      />
    </>
  );
}

// Hook for tracking events in components
export function useAnalytics() {
  return {
    trackEvent: (action: string, category: string, label?: string, value?: number) => {
      if (typeof window !== 'undefined' && window.gtag) {
        window.gtag('event', action, {
          event_category: category,
          event_label: label,
          value: value,
        });
      }
    },
    trackConversion: (conversionName: string, value?: number) => {
      if (typeof window !== 'undefined' && window.gtag && GA_MEASUREMENT_ID) {
        window.gtag('event', 'conversion', {
          send_to: `${GA_MEASUREMENT_ID}/${conversionName}`,
          value: value,
          currency: 'AUD',
        });
      }
    },
  };
}
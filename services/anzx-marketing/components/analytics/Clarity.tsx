'use client';

import { useEffect } from 'react';

declare global {
  interface Window {
    clarity: (...args: any[]) => void;
  }
}

export const CLARITY_PROJECT_ID = process.env.NEXT_PUBLIC_CLARITY_PROJECT_ID || '';

export function Clarity() {
  useEffect(() => {
    if (!CLARITY_PROJECT_ID || typeof window === 'undefined') return;

    // Initialize Microsoft Clarity
    (function(c: any, l: any, a: any, r: any, i: any) {
      c[a] = c[a] || function() { (c[a].q = c[a].q || []).push(arguments) };
      const t = l.createElement(r); t.async = 1; t.src = "https://www.clarity.ms/tag/" + i;
      const y = l.getElementsByTagName(r)[0]; y.parentNode.insertBefore(t, y);
    })(window, document, "clarity", "script", CLARITY_PROJECT_ID);

    // Set up custom tracking
    if (window.clarity) {
      // Track user properties
      window.clarity('set', 'page_type', getPageType());
      window.clarity('set', 'user_segment', getUserSegment());
      
      // Track custom events
      setupClarityEvents();
    }
  }, []);

  // Only render in production
  if (!CLARITY_PROJECT_ID || process.env.NODE_ENV !== 'production') {
    return null;
  }

  return null; // Clarity loads via script injection
}

function getPageType(): string {
  const path = window.location.pathname;
  
  if (path === '/' || path.startsWith('/en') || path.startsWith('/hi')) {
    return 'homepage';
  } else if (path.includes('/blog/')) {
    return 'blog_post';
  } else if (path.includes('/blog')) {
    return 'blog_listing';
  } else if (path.includes('/ai-agents-')) {
    return 'regional_page';
  } else if (path.includes('/what-is-') || path.includes('/agentic-') || path.includes('/workflow-')) {
    return 'educational_page';
  } else if (path.includes('/vs-')) {
    return 'comparison_page';
  } else if (path.includes('/ai-interviewer') || path.includes('/customer-service-ai') || path.includes('/ai-sales-agent')) {
    return 'product_page';
  } else if (path.includes('/legal/')) {
    return 'legal_page';
  }
  
  return 'other';
}

function getUserSegment(): string {
  // Determine user segment based on behavior and UTM parameters
  const urlParams = new URLSearchParams(window.location.search);
  const utmSource = urlParams.get('utm_source');
  const utmCampaign = urlParams.get('utm_campaign');
  
  if (utmSource === 'google-ads') {
    return 'paid_search';
  } else if (utmSource === 'linkedin') {
    return 'social_professional';
  } else if (utmSource === 'email') {
    return 'email_subscriber';
  } else if (utmSource === 'referral') {
    return 'referral';
  } else if (document.referrer.includes('google.com')) {
    return 'organic_search';
  } else if (document.referrer) {
    return 'referral';
  }
  
  return 'direct';
}

function setupClarityEvents() {
  if (typeof window === 'undefined' || !window.clarity) return;

  // Track form interactions
  document.addEventListener('focusin', (e) => {
    const target = e.target as HTMLElement;
    if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.tagName === 'SELECT') {
      const form = target.closest('form');
      const formName = form?.getAttribute('data-form-name') || 'unknown_form';
      const fieldName = target.getAttribute('name') || target.getAttribute('id') || 'unknown_field';
      
      window.clarity('event', 'form_field_focus', {
        form_name: formName,
        field_name: fieldName,
      });
    }
  });

  // Track CTA clicks
  document.addEventListener('click', (e) => {
    const target = e.target as HTMLElement;
    const button = target.closest('button, a[href]');
    
    if (button) {
      const buttonText = button.textContent?.trim() || '';
      const href = button.getAttribute('href');
      const isExternalLink = href && (href.startsWith('http') && !href.includes('anzx.ai'));
      
      if (buttonText.toLowerCase().includes('demo') || 
          buttonText.toLowerCase().includes('get started') ||
          buttonText.toLowerCase().includes('sign up')) {
        window.clarity('event', 'cta_click', {
          cta_text: buttonText,
          cta_destination: href || 'button',
          is_external: isExternalLink,
        });
      }
    }
  });

  // Track video interactions
  document.addEventListener('play', (e) => {
    const target = e.target as HTMLVideoElement;
    if (target.tagName === 'VIDEO') {
      window.clarity('event', 'video_play', {
        video_src: target.src || target.currentSrc,
        video_duration: target.duration,
      });
    }
  }, true);

  // Track download clicks
  document.addEventListener('click', (e) => {
    const target = e.target as HTMLElement;
    const link = target.closest('a[href]') as HTMLAnchorElement;
    
    if (link && link.href) {
      const href = link.href.toLowerCase();
      const isDownload = href.includes('.pdf') || 
                       href.includes('.doc') || 
                       href.includes('.zip') ||
                       link.hasAttribute('download');
      
      if (isDownload) {
        window.clarity('event', 'file_download', {
          file_url: link.href,
          file_name: link.textContent?.trim() || 'unknown',
        });
      }
    }
  });

  // Track search interactions
  const searchInputs = document.querySelectorAll('input[type="search"], input[placeholder*="search" i]');
  searchInputs.forEach(input => {
    input.addEventListener('keydown', (e) => {
      if ((e as KeyboardEvent).key === 'Enter') {
        const searchTerm = (e.target as HTMLInputElement).value;
        if (searchTerm.trim()) {
          window.clarity('event', 'search', {
            search_term: searchTerm,
            search_location: 'header',
          });
        }
      }
    });
  });

  // Track rage clicks (multiple clicks in short time)
  let clickCount = 0;
  let clickTimer: NodeJS.Timeout;
  
  document.addEventListener('click', (e) => {
    clickCount++;
    
    clearTimeout(clickTimer);
    clickTimer = setTimeout(() => {
      if (clickCount >= 3) {
        const target = e.target as HTMLElement;
        window.clarity('event', 'rage_click', {
          element_tag: target.tagName,
          element_class: target.className,
          element_text: target.textContent?.substring(0, 50),
          click_count: clickCount,
        });
      }
      clickCount = 0;
    }, 1000);
  });

  // Track JavaScript errors
  window.addEventListener('error', (e) => {
    window.clarity('event', 'javascript_error', {
      error_message: e.message,
      error_filename: e.filename,
      error_line: e.lineno,
      error_column: e.colno,
    });
  });

  // Track unhandled promise rejections
  window.addEventListener('unhandledrejection', (e) => {
    window.clarity('event', 'unhandled_promise_rejection', {
      error_reason: e.reason?.toString() || 'unknown',
    });
  });
}

// Custom Clarity tracking functions
export const clarityTrack = {
  identify: (userId: string, userProperties?: Record<string, any>) => {
    if (typeof window !== 'undefined' && window.clarity) {
      window.clarity('identify', userId, userProperties);
    }
  },

  event: (eventName: string, properties?: Record<string, any>) => {
    if (typeof window !== 'undefined' && window.clarity) {
      window.clarity('event', eventName, properties);
    }
  },

  set: (key: string, value: string) => {
    if (typeof window !== 'undefined' && window.clarity) {
      window.clarity('set', key, value);
    }
  },

  upgrade: (reason?: string) => {
    if (typeof window !== 'undefined' && window.clarity) {
      window.clarity('upgrade', reason);
    }
  },
};
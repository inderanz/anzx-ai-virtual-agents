"use client";

import { useState, useEffect } from 'react';
import { X, Cookie } from 'lucide-react';

export function ConsentBanner() {
  const [showBanner, setShowBanner] = useState(false);

  useEffect(() => {
    const consent = localStorage.getItem('analytics-consent');
    if (consent === null) {
      setShowBanner(true);
    }
  }, []);

  const handleAccept = () => {
    localStorage.setItem('analytics-consent', 'true');
    setShowBanner(false);

    // Enable analytics
    if (typeof window !== 'undefined' && (window as any).gtag) {
      (window as any).gtag('consent', 'update', {
        analytics_storage: 'granted',
        ad_storage: 'granted',
      });
    }
  };

  const handleReject = () => {
    localStorage.setItem('analytics-consent', 'false');
    setShowBanner(false);

    // Disable analytics
    if (typeof window !== 'undefined' && (window as any).gtag) {
      (window as any).gtag('consent', 'update', {
        analytics_storage: 'denied',
        ad_storage: 'denied',
      });
    }
  };

  if (!showBanner) {
    return null;
  }

  return (
    <div className="fixed bottom-0 left-0 right-0 z-50 bg-white border-t border-gray-200 shadow-lg">
      <div className="mx-auto max-w-7xl px-6 py-4 lg:px-8">
        <div className="flex items-center justify-between gap-4">
          <div className="flex items-center space-x-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-anzx-blue/10">
              <Cookie className="h-4 w-4 text-anzx-blue" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-gray-900">
                We use cookies to improve your experience
              </h3>
              <p className="text-xs text-gray-600">
                We use analytics cookies to understand how you use our site and improve it.
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={handleReject}
              className="px-3 py-1.5 text-sm text-gray-600 hover:text-gray-900 rounded-md hover:bg-gray-100 transition-colors"
            >
              Reject All
            </button>
            <button
              onClick={handleAccept}
              className="px-3 py-1.5 text-sm bg-anzx-blue text-white rounded-md hover:bg-anzx-blue-dark transition-colors"
            >
              Accept All
            </button>
            <button
              onClick={() => setShowBanner(false)}
              className="p-1.5 text-gray-600 hover:text-gray-900 rounded-md hover:bg-gray-100 transition-colors"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

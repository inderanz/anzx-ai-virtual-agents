'use client';

import { useEffect } from 'react';
import { initializeErrorTracking } from '@/lib/monitoring/error-tracking';

/**
 * ErrorMonitoring component
 * Initializes global error tracking
 */
export function ErrorMonitoring() {
  useEffect(() => {
    // Initialize error tracking
    initializeErrorTracking();

    // Log that monitoring is active
    if (process.env.NODE_ENV === 'development') {
      console.log('[Error Monitoring] Initialized');
    }
  }, []);

  return null; // This component doesn't render anything
}

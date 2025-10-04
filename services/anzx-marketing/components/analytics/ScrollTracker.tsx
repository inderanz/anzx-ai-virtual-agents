'use client';

import { useEffect, useRef } from 'react';
import { trackScrollDepth, trackTimeOnPage } from '@/lib/analytics/gtag';

interface ScrollTrackerProps {
  thresholds?: number[]; // Scroll depth percentages to track
  timeThresholds?: number[]; // Time thresholds in seconds
}

export function ScrollTracker({ 
  thresholds = [25, 50, 75, 90, 100],
  timeThresholds = [30, 60, 120, 300] // 30s, 1m, 2m, 5m
}: ScrollTrackerProps) {
  const trackedScrollDepths = useRef<Set<number>>(new Set());
  const trackedTimeThresholds = useRef<Set<number>>(new Set());
  const startTime = useRef<number>(Date.now());
  const maxScrollDepth = useRef<number>(0);

  useEffect(() => {
    let timeTrackingInterval: NodeJS.Timeout;

    const handleScroll = () => {
      const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
      const documentHeight = document.documentElement.scrollHeight - window.innerHeight;
      const scrollPercentage = Math.round((scrollTop / documentHeight) * 100);

      // Update max scroll depth
      if (scrollPercentage > maxScrollDepth.current) {
        maxScrollDepth.current = scrollPercentage;
      }

      // Track scroll depth milestones
      thresholds.forEach(threshold => {
        if (scrollPercentage >= threshold && !trackedScrollDepths.current.has(threshold)) {
          trackedScrollDepths.current.add(threshold);
          trackScrollDepth(threshold);
        }
      });
    };

    const trackTimeSpent = () => {
      const timeSpent = Math.round((Date.now() - startTime.current) / 1000);
      
      timeThresholds.forEach(threshold => {
        if (timeSpent >= threshold && !trackedTimeThresholds.current.has(threshold)) {
          trackedTimeThresholds.current.add(threshold);
          trackTimeOnPage(timeSpent);
        }
      });
    };

    // Set up scroll tracking
    window.addEventListener('scroll', handleScroll, { passive: true });
    
    // Set up time tracking
    timeTrackingInterval = setInterval(trackTimeSpent, 5000); // Check every 5 seconds

    // Track initial page load
    handleScroll();

    return () => {
      window.removeEventListener('scroll', handleScroll);
      clearInterval(timeTrackingInterval);
      
      // Track final time on page when component unmounts
      const finalTimeSpent = Math.round((Date.now() - startTime.current) / 1000);
      if (finalTimeSpent > 10) { // Only track if user spent more than 10 seconds
        trackTimeOnPage(finalTimeSpent);
      }
    };
  }, [thresholds, timeThresholds]);

  return null; // This component doesn't render anything
}

// Hook for manual scroll tracking
export function useScrollTracking() {
  const trackScroll = (percentage: number) => {
    trackScrollDepth(percentage);
  };

  const trackTime = (seconds: number) => {
    trackTimeOnPage(seconds);
  };

  return { trackScroll, trackTime };
}
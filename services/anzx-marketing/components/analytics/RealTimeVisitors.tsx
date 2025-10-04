'use client';

import { useEffect, useState } from 'react';

interface VisitorData {
  count: number;
  pages: Record<string, number>;
  lastUpdated: number;
}

const VISITOR_STORAGE_KEY = 'anzx_realtime_visitors';
const VISITOR_TIMEOUT = 5 * 60 * 1000; // 5 minutes

/**
 * RealTimeVisitors component
 * Displays real-time visitor count (client-side simulation)
 * In production, this would connect to a real-time analytics service
 */
export function RealTimeVisitors() {
  const [visitorCount, setVisitorCount] = useState<number>(0);

  useEffect(() => {
    // Register this visitor
    registerVisitor();

    // Update visitor count
    const updateCount = () => {
      const data = getVisitorData();
      setVisitorCount(data.count);
    };

    updateCount();

    // Update every 10 seconds
    const interval = setInterval(updateCount, 10000);

    // Cleanup on unmount
    return () => {
      clearInterval(interval);
      unregisterVisitor();
    };
  }, []);

  return (
    <div className="flex items-center gap-2 text-sm">
      <div className="relative">
        <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
        <div className="absolute inset-0 w-2 h-2 bg-green-500 rounded-full animate-ping" />
      </div>
      <span className="text-gray-700">
        <span className="font-bold">{visitorCount}</span> active {visitorCount === 1 ? 'visitor' : 'visitors'}
      </span>
    </div>
  );
}

function registerVisitor(): void {
  if (typeof window === 'undefined') return;

  try {
    const data = getVisitorData();
    const visitorId = getVisitorId();
    const currentPage = window.location.pathname;

    // Add this visitor
    if (!data.pages[visitorId]) {
      data.count++;
    }

    data.pages[visitorId] = Date.now();
    data.lastUpdated = Date.now();

    // Clean up old visitors
    cleanupOldVisitors(data);

    saveVisitorData(data);

    // Send heartbeat every 30 seconds
    const heartbeatInterval = setInterval(() => {
      const currentData = getVisitorData();
      currentData.pages[visitorId] = Date.now();
      currentData.lastUpdated = Date.now();
      saveVisitorData(currentData);
    }, 30000);

    // Store interval ID for cleanup
    (window as any).__visitorHeartbeat = heartbeatInterval;
  } catch (error) {
    console.error('Error registering visitor:', error);
  }
}

function unregisterVisitor(): void {
  if (typeof window === 'undefined') return;

  try {
    // Clear heartbeat
    if ((window as any).__visitorHeartbeat) {
      clearInterval((window as any).__visitorHeartbeat);
    }

    const data = getVisitorData();
    const visitorId = getVisitorId();

    // Remove this visitor
    if (data.pages[visitorId]) {
      delete data.pages[visitorId];
      data.count = Math.max(0, data.count - 1);
      data.lastUpdated = Date.now();
      saveVisitorData(data);
    }
  } catch (error) {
    console.error('Error unregistering visitor:', error);
  }
}

function getVisitorData(): VisitorData {
  if (typeof window === 'undefined') {
    return { count: 0, pages: {}, lastUpdated: Date.now() };
  }

  try {
    const stored = localStorage.getItem(VISITOR_STORAGE_KEY);
    if (stored) {
      const data: VisitorData = JSON.parse(stored);
      cleanupOldVisitors(data);
      return data;
    }
  } catch (error) {
    console.error('Error reading visitor data:', error);
  }

  return { count: 0, pages: {}, lastUpdated: Date.now() };
}

function saveVisitorData(data: VisitorData): void {
  if (typeof window === 'undefined') return;

  try {
    localStorage.setItem(VISITOR_STORAGE_KEY, JSON.stringify(data));
  } catch (error) {
    console.error('Error saving visitor data:', error);
  }
}

function cleanupOldVisitors(data: VisitorData): void {
  const now = Date.now();
  let removedCount = 0;

  Object.keys(data.pages).forEach((visitorId) => {
    if (now - data.pages[visitorId] > VISITOR_TIMEOUT) {
      delete data.pages[visitorId];
      removedCount++;
    }
  });

  if (removedCount > 0) {
    data.count = Math.max(0, data.count - removedCount);
  }
}

function getVisitorId(): string {
  if (typeof window === 'undefined') return 'unknown';

  // Try to get existing visitor ID
  let visitorId = sessionStorage.getItem('anzx_visitor_id');

  if (!visitorId) {
    // Generate new visitor ID
    visitorId = `visitor_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    sessionStorage.setItem('anzx_visitor_id', visitorId);
  }

  return visitorId;
}

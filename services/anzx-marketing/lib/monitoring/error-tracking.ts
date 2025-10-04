// Error tracking and logging

export interface ErrorContext {
  severity?: 'low' | 'medium' | 'high' | 'critical';
  componentStack?: string;
  errorInfo?: any;
  tags?: Record<string, string>;
  user?: {
    id?: string;
    email?: string;
  };
}

export function initializeErrorTracking() {
  if (typeof window === 'undefined') return;
  
  // Initialize error tracking service (Sentry, etc.)
  // Example: Sentry.init({ dsn: process.env.NEXT_PUBLIC_SENTRY_DSN });
  
  // Set up global error handlers
  window.addEventListener('error', (event) => {
    logError(new Error(event.message), {
      severity: 'high',
      tags: { type: 'uncaught_error' },
    });
  });
  
  window.addEventListener('unhandledrejection', (event) => {
    logError(new Error(event.reason), {
      severity: 'high',
      tags: { type: 'unhandled_rejection' },
    });
  });
}

export function logError(error: Error, context?: ErrorContext) {
  // Log to console in development
  if (process.env.NODE_ENV === 'development') {
    console.error('Error:', error);
    console.error('Context:', context);
  }

  // In production, you would send to error tracking service (Sentry, etc.)
  if (typeof window !== 'undefined' && process.env.NODE_ENV === 'production') {
    // Send to error tracking service
    // Example: Sentry.captureException(error, { contexts: context });
  }
}

export function logWarning(message: string, context?: Record<string, any>) {
  if (process.env.NODE_ENV === 'development') {
    console.warn('Warning:', message, context);
  }
}

export function logInfo(message: string, context?: Record<string, any>) {
  if (process.env.NODE_ENV === 'development') {
    console.log('Info:', message, context);
  }
}

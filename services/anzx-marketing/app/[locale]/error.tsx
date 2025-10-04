'use client';

import { useEffect } from 'react';
import { logError } from '@/lib/monitoring/error-tracking';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Log error to monitoring services
    logError(error, {
      severity: 'high',
      tags: {
        type: 'nextjs_error_page',
        digest: error.digest || 'unknown',
      },
    });
  }, [error]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <div className="max-w-lg w-full text-center">
        <div className="mb-8">
          <div className="text-8xl mb-4">😕</div>
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Oops! Something went wrong
          </h1>
          <p className="text-lg text-gray-600">
            We encountered an unexpected error. Our team has been notified and is working on a fix.
          </p>
        </div>

        <div className="space-y-4">
          <button
            onClick={reset}
            className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
          >
            Try Again
          </button>

          <button
            onClick={() => (window.location.href = '/')}
            className="w-full px-6 py-3 bg-gray-200 text-gray-900 rounded-lg font-medium hover:bg-gray-300 transition-colors"
          >
            Go to Homepage
          </button>
        </div>

        {process.env.NODE_ENV === 'development' && (
          <div className="mt-8 p-4 bg-red-50 border border-red-200 rounded-lg text-left">
            <h3 className="font-bold text-red-900 mb-2">Error Details (Development Only)</h3>
            <pre className="text-xs text-red-800 overflow-auto">
              {error.message}
              {error.stack && `\n\n${error.stack}`}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}

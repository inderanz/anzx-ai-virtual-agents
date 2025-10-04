import Link from 'next/link';

export default function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <div className="max-w-lg w-full text-center">
        <div className="mb-8">
          <div className="text-8xl mb-4">🔍</div>
          <h1 className="text-6xl font-bold text-gray-900 mb-2">404</h1>
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Page Not Found
          </h2>
          <p className="text-lg text-gray-600">
            Sorry, we couldn't find the page you're looking for. It might have been moved or deleted.
          </p>
        </div>

        <div className="space-y-4">
          <Link
            href="/"
            className="inline-block w-full px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
          >
            Go to Homepage
          </Link>

          <Link
            href="/help"
            className="inline-block w-full px-6 py-3 bg-gray-200 text-gray-900 rounded-lg font-medium hover:bg-gray-300 transition-colors"
          >
            Visit Help Center
          </Link>
        </div>

        <div className="mt-12 grid grid-cols-2 gap-4 text-left">
          <div>
            <h3 className="font-bold text-gray-900 mb-2">Popular Pages</h3>
            <ul className="space-y-1 text-sm text-gray-600">
              <li>
                <Link href="/ai-interviewer" className="hover:text-blue-600">
                  AI Interviewer
                </Link>
              </li>
              <li>
                <Link href="/customer-service-ai" className="hover:text-blue-600">
                  Customer Service AI
                </Link>
              </li>
              <li>
                <Link href="/ai-sales-agent" className="hover:text-blue-600">
                  AI Sales Agent
                </Link>
              </li>
            </ul>
          </div>

          <div>
            <h3 className="font-bold text-gray-900 mb-2">Resources</h3>
            <ul className="space-y-1 text-sm text-gray-600">
              <li>
                <Link href="/blog" className="hover:text-blue-600">
                  Blog
                </Link>
              </li>
              <li>
                <Link href="/integrations" className="hover:text-blue-600">
                  Integrations
                </Link>
              </li>
              <li>
                <Link href="/help" className="hover:text-blue-600">
                  Help Center
                </Link>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

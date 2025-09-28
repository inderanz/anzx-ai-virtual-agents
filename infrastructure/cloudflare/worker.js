/**
 * Cloudflare Worker for Cricket Agent Proxy
 * Proxies /api/cricket/* requests to cricket-agent Cloud Run service
 */

// CORS configuration
const CORS_HEADERS = {
  'Access-Control-Allow-Origin': 'https://anzx.ai',
  'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With',
  'Access-Control-Max-Age': '86400',
};

/**
 * Handle CORS preflight requests
 */
function handleCorsPreflight() {
  return new Response(null, {
    status: 204,
    headers: CORS_HEADERS,
  });
}

/**
 * Add CORS headers to response
 */
function addCorsHeaders(response) {
  const headers = new Headers(response.headers);
  Object.entries(CORS_HEADERS).forEach(([key, value]) => {
    headers.set(key, value);
  });
  return new Response(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers: headers,
  });
}

/**
 * Map /api/cricket/* path to cricket-agent path
 */
function mapPath(pathname) {
  if (pathname.startsWith('/api/cricket')) {
    return pathname.replace('/api/cricket', '');
  }
  return pathname;
}

/**
 * Main request handler
 */
export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const pathname = url.pathname;
    
    // Handle CORS preflight for /api/cricket/* routes
    if (request.method === 'OPTIONS' && pathname.startsWith('/api/cricket')) {
      return handleCorsPreflight();
    }
    
    // Proxy /api/cricket/* requests to cricket-agent
    if (pathname.startsWith('/api/cricket')) {
      try {
        // Map path by removing /api/cricket prefix
        const mappedPath = mapPath(pathname);
        const targetUrl = `${env.CRICKET_AGENT_URL}${mappedPath}${url.search}`;
        
        // Create new request with same method, headers, and body
        const proxyRequest = new Request(targetUrl, {
          method: request.method,
          headers: request.headers,
          body: request.body,
        });
        
        // Forward request to cricket-agent
        const response = await fetch(proxyRequest);
        
        // Add CORS headers to response
        return addCorsHeaders(response);
        
      } catch (error) {
        console.error('Proxy error:', error);
        return new Response(JSON.stringify({ 
          error: 'Proxy error', 
          message: error.message 
        }), {
          status: 502,
          headers: {
            'Content-Type': 'application/json',
            ...CORS_HEADERS,
          },
        });
      }
    }
    
    // For all other requests, pass through
    return fetch(request);
  },
};

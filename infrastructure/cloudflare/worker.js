/**
 * Cloudflare Worker for Cricket Agent Proxy and Chatbot
 * Proxies /api/cricket/* requests to cricket-agent Cloud Run service
 * Serves cricket chatbot at /cricket route
 */

// CORS configuration
const CORS_HEADERS = {
  'Access-Control-Allow-Origin': '*',
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
    
    // Handle trailing slash redirects for /cricket routes
    if (pathname === '/cricket/chat' && !pathname.endsWith('/')) {
      return Response.redirect(`${url.origin}/cricket/chat/`, 301);
    }
    
    // Serve cricket chatbot at /cricket route only
    if (pathname === '/cricket' || pathname.startsWith('/cricket/')) {
      try {
        // Redirect to Cloudflare Pages deployment
        const chatbotUrl = env.CRICKET_CHATBOT_URL || 'https://6ded74f7.anzx-cricket.pages.dev';
        let targetPath;
        
        if (pathname === '/cricket') {
          targetPath = '/';
        } else if (pathname.startsWith('/cricket/')) {
          targetPath = pathname.replace('/cricket', '');
        }
        
        const targetUrl = `${chatbotUrl}${targetPath}${url.search}`;
        
        console.log('Proxying cricket to:', targetUrl);
        
        // Fetch from Cloudflare Pages with proper headers
        const response = await fetch(targetUrl, {
          method: request.method,
          headers: {
            'User-Agent': request.headers.get('User-Agent') || 'Cloudflare-Worker',
            'Accept': request.headers.get('Accept') || '*/*',
            'Accept-Language': request.headers.get('Accept-Language') || 'en-US,en;q=0.9',
            'Accept-Encoding': request.headers.get('Accept-Encoding') || 'gzip, deflate, br',
            'Cache-Control': 'no-cache',
          },
        });
        
        console.log('Response status:', response.status);
        console.log('Response headers:', Object.fromEntries(response.headers.entries()));
        
        // Create new response with proper headers
        const newResponse = new Response(response.body, {
          status: response.status,
          statusText: response.statusText,
          headers: {
            ...Object.fromEntries(response.headers.entries()),
            ...CORS_HEADERS,
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0',
          },
        });
        
        return newResponse;
        
      } catch (error) {
        console.error('Chatbot proxy error:', error);
        return new Response(JSON.stringify({ 
          error: 'Chatbot proxy error', 
          message: error.message,
          targetUrl: targetUrl 
        }), {
          status: 502,
          headers: {
            'Content-Type': 'application/json',
            ...CORS_HEADERS,
          },
        });
      }
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

/**
 * Cloudflare Worker - Complete Proxy for anzx.ai
 * 
 * Routes:
 * - /cricket* → anzx-cricket Pages (d1e8b1c8.anzx-cricket.pages.dev)
 * - /api/cricket* → cricket-agent Cloud Run
 * - /* (everything else) → anzx-marketing Pages (e7218b3a.anzx-marketing.pages.dev)
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
 * Proxy request to target URL, preserving path and query
 */
async function proxyToPages(request, targetBaseUrl, pathPrefix = '') {
  const url = new URL(request.url);
  let targetPath = url.pathname;
  
  // Remove prefix if specified
  if (pathPrefix && targetPath.startsWith(pathPrefix)) {
    targetPath = targetPath.substring(pathPrefix.length) || '/';
  }
  
  const targetUrl = `${targetBaseUrl}${targetPath}${url.search}`;
  
  console.log(`Proxying: ${url.pathname} → ${targetUrl}`);
  
  try {
    // Create new request with original headers
    const proxyRequest = new Request(targetUrl, {
      method: request.method,
      headers: request.headers,
      body: request.body,
      redirect: 'manual', // Handle redirects manually
    });
    
    const response = await fetch(proxyRequest);
    
    // If it's a redirect, rewrite the Location header to use our domain
    if (response.status >= 300 && response.status < 400) {
      const location = response.headers.get('Location');
      if (location) {
        const newHeaders = new Headers(response.headers);
        // Rewrite Pages URL to our domain
        const rewrittenLocation = location
          .replace(targetBaseUrl, url.origin)
          .replace(/^\//, url.origin + '/');
        newHeaders.set('Location', rewrittenLocation);
        
        return new Response(response.body, {
          status: response.status,
          statusText: response.statusText,
          headers: newHeaders,
        });
      }
    }
    
    return response;
    
  } catch (error) {
    console.error('Proxy error:', error);
    return new Response(JSON.stringify({ 
      error: 'Proxy error', 
      message: error.message,
      targetUrl: targetUrl 
    }), {
      status: 502,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }
}

/**
 * Main request handler
 */
export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const pathname = url.pathname;
    
    // Handle CORS preflight
    if (request.method === 'OPTIONS') {
      return handleCorsPreflight();
    }
    
    // Route 1: /api/cricket/* → Cricket Agent Cloud Run
    if (pathname.startsWith('/api/cricket')) {
      try {
        const mappedPath = pathname.replace('/api/cricket', '');
        const targetUrl = `${env.CRICKET_AGENT_URL}${mappedPath}${url.search}`;
        
        const proxyRequest = new Request(targetUrl, {
          method: request.method,
          headers: request.headers,
          body: request.body,
        });
        
        const response = await fetch(proxyRequest);
        return addCorsHeaders(response);
        
      } catch (error) {
        console.error('Cricket API proxy error:', error);
        return new Response(JSON.stringify({ 
          error: 'Cricket API proxy error', 
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
    
    // Route 2: /cricket* → Cricket Chatbot Pages
    if (pathname === '/cricket' || pathname.startsWith('/cricket/')) {
      const chatbotUrl = env.CRICKET_CHATBOT_URL || 'https://d1e8b1c8.anzx-cricket.pages.dev';
      return proxyToPages(request, chatbotUrl, '/cricket');
    }
    
    // Route 3: /* (everything else) → Marketing Site Pages
    const marketingUrl = env.MARKETING_SITE_URL || 'https://fadf9881.anzx-marketing.pages.dev';
    return proxyToPages(request, marketingUrl);
  },
};

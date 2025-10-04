import createMiddleware from 'next-intl/middleware';
import { routing } from './routing';

// Middleware is disabled for static export
// For static export, locale routing is handled by the file structure
export default createMiddleware(routing);

export const config = {
  // Disable middleware for static export by matching nothing
  matcher: [],
};

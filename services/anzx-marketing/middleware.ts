import createMiddleware from 'next-intl/middleware';

export default createMiddleware({
  // A list of all locales that are supported
  locales: ['en', 'hi'],

  // Used when no locale matches
  defaultLocale: 'en',

  // Prefix for locale in URL (e.g., /hi/about)
  localePrefix: 'as-needed',
});

export const config = {
  // Match only internationalized pathnames
  matcher: ['/', '/(hi|en)/:path*', '/((?!api|_next|_vercel|.*\\..*).*)'],
};

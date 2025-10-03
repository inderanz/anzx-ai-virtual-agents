"use client";

import { useLocale } from 'next-intl';
import { usePathname } from 'next/navigation';
import Link from 'next/link';
import { Globe } from 'lucide-react';

export function LanguageSwitcherLink() {
  const locale = useLocale();
  const pathname = usePathname();

  // Get path without locale
  const getPathWithoutLocale = () => {
    const segments = pathname.split('/').filter(Boolean);
    const firstSegment = segments[0];
    
    if (firstSegment === 'en' || firstSegment === 'hi') {
      return '/' + segments.slice(1).join('/');
    }
    return pathname;
  };

  const pathWithoutLocale = getPathWithoutLocale();
  const otherLocale = locale === 'en' ? 'hi' : 'en';
  const otherLocalePath = otherLocale === 'en' 
    ? pathWithoutLocale || '/'
    : `/${otherLocale}${pathWithoutLocale || '/'}`;

  return (
    <div className="flex items-center gap-2">
      <Globe className="w-4 h-4 text-gray-600" />
      <Link
        href={otherLocalePath}
        className="px-3 py-1 text-sm border border-gray-300 rounded hover:border-anzx-blue hover:text-anzx-blue transition-colors"
      >
        {locale === 'en' ? 'हिंदी' : 'English'}
      </Link>
    </div>
  );
}

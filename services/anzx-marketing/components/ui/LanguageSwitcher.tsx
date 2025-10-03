"use client";

import { useLocale } from 'next-intl';
import { usePathname, useRouter } from 'next/navigation';
import { Globe } from 'lucide-react';
import { useTransition } from 'react';

export function LanguageSwitcher() {
  const locale = useLocale();
  const router = useRouter();
  const pathname = usePathname();
  const [isPending, startTransition] = useTransition();

  const switchLanguage = (newLocale: string) => {
    if (newLocale === locale) return;

    startTransition(() => {
      // Get the current path without locale prefix
      const segments = pathname.split('/').filter(Boolean);
      const currentLocale = segments[0];
      
      // Remove locale from path if it exists
      let pathWithoutLocale = pathname;
      if (currentLocale === 'en' || currentLocale === 'hi') {
        pathWithoutLocale = '/' + segments.slice(1).join('/');
      }
      
      // Build new path with new locale
      const newPath = newLocale === 'en' 
        ? pathWithoutLocale || '/'
        : `/${newLocale}${pathWithoutLocale || '/'}`;
      
      // Navigate to new path
      router.push(newPath);
      router.refresh();
    });
  };

  return (
    <div className="flex items-center gap-2">
      <Globe className="w-4 h-4 text-gray-600" />
      <select
        value={locale}
        onChange={(e) => switchLanguage(e.target.value)}
        disabled={isPending}
        className="bg-transparent border border-gray-300 rounded px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-anzx-blue disabled:opacity-50 cursor-pointer"
        aria-label="Select language"
      >
        <option value="en">English</option>
        <option value="hi">हिंदी</option>
      </select>
    </div>
  );
}

'use client';

import dynamic from 'next/dynamic';
import { useState, useEffect } from 'react';
import { Globe } from 'lucide-react';

const LanguageSwitcher = dynamic(
  () => import('./LanguageSwitcher').then(mod => ({ default: mod.LanguageSwitcher })),
  { 
    ssr: false,
    loading: () => (
      <div className="flex items-center gap-2">
        <Globe className="w-4 h-4 text-gray-600" />
        <div className="bg-transparent border border-gray-300 rounded px-2 py-1 text-sm w-20 h-8 animate-pulse bg-gray-200"></div>
      </div>
    )
  }
);

export default function ClientOnlyLanguageSwitcher() {
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  if (!isMounted) {
    return (
      <div className="flex items-center gap-2">
        <Globe className="w-4 h-4 text-gray-600" />
        <div className="bg-transparent border border-gray-300 rounded px-2 py-1 text-sm w-20 h-8 bg-gray-100"></div>
      </div>
    );
  }

  return <LanguageSwitcher />;
}
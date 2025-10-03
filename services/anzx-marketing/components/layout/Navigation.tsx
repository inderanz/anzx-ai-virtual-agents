"use client";

import { useState } from 'react';
import Link from 'next/link';
import { useTranslations } from 'next-intl';
import { ChevronDown } from 'lucide-react';

export function Navigation() {
  const t = useTranslations('nav');
  const [openDropdown, setOpenDropdown] = useState<string | null>(null);

  const products = [
    { name: t('aiInterviewer'), href: '/ai-interviewer' },
    { name: t('customerServiceAI'), href: '/customer-service-ai' },
    { name: t('aiSalesAgent'), href: '/ai-sales-agent' },
  ];

  return (
    <nav className="flex items-center space-x-6">
      {/* Products Dropdown */}
      <div
        className="relative"
        onMouseEnter={() => setOpenDropdown('products')}
        onMouseLeave={() => setOpenDropdown(null)}
      >
        <button className="flex items-center space-x-1 text-gray-700 hover:text-anzx-blue transition-colors">
          <span>{t('products')}</span>
          <ChevronDown size={16} />
        </button>
        {openDropdown === 'products' && (
          <div className="absolute top-full left-0 mt-2 w-64 bg-white rounded-lg shadow-lg py-2">
            {products.map((product) => (
              <Link
                key={product.href}
                href={product.href}
                className="block px-4 py-2 text-gray-700 hover:bg-gray-50 hover:text-anzx-blue transition-colors"
              >
                {product.name}
              </Link>
            ))}
          </div>
        )}
      </div>

      <Link
        href="/integrations"
        className="text-gray-700 hover:text-anzx-blue transition-colors"
      >
        {t('integrations')}
      </Link>

      <Link href="/blog" className="text-gray-700 hover:text-anzx-blue transition-colors">
        {t('blog')}
      </Link>

      <Link href="/vision" className="text-gray-700 hover:text-anzx-blue transition-colors">
        {t('vision')}
      </Link>

      <Link href="/help" className="text-gray-700 hover:text-anzx-blue transition-colors">
        {t('help')}
      </Link>
    </nav>
  );
}

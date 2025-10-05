"use client";

import { useState } from 'react';
import Link from 'next/link';
import { useTranslations } from 'next-intl';
import { usePathname, useRouter } from 'next/navigation';
import { ChevronDown } from 'lucide-react';

export function Navigation() {
  const t = useTranslations('nav');
  const pathname = usePathname();
  const router = useRouter();
  const [openDropdown, setOpenDropdown] = useState<string | null>(null);

  const products = [
    { name: 'Emma - AI Recruiting Agent', href: '/ai-recruiting-agent' },
    { name: 'Olivia - Customer Service AI', href: '/customer-service-ai' },
    { name: 'Jack - AI Sales Agent', href: '/ai-sales-agent-jack' },
    { name: 'Liam - AI Support Agent', href: '/ai-interviewer' },
    { name: 'Inder - Google Cloud Agent', href: '/google-cloud-agent' },
    { name: 'Alex - DevOps & GitOps Agent', href: '/devops-gitops-agent' },
    { name: 'Ashish - SRE Agent', href: '/sre-agent' },
  ];

  const handleProductClick = (e: React.MouseEvent, href: string) => {
    e.preventDefault();
    setOpenDropdown(null);
    
    // Check if we're on the homepage
    const isHomepage = pathname === '/' || pathname === '/en' || pathname === '/hi';
    
    if (isHomepage) {
      // Scroll to agent cards on homepage
      const element = document.getElementById('agent-cards');
      if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    } else {
      // Navigate to the specific agent page
      router.push(href);
    }
  };

  return (
    <nav className="flex items-center space-x-6">
      {/* Products Dropdown */}
      <div
        className="relative"
        onMouseEnter={() => setOpenDropdown('products')}
        onMouseLeave={() => setOpenDropdown(null)}
      >
        <button className="flex items-center space-x-1 text-white font-bold hover:text-blue-200 transition-colors">
          <span>{t('products')}</span>
          <ChevronDown size={16} />
        </button>
        {openDropdown === 'products' && (
          <div className="absolute top-full left-0 mt-2 w-64 bg-white rounded-lg shadow-lg py-2 z-50">
            {products.map((product) => (
              <a
                key={product.href}
                href={product.href}
                onClick={(e) => handleProductClick(e, product.href)}
                className="block px-4 py-2 text-gray-700 hover:bg-gray-50 hover:text-blue-600 transition-colors font-semibold cursor-pointer"
              >
                {product.name}
              </a>
            ))}
          </div>
        )}
      </div>

      <Link
        href="/integrations"
        className="text-white font-bold hover:text-blue-200 transition-colors"
      >
        {t('integrations')}
      </Link>

      <Link href="/blog" className="text-white font-bold hover:text-blue-200 transition-colors">
        {t('blog')}
      </Link>

      <Link href="/vision" className="text-white font-bold hover:text-blue-200 transition-colors">
        {t('vision')}
      </Link>

      <Link href="/help" className="text-white font-bold hover:text-blue-200 transition-colors">
        {t('help')}
      </Link>
    </nav>
  );
}

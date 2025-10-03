"use client";

import Link from 'next/link';
import { useTranslations } from 'next-intl';
import { LanguageSwitcher } from '../ui/LanguageSwitcher';

interface MobileMenuProps {
  isOpen: boolean;
  onClose: () => void;
}

export function MobileMenu({ isOpen, onClose }: MobileMenuProps) {
  const t = useTranslations('nav');

  if (!isOpen) return null;

  return (
    <div className="md:hidden bg-white border-t border-gray-200">
      <div className="px-4 py-6 space-y-4">
        <div className="space-y-2">
          <div className="text-sm font-semibold text-gray-500 uppercase">{t('products')}</div>
          <Link
            href="/ai-interviewer"
            className="block py-2 text-gray-700 hover:text-anzx-blue"
            onClick={onClose}
          >
            {t('aiInterviewer')}
          </Link>
          <Link
            href="/customer-service-ai"
            className="block py-2 text-gray-700 hover:text-anzx-blue"
            onClick={onClose}
          >
            {t('customerServiceAI')}
          </Link>
          <Link
            href="/ai-sales-agent"
            className="block py-2 text-gray-700 hover:text-anzx-blue"
            onClick={onClose}
          >
            {t('aiSalesAgent')}
          </Link>
        </div>

        <div className="border-t border-gray-200 pt-4 space-y-2">
          <Link
            href="/integrations"
            className="block py-2 text-gray-700 hover:text-anzx-blue"
            onClick={onClose}
          >
            {t('integrations')}
          </Link>
          <Link
            href="/blog"
            className="block py-2 text-gray-700 hover:text-anzx-blue"
            onClick={onClose}
          >
            {t('blog')}
          </Link>
          <Link
            href="/vision"
            className="block py-2 text-gray-700 hover:text-anzx-blue"
            onClick={onClose}
          >
            {t('vision')}
          </Link>
          <Link
            href="/help"
            className="block py-2 text-gray-700 hover:text-anzx-blue"
            onClick={onClose}
          >
            {t('help')}
          </Link>
        </div>

        <div className="border-t border-gray-200 pt-4 space-y-3">
          <LanguageSwitcher />
          <Link
            href="/login"
            className="block py-2 text-gray-700 hover:text-anzx-blue"
            onClick={onClose}
          >
            {t('login')}
          </Link>
          <Link
            href="/get-started"
            className="block w-full bg-anzx-blue text-white text-center px-4 py-2 rounded-lg hover:bg-anzx-blue-dark"
            onClick={onClose}
          >
            {t('getStarted')}
          </Link>
        </div>
      </div>
    </div>
  );
}

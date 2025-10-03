"use client";

import Link from 'next/link';
import { useTranslations } from 'next-intl';
import { useState } from 'react';

export function Footer() {
  const t = useTranslations('footer');
  const [email, setEmail] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [message, setMessage] = useState('');

  const handleNewsletterSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setMessage('');

    try {
      // TODO: Integrate with API
      await new Promise((resolve) => setTimeout(resolve, 1000));
      setMessage('Thank you for subscribing!');
      setEmail('');
    } catch (error) {
      setMessage('Something went wrong. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <footer className="bg-gray-900 text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Company */}
          <div>
            <h3 className="text-lg font-semibold mb-4">{t('company')}</h3>
            <ul className="space-y-2">
              <li>
                <Link href="/vision" className="text-gray-400 hover:text-white transition-colors">
                  {t('links.vision')}
                </Link>
              </li>
              <li>
                <Link href="/press" className="text-gray-400 hover:text-white transition-colors">
                  {t('links.press')}
                </Link>
              </li>
              <li>
                <Link href="/careers" className="text-gray-400 hover:text-white transition-colors">
                  {t('links.careers')}
                </Link>
              </li>
              <li>
                <Link href="/contact" className="text-gray-400 hover:text-white transition-colors">
                  {t('links.contact')}
                </Link>
              </li>
            </ul>
          </div>

          {/* Products */}
          <div>
            <h3 className="text-lg font-semibold mb-4">{t('products')}</h3>
            <ul className="space-y-2">
              <li>
                <Link
                  href="/ai-interviewer"
                  className="text-gray-400 hover:text-white transition-colors"
                >
                  AI Interviewer
                </Link>
              </li>
              <li>
                <Link
                  href="/customer-service-ai"
                  className="text-gray-400 hover:text-white transition-colors"
                >
                  Customer Service AI
                </Link>
              </li>
              <li>
                <Link
                  href="/ai-sales-agent"
                  className="text-gray-400 hover:text-white transition-colors"
                >
                  AI Sales Agent
                </Link>
              </li>
              <li>
                <Link
                  href="/integrations"
                  className="text-gray-400 hover:text-white transition-colors"
                >
                  Integrations
                </Link>
              </li>
            </ul>
          </div>

          {/* Resources */}
          <div>
            <h3 className="text-lg font-semibold mb-4">{t('resources')}</h3>
            <ul className="space-y-2">
              <li>
                <Link href="/blog" className="text-gray-400 hover:text-white transition-colors">
                  {t('links.blog')}
                </Link>
              </li>
              <li>
                <Link href="/help" className="text-gray-400 hover:text-white transition-colors">
                  {t('links.help')}
                </Link>
              </li>
              <li>
                <Link
                  href="/documentation"
                  className="text-gray-400 hover:text-white transition-colors"
                >
                  {t('links.documentation')}
                </Link>
              </li>
              <li>
                <Link
                  href="/api-reference"
                  className="text-gray-400 hover:text-white transition-colors"
                >
                  {t('links.apiReference')}
                </Link>
              </li>
            </ul>
          </div>

          {/* Newsletter */}
          <div>
            <h3 className="text-lg font-semibold mb-4">{t('newsletter.title')}</h3>
            <p className="text-gray-400 text-sm mb-4">{t('newsletter.description')}</p>
            <form onSubmit={handleNewsletterSubmit} className="space-y-2">
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder={t('newsletter.placeholder')}
                className="w-full px-4 py-2 rounded-lg bg-gray-800 text-white border border-gray-700 focus:outline-none focus:ring-2 focus:ring-anzx-blue"
                required
              />
              <button
                type="submit"
                disabled={isSubmitting}
                className="w-full bg-anzx-blue text-white px-4 py-2 rounded-lg hover:bg-anzx-blue-dark transition-colors disabled:opacity-50"
              >
                {isSubmitting ? 'Subscribing...' : t('newsletter.subscribe')}
              </button>
              {message && <p className="text-sm text-gray-400">{message}</p>}
            </form>
          </div>
        </div>

        {/* Bottom */}
        <div className="border-t border-gray-800 mt-12 pt-8">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <p className="text-gray-400 text-sm">{t('copyright')}</p>
            <div className="flex space-x-6 mt-4 md:mt-0">
              <Link
                href="/legal/privacy-policy"
                className="text-gray-400 hover:text-white text-sm transition-colors"
              >
                {t('links.privacyPolicy')}
              </Link>
              <Link
                href="/legal/terms"
                className="text-gray-400 hover:text-white text-sm transition-colors"
              >
                {t('links.termsOfService')}
              </Link>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}

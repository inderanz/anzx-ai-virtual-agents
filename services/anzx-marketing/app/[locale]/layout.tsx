import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import { NextIntlClientProvider } from 'next-intl';
import { notFound } from 'next/navigation';
import { Analytics } from '@/components/analytics/Analytics';
import { Clarity } from '@/components/analytics/Clarity';
import { ScrollTracker } from '@/components/analytics/ScrollTracker';
import { ConversionTracker } from '@/components/analytics/ConversionTracker';
import { ErrorMonitoring } from '@/components/monitoring/ErrorMonitoring';
import '../globals.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL || 'https://anzx.ai'),
  title: {
    template: '%s | ANZX.ai',
    default: 'AI Agents for Business | ANZX.ai',
  },
  description:
    'Enterprise-grade AI agents for customer service, sales, and recruiting. Trusted by businesses across Australia, New Zealand, India, and Singapore.',
};

export default async function LocaleLayout({
  children,
  params: { locale },
}: {
  children: React.ReactNode;
  params: { locale: string };
}) {
  let messages;
  try {
    messages = (await import(`../../messages/${locale}.json`)).default;
  } catch (error) {
    notFound();
  }

  return (
    <html lang={locale} className={locale === 'hi' ? 'font-hindi' : ''}>
      <body className={inter.className}>
        <a href="#main-content" className="skip-to-content">
          Skip to main content
        </a>
        <NextIntlClientProvider locale={locale} messages={messages}>
          <Analytics />
          <Clarity />
          <ScrollTracker />
          <ConversionTracker />
          <ErrorMonitoring />
          {children}
        </NextIntlClientProvider>
      </body>
    </html>
  );
}

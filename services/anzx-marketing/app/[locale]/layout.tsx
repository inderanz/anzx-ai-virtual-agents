import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import { NextIntlClientProvider } from 'next-intl';
import { notFound } from 'next/navigation';
import '../globals.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
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
      <head>
        <link rel="icon" href="/favicon.ico" sizes="any" />
        <meta name="theme-color" content="#0066CC" />
        {locale === 'hi' && (
          <link
            rel="preload"
            href="https://fonts.googleapis.com/css2?family=Noto+Sans+Devanagari:wght@400;500;600;700&display=swap"
            as="style"
          />
        )}
      </head>
      <body className={inter.className}>
        <a href="#main-content" className="skip-to-content">
          Skip to main content
        </a>
        <NextIntlClientProvider locale={locale} messages={messages}>
          {children}
        </NextIntlClientProvider>
      </body>
    </html>
  );
}

import { Metadata } from 'next';
import { HomeHero } from '@/components/home/HomeHero';
import { LogoCarousel } from '@/components/home/LogoCarousel';
import { FeatureGrid } from '@/components/home/FeatureGrid';
import { Header } from '@/components/layout/Header';
import { Footer } from '@/components/layout/Footer';
import { ConsentBanner } from '@/components/ui/ConsentBanner';

export const metadata: Metadata = {
  title: 'AI Agents for Business | ANZX.ai',
  description:
    'Enterprise-grade AI agents for customer service, sales, and recruiting. Trusted by businesses across Australia, New Zealand, India, and Singapore.',
  keywords: [
    'AI agents',
    'artificial intelligence',
    'customer service AI',
    'sales automation',
    'recruiting automation',
    'business automation',
    'enterprise AI',
  ],
  openGraph: {
    title: 'AI Agents for Business | ANZX.ai',
    description:
      'Enterprise-grade AI agents for customer service, sales, and recruiting.',
    url: 'https://anzx.ai',
    siteName: 'ANZX.ai',
    images: [
      {
        url: '/images/og-image.jpg',
        width: 1200,
        height: 630,
        alt: 'ANZX.ai - AI Agents for Business',
      },
    ],
    locale: 'en_AU',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'AI Agents for Business | ANZX.ai',
    description:
      'Enterprise-grade AI agents for customer service, sales, and recruiting.',
    images: ['/images/twitter-card.jpg'],
    creator: '@anzxai',
  },
  alternates: {
    canonical: 'https://anzx.ai',
    languages: {
      en: 'https://anzx.ai',
      hi: 'https://anzx.ai/hi',
    },
  },
};

export default function HomePage() {
  return (
    <>
      <Header />
      <main id="main-content">
        <HomeHero />
        <LogoCarousel />
        <FeatureGrid />
      </main>
      <Footer />
      <ConsentBanner />

      {/* Structured Data */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            '@context': 'https://schema.org',
            '@type': 'Organization',
            name: 'ANZX.ai',
            url: 'https://anzx.ai',
            logo: 'https://anzx.ai/images/logo.png',
            description: 'Enterprise-grade AI agents for Asia-Pacific businesses',
            address: {
              '@type': 'PostalAddress',
              addressCountry: 'AU',
            },
            sameAs: [
              'https://twitter.com/anzxai',
              'https://linkedin.com/company/anzx-ai',
            ],
          }),
        }}
      />
    </>
  );
}

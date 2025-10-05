import { Metadata } from 'next';
import { notFound } from 'next/navigation';
import { Header } from '@/components/layout/Header';
import { Footer } from '@/components/layout/Footer';
import { ProductHero } from '@/components/product/ProductHero';
import { getAgentById } from '@/lib/constants/agents';
import { routing } from '@/routing';

export function generateStaticParams() {
  return routing.locales.map((locale) => ({ locale }));
}

export const metadata: Metadata = {
  title: 'Jack - AI Sales Agent | ANZX.ai',
  description:
    'Meet Jack, your AI sales agent that qualifies leads and makes sales calls automatically to fill your pipeline.',
  keywords: [
    'AI sales agent',
    'lead qualification',
    'outbound calling',
    'sales automation',
    'CRM integration',
    'SDR automation',
  ],
};

export default function AISalesAgentPage() {
  const agent = getAgentById('jack');

  if (!agent) {
    notFound();
  }

  return (
    <>
      <Header />
      <main id="main-content">
        <ProductHero agent={agent} />
      </main>
      <Footer />
    </>
  );
}

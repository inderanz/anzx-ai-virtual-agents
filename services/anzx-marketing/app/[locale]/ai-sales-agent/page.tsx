import { Metadata } from 'next';
import { notFound } from 'next/navigation';
import { Header } from '@/components/layout/Header';
import { Footer } from '@/components/layout/Footer';
import { ProductHero } from '@/components/product/ProductHero';
import { getAgentById } from '@/lib/constants/agents';

export const metadata: Metadata = {
  title: 'Jack - AI Sales Agent | ANZX.ai',
  description:
    'Meet Jack, your AI sales agent that qualifies leads and makes sales calls automatically. Boost your pipeline with intelligent automation.',
  keywords: [
    'AI sales',
    'sales automation',
    'lead qualification',
    'outbound calling',
    'SDR automation',
    'sales intelligence',
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

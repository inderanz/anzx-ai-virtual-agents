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
  title: 'Ashish - SRE Agent | ANZX.ai',
  description:
    'Meet Ashish, your AI Site Reliability Engineer that monitors system health, manages incidents, and ensures your services meet SLOs 24/7.',
  keywords: [
    'site reliability engineering',
    'SRE automation',
    'incident management',
    'system monitoring',
    'SLO tracking',
    'reliability engineering',
  ],
};

export default function SREAgentPage() {
  const agent = getAgentById('ashish');

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

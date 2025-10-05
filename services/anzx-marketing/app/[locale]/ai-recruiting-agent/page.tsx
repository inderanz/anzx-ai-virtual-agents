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
  title: 'Emma - AI Recruiting Agent | ANZX.ai',
  description:
    'Meet Emma, your AI recruiting agent that screens candidates and schedules interviews automatically 24/7.',
  keywords: [
    'AI recruiting',
    'candidate screening',
    'interview scheduling',
    'recruitment automation',
    'ATS integration',
    'hiring automation',
  ],
};

export default function AIRecruitingAgentPage() {
  const agent = getAgentById('emma');

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

import { Metadata } from 'next';
import { notFound } from 'next/navigation';
import { Header } from '@/components/layout/Header';
import { Footer } from '@/components/layout/Footer';
import { ProductHero } from '@/components/product/ProductHero';
import { getAgentById } from '@/lib/constants/agents';

export const metadata: Metadata = {
  title: 'Emma - AI Recruiting Agent | ANZX.ai',
  description:
    'Meet Emma, your AI recruiting agent that screens candidates and schedules interviews automatically. Available 24/7 with ATS integration.',
  keywords: [
    'AI recruiting',
    'recruitment automation',
    'candidate screening',
    'interview scheduling',
    'ATS integration',
    'hiring automation',
  ],
};

export default function AIInterviewerPage() {
  const agent = getAgentById('emma');

  if (!agent) {
    notFound();
  }

  return (
    <>
      <Header />
      <main id="main-content">
        <ProductHero agent={agent} />
        {/* More sections will be added */}
      </main>
      <Footer />
    </>
  );
}

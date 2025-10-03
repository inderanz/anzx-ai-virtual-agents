import { Metadata } from 'next';
import { notFound } from 'next/navigation';
import { Header } from '@/components/layout/Header';
import { Footer } from '@/components/layout/Footer';
import { ProductHero } from '@/components/product/ProductHero';
import { getAgentById } from '@/lib/constants/agents';

export const metadata: Metadata = {
  title: 'Olivia - AI Customer Service Agent | ANZX.ai',
  description:
    'Meet Olivia, your AI customer service agent that handles inquiries 24/7 across phone, email, and chat in 50+ languages.',
  keywords: [
    'AI customer service',
    'customer support automation',
    'multi-channel support',
    'multilingual support',
    '24/7 support',
    'helpdesk automation',
  ],
};

export default function CustomerServiceAIPage() {
  const agent = getAgentById('olivia');

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

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
  title: 'Alex - DevOps & GitOps Agent | ANZX.ai',
  description:
    'Meet Alex, your AI DevOps engineer that automates CI/CD pipelines, manages GitOps workflows, and orchestrates Kubernetes deployments.',
  keywords: [
    'DevOps automation',
    'GitOps workflows',
    'CI/CD pipelines',
    'Kubernetes management',
    'deployment automation',
    'infrastructure as code',
  ],
};

export default function DevOpsGitOpsAgentPage() {
  const agent = getAgentById('alex');

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

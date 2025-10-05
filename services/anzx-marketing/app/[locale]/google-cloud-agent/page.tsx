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
    title: 'Inder - Google Cloud Agent | ANZX.ai',
    description:
        'Meet Inder, your AI Google Cloud specialist that manages infrastructure, optimizes costs, and automates cloud operations.',
    keywords: [
        'Google Cloud automation',
        'GCP management',
        'cloud cost optimization',
        'infrastructure automation',
        'cloud security',
        'GCP agent',
    ],
};

export default function GoogleCloudAgentPage() {
    const agent = getAgentById('inder');

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

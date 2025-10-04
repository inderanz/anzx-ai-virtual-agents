import { Metadata } from 'next';
import { getTranslations } from 'next-intl/server';
import EducationalHero from '@/components/educational/EducationalHero';
import TableOfContents from '@/components/educational/TableOfContents';
import DefinitionSection from '@/components/educational/DefinitionSection';
import HowItWorksSection from '@/components/educational/HowItWorksSection';
import TypesOfAgentsSection from '@/components/educational/TypesOfAgentsSection';
import BenefitsSection from '@/components/educational/BenefitsSection';
import UseCasesSection from '@/components/educational/UseCasesSection';
import ComparisonSection from '@/components/educational/ComparisonSection';
import GetStartedCTA from '@/components/educational/GetStartedCTA';

export function generateStaticParams() {
  return [{ locale: 'en' }, { locale: 'hi' }];
}

export async function generateMetadata(): Promise<Metadata> {
  const t = await getTranslations('educational.whatIsAiAgent');
  
  return {
    title: `${t('meta.title')} | ANZX.ai`,
    description: t('meta.description'),
    openGraph: {
      title: `${t('meta.title')} | ANZX.ai`,
      description: t('meta.description'),
      images: ['/images/og/what-is-ai-agent.jpg'],
    },
    alternates: {
      canonical: 'https://anzx.ai/what-is-an-ai-agent',
    },
  };
}

const tableOfContentsItems = [
  { id: 'definition', title: 'What is an AI Agent?' },
  { id: 'how-it-works', title: 'How AI Agents Work' },
  { id: 'types', title: 'Types of AI Agents' },
  { id: 'benefits', title: 'Key Benefits' },
  { id: 'use-cases', title: 'Real-World Use Cases' },
  { id: 'comparison', title: 'AI Agents vs Traditional Automation' },
  { id: 'get-started', title: 'Getting Started' },
];

export default async function WhatIsAiAgentPage() {
  return (
    <main className="min-h-screen">
      {/* Hero Section */}
      <EducationalHero
        title="What is an AI Agent?"
        subtitle="A comprehensive guide to understanding AI agents, how they work, and how they can transform your business operations."
        heroImage="/images/educational/ai-agent-concept.jpg"
        readingTime="8 min read"
      />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-12">
          {/* Table of Contents - Sticky Sidebar */}
          <div className="lg:col-span-1">
            <TableOfContents items={tableOfContentsItems} />
          </div>

          {/* Main Content */}
          <div className="lg:col-span-3 space-y-16">
            {/* Definition Section */}
            <DefinitionSection id="definition" />

            {/* How It Works Section */}
            <HowItWorksSection id="how-it-works" />

            {/* Types of Agents Section */}
            <TypesOfAgentsSection id="types" />

            {/* Benefits Section */}
            <BenefitsSection id="benefits" />

            {/* Use Cases Section */}
            <UseCasesSection id="use-cases" />

            {/* Comparison Section */}
            <ComparisonSection id="comparison" />

            {/* Get Started CTA */}
            <GetStartedCTA id="get-started" />
          </div>
        </div>
      </div>
    </main>
  );
}
import { Metadata } from 'next';
import { getTranslations } from 'next-intl/server';
import EducationalHero from '@/components/educational/EducationalHero';
import TableOfContents from '@/components/educational/TableOfContents';
import AgenticDefinitionSection from '@/components/educational/AgenticDefinitionSection';
import AgenticCapabilitiesSection from '@/components/educational/AgenticCapabilitiesSection';
import AgenticArchitectureSection from '@/components/educational/AgenticArchitectureSection';
import AgenticUseCasesSection from '@/components/educational/AgenticUseCasesSection';
import AgenticVsTraditionalSection from '@/components/educational/AgenticVsTraditionalSection';
import AgenticImplementationSection from '@/components/educational/AgenticImplementationSection';
import GetStartedCTA from '@/components/educational/GetStartedCTA';

export function generateStaticParams() {
  return [{ locale: 'en' }, { locale: 'hi' }];
}

export async function generateMetadata(): Promise<Metadata> {
  const t = await getTranslations('educational.agenticAi');
  
  return {
    title: `${t('meta.title')} | ANZX.ai`,
    description: t('meta.description'),
    openGraph: {
      title: `${t('meta.title')} | ANZX.ai`,
      description: t('meta.description'),
      images: ['/images/og/agentic-ai-guide.jpg'],
    },
    alternates: {
      canonical: 'https://anzx.ai/agentic-ai',
    },
  };
}

const tableOfContentsItems = [
  { id: 'definition', title: 'What is Agentic AI?' },
  { id: 'capabilities', title: 'Key Capabilities' },
  { id: 'architecture', title: 'How It Works' },
  { id: 'use-cases', title: 'Business Applications' },
  { id: 'comparison', title: 'Agentic AI vs Traditional AI' },
  { id: 'implementation', title: 'Implementation Guide' },
  { id: 'get-started', title: 'Getting Started' },
];

export default async function AgenticAiPage() {
  return (
    <main className="min-h-screen">
      {/* Hero Section */}
      <EducationalHero
        title="Agentic AI: The Future of Autonomous Intelligence"
        subtitle="Discover how agentic AI systems can act independently, make decisions, and achieve goals without constant human supervision."
        heroImage="/images/educational/agentic-ai-concept.jpg"
        readingTime="10 min read"
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
            <AgenticDefinitionSection id="definition" />

            {/* Capabilities Section */}
            <AgenticCapabilitiesSection id="capabilities" />

            {/* Architecture Section */}
            <AgenticArchitectureSection id="architecture" />

            {/* Use Cases Section */}
            <AgenticUseCasesSection id="use-cases" />

            {/* Comparison Section */}
            <AgenticVsTraditionalSection id="comparison" />

            {/* Implementation Section */}
            <AgenticImplementationSection id="implementation" />

            {/* Get Started CTA */}
            <GetStartedCTA id="get-started" />
          </div>
        </div>
      </div>
    </main>
  );
}
import { Metadata } from 'next';
import { getTranslations } from 'next-intl/server';
import ComparisonHero from '@/components/comparison/ComparisonHero';
import ComparisonTable from '@/components/comparison/ComparisonTable';
import ComparisonFeatures from '@/components/comparison/ComparisonFeatures';
import ComparisonUseCases from '@/components/comparison/ComparisonUseCases';
import ComparisonDecisionGuide from '@/components/comparison/ComparisonDecisionGuide';
import GetStartedCTA from '@/components/educational/GetStartedCTA';

export async function generateMetadata(): Promise<Metadata> {
  return {
    title: 'AI Agents vs RPA: Complete Comparison Guide | ANZX.ai',
    description: 'Compare AI agents and RPA automation. Learn the differences, benefits, and when to use each approach for your business automation needs.',
    openGraph: {
      title: 'AI Agents vs RPA: Complete Comparison Guide | ANZX.ai',
      description: 'Compare AI agents and RPA automation. Learn the differences, benefits, and when to use each approach for your business automation needs.',
      images: ['/images/og/ai-agents-vs-rpa.jpg'],
    },
    alternates: {
      canonical: 'https://anzx.ai/ai-agents-vs-rpa',
    },
  };
}

const comparisonData = {
  title: 'AI Agents vs RPA',
  subtitle: 'Intelligent Automation vs Rule-Based Process Automation',
  leftOption: {
    name: 'AI Agents',
    description: 'Intelligent, adaptive systems that can understand context and make decisions',
    logo: '/images/logos/anzx-ai-agents.svg',
    color: 'blue',
  },
  rightOption: {
    name: 'RPA (Robotic Process Automation)',
    description: 'Rule-based automation that follows predetermined workflows',
    logo: '/images/logos/rpa-generic.svg',
    color: 'gray',
  },
};

export default async function AiAgentsVsRpaPage() {
  return (
    <main className="min-h-screen">
      {/* Hero Section */}
      <ComparisonHero
        title={comparisonData.title}
        subtitle={comparisonData.subtitle}
        leftOption={comparisonData.leftOption}
        rightOption={comparisonData.rightOption}
      />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 space-y-16">
        {/* Comparison Table */}
        <ComparisonTable 
          leftOption={comparisonData.leftOption}
          rightOption={comparisonData.rightOption}
          type="ai-vs-rpa"
        />

        {/* Feature Comparison */}
        <ComparisonFeatures 
          leftOption={comparisonData.leftOption}
          rightOption={comparisonData.rightOption}
          type="ai-vs-rpa"
        />

        {/* Use Cases */}
        <ComparisonUseCases 
          leftOption={comparisonData.leftOption}
          rightOption={comparisonData.rightOption}
          type="ai-vs-rpa"
        />

        {/* Decision Guide */}
        <ComparisonDecisionGuide 
          leftOption={comparisonData.leftOption}
          rightOption={comparisonData.rightOption}
          type="ai-vs-rpa"
        />

        {/* Get Started CTA */}
        <GetStartedCTA id="get-started" />
      </div>
    </main>
  );
}
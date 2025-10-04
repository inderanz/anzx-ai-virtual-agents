import { Metadata } from 'next';
import ComparisonHero from '@/components/comparison/ComparisonHero';
import ComparisonTable from '@/components/comparison/ComparisonTable';
import ComparisonFeatures from '@/components/comparison/ComparisonFeatures';
import ComparisonUseCases from '@/components/comparison/ComparisonUseCases';
import ComparisonDecisionGuide from '@/components/comparison/ComparisonDecisionGuide';
import GetStartedCTA from '@/components/educational/GetStartedCTA';
import { routing } from '@/routing';

export function generateStaticParams() {
  return routing.locales.map((locale) => ({ locale }));
}

export async function generateMetadata(): Promise<Metadata> {
  return {
    title: 'AI Agents vs Traditional Automation: Which is Right for You? | ANZX.ai',
    description: 'Compare AI agents with traditional automation tools. Understand the key differences and choose the best approach for your business needs.',
    openGraph: {
      title: 'AI Agents vs Traditional Automation: Which is Right for You? | ANZX.ai',
      description: 'Compare AI agents with traditional automation tools. Understand the key differences and choose the best approach for your business needs.',
      images: ['/images/og/ai-agents-vs-automation.jpg'],
    },
    alternates: {
      canonical: 'https://anzx.ai/ai-agents-vs-automation',
    },
  };
}

const comparisonData = {
  title: 'AI Agents vs Traditional Automation',
  subtitle: 'Intelligent Decision-Making vs Rule-Based Processing',
  leftOption: {
    name: 'AI Agents',
    description: 'Autonomous systems that can adapt, learn, and make intelligent decisions',
    logo: '/images/logos/anzx-ai-agents.svg',
    color: 'blue',
  },
  rightOption: {
    name: 'Traditional Automation',
    description: 'Pre-programmed systems that follow fixed rules and workflows',
    logo: '/images/logos/traditional-automation.svg',
    color: 'gray',
  },
};

export default async function AiAgentsVsAutomationPage() {
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
          type="ai-vs-automation"
        />

        {/* Feature Comparison */}
        <ComparisonFeatures 
          leftOption={comparisonData.leftOption}
          rightOption={comparisonData.rightOption}
          type="ai-vs-automation"
        />

        {/* Use Cases */}
        <ComparisonUseCases 
          leftOption={comparisonData.leftOption}
          rightOption={comparisonData.rightOption}
          type="ai-vs-automation"
        />

        {/* Decision Guide */}
        <ComparisonDecisionGuide 
          leftOption={comparisonData.leftOption}
          rightOption={comparisonData.rightOption}
          type="ai-vs-automation"
        />

        {/* Get Started CTA */}
        <GetStartedCTA id="get-started" />
      </div>
    </main>
  );
}

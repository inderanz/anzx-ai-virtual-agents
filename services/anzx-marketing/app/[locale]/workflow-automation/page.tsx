import { Metadata } from 'next';
import { getTranslations } from 'next-intl/server';
import EducationalHero from '@/components/educational/EducationalHero';
import TableOfContents from '@/components/educational/TableOfContents';
import WorkflowDefinitionSection from '@/components/educational/WorkflowDefinitionSection';
import WorkflowTypesSection from '@/components/educational/WorkflowTypesSection';
import WorkflowBenefitsSection from '@/components/educational/WorkflowBenefitsSection';
import WorkflowExamplesSection from '@/components/educational/WorkflowExamplesSection';
import WorkflowImplementationSection from '@/components/educational/WorkflowImplementationSection';
import WorkflowToolsSection from '@/components/educational/WorkflowToolsSection';
import GetStartedCTA from '@/components/educational/GetStartedCTA';

export async function generateMetadata(): Promise<Metadata> {
  const t = await getTranslations('educational.workflowAutomation');
  
  return {
    title: `${t('meta.title')} | ANZX.ai`,
    description: t('meta.description'),
    openGraph: {
      title: `${t('meta.title')} | ANZX.ai`,
      description: t('meta.description'),
      images: ['/images/og/workflow-automation-guide.jpg'],
    },
    alternates: {
      canonical: 'https://anzx.ai/workflow-automation',
    },
  };
}

const tableOfContentsItems = [
  { id: 'definition', title: 'What is Workflow Automation?' },
  { id: 'types', title: 'Types of Workflow Automation' },
  { id: 'benefits', title: 'Benefits & ROI' },
  { id: 'examples', title: 'Real-World Examples' },
  { id: 'tools', title: 'Tools & Technologies' },
  { id: 'implementation', title: 'Implementation Strategy' },
  { id: 'get-started', title: 'Getting Started' },
];

export default async function WorkflowAutomationPage() {
  return (
    <main className="min-h-screen">
      {/* Hero Section */}
      <EducationalHero
        title="Workflow Automation: Streamline Your Business Processes"
        subtitle="Learn how to automate repetitive tasks, improve efficiency, and scale your operations with intelligent workflow automation."
        heroImage="/images/educational/workflow-automation-concept.jpg"
        readingTime="12 min read"
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
            <WorkflowDefinitionSection id="definition" />

            {/* Types Section */}
            <WorkflowTypesSection id="types" />

            {/* Benefits Section */}
            <WorkflowBenefitsSection id="benefits" />

            {/* Examples Section */}
            <WorkflowExamplesSection id="examples" />

            {/* Tools Section */}
            <WorkflowToolsSection id="tools" />

            {/* Implementation Section */}
            <WorkflowImplementationSection id="implementation" />

            {/* Get Started CTA */}
            <GetStartedCTA id="get-started" />
          </div>
        </div>
      </div>
    </main>
  );
}
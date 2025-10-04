import { Metadata } from 'next';
import { getTranslations } from 'next-intl/server';
import RegionalHero from '@/components/regional/RegionalHero';
import CaseStudySection from '@/components/regional/CaseStudySection';
import LocalFeaturesSection from '@/components/regional/LocalFeaturesSection';
import ComplianceSection from '@/components/regional/ComplianceSection';
import PricingSection from '@/components/regional/PricingSection';
import { getRegionData } from '@/lib/constants/regions';

export function generateStaticParams() {
  return [{ locale: 'en' }, { locale: 'hi' }];
}

export async function generateMetadata(): Promise<Metadata> {
  const t = await getTranslations('regional.singapore');
  
  return {
    title: `${t('meta.title')} | ANZX.ai`,
    description: t('meta.description'),
    openGraph: {
      title: `${t('meta.title')} | ANZX.ai`,
      description: t('meta.description'),
      images: ['/images/og/singapore-ai-agents.jpg'],
      locale: 'en_SG',
    },
    alternates: {
      canonical: 'https://anzx.ai/ai-agents-singapore',
    },
  };
}

export default async function SingaporePage() {
  const regionData = getRegionData('singapore');
  
  if (!regionData) {
    return <div>Region not found</div>;
  }

  return (
    <main className="min-h-screen">
      {/* Hero Section */}
      <RegionalHero
        country={regionData.country}
        countryCode={regionData.countryCode}
        currency={regionData.currency}
        flagEmoji={regionData.flagEmoji}
        heroImage={regionData.heroImage}
        businessHours={regionData.businessHours}
        phoneNumber={regionData.phoneNumber}
      />

      {/* Case Studies Section */}
      <CaseStudySection
        caseStudies={regionData.caseStudies}
        country={regionData.country}
      />

      {/* Local Features Section */}
      <LocalFeaturesSection
        features={regionData.localFeatures}
        country={regionData.country}
      />

      {/* Pricing Section */}
      <PricingSection
        pricing={regionData.pricing}
        currency={regionData.currency}
        country={regionData.country}
      />

      {/* Compliance Section */}
      <ComplianceSection
        compliance={regionData.compliance}
        country={regionData.country}
      />
    </main>
  );
}
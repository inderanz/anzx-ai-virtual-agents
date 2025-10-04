import { Metadata } from 'next';
import { getTranslations } from 'next-intl/server';
import RegionalHero from '@/components/regional/RegionalHero';
import CaseStudySection from '@/components/regional/CaseStudySection';
import LocalFeaturesSection from '@/components/regional/LocalFeaturesSection';
import ComplianceSection from '@/components/regional/ComplianceSection';
import PricingSection from '@/components/regional/PricingSection';
import HindiLanguagePromotion from '@/components/regional/HindiLanguagePromotion';
import { getRegionData } from '@/lib/constants/regions';

export function generateStaticParams() {
  return [{ locale: 'en' }, { locale: 'hi' }];
}

export async function generateMetadata(): Promise<Metadata> {
  const t = await getTranslations('regional.india');
  
  return {
    title: `${t('meta.title')} | ANZX.ai`,
    description: t('meta.description'),
    openGraph: {
      title: `${t('meta.title')} | ANZX.ai`,
      description: t('meta.description'),
      images: ['/images/og/india-ai-agents.jpg'],
      locale: 'en_IN',
    },
    alternates: {
      canonical: 'https://anzx.ai/ai-agents-india',
      languages: {
        'hi': 'https://anzx.ai/hi/ai-agents-india',
      },
    },
  };
}

export default async function IndiaPage() {
  const regionData = getRegionData('india');
  
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

      {/* Hindi Language Promotion - Unique to India */}
      <HindiLanguagePromotion />

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
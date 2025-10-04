'use client';

import { useTranslations } from 'next-intl';
import Link from 'next/link';
import { OptimizedImage } from '@/components/ui/OptimizedImage';
import { Button } from '@/components/ui/Button';
import InteractiveFluidBackground from '@/components/ui/InteractiveFluidBackground';

interface RegionalHeroProps {
  country: string;
  countryCode: string;
  currency: string;
  flagEmoji: string;
  heroImage: string;
  businessHours: string;
  phoneNumber: string;
}

export default function RegionalHero({
  country,
  countryCode,
  currency,
  flagEmoji,
  heroImage,
  businessHours,
  phoneNumber,
}: RegionalHeroProps) {
  const t = useTranslations('regional');

  return (
    <div className="relative bg-gradient-to-br from-blue-50 to-indigo-100 overflow-hidden">
      {/* Interactive Fluid Background */}
      <InteractiveFluidBackground className="opacity-60" />
      {/* Background Pattern */}
      <div className="absolute inset-0 bg-grid-pattern opacity-5"></div>
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 lg:py-24">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          {/* Content */}
          <div className="space-y-8">
            <div className="space-y-4">
              <div className="flex items-center gap-3">
                <span className="text-4xl">{flagEmoji}</span>
                <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium">
                  {country}
                </span>
              </div>
              
              <h1 className="text-4xl lg:text-6xl font-bold text-gray-900 leading-tight">
                {t('hero.title', { country })}
              </h1>
              
              <p className="text-xl text-gray-600 leading-relaxed">
                {t('hero.subtitle', { country })}
              </p>
            </div>

            {/* Local Information */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
              <div className="bg-white rounded-lg p-4 shadow-sm">
                <h3 className="font-semibold text-gray-900 mb-2">{t('info.businessHours')}</h3>
                <p className="text-gray-600">{businessHours}</p>
              </div>
              
              <div className="bg-white rounded-lg p-4 shadow-sm">
                <h3 className="font-semibold text-gray-900 mb-2">{t('info.localSupport')}</h3>
                <p className="text-gray-600">{phoneNumber}</p>
              </div>
            </div>

            {/* CTAs */}
            <div className="flex flex-col sm:flex-row gap-4">
              <Button size="lg" className="flex-1 sm:flex-none">
                {t('cta.getStarted')}
              </Button>
              
              <Button variant="outline" size="lg" className="flex-1 sm:flex-none">
                {t('cta.bookDemo')}
              </Button>
            </div>

            {/* Trust Indicators */}
            <div className="pt-8 border-t border-gray-200">
              <p className="text-sm text-gray-500 mb-4">{t('trust.title')}</p>
              <div className="flex items-center gap-6">
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">500+</div>
                  <div className="text-sm text-gray-500">{t('trust.businesses', { country })}</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">99.9%</div>
                  <div className="text-sm text-gray-500">{t('trust.uptime')}</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">24/7</div>
                  <div className="text-sm text-gray-500">{t('trust.support')}</div>
                </div>
              </div>
            </div>
          </div>

          {/* Hero Image */}
          <div className="relative">
            <div className="aspect-square relative overflow-hidden rounded-2xl shadow-2xl">
              <OptimizedImage
                src={heroImage}
                alt={t('hero.imageAlt', { country })}
                width={600}
                height={600}
                className="w-full h-full object-cover"
                priority
              />
            </div>
            
            {/* Floating Elements */}
            <div className="absolute -top-4 -right-4 bg-white rounded-lg p-4 shadow-lg">
              <div className="text-center">
                <div className="text-lg font-bold text-green-600">✓ {t('badges.compliant')}</div>
                <div className="text-sm text-gray-500">{country} {t('badges.regulations')}</div>
              </div>
            </div>
            
            <div className="absolute -bottom-4 -left-4 bg-white rounded-lg p-4 shadow-lg">
              <div className="text-center">
                <div className="text-lg font-bold text-blue-600">{currency}</div>
                <div className="text-sm text-gray-500">{t('badges.localPricing')}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
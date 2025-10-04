'use client';

import { useTranslations } from 'next-intl';
import { Card, CardContent } from '@/components/ui/card';
import { 
  Shield, 
  Globe, 
  Database, 
  Phone,
  MapPin,
  Clock,
  CheckCircle
} from 'lucide-react';

interface LocalFeaturesSectionProps {
  features: string[];
  country: string;
}

const getFeatureIcon = (feature: string) => {
  const lowerFeature = feature.toLowerCase();
  
  if (lowerFeature.includes('compliance') || lowerFeature.includes('regulation')) {
    return Shield;
  }
  if (lowerFeature.includes('language') || lowerFeature.includes('english')) {
    return Globe;
  }
  if (lowerFeature.includes('data') || lowerFeature.includes('residency')) {
    return Database;
  }
  if (lowerFeature.includes('banking') || lowerFeature.includes('payment')) {
    return Phone;
  }
  if (lowerFeature.includes('local')) {
    return MapPin;
  }
  if (lowerFeature.includes('support') || lowerFeature.includes('24')) {
    return Clock;
  }
  
  return CheckCircle;
};

export default function LocalFeaturesSection({ features, country }: LocalFeaturesSectionProps) {
  const t = useTranslations('regional.features');

  return (
    <section className="py-16 lg:py-24 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl lg:text-4xl font-bold text-gray-900 mb-4">
            {t('title', { country })}
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            {t('subtitle', { country })}
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {features.map((feature, index) => {
            const IconComponent = getFeatureIcon(feature);
            
            return (
              <Card key={index} className="hover:shadow-md transition-shadow duration-300">
                <CardContent className="p-6">
                  <div className="flex items-start gap-4">
                    <div className="flex-shrink-0">
                      <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                        <IconComponent className="h-6 w-6 text-blue-600" />
                      </div>
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900 mb-2">
                        {feature}
                      </h3>
                      <p className="text-gray-600 text-sm">
                        {t('description', { feature, country })}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* Additional Benefits */}
        <div className="mt-16 text-center">
          <div className="bg-white rounded-2xl p-8 shadow-sm">
            <h3 className="text-2xl font-bold text-gray-900 mb-4">
              {t('benefits.title', { country })}
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div className="text-center">
                <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <MapPin className="h-8 w-8 text-green-600" />
                </div>
                <h4 className="font-semibold text-gray-900 mb-2">
                  {t('benefits.local.title')}
                </h4>
                <p className="text-gray-600 text-sm">
                  {t('benefits.local.description', { country })}
                </p>
              </div>
              
              <div className="text-center">
                <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Shield className="h-8 w-8 text-blue-600" />
                </div>
                <h4 className="font-semibold text-gray-900 mb-2">
                  {t('benefits.compliance.title')}
                </h4>
                <p className="text-gray-600 text-sm">
                  {t('benefits.compliance.description', { country })}
                </p>
              </div>
              
              <div className="text-center">
                <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Clock className="h-8 w-8 text-purple-600" />
                </div>
                <h4 className="font-semibold text-gray-900 mb-2">
                  {t('benefits.support.title')}
                </h4>
                <p className="text-gray-600 text-sm">
                  {t('benefits.support.description', { country })}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
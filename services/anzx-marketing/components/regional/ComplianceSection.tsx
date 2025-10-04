'use client';

import { useTranslations } from 'next-intl';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Shield, FileCheck, Lock, Award } from 'lucide-react';

interface ComplianceSectionProps {
  compliance: string[];
  country: string;
}

const getComplianceIcon = (compliance: string) => {
  const lowerCompliance = compliance.toLowerCase();
  
  if (lowerCompliance.includes('privacy') || lowerCompliance.includes('data protection')) {
    return Lock;
  }
  if (lowerCompliance.includes('iso') || lowerCompliance.includes('certified')) {
    return Award;
  }
  if (lowerCompliance.includes('act') || lowerCompliance.includes('law')) {
    return FileCheck;
  }
  
  return Shield;
};

export default function ComplianceSection({ compliance, country }: ComplianceSectionProps) {
  const t = useTranslations('regional.compliance');

  return (
    <section className="py-16 lg:py-24 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <div className="flex items-center justify-center gap-2 mb-4">
            <Shield className="h-8 w-8 text-green-600" />
            <Badge variant="secondary" className="text-sm">
              {t('badge')}
            </Badge>
          </div>
          <h2 className="text-3xl lg:text-4xl font-bold text-gray-900 mb-4">
            {t('title', { country })}
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            {t('subtitle', { country })}
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-16">
          {compliance.map((item, index) => {
            const IconComponent = getComplianceIcon(item);
            
            return (
              <Card key={index} className="hover:shadow-md transition-shadow duration-300">
                <CardContent className="p-6">
                  <div className="flex items-start gap-4">
                    <div className="flex-shrink-0">
                      <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                        <IconComponent className="h-6 w-6 text-green-600" />
                      </div>
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900 mb-2">
                        {item}
                      </h3>
                      <p className="text-gray-600 text-sm">
                        {t('description', { compliance: item, country })}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* Security Highlights */}
        <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-2xl p-8">
          <div className="text-center mb-8">
            <h3 className="text-2xl font-bold text-gray-900 mb-4">
              {t('security.title')}
            </h3>
            <p className="text-gray-600 max-w-2xl mx-auto">
              {t('security.subtitle', { country })}
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="w-16 h-16 bg-white rounded-full flex items-center justify-center mx-auto mb-4 shadow-sm">
                <Lock className="h-8 w-8 text-blue-600" />
              </div>
              <h4 className="font-semibold text-gray-900 mb-2">
                {t('security.encryption.title')}
              </h4>
              <p className="text-gray-600 text-sm">
                {t('security.encryption.description')}
              </p>
            </div>
            
            <div className="text-center">
              <div className="w-16 h-16 bg-white rounded-full flex items-center justify-center mx-auto mb-4 shadow-sm">
                <Shield className="h-8 w-8 text-green-600" />
              </div>
              <h4 className="font-semibold text-gray-900 mb-2">
                {t('security.monitoring.title')}
              </h4>
              <p className="text-gray-600 text-sm">
                {t('security.monitoring.description')}
              </p>
            </div>
            
            <div className="text-center">
              <div className="w-16 h-16 bg-white rounded-full flex items-center justify-center mx-auto mb-4 shadow-sm">
                <FileCheck className="h-8 w-8 text-purple-600" />
              </div>
              <h4 className="font-semibold text-gray-900 mb-2">
                {t('security.audits.title')}
              </h4>
              <p className="text-gray-600 text-sm">
                {t('security.audits.description')}
              </p>
            </div>
            
            <div className="text-center">
              <div className="w-16 h-16 bg-white rounded-full flex items-center justify-center mx-auto mb-4 shadow-sm">
                <Award className="h-8 w-8 text-orange-600" />
              </div>
              <h4 className="font-semibold text-gray-900 mb-2">
                {t('security.certifications.title')}
              </h4>
              <p className="text-gray-600 text-sm">
                {t('security.certifications.description')}
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
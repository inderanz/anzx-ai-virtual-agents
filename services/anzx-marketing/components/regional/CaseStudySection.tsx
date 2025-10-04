'use client';

import { useTranslations } from 'next-intl';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { CheckCircle } from 'lucide-react';

interface CaseStudy {
  title: string;
  company: string;
  industry: string;
  challenge: string;
  solution: string;
  results: string[];
}

interface CaseStudySectionProps {
  caseStudies: CaseStudy[];
  country: string;
}

export default function CaseStudySection({ caseStudies, country }: CaseStudySectionProps) {
  const t = useTranslations('regional.caseStudies');

  return (
    <section className="py-16 lg:py-24 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl lg:text-4xl font-bold text-gray-900 mb-4">
            {t('title', { country })}
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            {t('subtitle', { country })}
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {caseStudies.map((caseStudy, index) => (
            <Card key={index} className="h-full hover:shadow-lg transition-shadow duration-300">
              <CardHeader>
                <div className="flex items-start justify-between mb-4">
                  <Badge variant="secondary" className="mb-2">
                    {caseStudy.industry}
                  </Badge>
                </div>
                <CardTitle className="text-xl mb-2">
                  {caseStudy.title}
                </CardTitle>
                <p className="text-gray-600 font-medium">
                  {caseStudy.company}
                </p>
              </CardHeader>
              
              <CardContent className="space-y-6">
                <div>
                  <h4 className="font-semibold text-gray-900 mb-2">
                    {t('challenge')}
                  </h4>
                  <p className="text-gray-600">
                    {caseStudy.challenge}
                  </p>
                </div>

                <div>
                  <h4 className="font-semibold text-gray-900 mb-2">
                    {t('solution')}
                  </h4>
                  <p className="text-gray-600">
                    {caseStudy.solution}
                  </p>
                </div>

                <div>
                  <h4 className="font-semibold text-gray-900 mb-3">
                    {t('results')}
                  </h4>
                  <ul className="space-y-2">
                    {caseStudy.results.map((result, resultIndex) => (
                      <li key={resultIndex} className="flex items-start gap-2">
                        <CheckCircle className="h-5 w-5 text-green-500 mt-0.5 flex-shrink-0" />
                        <span className="text-gray-600">{result}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
}
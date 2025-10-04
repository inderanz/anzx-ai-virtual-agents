'use client';

import { useTranslations } from 'next-intl';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/badge';
import { Check, Star } from 'lucide-react';
import { CurrencyDisplay } from './CurrencyDisplay';

interface PricingSectionProps {
  pricing: {
    starter: number;
    professional: number;
    enterprise: string;
  };
  currency: string;
  country: string;
}

export default function PricingSection({ pricing, currency, country }: PricingSectionProps) {
  const t = useTranslations('regional.pricing');

  const plans = [
    {
      name: t('plans.starter.name'),
      price: pricing.starter,
      description: t('plans.starter.description'),
      features: [
        t('plans.starter.features.0'),
        t('plans.starter.features.1'),
        t('plans.starter.features.2'),
        t('plans.starter.features.3'),
      ],
      cta: t('plans.starter.cta'),
      popular: false,
    },
    {
      name: t('plans.professional.name'),
      price: pricing.professional,
      description: t('plans.professional.description'),
      features: [
        t('plans.professional.features.0'),
        t('plans.professional.features.1'),
        t('plans.professional.features.2'),
        t('plans.professional.features.3'),
        t('plans.professional.features.4'),
        t('plans.professional.features.5'),
      ],
      cta: t('plans.professional.cta'),
      popular: true,
    },
    {
      name: t('plans.enterprise.name'),
      price: pricing.enterprise,
      description: t('plans.enterprise.description'),
      features: [
        t('plans.enterprise.features.0'),
        t('plans.enterprise.features.1'),
        t('plans.enterprise.features.2'),
        t('plans.enterprise.features.3'),
        t('plans.enterprise.features.4'),
        t('plans.enterprise.features.5'),
      ],
      cta: t('plans.enterprise.cta'),
      popular: false,
    },
  ];

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
          <div className="mt-6">
            <Badge variant="secondary" className="text-sm">
              {t('localPricing', { currency })}
            </Badge>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {plans.map((plan, index) => (
            <Card 
              key={index} 
              className={`relative h-full ${
                plan.popular 
                  ? 'border-blue-500 shadow-lg scale-105' 
                  : 'hover:shadow-md'
              } transition-all duration-300`}
            >
              {plan.popular && (
                <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                  <Badge className="bg-blue-500 text-white px-4 py-1">
                    <Star className="h-3 w-3 mr-1" />
                    {t('mostPopular')}
                  </Badge>
                </div>
              )}
              
              <CardHeader className="text-center pb-8">
                <CardTitle className="text-2xl font-bold text-gray-900 mb-2">
                  {plan.name}
                </CardTitle>
                <div className="mb-4">
                  {typeof plan.price === 'number' ? (
                    <div className="flex items-center justify-center gap-1">
                      <CurrencyDisplay 
                        amount={plan.price} 
                        currency={currency}
                        className="text-4xl font-bold text-gray-900"
                      />
                      <span className="text-gray-500">/{t('perMonth')}</span>
                    </div>
                  ) : (
                    <div className="text-4xl font-bold text-gray-900">
                      {plan.price}
                    </div>
                  )}
                </div>
                <p className="text-gray-600">
                  {plan.description}
                </p>
              </CardHeader>
              
              <CardContent className="space-y-6">
                <ul className="space-y-3">
                  {plan.features.map((feature, featureIndex) => (
                    <li key={featureIndex} className="flex items-start gap-3">
                      <Check className="h-5 w-5 text-green-500 mt-0.5 flex-shrink-0" />
                      <span className="text-gray-600">{feature}</span>
                    </li>
                  ))}
                </ul>
                
                <Button 
                  className={`w-full ${
                    plan.popular 
                      ? 'bg-blue-600 hover:bg-blue-700' 
                      : ''
                  }`}
                  variant={plan.popular ? 'primary' : 'outline'}
                  size="lg"
                >
                  {plan.cta}
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Additional Information */}
        <div className="mt-16 text-center">
          <div className="bg-white rounded-2xl p-8 shadow-sm">
            <h3 className="text-2xl font-bold text-gray-900 mb-4">
              {t('guarantee.title')}
            </h3>
            <p className="text-gray-600 mb-6 max-w-2xl mx-auto">
              {t('guarantee.description', { country })}
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button size="lg">
                {t('guarantee.cta.trial')}
              </Button>
              <Button variant="outline" size="lg">
                {t('guarantee.cta.demo')}
              </Button>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
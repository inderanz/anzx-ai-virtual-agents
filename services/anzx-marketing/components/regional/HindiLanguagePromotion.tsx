'use client';

import { useTranslations } from 'next-intl';
import Link from 'next/link';
import { Button } from '@/components/ui/Button';
import { Globe, ArrowRight } from 'lucide-react';

export default function HindiLanguagePromotion() {
  const t = useTranslations('regional.india.hindi');

  return (
    <section className="py-16 bg-gradient-to-r from-orange-50 to-green-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <div className="flex items-center justify-center gap-3 mb-6">
            <Globe className="h-8 w-8 text-orange-600" />
            <span className="text-2xl">🇮🇳</span>
            <span className="bg-orange-100 text-orange-800 px-4 py-2 rounded-full text-sm font-medium">
              {t('badge')}
            </span>
          </div>
          
          <h2 className="text-3xl lg:text-4xl font-bold text-gray-900 mb-4">
            {t('title')}
          </h2>
          
          <p className="text-xl text-gray-600 mb-6 max-w-3xl mx-auto">
            {t('subtitle')}
          </p>

          {/* Hindi Text Sample */}
          <div className="bg-white rounded-2xl p-8 shadow-sm mb-8 max-w-4xl mx-auto">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div className="text-left">
                <h3 className="text-lg font-semibold text-gray-900 mb-3">
                  English
                </h3>
                <p className="text-gray-600 leading-relaxed">
                  "Welcome to ANZX.ai! Our AI agents can help automate your business processes, 
                  handle customer service, and boost your productivity. Get started today with 
                  our enterprise-grade AI solutions."
                </p>
              </div>
              
              <div className="text-left">
                <h3 className="text-lg font-semibold text-gray-900 mb-3">
                  हिंदी (Hindi)
                </h3>
                <p className="text-gray-600 leading-relaxed" style={{ fontFamily: 'system-ui, -apple-system, sans-serif' }}>
                  "ANZX.ai में आपका स्वागत है! हमारे AI एजेंट आपके व्यावसायिक प्रक्रियाओं को स्वचालित करने, 
                  ग्राहक सेवा संभालने और आपकी उत्पादकता बढ़ाने में मदद कर सकते हैं। हमारे एंटरप्राइज़-ग्रेड 
                  AI समाधानों के साथ आज ही शुरुआत करें।"
                </p>
              </div>
            </div>
          </div>

          {/* Features in Hindi */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="bg-white rounded-lg p-6 shadow-sm">
              <div className="text-2xl mb-3">🗣️</div>
              <h4 className="font-semibold text-gray-900 mb-2">
                {t('features.multilingual.title')}
              </h4>
              <p className="text-gray-600 text-sm">
                {t('features.multilingual.description')}
              </p>
            </div>
            
            <div className="bg-white rounded-lg p-6 shadow-sm">
              <div className="text-2xl mb-3">🏢</div>
              <h4 className="font-semibold text-gray-900 mb-2">
                {t('features.business.title')}
              </h4>
              <p className="text-gray-600 text-sm">
                {t('features.business.description')}
              </p>
            </div>
            
            <div className="bg-white rounded-lg p-6 shadow-sm">
              <div className="text-2xl mb-3">🛡️</div>
              <h4 className="font-semibold text-gray-900 mb-2">
                {t('features.compliance.title')}
              </h4>
              <p className="text-gray-600 text-sm">
                {t('features.compliance.description')}
              </p>
            </div>
          </div>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/hi">
              <Button size="lg" className="bg-orange-600 hover:bg-orange-700">
                {t('cta.viewHindi')}
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
            
            <Button variant="outline" size="lg">
              {t('cta.demo')}
            </Button>
          </div>

          {/* Trust Indicators */}
          <div className="mt-12 pt-8 border-t border-gray-200">
            <p className="text-sm text-gray-500 mb-4">
              {t('trust.title')}
            </p>
            <div className="flex items-center justify-center gap-8">
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-600">10+</div>
                <div className="text-sm text-gray-500">{t('trust.languages')}</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-600">1M+</div>
                <div className="text-sm text-gray-500">{t('trust.users')}</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-600">99.9%</div>
                <div className="text-sm text-gray-500">{t('trust.accuracy')}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
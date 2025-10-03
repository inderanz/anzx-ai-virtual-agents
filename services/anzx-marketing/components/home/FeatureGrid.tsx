"use client";

import { motion } from 'framer-motion';
import { useTranslations } from 'next-intl';
import { Clock, Globe, Shield, Zap, TrendingUp, Users } from 'lucide-react';
import { LazySection } from '../ui/LazySection';

const features = [
  {
    icon: Clock,
    key: 'available247',
  },
  {
    icon: Globe,
    key: 'multiLanguage',
  },
  {
    icon: Shield,
    key: 'enterpriseGrade',
  },
  {
    icon: Zap,
    key: 'easyIntegration',
  },
  {
    icon: TrendingUp,
    key: 'aiPowered',
  },
  {
    icon: Users,
    key: 'scalable',
  },
];

export function FeatureGrid() {
  const t = useTranslations('features');

  return (
    <LazySection className="py-20 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">{t('title')}</h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">{t('subtitle')}</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <motion.div
                key={feature.key}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                whileHover={{ y: -5, scale: 1.02 }}
                className="bg-white rounded-xl p-8 shadow-lg hover:shadow-xl transition-all"
              >
                <div className="w-12 h-12 bg-gradient-to-br from-anzx-blue to-anzx-orange rounded-lg flex items-center justify-center mb-4">
                  <Icon className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  {t(`items.${feature.key}.title`)}
                </h3>
                <p className="text-gray-600">{t(`items.${feature.key}.description`)}</p>
              </motion.div>
            );
          })}
        </div>
      </div>
    </LazySection>
  );
}

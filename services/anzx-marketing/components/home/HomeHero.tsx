"use client";

import { useTranslations } from 'next-intl';
import { useEffect, useRef } from 'react';
// import { motion } from 'framer-motion'; // Temporarily disabled for hydration fix
import { PrimaryButton, SecondaryButton } from '../ui/Button';
import ClientOnlyAnimatedHeadline from '../animations/ClientOnlyAnimatedHeadline';
import InteractiveFluidBackground from '../ui/InteractiveFluidBackground';
import MouseTrailEffect from '../ui/MouseTrailEffect';
import { agents } from '@/lib/constants/agents';
import { Play, Sparkles } from 'lucide-react';

export function HomeHero() {
  const t = useTranslations('hero');

  return (
    <section className="hero relative min-h-screen flex items-center justify-center overflow-hidden">
      <MouseTrailEffect />
      {/* Interactive Fluid Background */}
      <div className="absolute inset-0 bg-gradient-to-br from-gray-50 via-white to-blue-50">
        <InteractiveFluidBackground className="opacity-80" />
        
        {/* Subtle overlay for content readability */}
        <div className="absolute inset-0 bg-white/10 backdrop-blur-[0.5px]" />
      </div>

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 z-10">
        <div className="text-center">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-white/80 backdrop-blur-sm border border-gray-200 rounded-full text-sm font-medium text-gray-700 mb-8 shadow-sm">
            <Sparkles className="w-4 h-4 text-anzx-blue" />
            <span>Powered by Advanced AI</span>
          </div>

          {/* Headline */}
          <div>
            <h1 className="text-5xl md:text-6xl lg:text-7xl font-extrabold mb-6 leading-tight">
              <span className="bg-gradient-to-r from-anzx-blue via-purple-600 to-anzx-orange bg-clip-text text-transparent">
                AI Agents
              </span>{' '}
              for{' '}
              <ClientOnlyAnimatedHeadline
                words={[
                  'Customer Service',
                  'Sales Automation',
                  'Recruiting',
                  'Technical Support',
                ]}
                className="bg-gradient-to-r from-anzx-blue via-purple-600 to-anzx-orange bg-clip-text text-transparent"
              />
            </h1>
          </div>

          {/* Subheadline */}
          <p className="text-xl md:text-2xl text-gray-600 mb-10 max-w-3xl mx-auto leading-relaxed">
            {t('subheadline')}
          </p>

          {/* CTAs */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16">
            <PrimaryButton size="lg" className="shadow-xl hover:shadow-2xl">
              {t('primaryCTA')}
            </PrimaryButton>
            <SecondaryButton size="lg" icon={<Play size={20} />}>
              {t('secondaryCTA')}
            </SecondaryButton>
          </div>

          {/* Stats */}
          <div className="flex flex-wrap justify-center gap-8 mb-16">
            {[
              { value: '99.9%', label: 'Uptime' },
              { value: '<100ms', label: 'Response Time' },
              { value: '24/7', label: 'AI Availability' },
            ].map((stat, index) => (
              <div key={index} className="text-center">
                <div className="text-3xl md:text-4xl font-bold text-gray-900 mb-1">
                  {stat.value}
                </div>
                <div className="text-sm text-gray-600">{stat.label}</div>
              </div>
            ))}
          </div>

          {/* Agent Cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-5xl mx-auto">
            {agents.map((agent, index) => (
              <div
                key={agent.id}
                className="group bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-lg hover:shadow-2xl transition-all cursor-pointer border border-gray-100 hover:scale-105 hover:-translate-y-2"
              >
                <div className="w-16 h-16 mx-auto mb-4 bg-gradient-to-br from-anzx-blue to-anzx-orange rounded-full flex items-center justify-center text-white text-2xl font-bold shadow-lg group-hover:shadow-xl transition-shadow">
                  {agent.name[0]}
                </div>
                <h3 className="font-semibold text-gray-900 mb-1">{agent.name}</h3>
                <p className="text-sm text-gray-600">{agent.role}</p>
              </div>
            ))}
          </div>

          {/* Trust indicators */}
          <div className="mt-16 text-sm text-gray-500">
            {t('trustedBy')}
          </div>
        </div>
      </div>

      <style jsx>{`
        @keyframes gradient {
          0%, 100% {
            background-position: 0% 50%;
          }
          50% {
            background-position: 100% 50%;
          }
        }

        @keyframes float {
          0%, 100% {
            transform: translateY(0px) translateX(0px);
          }
          50% {
            transform: translateY(-30px) translateX(20px);
          }
        }

        @keyframes float-delayed {
          0%, 100% {
            transform: translateY(0px) translateX(0px);
          }
          50% {
            transform: translateY(30px) translateX(-20px);
          }
        }

        @keyframes float-slow {
          0%, 100% {
            transform: translateY(0px) translateX(0px) scale(1);
          }
          50% {
            transform: translateY(-20px) translateX(15px) scale(1.1);
          }
        }

        .animate-gradient {
          background-size: 200% 200%;
          animation: gradient 15s ease infinite;
        }

        .animate-float {
          animation: float 20s ease-in-out infinite;
        }

        .animate-float-delayed {
          animation: float-delayed 25s ease-in-out infinite;
        }

        .animate-float-slow {
          animation: float-slow 30s ease-in-out infinite;
        }
      `}</style>
    </section>
  );
}

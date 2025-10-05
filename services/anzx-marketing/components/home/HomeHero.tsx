"use client";

import { useTranslations } from 'next-intl';
import ClientOnlyAnimatedHeadline from '../animations/ClientOnlyAnimatedHeadline';
import MouseTrailEffect from '../ui/MouseTrailEffect';
import { agents } from '@/lib/constants/agents';
import { Play, Sparkles } from 'lucide-react';
import { AnimatedAgentCard } from './AnimatedAgentCard';

export function HomeHero() {
  const t = useTranslations('hero');

  return (
    <section className="hero-section relative min-h-screen flex items-center justify-center overflow-hidden">
      <MouseTrailEffect />
      {/* CSS-based Rotating Gradient Background (like cricket-marketing) */}
      <div className="hero-animated-background" />

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 z-10">
        <div className="text-center">
          {/* Badge - Professional Corporate */}
          <div className="inline-flex items-center gap-2 px-6 py-3 mb-8 relative group">
            {/* Subtle professional glow */}
            <div className="absolute inset-0 rounded-full bg-gradient-to-r from-slate-400 via-slate-300 to-slate-400 opacity-40 blur-sm group-hover:opacity-60 transition-all duration-500 animate-gradient-shift"></div>

            {/* Inner content */}
            <div className="relative flex items-center gap-3 px-5 py-2.5 bg-slate-900/95 backdrop-blur-xl rounded-full border border-slate-300/40 shadow-2xl">
              <Sparkles className="w-4 h-4 text-slate-300 animate-pulse" />
              <span className="font-semibold text-slate-200 tracking-wide">
                Powered by Advanced AI
              </span>
              <div className="w-2 h-2 rounded-full bg-emerald-400 animate-ping absolute -right-1 -top-1 opacity-75"></div>
            </div>
          </div>

          {/* Headline */}
          <div>
            <h1 className="text-5xl md:text-6xl lg:text-7xl font-extrabold mb-6 leading-tight text-white">
              <span className="font-extrabold">
                AI Agents
              </span>{' '}
              for{' '}
              <ClientOnlyAnimatedHeadline
                words={[
                  'Customer Service',
                  'Sales Automation',
                  'Recruiting',
                  'Technical Support',
                  'Google Cloud Ops',
                  'DevOps & GitOps',
                  'Site Reliability',
                ]}
                className="text-white font-extrabold"
              />
            </h1>
          </div>

          {/* Subheadline */}
          <p className="text-xl md:text-2xl text-white/90 mb-10 max-w-3xl mx-auto leading-relaxed font-semibold">
            {t('subheadline')}
          </p>

          {/* CTAs */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16" id="hero-ctas">
            <button
              onClick={() => {
                const element = document.getElementById('agent-cards');
                if (element) {
                  element.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
              }}
              className="inline-flex items-center justify-center gap-2 px-8 py-4 text-lg font-bold rounded-lg transition-all duration-200 bg-white text-teal-700 shadow-2xl hover:shadow-[0_20px_40px_rgba(255,255,255,0.3)] hover:scale-105 hover:bg-gray-50"
            >
              <Sparkles className="w-5 h-5" />
              {t('primaryCTA')}
            </button>
            <button
              className="inline-flex items-center justify-center gap-2 px-8 py-4 text-lg font-bold rounded-lg transition-all duration-200 bg-teal-600/30 backdrop-blur-sm border-2 border-teal-400/50 text-white shadow-xl hover:bg-teal-600/40 hover:border-teal-300 hover:scale-105"
            >
              <Play className="w-5 h-5" />
              {t('secondaryCTA')}
            </button>
          </div>

          {/* Stats */}
          <div className="flex flex-wrap justify-center gap-8 mb-16">
            {[
              { value: '99.9%', label: 'Uptime' },
              { value: '<100ms', label: 'Response Time' },
              { value: '24/7', label: 'AI Availability' },
            ].map((stat) => (
              <div key={stat.label} className="text-center">
                <div className="text-3xl md:text-4xl font-extrabold text-white mb-1">
                  {stat.value}
                </div>
                <div className="text-sm text-white/80 font-semibold">{stat.label}</div>
              </div>
            ))}
          </div>

          {/* Agent Cards - Cricket Chat Style with Realistic Responses */}
          <div id="agent-cards" className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-5xl mx-auto scroll-mt-20">
            {agents.map((agent) => (
              <AnimatedAgentCard key={agent.id} agent={agent} />
            ))}
          </div>

          {/* Trust indicators */}
          <div className="mt-16 text-sm text-white/70 font-semibold">
            {t('trustedBy')}
          </div>
        </div>
      </div>

      <style jsx>{`
        .hero-section {
          position: relative;
          background: linear-gradient(135deg, #0f172a 0%, #1e293b 25%, #0f766e 50%, #0d9488 75%, #14b8a6 100%);
        }

        .hero-animated-background {
          position: absolute;
          top: -50%;
          left: -50%;
          width: 200%;
          height: 200%;
          background: conic-gradient(
            from 0deg,
            #0f172a 0deg,
            #1e293b 60deg,
            #0f766e 120deg,
            #0d9488 180deg,
            #14b8a6 240deg,
            #0f766e 300deg,
            #0f172a 360deg
          );
          animation: hero-rotate 20s linear infinite;
          opacity: 0.8;
          z-index: 1;
        }

        .hero-animated-background::after {
          content: '';
          position: absolute;
          top: 50%;
          left: 50%;
          width: 100%;
          height: 100%;
          transform: translate(-50%, -50%);
          background: radial-gradient(
            circle at 20% 30%,
            rgba(20, 184, 166, 0.3) 0%,
            transparent 50%
          ),
          radial-gradient(
            circle at 80% 70%,
            rgba(13, 148, 136, 0.2) 0%,
            transparent 50%
          ),
          radial-gradient(
            circle at 50% 50%,
            rgba(15, 118, 110, 0.1) 0%,
            transparent 70%
          );
        }

        @keyframes hero-rotate {
          0% {
            transform: rotate(0deg);
          }
          100% {
            transform: rotate(360deg);
          }
        }

        @keyframes gradient-shift {
          0%, 100% {
            background-position: 0% 50%;
          }
          50% {
            background-position: 100% 50%;
          }
        }

        @keyframes gradient-text {
          0%, 100% {
            background-position: 0% 50%;
          }
          50% {
            background-position: 100% 50%;
          }
        }

        .animate-gradient-shift {
          background-size: 200% 200%;
          animation: gradient-shift 3s ease infinite;
        }

        .animate-gradient-text {
          background-size: 200% 200%;
          animation: gradient-text 3s ease infinite;
        }

        @media (prefers-reduced-motion: reduce) {
          .hero-animated-background {
            animation: none;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 25%, #0f766e 50%, #0d9488 75%, #14b8a6 100%);
          }
          .animate-gradient-shift,
          .animate-gradient-text {
            animation: none;
          }
        }
      `}</style>
    </section>
  );
}

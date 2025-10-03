"use client";

import { useTranslations } from 'next-intl';
import { useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { PrimaryButton, SecondaryButton } from '../ui/Button';
import { AnimatedHeadline } from '../animations/AnimatedHeadline';
import { agents } from '@/lib/constants/agents';
import { Play, Sparkles } from 'lucide-react';

export function HomeHero() {
  const t = useTranslations('hero');
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    const particles: Array<{
      x: number;
      y: number;
      vx: number;
      vy: number;
      size: number;
    }> = [];

    // Create particles
    for (let i = 0; i < 50; i++) {
      particles.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        vx: (Math.random() - 0.5) * 0.5,
        vy: (Math.random() - 0.5) * 0.5,
        size: Math.random() * 2 + 1,
      });
    }

    function animate() {
      if (!ctx || !canvas) return;
      
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Draw connections
      particles.forEach((p1, i) => {
        particles.slice(i + 1).forEach((p2) => {
          const dx = p1.x - p2.x;
          const dy = p1.y - p2.y;
          const distance = Math.sqrt(dx * dx + dy * dy);

          if (distance < 150) {
            ctx.beginPath();
            ctx.strokeStyle = `rgba(102, 126, 234, ${0.2 * (1 - distance / 150)})`;
            ctx.lineWidth = 1;
            ctx.moveTo(p1.x, p1.y);
            ctx.lineTo(p2.x, p2.y);
            ctx.stroke();
          }
        });

        // Update particle position
        p1.x += p1.vx;
        p1.y += p1.vy;

        // Bounce off edges
        if (p1.x < 0 || p1.x > canvas.width) p1.vx *= -1;
        if (p1.y < 0 || p1.y > canvas.height) p1.vy *= -1;

        // Draw particle
        ctx.beginPath();
        ctx.arc(p1.x, p1.y, p1.size, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(102, 126, 234, 0.6)';
        ctx.fill();
      });

      requestAnimationFrame(animate);
    }

    animate();

    const handleResize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
      {/* Animated background with gradient */}
      <div className="absolute inset-0 bg-gradient-to-br from-gray-50 via-white to-blue-50">
        {/* Animated gradient overlay */}
        <div className="absolute inset-0 bg-gradient-to-br from-anzx-blue/5 via-purple-500/5 to-anzx-orange/5 animate-gradient" />
        
        {/* Floating circles */}
        <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-anzx-blue/10 rounded-full blur-3xl animate-float" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-anzx-orange/10 rounded-full blur-3xl animate-float-delayed" />
        <div className="absolute top-1/2 right-1/3 w-48 h-48 bg-purple-500/10 rounded-full blur-3xl animate-float-slow" />
        
        {/* Interactive canvas */}
        <canvas
          ref={canvasRef}
          className="absolute inset-0 pointer-events-none opacity-40"
        />
      </div>

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 z-10">
        <div className="text-center">
          {/* Badge */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="inline-flex items-center gap-2 px-4 py-2 bg-white/80 backdrop-blur-sm border border-gray-200 rounded-full text-sm font-medium text-gray-700 mb-8 shadow-sm"
          >
            <Sparkles className="w-4 h-4 text-anzx-blue" />
            <span>Powered by Advanced AI</span>
          </motion.div>

          {/* Headline */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
          >
            <h1 className="text-5xl md:text-6xl lg:text-7xl font-extrabold mb-6 leading-tight">
              <span className="bg-gradient-to-r from-anzx-blue via-purple-600 to-anzx-orange bg-clip-text text-transparent">
                AI Agents
              </span>{' '}
              for{' '}
              <AnimatedHeadline
                words={[
                  'Customer Service',
                  'Sales Automation',
                  'Recruiting',
                  'Technical Support',
                ]}
                className="bg-gradient-to-r from-anzx-blue via-purple-600 to-anzx-orange bg-clip-text text-transparent"
              />
            </h1>
          </motion.div>

          {/* Subheadline */}
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="text-xl md:text-2xl text-gray-600 mb-10 max-w-3xl mx-auto leading-relaxed"
          >
            {t('subheadline')}
          </motion.p>

          {/* CTAs */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
            className="flex flex-col sm:flex-row gap-4 justify-center mb-16"
          >
            <PrimaryButton size="lg" className="shadow-xl hover:shadow-2xl">
              {t('primaryCTA')}
            </PrimaryButton>
            <SecondaryButton size="lg" icon={<Play size={20} />}>
              {t('secondaryCTA')}
            </SecondaryButton>
          </motion.div>

          {/* Stats */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            className="flex flex-wrap justify-center gap-8 mb-16"
          >
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
          </motion.div>

          {/* Agent Cards */}
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.5 }}
            className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-5xl mx-auto"
          >
            {agents.map((agent, index) => (
              <motion.div
                key={agent.id}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.4, delay: 0.6 + index * 0.1 }}
                whileHover={{ scale: 1.05, y: -8 }}
                className="group bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-lg hover:shadow-2xl transition-all cursor-pointer border border-gray-100"
              >
                <div className="w-16 h-16 mx-auto mb-4 bg-gradient-to-br from-anzx-blue to-anzx-orange rounded-full flex items-center justify-center text-white text-2xl font-bold shadow-lg group-hover:shadow-xl transition-shadow">
                  {agent.name[0]}
                </div>
                <h3 className="font-semibold text-gray-900 mb-1">{agent.name}</h3>
                <p className="text-sm text-gray-600">{agent.role}</p>
              </motion.div>
            ))}
          </motion.div>

          {/* Trust indicators */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.6, delay: 1 }}
            className="mt-16 text-sm text-gray-500"
          >
            {t('trustedBy')}
          </motion.div>
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

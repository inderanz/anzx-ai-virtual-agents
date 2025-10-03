"use client";

import { motion } from 'framer-motion';
import { PrimaryButton, SecondaryButton } from '../ui/Button';
import { Agent } from '@/lib/constants/agents';
import { Check } from 'lucide-react';

interface ProductHeroProps {
  agent: Agent;
}

export function ProductHero({ agent }: ProductHeroProps) {
  return (
    <section className="relative min-h-[80vh] flex items-center bg-gradient-to-br from-gray-50 via-white to-blue-50 pt-24">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          {/* Left: Content */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6 }}
          >
            <div className="inline-block px-4 py-2 bg-anzx-blue/10 rounded-full text-anzx-blue text-sm font-semibold mb-4">
              {agent.type.replace('_', ' ').toUpperCase()}
            </div>
            
            <h1 className="text-5xl md:text-6xl font-bold mb-6">
              Meet <span className="gradient-text">{agent.name}</span>
              <br />
              <span className="text-gray-700">{agent.role}</span>
            </h1>

            <p className="text-xl text-gray-600 mb-8">{agent.longDescription}</p>

            <div className="flex flex-col sm:flex-row gap-4 mb-12">
              <PrimaryButton size="lg">Request Demo</PrimaryButton>
              <SecondaryButton size="lg">Watch Video</SecondaryButton>
            </div>

            {/* Key capabilities */}
            <div className="space-y-3">
              {agent.capabilities.slice(0, 4).map((capability, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.4, delay: 0.2 + index * 0.1 }}
                  className="flex items-center space-x-3"
                >
                  <div className="flex-shrink-0 w-6 h-6 bg-green-100 rounded-full flex items-center justify-center">
                    <Check className="w-4 h-4 text-green-600" />
                  </div>
                  <span className="text-gray-700">{capability}</span>
                </motion.div>
              ))}
            </div>
          </motion.div>

          {/* Right: Agent Avatar */}
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="relative"
          >
            <div className="w-full aspect-square max-w-md mx-auto bg-gradient-to-br from-anzx-blue to-anzx-orange rounded-3xl flex items-center justify-center text-white text-9xl font-bold shadow-2xl">
              {agent.name[0]}
            </div>
            
            {/* Floating stats */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.8 }}
              className="absolute -bottom-6 -left-6 bg-white rounded-xl shadow-xl p-6"
            >
              <div className="text-3xl font-bold text-anzx-blue">24/7</div>
              <div className="text-sm text-gray-600">Always Available</div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 1 }}
              className="absolute -top-6 -right-6 bg-white rounded-xl shadow-xl p-6"
            >
              <div className="text-3xl font-bold text-anzx-orange">50+</div>
              <div className="text-sm text-gray-600">Languages</div>
            </motion.div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}

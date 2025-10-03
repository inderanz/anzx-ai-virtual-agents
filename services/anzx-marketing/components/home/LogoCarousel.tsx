"use client";

import { motion } from 'framer-motion';

const partners = [
  { name: 'Partner 1', logo: '/images/partners/partner-1.svg' },
  { name: 'Partner 2', logo: '/images/partners/partner-2.svg' },
  { name: 'Partner 3', logo: '/images/partners/partner-3.svg' },
  { name: 'Partner 4', logo: '/images/partners/partner-4.svg' },
  { name: 'Partner 5', logo: '/images/partners/partner-5.svg' },
  { name: 'Partner 6', logo: '/images/partners/partner-6.svg' },
];

export function LogoCarousel() {
  return (
    <section className="py-12 bg-white/50 backdrop-blur-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-8">
          <p className="text-sm text-gray-600 uppercase tracking-wide">
            Trusted by leading organizations across Asia-Pacific
          </p>
        </div>

        <div className="relative overflow-hidden">
          <div className="flex animate-marquee">
            {[...partners, ...partners].map((partner, index) => (
              <div
                key={index}
                className="flex-shrink-0 mx-8 w-32 h-16 flex items-center justify-center grayscale hover:grayscale-0 transition-all"
              >
                <div className="w-full h-full bg-gray-200 rounded flex items-center justify-center text-gray-400 text-xs">
                  {partner.name}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

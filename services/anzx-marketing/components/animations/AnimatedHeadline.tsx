"use client";

import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface AnimatedHeadlineProps {
  words?: string[];
  speedMs?: number;
  className?: string;
}

export function AnimatedHeadline({
  words = [
    'Customer Service',
    'Sales Automation',
    'Recruiting',
    'Technical Support',
    'Lead Qualification',
  ],
  speedMs = 1800,
  className = '',
}: AnimatedHeadlineProps) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isVisible, setIsVisible] = useState(false);
  const [shouldAnimate, setShouldAnimate] = useState(true);
  const containerRef = useRef<HTMLDivElement>(null);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  // Check for reduced motion preference
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    setShouldAnimate(!mediaQuery.matches);

    const handleChange = (e: MediaQueryListEvent) => {
      setShouldAnimate(!e.matches);
    };

    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, []);

  // Intersection Observer for viewport visibility
  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        setIsVisible(entry.isIntersecting);
      },
      { threshold: 0.1 }
    );

    if (containerRef.current) {
      observer.observe(containerRef.current);
    }

    return () => observer.disconnect();
  }, []);

  // Animation cycle
  useEffect(() => {
    if (!shouldAnimate || !isVisible || words.length <= 1) return;

    const startAnimation = () => {
      intervalRef.current = setInterval(() => {
        setCurrentIndex((prevIndex) => (prevIndex + 1) % words.length);
      }, speedMs);
    };

    startAnimation();

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [words.length, speedMs, shouldAnimate, isVisible]);

  const currentPhrase = words[currentIndex] || words[0];

  return (
    <div ref={containerRef} className={`inline-block overflow-hidden ${className}`}>
      <AnimatePresence mode="wait">
        <motion.span
          key={currentPhrase}
          initial={{
            opacity: 0,
            y: 20,
          }}
          animate={{
            opacity: 1,
            y: 0,
          }}
          exit={{
            opacity: 0,
            y: -20,
          }}
          transition={{
            duration: shouldAnimate ? 0.4 : 0,
            ease: 'easeInOut',
          }}
          className="inline-block text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-purple-400 via-pink-400 via-orange-400 to-cyan-400 animate-gradient-flow font-extrabold"
          style={{
            backgroundSize: '300% 300%',
          }}
          aria-live="polite"
          aria-label={`${currentPhrase}`}
        >
          {currentPhrase}
        </motion.span>
      </AnimatePresence>
      
      <style jsx>{`
        @keyframes gradient-flow {
          0% {
            background-position: 0% 50%;
          }
          50% {
            background-position: 100% 50%;
          }
          100% {
            background-position: 0% 50%;
          }
        }
        
        .animate-gradient-flow {
          animation: gradient-flow 8s ease infinite;
        }
      `}</style>
    </div>
  );
}

"use client";

import React, { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { animationPresets } from '@/lib/utils/motion-lib';

interface OptimizedImageProps {
  src: string;
  alt: string;
  width?: number;
  height?: number;
  className?: string;
  priority?: boolean;
  lazy?: boolean;
}

export function OptimizedImage({
  src,
  alt,
  width,
  height,
  className = '',
  priority = false,
  lazy = true,
}: OptimizedImageProps) {
  const [isLoaded, setIsLoaded] = useState(false);
  const [isVisible, setIsVisible] = useState(!lazy || priority);
  const [hasError, setHasError] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!lazy || priority) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
        }
      },
      { threshold: 0.1 }
    );

    if (ref.current) {
      observer.observe(ref.current);
    }

    return () => observer.disconnect();
  }, [lazy, priority]);

  return (
    <div ref={ref} className={`relative ${className}`}>
      {isVisible && (
        <motion.div {...animationPresets.fadeIn} style={{ position: 'relative', width, height }}>
          {!hasError ? (
            <img
              src={src}
              alt={alt}
              width={width}
              height={height}
              onLoad={() => setIsLoaded(true)}
              onError={() => setHasError(true)}
              style={{
                opacity: isLoaded ? 1 : 0,
                transition: 'opacity 0.3s ease',
                width: '100%',
                height: '100%',
                objectFit: 'contain',
              }}
              loading={priority ? 'eager' : 'lazy'}
              decoding="async"
            />
          ) : (
            <div className="w-full h-full bg-gray-100 flex items-center justify-center text-gray-400 text-sm">
              Image failed to load
            </div>
          )}
        </motion.div>
      )}
    </div>
  );
}

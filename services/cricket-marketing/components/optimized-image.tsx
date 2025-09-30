"use client"

import React, { useState, useRef, useEffect } from 'react'
import { motion } from 'framer-motion'
import { animationPresets } from './motion-lib'

interface OptimizedImageProps {
  src: string
  alt: string
  width?: number
  height?: number
  className?: string
  priority?: boolean
  lazy?: boolean
}

export function OptimizedImage({ 
  src, 
  alt, 
  width, 
  height, 
  className = '',
  priority = false,
  lazy = true
}: OptimizedImageProps) {
  const [isLoaded, setIsLoaded] = useState(false)
  const [isVisible, setIsVisible] = useState(!lazy || priority)
  const [hasError, setHasError] = useState(false)
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!lazy || priority) return

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true)
        }
      },
      { threshold: 0.1 }
    )

    if (ref.current) {
      observer.observe(ref.current)
    }

    return () => observer.disconnect()
  }, [lazy, priority])

  const handleLoad = () => {
    setIsLoaded(true)
  }

  const handleError = () => {
    setHasError(true)
  }

  return (
    <div ref={ref} className={`image-container ${className}`}>
      {isVisible && (
        <motion.div
          {...animationPresets.fadeIn}
          style={{ position: 'relative', width, height }}
        >
          {!hasError ? (
            <img
              src={src}
              alt={alt}
              width={width}
              height={height}
              onLoad={handleLoad}
              onError={handleError}
              style={{
                opacity: isLoaded ? 1 : 0,
                transition: 'opacity 0.3s ease',
                width: '100%',
                height: '100%',
                objectFit: 'contain'
              }}
              loading={priority ? 'eager' : 'lazy'}
              decoding="async"
            />
          ) : (
            <div 
              style={{
                width: '100%',
                height: '100%',
                backgroundColor: '#f3f4f6',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#6b7280',
                fontSize: '14px'
              }}
            >
              Image failed to load
            </div>
          )}
        </motion.div>
      )}
    </div>
  )
}

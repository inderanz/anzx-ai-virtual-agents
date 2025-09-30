"use client"

import React, { useState, useEffect, useRef } from 'react'
import { motion } from 'framer-motion'
import { animationPresets } from './motion-lib'

interface LazySectionProps {
  children: React.ReactNode
  className?: string
  threshold?: number
  rootMargin?: string
}

export function LazySection({ 
  children, 
  className = '', 
  threshold = 0.1,
  rootMargin = '50px'
}: LazySectionProps) {
  const [isVisible, setIsVisible] = useState(false)
  const [hasBeenVisible, setHasBeenVisible] = useState(false)
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && !hasBeenVisible) {
          setIsVisible(true)
          setHasBeenVisible(true)
        }
      },
      { 
        threshold,
        rootMargin
      }
    )

    if (ref.current) {
      observer.observe(ref.current)
    }

    return () => observer.disconnect()
  }, [threshold, rootMargin, hasBeenVisible])

  return (
    <div ref={ref} className={className}>
      {isVisible ? (
        <motion.div {...animationPresets.slideUp}>
          {children}
        </motion.div>
      ) : (
        <div style={{ minHeight: '200px' }} />
      )}
    </div>
  )
}

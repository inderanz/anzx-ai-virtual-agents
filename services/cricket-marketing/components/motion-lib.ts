/**
 * Motion utilities for consistent animations across the application
 * Respects prefers-reduced-motion and provides consistent easing/timing
 */

export interface MotionConfig {
  duration: number
  ease: string
  delay?: number
}

export interface MotionVariants {
  initial: Record<string, any>
  animate: Record<string, any>
  exit?: Record<string, any>
}

// Check for reduced motion preference
export const shouldAnimate = (): boolean => {
  if (typeof window === 'undefined') return true
  return !window.matchMedia('(prefers-reduced-motion: reduce)').matches
}

// Default entrance animation: fade + slide
export const getEntranceAnimation = (y: number = 16): MotionVariants => {
  const animate = shouldAnimate()
  
  return {
    initial: animate ? { opacity: 0, y } : { opacity: 1, y: 0 },
    animate: { opacity: 1, y: 0 },
    exit: animate ? { opacity: 0, y: -y } : { opacity: 1, y: 0 }
  }
}

// Button hover animation
export const getButtonHoverAnimation = (): Record<string, any> => {
  const animate = shouldAnimate()
  
  return {
    scale: animate ? 1.02 : 1,
    transition: {
      duration: animate ? 0.12 : 0,
      ease: 'easeOut'
    }
  }
}

// Stagger animation for lists
export const getStaggerAnimation = (staggerChildren: number = 0.1): Record<string, any> => {
  const animate = shouldAnimate()
  
  return {
    animate: {
      transition: {
        staggerChildren: animate ? staggerChildren : 0
      }
    }
  }
}

// Fade in animation
export const getFadeInAnimation = (delay: number = 0): MotionVariants => {
  const animate = shouldAnimate()
  
  return {
    initial: animate ? { opacity: 0 } : { opacity: 1 },
    animate: { 
      opacity: 1,
      transition: {
        duration: animate ? 0.5 : 0,
        ease: 'easeOut',
        delay: animate ? delay : 0
      }
    }
  }
}

// Slide up animation
export const getSlideUpAnimation = (y: number = 20): MotionVariants => {
  const animate = shouldAnimate()
  
  return {
    initial: animate ? { opacity: 0, y } : { opacity: 1, y: 0 },
    animate: { 
      opacity: 1, 
      y: 0,
      transition: {
        duration: animate ? 0.5 : 0,
        ease: 'easeOut'
      }
    }
  }
}

// Scale animation for cards
export const getScaleAnimation = (scale: number = 1.05): Record<string, any> => {
  const animate = shouldAnimate()
  
  return {
    whileHover: {
      scale: animate ? scale : 1,
      transition: {
        duration: animate ? 0.2 : 0,
        ease: 'easeOut'
      }
    }
  }
}

// Common transition configurations
export const transitions = {
  default: {
    duration: 0.5,
    ease: 'easeOut'
  },
  fast: {
    duration: 0.2,
    ease: 'easeOut'
  },
  slow: {
    duration: 0.8,
    ease: 'easeOut'
  }
} as const

// Animation presets for common use cases
export const animationPresets = {
  hero: getEntranceAnimation(32),
  card: getEntranceAnimation(24),
  button: getButtonHoverAnimation(),
  fadeIn: getFadeInAnimation(),
  slideUp: getSlideUpAnimation(),
  stagger: getStaggerAnimation(0.15)
} as const

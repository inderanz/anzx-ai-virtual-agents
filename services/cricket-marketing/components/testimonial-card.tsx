"use client"

import React from 'react'
import { motion } from 'framer-motion'
import { animationPresets, getScaleAnimation } from './motion-lib'

export function TestimonialCard() {
  return (
    <motion.div 
      className="testimonial-card"
      {...animationPresets.card}
      {...getScaleAnimation(1.02)}
    >
      <div className="testimonial-content">
        <motion.div 
          className="testimonial-quote"
          {...animationPresets.fadeIn}
          transition={{ delay: 0.2 }}
        >
          <blockquote>
            "Cut team admin by 85% with ANZX Cricket Agent."
          </blockquote>
        </motion.div>
        <motion.div 
          className="testimonial-attribution"
          {...animationPresets.slideUp}
          transition={{ delay: 0.4 }}
        >
          <div className="club-logo">
            <img 
              src="/images/club-logo-placeholder.svg" 
              alt="Caroline Springs Cricket Club" 
              className="club-logo-img"
            />
          </div>
          <div className="attribution-text">
            <div className="club-name">Caroline Springs Cricket Club</div>
            <div className="club-role">Team Management</div>
          </div>
        </motion.div>
      </div>
    </motion.div>
  )
}

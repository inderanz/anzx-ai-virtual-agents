"use client"

import React from 'react'

interface TrustBadgesProps {
  variant?: 'hero' | 'footer'
  className?: string
}

export function TrustBadges({ variant = 'hero', className = '' }: TrustBadgesProps) {
  const badges = [
    { text: 'Australian Hosted', icon: '🇦🇺' },
    { text: 'SOC 2 Compliant', icon: '🛡️' },
    { text: 'Privacy Act Compliant', icon: '🔒' }
  ]

  const baseClasses = variant === 'hero' 
    ? 'trust-badges trust-badges-hero' 
    : 'trust-badges trust-badges-footer'

  return (
    <div className={`${baseClasses} ${className}`}>
      {badges.map((badge, index) => (
        <div key={index} className="trust-badge">
          <span className="trust-badge-icon">{badge.icon}</span>
          <span className="trust-badge-text">{badge.text}</span>
        </div>
      ))}
    </div>
  )
}

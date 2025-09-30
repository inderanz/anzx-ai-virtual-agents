"use client"

import React from 'react'
import { motion } from 'framer-motion'
import { animationPresets, getScaleAnimation } from './motion-lib'

interface MetricProps {
  value: string
  label: string
  dataAttribute: string
}

function Metric({ value, label, dataAttribute }: MetricProps) {
  return (
    <motion.div 
      className="metric-item"
      data-analytics={dataAttribute}
      {...animationPresets.card}
      {...getScaleAnimation(1.05)}
    >
      <div className="metric-value">
        {value}
      </div>
      <div className="metric-label">
        {label}
      </div>
    </motion.div>
  )
}

export function MetricsRow() {
  return (
    <motion.div 
      className="metrics-row"
      {...animationPresets.stagger}
    >
      <Metric 
        value="<10s" 
        label="to answer fixtures" 
        dataAttribute="response-time"
      />
      <Metric 
        value="100%" 
        label="club coverage" 
        dataAttribute="coverage"
      />
      <Metric 
        value="24/7" 
        label="availability" 
        dataAttribute="availability"
      />
    </motion.div>
  )
}

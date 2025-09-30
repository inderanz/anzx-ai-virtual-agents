"use client"

import React from 'react'
import { cricketStructuredData, faqStructuredData } from './seo-lib'

export function StructuredData() {
  return (
    <>
      {/* Application Structured Data */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify(cricketStructuredData)
        }}
      />
      
      {/* FAQ Structured Data */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify(faqStructuredData)
        }}
      />
    </>
  )
}

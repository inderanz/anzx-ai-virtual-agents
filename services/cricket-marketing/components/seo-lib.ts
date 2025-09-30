/**
 * SEO utilities for the cricket agent page
 */

export interface SEOData {
  title: string
  description: string
  keywords: string[]
  ogImage: string
  canonical: string
  structuredData?: any
}

export const cricketSEO: SEOData = {
  title: 'ANZX Cricket Agent - AI-Powered Cricket Assistant | Caroline Springs Cricket Club',
  description: 'Get instant answers about fixtures, players, ladder positions, and more with our AI-powered cricket assistant. 24/7 availability for Caroline Springs Cricket Club.',
  keywords: [
    'cricket assistant',
    'AI cricket',
    'cricket fixtures',
    'cricket ladder',
    'cricket statistics',
    'Caroline Springs Cricket Club',
    'cricket AI agent',
    'cricket information',
    'cricket queries'
  ],
  ogImage: '/images/cricket-agent-og.jpg',
  canonical: 'https://anzx.ai/cricket'
}

export const cricketStructuredData = {
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "ANZX Cricket Agent",
  "description": "AI-powered cricket assistant for Caroline Springs Cricket Club",
  "applicationCategory": "SportsApplication",
  "operatingSystem": "Web",
  "offers": {
    "@type": "Offer",
    "price": "0",
    "priceCurrency": "AUD"
  },
  "provider": {
    "@type": "Organization",
    "name": "ANZX.ai",
    "url": "https://anzx.ai"
  },
  "featureList": [
    "Real-time cricket fixtures",
    "Player statistics",
    "Ladder positions",
    "Team information",
    "24/7 availability"
  ]
}

export const faqStructuredData = {
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "What can the ANZX Cricket Agent help with?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "The ANZX Cricket Agent can help with player information, fixtures, ladder positions, team rosters, and match statistics for Caroline Springs Cricket Club."
      }
    },
    {
      "@type": "Question",
      "name": "How accurate is the cricket information provided?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Our AI agent provides real-time, accurate information directly from official cricket databases, ensuring up-to-date and reliable data."
      }
    },
    {
      "@type": "Question",
      "name": "Is the cricket agent available 24/7?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Yes, the ANZX Cricket Agent is available 24/7 to answer your cricket-related questions at any time."
      }
    },
    {
      "@type": "Question",
      "name": "Can I ask questions in natural language?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Absolutely! You can ask questions in natural language like 'Which team is Harshvarshan in?' or 'Show me the ladder for Blue U10'."
      }
    }
  ]
}

export function generateMetaTags(seo: SEOData) {
  return {
    title: seo.title,
    description: seo.description,
    keywords: seo.keywords.join(', '),
    openGraph: {
      title: seo.title,
      description: seo.description,
      url: seo.canonical,
      siteName: 'ANZX.ai',
      images: [
        {
          url: seo.ogImage,
          width: 1200,
          height: 630,
          alt: seo.title
        }
      ],
      locale: 'en_AU',
      type: 'website'
    },
    twitter: {
      card: 'summary_large_image',
      title: seo.title,
      description: seo.description,
      images: [seo.ogImage]
    },
    robots: {
      index: true,
      follow: true,
      googleBot: {
        index: true,
        follow: true,
        'max-video-preview': -1,
        'max-image-preview': 'large' as const,
        'max-snippet': -1
      }
    },
    alternates: {
      canonical: seo.canonical
    }
  }
}
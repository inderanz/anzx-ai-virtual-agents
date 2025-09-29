export const siteConfig = {
  name: "ANZx Cricket Agent",
  description: "AI-powered cricket information system for Australian cricket clubs. Real-time fixtures, ladders, player stats, and WhatsApp integration.",
  url: "https://anzx.ai/cricket",
  ogImage: "https://anzx.ai/og-cricket.jpg",
  links: {
    twitter: "https://twitter.com/anzx_ai",
    github: "https://github.com/inderanz/anzx-ai-virtual-agents",
    linkedin: "https://linkedin.com/company/anzx-ai",
  },
}

export const navigation = {
  main: [
    { name: "Features", href: "#features" },
    { name: "How it Works", href: "#how-it-works" },
    { name: "Pricing", href: "#pricing" },
    { name: "About", href: "#about" },
    { name: "Contact", href: "#contact" },
  ],
  footer: [
    { name: "Privacy Policy", href: "/legal/privacy" },
    { name: "Terms of Service", href: "/legal/terms" },
    { name: "Cookie Policy", href: "/legal/cookies" },
    { name: "Status", href: "https://status.anzx.ai", external: true },
  ],
}

export const hero = {
  title: "AI Cricket Agent for Australian Clubs",
  subtitle: "Real-time cricket information, fixtures, ladders, and player stats powered by PlayHQ integration and WhatsApp messaging.",
  description: "Transform your cricket club's communication with intelligent AI that answers questions about fixtures, standings, player performance, and more. Built for Australian cricket clubs with PlayHQ integration.",
  cta: {
    primary: {
      text: "Start Free Trial",
      href: "#contact",
      variant: "default" as const,
    },
    secondary: {
      text: "Watch Demo",
      href: "#demo",
      variant: "outline" as const,
    },
  },
  stats: [
    { label: "Response Time", value: "< 200ms" },
    { label: "Accuracy", value: "99.9%" },
    { label: "Uptime", value: "99.9%" },
    { label: "Clubs Supported", value: "500+" },
  ],
}

export const features = {
  title: "Everything Your Cricket Club Needs",
  subtitle: "Comprehensive cricket information at your fingertips",
  items: [
    {
      title: "Real-time Fixtures",
      description: "Get instant updates on upcoming matches, venues, and times for all your teams.",
      icon: "Calendar",
      features: ["Live fixture updates", "Venue information", "Match scheduling", "Team notifications"],
    },
    {
      title: "Live Ladder Positions",
      description: "Track your team's position in the competition with real-time ladder updates.",
      icon: "TrendingUp",
      features: ["Live ladder updates", "Points tracking", "Position changes", "Competition standings"],
    },
    {
      title: "Player Statistics",
      description: "Access detailed player performance data including batting, bowling, and fielding stats.",
      icon: "BarChart3",
      features: ["Batting averages", "Bowling figures", "Fielding stats", "Performance trends"],
    },
    {
      title: "WhatsApp Integration",
      description: "Get cricket information directly in your WhatsApp groups with natural language queries.",
      icon: "MessageCircle",
      features: ["Group chat integration", "Natural language queries", "Instant responses", "Team notifications"],
    },
    {
      title: "Multi-team Support",
      description: "Manage multiple teams, grades, and seasons from a single platform.",
      icon: "Users",
      features: ["Multiple teams", "Grade management", "Season tracking", "Team switching"],
    },
    {
      title: "Smart Notifications",
      description: "Receive intelligent alerts about match changes, results, and important updates.",
      icon: "Bell",
      features: ["Match reminders", "Result notifications", "Change alerts", "Custom preferences"],
    },
  ],
}

export const integrations = {
  title: "Seamlessly Integrated",
  subtitle: "Works with the tools your cricket club already uses",
  items: [
    {
      name: "PlayHQ",
      description: "Official Australian cricket data",
      logo: "/logos/playhq.svg",
      features: ["Live fixtures", "Ladder data", "Player stats", "Match results"],
    },
    {
      name: "WhatsApp",
      description: "Team communication platform",
      logo: "/logos/whatsapp.svg",
      features: ["Group integration", "Direct messaging", "Broadcast lists", "Media sharing"],
    },
    {
      name: "Vertex AI",
      description: "Google's advanced AI technology",
      logo: "/logos/vertex-ai.svg",
      features: ["Natural language", "Context understanding", "Smart responses", "Learning capabilities"],
    },
    {
      name: "Google Cloud",
      description: "Enterprise-grade infrastructure",
      logo: "/logos/google-cloud.svg",
      features: ["99.9% uptime", "Global scaling", "Security", "Compliance"],
    },
  ],
}

export const howItWorks = {
  title: "How It Works",
  subtitle: "Three simple steps to get started",
  steps: [
    {
      step: "01",
      title: "Connect Your Club",
      description: "Link your PlayHQ account and WhatsApp groups to get started in minutes.",
      icon: "Link",
      details: [
        "Secure PlayHQ integration",
        "WhatsApp group setup",
        "Team configuration",
        "Permission management",
      ],
    },
    {
      step: "02",
      title: "Train Your Agent",
      description: "Our AI learns your club's specific teams, players, and preferences automatically.",
      icon: "Brain",
      details: [
        "Automatic team detection",
        "Player recognition",
        "Preference learning",
        "Custom responses",
      ],
    },
    {
      step: "03",
      title: "Start Chatting",
      description: "Ask questions in natural language and get instant, accurate cricket information.",
      icon: "MessageSquare",
      details: [
        "Natural language queries",
        "Instant responses",
        "Context awareness",
        "Multi-language support",
      ],
    },
  ],
}

export const pricing = {
  title: "Simple, Transparent Pricing",
  subtitle: "Choose the plan that fits your cricket club",
  plans: [
    {
      name: "Starter",
      price: "$29",
      period: "per month",
      description: "Perfect for small cricket clubs",
      features: [
        "Up to 3 teams",
        "Basic fixtures & ladders",
        "WhatsApp integration",
        "Email support",
        "Standard response time",
      ],
      cta: "Start Free Trial",
      popular: false,
    },
    {
      name: "Professional",
      price: "$79",
      period: "per month",
      description: "Ideal for medium-sized clubs",
      features: [
        "Up to 10 teams",
        "Advanced player stats",
        "Custom notifications",
        "Priority support",
        "API access",
        "Analytics dashboard",
      ],
      cta: "Start Free Trial",
      popular: true,
    },
    {
      name: "Enterprise",
      price: "Custom",
      period: "contact us",
      description: "For large cricket organizations",
      features: [
        "Unlimited teams",
        "White-label solution",
        "Custom integrations",
        "Dedicated support",
        "Advanced analytics",
        "SLA guarantee",
      ],
      cta: "Contact Sales",
      popular: false,
    },
  ],
  faq: [
    {
      question: "How quickly can I get started?",
      answer: "You can be up and running in under 10 minutes. Simply connect your PlayHQ account and WhatsApp groups, and you're ready to go.",
    },
    {
      question: "What cricket data is available?",
      answer: "We provide real-time access to fixtures, ladders, player statistics, match results, and team rosters from PlayHQ's comprehensive database.",
    },
    {
      question: "Can I customize the AI responses?",
      answer: "Yes! Our AI learns your club's specific terminology, preferences, and communication style to provide personalized responses.",
    },
    {
      question: "Is my data secure?",
      answer: "Absolutely. We use enterprise-grade security with Google Cloud infrastructure, ensuring your club's data is protected and compliant with Australian privacy laws.",
    },
    {
      question: "Do you offer a free trial?",
      answer: "Yes! Start with a 14-day free trial to experience all features. No credit card required.",
    },
    {
      question: "What if I need help getting started?",
      answer: "Our team provides comprehensive onboarding support, including setup assistance, training sessions, and ongoing technical support.",
    },
  ],
}

export const testimonials = {
  title: "Trusted by Cricket Clubs Across Australia",
  subtitle: "See what club administrators are saying",
  items: [
    {
      content: "The cricket agent has transformed how we communicate with our members. Instant fixture updates and ladder positions right in our WhatsApp groups.",
      author: {
        name: "Sarah Mitchell",
        role: "Club Secretary",
        club: "Melbourne Cricket Club",
        avatar: "/testimonials/sarah-mitchell.jpg",
      },
    },
    {
      content: "Finally, a solution that understands cricket terminology and provides accurate information. Our members love getting instant answers about their teams.",
      author: {
        name: "David Chen",
        role: "Team Manager",
        club: "Sydney Cricket Association",
        avatar: "/testimonials/david-chen.jpg",
      },
    },
    {
      content: "The integration with PlayHQ is seamless. We get real-time data without any manual work. It's like having a cricket expert available 24/7.",
      author: {
        name: "Emma Thompson",
        role: "Club President",
        club: "Brisbane Cricket Club",
        avatar: "/testimonials/emma-thompson.jpg",
      },
    },
  ],
}

export const cta = {
  title: "Ready to Transform Your Cricket Club?",
  subtitle: "Join hundreds of Australian cricket clubs already using our AI agent",
  description: "Start your free trial today and experience the future of cricket club communication.",
  cta: {
    primary: {
      text: "Start Free Trial",
      href: "#contact",
    },
    secondary: {
      text: "Schedule Demo",
      href: "#demo",
    },
  },
}

export const footer = {
  description: "ANZx Cricket Agent - AI-powered cricket information for Australian clubs. Real-time fixtures, ladders, and player stats with WhatsApp integration.",
  links: {
    product: [
      { name: "Features", href: "#features" },
      { name: "Pricing", href: "#pricing" },
      { name: "API", href: "/api" },
      { name: "Documentation", href: "/docs" },
    ],
    company: [
      { name: "About", href: "#about" },
      { name: "Blog", href: "/blog" },
      { name: "Careers", href: "/careers" },
      { name: "Contact", href: "#contact" },
    ],
    support: [
      { name: "Help Center", href: "/help" },
      { name: "Status", href: "https://status.anzx.ai", external: true },
      { name: "Community", href: "/community" },
      { name: "Support", href: "/support" },
    ],
    legal: [
      { name: "Privacy Policy", href: "/legal/privacy" },
      { name: "Terms of Service", href: "/legal/terms" },
      { name: "Cookie Policy", href: "/legal/cookies" },
      { name: "GDPR", href: "/legal/gdpr" },
    ],
  },
  social: [
    { name: "Twitter", href: "https://twitter.com/anzx_ai", icon: "Twitter" },
    { name: "LinkedIn", href: "https://linkedin.com/company/anzx-ai", icon: "Linkedin" },
    { name: "GitHub", href: "https://github.com/inderanz/anzx-ai-virtual-agents", icon: "Github" },
  ],
}

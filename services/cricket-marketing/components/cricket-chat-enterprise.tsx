"use client"

import React, { useState, useEffect } from 'react'
import { Trophy, Users, Calendar, BarChart3, Clock } from 'lucide-react'
import { ChatPreviewCard } from '@/components/chat-preview-card'
import { TrustBadges } from '@/components/trust-badges'
import { ChatDockWrapper } from '@/components/chat-dock-wrapper'
import { AnimatedHeadline } from '@/components/animated-headline'
import { MetricsRow } from '@/components/metrics-row'
import { TestimonialCard } from '@/components/testimonial-card'
import { AnimatedCounter } from '@/components/animated-counter'
import { motion } from 'framer-motion'
import { animationPresets } from './motion-lib'
import { LazySection } from './lazy-section'
import { useAnalytics } from './analytics-lib'

export function CricketChatEnterprise() {
  const analytics = useAnalytics()
  const [showDemoCTA, setShowDemoCTA] = useState(false)
  const [isScrolled, setIsScrolled] = useState(false)

  // Handle scroll for sticky header
  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 80)
    }

    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])


  const handleTryAgent = () => {
    // Open full chat page
    window.location.href = '/cricket/chat'
  }

  const handleWatchDemo = () => {
    // Open demo modal (placeholder for now)
    alert('Demo video will open here. This is a placeholder for the 60-second demo modal.')
  }

  const handleDemoChip = async (query: string) => {
    // Scroll to features section
    const featuresSection = document.querySelector('[data-testid="cricket-features"]')
    if (featuresSection) {
      featuresSection.scrollIntoView({ behavior: 'smooth' })
    }
    
    // Show CTA after demo
    setTimeout(() => {
      setShowDemoCTA(true)
    }, 1000)
  }

  const handleConnectClub = () => {
    // Scroll to features section
    const featuresSection = document.querySelector('[data-testid="cricket-features"]')
    if (featuresSection) {
      featuresSection.scrollIntoView({ behavior: 'smooth' })
    }
    
    // Show contact information
    alert('To connect your club data, please contact our support team at support@anzx.ai or call us at (03) 1234 5678. We\'ll help you set up real-time data integration for your cricket club.')
  }


  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className={`navbar ${isScrolled ? 'navbar-scrolled' : ''}`}>
        <div className="nav-container">
          <div className="nav-logo">
            <a href="/">
              <img src="/images/anzx-logo.png" alt="ANZX.ai" className="logo" />
            </a>
          </div>
          <div className="nav-menu" id="nav-menu">
            <div className="nav-links">
              <a href="/#solutions" className="nav-link">Solutions</a>
              <a href="/#platform" className="nav-link">Platform</a>
              <a href="/#pricing" className="nav-link">Pricing</a>
              <a href="/#resources" className="nav-link">Resources</a>
              <a href="/#company" className="nav-link">Company</a>
              <a href="/cricket" className="nav-link active">Cricket Agent</a>
            </div>
            <div className="nav-actions">
              <a href="/auth/login" className="nav-link nav-login">Sign In</a>
              <a href="/auth/register" className={`btn ${isScrolled ? 'btn-primary' : 'btn-outline'} nav-cta`}>Get Started</a>
            </div>
          </div>
          <div className="nav-toggle" id="nav-toggle">
            <span className="bar"></span>
            <span className="bar"></span>
            <span className="bar"></span>
          </div>
        </div>
      </nav>

      {/* Cricket Agent Header */}
      <section className="cricket-header" data-testid="cricket-hero">
        <div className="container">
          <motion.div 
            className="cricket-header-content"
            {...animationPresets.hero}
          >
            <motion.div 
              className="cricket-badge"
              {...animationPresets.fadeIn}
              transition={{ delay: 0.2 }}
            >
              <span className="badge-icon">🏏</span>
              <span>Australia Cricket Clubs</span>
            </motion.div>
            <h1 className="cricket-title">
              <AnimatedHeadline 
                speedMs={1800}
              />
            </h1>
            <motion.p 
              className="cricket-description-enhanced"
              {...animationPresets.slideUp}
              transition={{ delay: 0.4 }}
            >
              Get real-time information about <strong>fixtures</strong>, <strong>players</strong>, <strong>ladder positions</strong>, and more. 
              Ask questions in natural language and get <strong>instant, accurate responses</strong>.
            </motion.p>
            <motion.div 
              className="cricket-stats"
              {...animationPresets.stagger}
              transition={{ delay: 0.6 }}
            >
              <motion.div className="stat-item" {...animationPresets.card}>
              <div className="stat-number">
                <AnimatedCounter end={24} duration={2} />
              </div>
              <div className="stat-label">Canonical Queries</div>
            </motion.div>
            <motion.div className="stat-item" {...animationPresets.card}>
              <div className="stat-number">
                <AnimatedCounter end={8} duration={2.5} />
              </div>
              <div className="stat-label">Teams</div>
              </motion.div>
              <motion.div className="stat-item" {...animationPresets.card}>
                <div className="stat-number">24/7</div>
                <div className="stat-label">Available</div>
              </motion.div>
            </motion.div>
            
            {/* Chat Preview Card */}
            <motion.div
              {...animationPresets.slideUp}
              transition={{ delay: 0.8 }}
            >
              <ChatPreviewCard 
                onTryAgent={handleTryAgent}
                onWatchDemo={handleWatchDemo}
              />
            </motion.div>
            
            {/* Trust Badges */}
            <motion.div
              {...animationPresets.fadeIn}
              transition={{ delay: 1.0 }}
            >
              <TrustBadges variant="hero" />
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* Metrics Row */}
      <LazySection className="metrics-section">
        <div className="container">
          <MetricsRow />
        </div>
      </LazySection>

      {/* Testimonial Section */}
      <LazySection className="testimonial-section">
        <div className="container">
          <TestimonialCard />
        </div>
      </LazySection>


      {/* Cricket Features */}
      <section className="cricket-features" data-testid="cricket-features">
        <div className="container">
          <div className="section-header">
            <div className="section-badge">
              <span className="badge-icon">⚡</span>
              <span>Features</span>
            </div>
            <h2 className="section-title">What You Can Ask</h2>
            <p className="section-description">
              Our cricket assistant understands natural language and can answer a wide range of questions about the club.
            </p>
          </div>
          
          <div className="features-grid">
            <div className="feature-card" data-reveal="1">
              <div className="feature-icon">
                <Users size={24} />
              </div>
              <h3 className="feature-title">Player Information</h3>
              <p className="feature-description">Find out which team a player belongs to or get their latest performance stats.</p>
              <div className="feature-examples">
                <div className="feature-example">
                  <strong>Example:</strong> "Which team is Harshvarshan in?"
                </div>
                <div className="feature-example">
                  <strong>Example:</strong> "Who are the players for Caroline Springs Gold U10?"
                </div>
              </div>
            </div>
            
            <div className="feature-card" data-reveal="2">
              <div className="feature-icon">
                <Calendar size={24} />
              </div>
              <h3 className="feature-title">Fixtures & Schedule</h3>
              <p className="feature-description">Get upcoming matches, venues, and match details for any team.</p>
              <div className="feature-examples">
                <div className="feature-example">
                  <strong>Example:</strong> "List all fixtures for Caroline Springs Blue U10"
                </div>
                <div className="feature-example">
                  <strong>Example:</strong> "When is the next game for Caroline Springs White U10?"
                </div>
              </div>
            </div>
            
            <div className="feature-card" data-reveal="3">
              <div className="feature-icon">
                <Trophy size={24} />
              </div>
              <h3 className="feature-title">Ladder Positions</h3>
              <p className="feature-description">Check current standings, points, and performance statistics.</p>
              <div className="feature-examples">
                <div className="feature-example">
                  <strong>Example:</strong> "Where are Caroline Springs Blue U10 on the ladder?"
                </div>
                <div className="feature-example">
                  <strong>Example:</strong> "Show me the current ladder standings"
                </div>
              </div>
            </div>
            
            <div className="feature-card" data-reveal="4">
              <div className="feature-icon">
                <BarChart3 size={24} />
              </div>
              <h3 className="feature-title">Player Statistics</h3>
              <p className="feature-description">Get detailed performance data from recent matches.</p>
              <div className="feature-examples">
                <div className="feature-example">
                  <strong>Example:</strong> "How many runs did Hemant Shah score last match?"
                </div>
                <div className="feature-example">
                  <strong>Example:</strong> "Who scored most runs last match?"
                </div>
              </div>
            </div>
          </div>

          {/* Live Demo Section */}
          <div className="live-demo-section">
            <div className="live-demo-header">
              <h3 className="live-demo-title">Try It Live</h3>
              <p className="live-demo-description">Click any example below to see the assistant in action</p>
            </div>
            
            <div className="demo-chips">
              <button 
                className="demo-chip" 
                onClick={() => handleDemoChip("Fixtures for Blue U10 this week")}
                aria-label="Try: Fixtures for Blue U10 this week"
              >
                <Calendar size={16} />
                Fixtures for Blue U10 this week
              </button>
              
              <button 
                className="demo-chip" 
                onClick={() => handleDemoChip("Ladder position for White U10")}
                aria-label="Try: Ladder position for White U10"
              >
                <Trophy size={16} />
                Ladder position for White U10
              </button>
              
              <button 
                className="demo-chip" 
                onClick={() => handleDemoChip("Who scored most runs last match?")}
                aria-label="Try: Who scored most runs last match?"
              >
                <BarChart3 size={16} />
                Who scored most runs last match?
              </button>
            </div>

            {showDemoCTA && (
              <div className="demo-cta">
                <div className="demo-cta-content">
                  <h4>Connect Your Club Data</h4>
                  <p>Get real-time information for your cricket club</p>
                  <button className="btn btn-primary" onClick={handleConnectClub}>
                    Connect Club Data
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="footer" data-testid="cricket-footer">
        <div className="container">
          <div className="footer-content">
            <div className="footer-section footer-product">
              <div className="footer-logo">
                <img src="/images/anzx-logo.png" alt="ANZX.ai" className="logo" />
              </div>
              <p className="footer-description">
                Next-generation AI agents for Australian businesses. 
                Built with enterprise-grade security, compliance, and performance.
              </p>
              <div className="footer-newsletter">
                <h4 className="newsletter-title">Stay Updated</h4>
                <form className="newsletter-form">
                  <input 
                    type="email" 
                    placeholder="Enter your email" 
                    className="newsletter-input"
                    required
                    aria-label="Email address for newsletter"
                  />
                  <button type="submit" className="newsletter-btn">Subscribe</button>
                </form>
              </div>
            </div>
            <div className="footer-section footer-company">
              <h4 className="footer-title">Company</h4>
              <ul className="footer-links">
                <li><a href="/about">About</a></li>
                <li><a href="/careers">Careers</a></li>
                <li><a href="/contact">Contact</a></li>
                <li><a href="/cricket">Cricket Agent</a></li>
              </ul>
            </div>
            <div className="footer-section footer-legal">
              <h4 className="footer-title">Legal</h4>
              <ul className="footer-links">
                <li><a href="/privacy">Privacy Policy</a></li>
                <li><a href="/terms">Terms of Service</a></li>
                <li><a href="/security">Security</a></li>
                <li><a href="/compliance">Compliance</a></li>
              </ul>
            </div>
            <div className="footer-section footer-social">
              <h4 className="footer-title">Connect</h4>
              <div className="social-links">
                <a href="#" className="social-link" aria-label="LinkedIn">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
                  </svg>
                </a>
                <a href="#" className="social-link" aria-label="Twitter">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 002.163-2.723c-.951.555-2.005.959-3.127 1.184a4.92 4.92 0 00-8.384 4.482C7.69 8.095 4.067 6.13 1.64 3.162a4.822 4.822 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.228-.616v.06a4.923 4.923 0 003.946 4.827 4.996 4.996 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z"/>
                  </svg>
                </a>
                <a href="#" className="social-link" aria-label="GitHub">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                  </svg>
                </a>
              </div>
            </div>
          </div>
          <div className="footer-bottom">
            <p>&copy; 2024 ANZX.ai. All rights reserved. Built in Australia 🇦🇺</p>
            <TrustBadges variant="footer" />
          </div>
        </div>
      </footer>

      {/* Chat Dock */}
      <ChatDockWrapper />
    </div>
  )
}
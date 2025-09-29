"use client"

import React, { useState, useRef, useEffect } from 'react'
import { Activity, Send, Trophy, Users, Calendar, BarChart3, Clock, List } from 'lucide-react'

export function CricketChatEnterprise() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'ai',
      content: `Hello! I'm your cricket assistant for Caroline Springs Cricket Club. I can help you with:

**Player Information:** "Which team is John Smith in?"
**Player Stats:** "How many runs did Jane Doe score last match?"
**Fixtures:** "List all fixtures for Caroline Springs Blue U10"
**Ladder Position:** "Where are Caroline Springs Blue U10 on the ladder?"
**Next Match:** "When is the next game for Caroline Springs White U10?"
**Team Roster:** "Who are the players for Caroline Springs Blue U10?"

What would you like to know?`,
      timestamp: 'Just now'
    }
  ])
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputValue,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }

    setMessages(prev => [...prev, userMessage])
    setInputValue('')
    setIsLoading(true)

    try {
      const response = await fetch('https://cricket-agent-7x6g2q3xaq-uc.a.run.app/ask', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: inputValue,
          session_id: 'web-chat'
        })
      })

      const data = await response.json()
      
      const aiMessage = {
        id: Date.now() + 1,
        type: 'ai',
        content: data.response || 'Sorry, I couldn\'t process your request. Please try again.',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }

      setMessages(prev => [...prev, aiMessage])
    } catch (error) {
      console.error('Error calling cricket agent:', error)
      const errorMessage = {
        id: Date.now() + 1,
        type: 'ai',
        content: 'Sorry, I\'m having trouble connecting to the cricket database. Please try again later.',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const handleSuggestionClick = (query: string) => {
    setInputValue(query)
    inputRef.current?.focus()
  }

  const suggestions = [
    { query: "List all fixtures for Caroline Springs Blue U10", label: "Fixtures", icon: Calendar },
    { query: "Where are Caroline Springs Blue U10 on the ladder?", label: "Ladder", icon: BarChart3 },
    { query: "Who are the players for Caroline Springs Blue U10?", label: "Players", icon: Users },
    { query: "When is the next game for Caroline Springs White U10?", label: "Next Match", icon: Clock }
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="navbar">
        <div className="nav-container">
          <div className="nav-logo">
            <a href="/">
              <img src="/images/logo.svg" alt="ANZx.ai" className="logo" />
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
              <a href="/auth/register" className="btn btn-primary nav-cta">Get Started</a>
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
      <section className="cricket-header">
        <div className="container">
          <div className="cricket-header-content">
            <div className="cricket-badge">
              <span className="badge-icon">🏏</span>
              <span>Caroline Springs Cricket Club</span>
            </div>
            <h1 className="cricket-title">
              Intelligent <span className="cricket-gradient-text">Cricket Assistant</span>
            </h1>
            <p className="cricket-description">
              Get real-time information about fixtures, players, ladder positions, and more. 
              Ask questions in natural language and get instant, accurate responses.
            </p>
            <div className="cricket-stats">
              <div className="stat-item">
                <div className="stat-number">6</div>
                <div className="stat-label">Canonical Queries</div>
              </div>
              <div className="stat-item">
                <div className="stat-number">2</div>
                <div className="stat-label">Teams</div>
              </div>
              <div className="stat-item">
                <div className="stat-number">24/7</div>
                <div className="stat-label">Available</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Cricket Chat Interface */}
      <section className="cricket-chat">
        <div className="container">
          <div className="chat-container">
            <div className="chat-header">
              <div className="chat-title">
                <div className="chat-avatar">
                  <span className="avatar-icon">🏏</span>
                </div>
                <div className="chat-info">
                  <h3>Cricket Assistant</h3>
                  <p>Caroline Springs Cricket Club</p>
                </div>
              </div>
              <div className="chat-status">
                <div className="status-indicator online"></div>
                <span>Online</span>
              </div>
            </div>
            
            <div className="chat-messages" id="chat-messages">
              {messages.map((message) => (
                <div key={message.id} className={`message ${message.type === 'user' ? 'user-message' : 'ai-message'}`}>
                  <div className="message-avatar">
                    <span className="avatar-icon">{message.type === 'user' ? '👤' : '🏏'}</span>
                  </div>
                  <div className="message-content">
                    <div className="message-text">
                      {message.content.split('\n').map((line, index) => {
                        if (line.startsWith('**') && line.endsWith('**')) {
                          return <p key={index}><strong>{line.slice(2, -2)}</strong></p>
                        }
                        if (line.trim() === '') {
                          return <br key={index} />
                        }
                        return <p key={index}>{line}</p>
                      })}
                    </div>
                    <div className="message-time">{message.timestamp}</div>
                  </div>
                </div>
              ))}
              {isLoading && (
                <div className="message ai-message">
                  <div className="message-avatar">
                    <span className="avatar-icon">🏏</span>
                  </div>
                  <div className="message-content">
                    <div className="message-typing">
                      <span>Cricket Assistant is typing</span>
                      <div className="typing-dots">
                        <span></span>
                        <span></span>
                        <span></span>
                      </div>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
            
            <div className="chat-input-container">
              <div className="chat-input-wrapper">
                <input 
                  ref={inputRef}
                  type="text" 
                  id="chat-input" 
                  className="chat-input" 
                  placeholder="Ask about fixtures, players, ladder positions..."
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyPress={handleKeyPress}
                  disabled={isLoading}
                  autoComplete="off"
                />
                <button 
                  id="send-button" 
                  className="send-button" 
                  onClick={handleSendMessage}
                  disabled={!inputValue.trim() || isLoading}
                >
                  <Send size={20} />
                </button>
              </div>
              <div className="chat-suggestions" id="chat-suggestions">
                {suggestions.map((suggestion, index) => {
                  const IconComponent = suggestion.icon
                  return (
                    <button 
                      key={index}
                      className="suggestion-btn" 
                      onClick={() => handleSuggestionClick(suggestion.query)}
                    >
                      <IconComponent size={16} />
                      {suggestion.label}
                    </button>
                  )
                })}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Cricket Features */}
      <section className="cricket-features">
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
            <div className="feature-card">
              <div className="feature-icon">
                <span className="icon">👥</span>
              </div>
              <h3 className="feature-title">Player Information</h3>
              <p className="feature-description">Find out which team a player belongs to or get their latest performance stats.</p>
              <div className="feature-example">
                <strong>Example:</strong> "Which team is John Smith in?"
              </div>
            </div>
            
            <div className="feature-card">
              <div className="feature-icon">
                <span className="icon">📅</span>
              </div>
              <h3 className="feature-title">Fixtures & Schedule</h3>
              <p className="feature-description">Get upcoming matches, venues, and match details for any team.</p>
              <div className="feature-example">
                <strong>Example:</strong> "List all fixtures for Caroline Springs Blue U10"
              </div>
            </div>
            
            <div className="feature-card">
              <div className="feature-icon">
                <span className="icon">🏆</span>
              </div>
              <h3 className="feature-title">Ladder Positions</h3>
              <p className="feature-description">Check current standings, points, and performance statistics.</p>
              <div className="feature-example">
                <strong>Example:</strong> "Where are Caroline Springs Blue U10 on the ladder?"
              </div>
            </div>
            
            <div className="feature-card">
              <div className="feature-icon">
                <span className="icon">📊</span>
              </div>
              <h3 className="feature-title">Player Statistics</h3>
              <p className="feature-description">Get detailed performance data from recent matches.</p>
              <div className="feature-example">
                <strong>Example:</strong> "How many runs did Jane Doe score last match?"
              </div>
            </div>
            
            <div className="feature-card">
              <div className="feature-icon">
                <span className="icon">⏰</span>
              </div>
              <h3 className="feature-title">Next Match Info</h3>
              <p className="feature-description">Find out when and where the next game is scheduled.</p>
              <div className="feature-example">
                <strong>Example:</strong> "When is the next game for Caroline Springs White U10?"
              </div>
            </div>
            
            <div className="feature-card">
              <div className="feature-icon">
                <span className="icon">📋</span>
              </div>
              <h3 className="feature-title">Team Rosters</h3>
              <p className="feature-description">View complete player lists for any team.</p>
              <div className="feature-example">
                <strong>Example:</strong> "Who are the players for Caroline Springs Blue U10?"
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="footer">
        <div className="container">
          <div className="footer-content">
            <div className="footer-section">
              <div className="footer-logo">
                <img src="/images/logo-white.svg" alt="ANZx.ai" className="logo" />
              </div>
              <p className="footer-description">
                Next-generation AI agents for Australian businesses. 
                Built with enterprise-grade security, compliance, and performance.
              </p>
              <div className="footer-social">
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
            <div className="footer-section">
              <h4 className="footer-title">Solutions</h4>
              <ul className="footer-links">
                <li><a href="/#solutions">Customer Support</a></li>
                <li><a href="/#solutions">Sales & Lead Gen</a></li>
                <li><a href="/#solutions">Business Intelligence</a></li>
                <li><a href="/cricket">Cricket Agent</a></li>
              </ul>
            </div>
            <div className="footer-section">
              <h4 className="footer-title">Resources</h4>
              <ul className="footer-links">
                <li><a href="/docs">Documentation</a></li>
                <li><a href="/docs/api">API Reference</a></li>
                <li><a href="/blog">Blog</a></li>
                <li><a href="/status">Status</a></li>
              </ul>
            </div>
            <div className="footer-section">
              <h4 className="footer-title">Company</h4>
              <ul className="footer-links">
                <li><a href="/about">About</a></li>
                <li><a href="/careers">Careers</a></li>
                <li><a href="/contact">Contact</a></li>
                <li><a href="/privacy">Privacy</a></li>
              </ul>
            </div>
          </div>
          <div className="footer-bottom">
            <p>&copy; 2024 ANZx.ai. All rights reserved. Built in Australia 🇦🇺</p>
            <div className="footer-badges">
              <span className="badge">SOC 2 Compliant</span>
              <span className="badge">Australian Hosted</span>
              <span className="badge">Privacy Act Compliant</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}
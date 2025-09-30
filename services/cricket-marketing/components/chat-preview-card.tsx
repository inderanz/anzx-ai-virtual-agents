"use client"

import React, { useState, useEffect } from 'react'
import { Play, MessageCircle } from 'lucide-react'

interface ChatPreviewCardProps {
  onTryAgent: () => void
  onWatchDemo: () => void
}

export function ChatPreviewCard({ onTryAgent, onWatchDemo }: ChatPreviewCardProps) {
  const [currentStep, setCurrentStep] = useState(0)
  const [isTyping, setIsTyping] = useState(false)
  const [displayedText, setDisplayedText] = useState('')

  const chatExample = {
    question: "Where are Caroline Springs Blue U10 on the ladder?",
    answer: "Caroline Springs Blue U10 is currently in 3rd position on the ladder with 8 points from 4 matches. They have 2 wins, 1 loss, and 1 draw. The team is performing well and has a good chance of making the finals."
  }

  useEffect(() => {
    const steps = [
      { type: 'question', text: chatExample.question, delay: 1000 },
      { type: 'typing', text: '', delay: 2000 },
      { type: 'answer', text: chatExample.answer, delay: 3000 }
    ]

    let timeoutId: NodeJS.Timeout
    let currentIndex = 0

    const runStep = () => {
      if (currentIndex < steps.length) {
        const step = steps[currentIndex]
        setCurrentStep(currentIndex)
        
        if (step.type === 'typing') {
          setIsTyping(true)
          setDisplayedText('')
        } else {
          setIsTyping(false)
          setDisplayedText(step.text)
        }

        timeoutId = setTimeout(() => {
          currentIndex++
          runStep()
        }, step.delay)
      } else {
        // Restart the cycle after a pause
        setTimeout(() => {
          currentIndex = 0
          runStep()
        }, 5000)
      }
    }

    // Start the animation after initial delay
    timeoutId = setTimeout(runStep, 2000)

    return () => {
      if (timeoutId) clearTimeout(timeoutId)
    }
  }, [])

  return (
    <div className="chat-preview-card">
      <div className="chat-preview-header">
        <div className="chat-preview-avatar">
          <span className="avatar-icon">🏏</span>
        </div>
        <div className="chat-preview-info">
          <h4>Cricket Assistant</h4>
          <p>A Leading Cricket Club</p>
        </div>
        <div className="chat-preview-status">
          <div className="status-dot online"></div>
          <span>Online</span>
        </div>
      </div>

      <div className="chat-preview-messages">
        {/* User Question */}
        {currentStep >= 0 && (
          <div className="message user-message">
            <div className="message-avatar">
              <span className="avatar-icon">👤</span>
            </div>
            <div className="message-content">
              <div className="message-text">
                {currentStep === 0 ? displayedText : chatExample.question}
              </div>
              <div className="message-time">Just now</div>
            </div>
          </div>
        )}

        {/* AI Response */}
        {currentStep >= 1 && (
          <div className="message ai-message">
            <div className="message-avatar">
              <span className="avatar-icon">🏏</span>
            </div>
            <div className="message-content">
              {isTyping ? (
                <div className="message-typing">
                  <span>Cricket Assistant is typing</span>
                  <div className="typing-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              ) : (
                <div className="message-text">
                  {displayedText}
                </div>
              )}
              <div className="message-time">Just now</div>
            </div>
          </div>
        )}
      </div>

      <div className="chat-preview-actions">
        <button 
          className="btn btn-primary chat-preview-cta"
          onClick={onTryAgent}
          aria-label="Try the Cricket Agent"
        >
          <MessageCircle size={16} />
          Try the Cricket Agent
        </button>
        <button 
          className="btn btn-secondary chat-preview-cta"
          onClick={onWatchDemo}
          aria-label="Watch 60-second demo"
        >
          <Play size={16} />
          Watch 60-sec Demo
        </button>
      </div>
    </div>
  )
}

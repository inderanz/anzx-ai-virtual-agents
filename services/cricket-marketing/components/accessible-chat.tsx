"use client"

import React, { useRef, useEffect } from 'react'
import { useAnalytics } from './analytics-lib'

interface AccessibleChatProps {
  children: React.ReactNode
  className?: string
}

export function AccessibleChat({ children, className = '' }: AccessibleChatProps) {
  const chatRef = useRef<HTMLElement>(null)
  const analytics = useAnalytics()

  useEffect(() => {
    // Track chat opened event
    analytics.trackChatOpened()

    // Set up keyboard navigation
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        // Close chat or return focus to trigger
        const trigger = document.querySelector('[data-chat-trigger]') as HTMLElement
        trigger?.focus()
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [analytics])

  return (
    <section
      ref={chatRef}
      role="log"
      aria-live="polite"
      aria-relevant="additions text"
      aria-label="Cricket Assistant Chat"
      className={className}
      tabIndex={-1}
    >
      {children}
    </section>
  )
}

interface AccessibleMessageProps {
  children: React.ReactNode
  isUser?: boolean
  timestamp: string
  className?: string
}

export function AccessibleMessage({ 
  children, 
  isUser = false, 
  timestamp, 
  className = '' 
}: AccessibleMessageProps) {
  const messageRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    // Announce new messages to screen readers
    if (messageRef.current) {
      const announcement = isUser ? 'You said' : 'Cricket Assistant replied'
      const announcementElement = document.createElement('div')
      announcementElement.setAttribute('aria-live', 'polite')
      announcementElement.setAttribute('aria-atomic', 'true')
      announcementElement.className = 'sr-only'
      announcementElement.textContent = `${announcement} at ${timestamp}`
      
      document.body.appendChild(announcementElement)
      
      // Clean up after announcement
      setTimeout(() => {
        document.body.removeChild(announcementElement)
      }, 1000)
    }
  }, [isUser, timestamp])

  return (
    <div
      ref={messageRef}
      role={isUser ? 'user-message' : 'assistant-message'}
      aria-label={`${isUser ? 'Your message' : 'Assistant response'} at ${timestamp}`}
      className={className}
    >
      {children}
    </div>
  )
}

interface AccessibleButtonProps {
  children: React.ReactNode
  onClick: () => void
  ariaLabel: string
  className?: string
  disabled?: boolean
}

export function AccessibleButton({ 
  children, 
  onClick, 
  ariaLabel, 
  className = '',
  disabled = false
}: AccessibleButtonProps) {
  const buttonRef = useRef<HTMLButtonElement>(null)

  const handleClick = () => {
    if (!disabled) {
      onClick()
    }
  }

  const handleKeyDown = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault()
      handleClick()
    }
  }

  return (
    <button
      ref={buttonRef}
      onClick={handleClick}
      onKeyDown={handleKeyDown}
      aria-label={ariaLabel}
      disabled={disabled}
      className={`focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${className}`}
      style={{
        outline: 'none'
      }}
    >
      {children}
    </button>
  )
}

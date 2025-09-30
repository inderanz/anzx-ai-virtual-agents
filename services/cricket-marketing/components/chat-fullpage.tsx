"use client"

import React, { useState, useEffect, useRef } from 'react'
import { MessageCircle, Send, Copy, RotateCcw, RefreshCw } from 'lucide-react'

interface Message {
  id: number
  type: 'user' | 'ai'
  content: string
  timestamp: string
  isStreaming?: boolean
}

export function ChatFullPage() {
  const [messages, setMessages] = useState<Message[]>([])
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isAtBottom, setIsAtBottom] = useState(true)
  const [showNewMessages, setShowNewMessages] = useState(false)
  
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)
  const messagesContainerRef = useRef<HTMLDivElement>(null)

  // Initialize with welcome message
  useEffect(() => {
    const savedMessages = localStorage.getItem('cricket-chat-messages')
    if (savedMessages) {
      setMessages(JSON.parse(savedMessages))
    } else {
      const welcomeMessage: Message = {
        id: 1,
        type: 'ai',
        content: `Hello! I'm your cricket assistant for A Leading Cricket Club. I can help you with:

**Player Information:** "Which team is John Smith in?"
**Player Stats:** "How many runs did Jane Doe score last match?"
**Fixtures:** "List all fixtures for Caroline Springs Blue U10"
**Ladder Position:** "Where are Caroline Springs Blue U10 on the ladder?"
**Next Match:** "When is the next game for Caroline Springs White U10?"
**Team Roster:** "Who are the players for Caroline Springs Blue U10?"

What would you like to know?`,
        timestamp: 'Just now'
      }
      setMessages([welcomeMessage])
    }
  }, [])

  // Save messages to localStorage
  useEffect(() => {
    if (messages.length > 0) {
      localStorage.setItem('cricket-chat-messages', JSON.stringify(messages))
    }
  }, [messages])

  // Auto-scroll behavior
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const handleScroll = () => {
    if (!messagesContainerRef.current) return
    
    const { scrollTop, scrollHeight, clientHeight } = messagesContainerRef.current
    const isAtBottomNow = scrollTop + clientHeight >= scrollHeight - 10
    
    setIsAtBottom(isAtBottomNow)
    
    if (!isAtBottomNow && !showNewMessages) {
      setShowNewMessages(true)
    } else if (isAtBottomNow && showNewMessages) {
      setShowNewMessages(false)
    }
  }

  // Auto-scroll when new messages arrive
  useEffect(() => {
    if (isAtBottom) {
      scrollToBottom()
    }
  }, [messages, isAtBottom])

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now(),
      type: 'user',
      content: inputValue,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }

    setMessages(prev => [...prev, userMessage])
    setInputValue('')
    setIsLoading(true)

    // Add streaming message
    const streamingMessage: Message = {
      id: Date.now() + 1,
      type: 'ai',
      content: '',
      timestamp: 'Just now',
      isStreaming: true
    }
    setMessages(prev => [...prev, streamingMessage])

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
      
      // Simulate streaming with jitter
      const responseText = data.response || 'Sorry, I couldn\'t process your request. Please try again.'
      const tokens = responseText.split(' ')
      let currentContent = ''
      
      for (let i = 0; i < tokens.length; i++) {
        await new Promise(resolve => setTimeout(resolve, 200 + Math.random() * 300))
        currentContent += (i > 0 ? ' ' : '') + tokens[i]
        
        setMessages(prev => prev.map(msg => 
          msg.isStreaming 
            ? { ...msg, content: currentContent }
            : msg
        ))
      }

      // Finalize message
      setMessages(prev => prev.map(msg => 
        msg.isStreaming 
          ? { ...msg, isStreaming: false, content: responseText }
          : msg
      ))

    } catch (error) {
      console.error('Error calling cricket agent:', error)
      setMessages(prev => prev.map(msg => 
        msg.isStreaming 
          ? { 
              ...msg, 
              isStreaming: false, 
              content: 'Sorry, I\'m having trouble connecting to the cricket database. Please try again later.' 
            }
          : msg
      ))
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

  const handleCopyMessage = (content: string) => {
    navigator.clipboard.writeText(content)
  }

  const handleRetryMessage = (messageId: number) => {
    // Find the user message before this AI message
    const messageIndex = messages.findIndex(msg => msg.id === messageId)
    if (messageIndex > 0) {
      const userMessage = messages[messageIndex - 1]
      if (userMessage.type === 'user') {
        setInputValue(userMessage.content)
        inputRef.current?.focus()
      }
    }
  }

  const handleRegenerateMessage = (messageId: number) => {
    // Remove the AI message and regenerate
    setMessages(prev => prev.filter(msg => msg.id !== messageId))
    // Trigger regeneration logic here
  }

  const handleNewMessagesClick = () => {
    scrollToBottom()
    setShowNewMessages(false)
  }

  return (
    <div className="chat-dock chat-dock-fullpage">
      {/* Header */}
      <div className="chat-dock-header">
        <div className="chat-dock-title">
          <div className="chat-dock-avatar">
            <span className="avatar-icon">🏏</span>
          </div>
          <div className="chat-dock-info">
            <h3>Cricket Assistant</h3>
            <p>A Leading Cricket Club</p>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="chat-dock-content">
        <div 
          className="chat-dock-messages"
          ref={messagesContainerRef}
          onScroll={handleScroll}
        >
          {messages.map((message) => (
            <div key={message.id} className={`chat-dock-message ${message.type === 'user' ? 'user-message' : 'ai-message'}`}>
              <div className="chat-dock-message-avatar">
                <span className="avatar-icon">{message.type === 'user' ? '👤' : '🏏'}</span>
              </div>
              <div className="chat-dock-message-content">
                <div className="chat-dock-message-text">
                  {message.isStreaming ? (
                    <div className="streaming-content">
                      {message.content}
                      <span className="streaming-cursor">|</span>
                    </div>
                  ) : (
                    message.content.split('\n').map((line, index) => {
                      if (line.startsWith('**') && line.endsWith('**')) {
                        return <p key={index}><strong>{line.slice(2, -2)}</strong></p>
                      }
                      if (line.trim() === '') {
                        return <br key={index} />
                      }
                      return <p key={index}>{line}</p>
                    })
                  )}
                </div>
                <div className="chat-dock-message-actions">
                  <button
                    className="message-action"
                    onClick={() => handleCopyMessage(message.content)}
                    aria-label="Copy message"
                  >
                    <Copy size={14} />
                  </button>
                  {message.type === 'ai' && !message.isStreaming && (
                    <>
                      <button
                        className="message-action"
                        onClick={() => handleRetryMessage(message.id)}
                        aria-label="Retry message"
                      >
                        <RotateCcw size={14} />
                      </button>
                      <button
                        className="message-action"
                        onClick={() => handleRegenerateMessage(message.id)}
                        aria-label="Regenerate message"
                      >
                        <RefreshCw size={14} />
                      </button>
                    </>
                  )}
                </div>
                <div className="chat-dock-message-time">{message.timestamp}</div>
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="chat-dock-message ai-message">
              <div className="chat-dock-message-avatar">
                <span className="avatar-icon">🏏</span>
              </div>
              <div className="chat-dock-message-content">
                <div className="chat-dock-message-typing">
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

        {/* New messages pill */}
        {showNewMessages && (
          <button
            className="new-messages-pill"
            onClick={handleNewMessagesClick}
          >
            New messages
          </button>
        )}

        {/* Input */}
        <div className="chat-dock-input">
          <div className="chat-dock-input-wrapper">
            <input
              ref={inputRef}
              type="text"
              className="chat-dock-input-field"
              placeholder="Ask about fixtures, players, ladder positions..."
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={isLoading}
              autoComplete="off"
            />
            <button
              className="chat-dock-send"
              onClick={handleSendMessage}
              disabled={!inputValue.trim() || isLoading}
              aria-label="Send message"
            >
              <Send size={16} />
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

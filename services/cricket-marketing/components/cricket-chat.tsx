"use client"

import { useState, useRef, useEffect } from "react"
import { Send, Loader2, Bot, User, Trophy, TrendingUp, Calendar, Users, Star, Clock, CheckCircle, Sparkles, ChevronRight, Activity, ExternalLink, Menu, X, Play, Zap } from "lucide-react"
import { Button } from "@/components/ui/button"

interface Message {
  id: string
  type: "user" | "assistant"
  content: string
  timestamp: Date
  intent?: string
  latency?: number
}

const QUICK_ACTIONS = [
  { 
    text: "List all fixtures for Caroline Springs Blue U10", 
    icon: Calendar, 
    color: "from-blue-500 to-blue-600",
    label: "Fixtures"
  },
  { 
    text: "Where are Caroline Springs Blue U10 on the ladder?", 
    icon: TrendingUp, 
    color: "from-green-500 to-green-600",
    label: "Ladder"
  },
  { 
    text: "Who are the players for Caroline Springs Blue U10?", 
    icon: Users, 
    color: "from-purple-500 to-purple-600",
    label: "Players"
  },
  { 
    text: "When is the next game for Caroline Springs White U10?", 
    icon: Clock, 
    color: "from-orange-500 to-orange-600",
    label: "Next Match"
  },
]

const FEATURES = [
  {
    icon: Users,
    title: "Player Information",
    description: "Find out which team a player belongs to or get their latest performance stats.",
    example: "Which team is John Smith in?"
  },
  {
    icon: Calendar,
    title: "Fixtures & Schedule",
    description: "Get upcoming matches, venues, and match details for any team.",
    example: "List all fixtures for Caroline Springs Blue U10"
  },
  {
    icon: Trophy,
    title: "Ladder Positions",
    description: "Check current standings, points, and performance statistics.",
    example: "Where are Caroline Springs Blue U10 on the ladder?"
  },
  {
    icon: TrendingUp,
    title: "Player Statistics",
    description: "Get detailed performance data from recent matches.",
    example: "How many runs did Jane Doe score last match?"
  },
  {
    icon: Clock,
    title: "Next Match Info",
    description: "Find out when and where the next game is scheduled.",
    example: "When is the next game for Caroline Springs White U10?"
  },
  {
    icon: CheckCircle,
    title: "Team Rosters",
    description: "View complete player lists for any team.",
    example: "Who are the players for Caroline Springs Blue U10?"
  }
]

export function CricketChat() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      type: "assistant",
      content: "Hello! I'm your cricket assistant for Caroline Springs Cricket Club. I can help you with:\n\n• **Player Information:** \"Which team is John Smith in?\"\n• **Player Stats:** \"How many runs did Jane Doe score last match?\"\n• **Fixtures:** \"List all fixtures for Caroline Springs Blue U10\"\n• **Ladder Position:** \"Where are Caroline Springs Blue U10 on the ladder?\"\n• **Next Match:** \"When is the next game for Caroline Springs White U10?\"\n• **Team Roster:** \"Who are the players for Caroline Springs Blue U10?\"\n\nWhat would you like to know?",
      timestamp: new Date()
    },
  ])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [isTyping, setIsTyping] = useState(false)
  const [showChat, setShowChat] = useState(false)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const sendMessage = async (content: string) => {
    if (!content.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      type: "user",
      content: content.trim(),
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInput("")
    setIsLoading(true)
    setIsTyping(true)

    try {
      const startTime = Date.now()
      const response = await fetch('https://cricket-agent-aa5gcxefza-ts.a.run.app/v1/ask', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: content.trim(),
          source: "web"
        })
      })

      if (!response.ok) {
        throw new Error('Failed to get response')
      }

      const data = await response.json()
      const latency = Date.now() - startTime
      
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: "assistant",
        content: data.answer || "I'm sorry, I couldn't process your request. Please try again.",
        timestamp: new Date(),
        intent: data.meta?.intent,
        latency: latency
      }

      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      console.error('Error sending message:', error)
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: "assistant",
        content: "I apologize, but I'm experiencing connectivity issues. Please try again in a moment.",
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
      setIsTyping(false)
    }
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    sendMessage(input)
  }

  const handleQuickAction = (action: typeof QUICK_ACTIONS[0]) => {
    sendMessage(action.text)
    setShowChat(true)
  }

  const formatMessage = (content: string) => {
    return content.split('\n').map((line, index) => {
      if (line.startsWith('• **') && line.includes('**:')) {
        const [bold, rest] = line.split('**:')
        return (
          <div key={index} className="flex items-start gap-2 mb-2">
            <span className="text-blue-400 mt-1">•</span>
            <span>
              <strong className="text-white">{bold.replace('• **', '')}</strong>:
              {rest}
            </span>
          </div>
        )
      }
      if (line.startsWith('**') && line.endsWith('**')) {
        return (
          <div key={index} className="font-semibold text-white mb-2">
            {line.replace(/\*\*/g, '')}
          </div>
        )
      }
      return <div key={index} className="mb-1">{line}</div>
    })
  }

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
      {/* Navigation */}
      <nav className="relative z-50 bg-white/10 backdrop-blur-md border-b border-white/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-3">
              <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center shadow-lg">
                <Activity className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-white">ANZx Cricket</h1>
                <p className="text-sm text-blue-200">AI Cricket Assistant</p>
              </div>
            </div>
            
            <div className="hidden md:flex items-center space-x-6">
              <a href="https://anzx.ai" className="text-blue-200 hover:text-white transition-colors flex items-center gap-2">
                ANZx Platform
                <ExternalLink className="h-4 w-4" />
              </a>
              <a href="https://anzx.ai/contact" className="text-blue-200 hover:text-white transition-colors">Contact</a>
              <a href="https://anzx.ai/legal/privacy" className="text-blue-200 hover:text-white transition-colors">Privacy</a>
            </div>

            <button
              className="md:hidden text-white"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            >
              {mobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
            </button>
          </div>

          {/* Mobile Menu */}
          {mobileMenuOpen && (
            <div className="md:hidden py-4 border-t border-white/10">
              <div className="flex flex-col space-y-3">
                <a href="https://anzx.ai" className="text-blue-200 hover:text-white transition-colors">ANZx Platform</a>
                <a href="https://anzx.ai/contact" className="text-blue-200 hover:text-white transition-colors">Contact</a>
                <a href="https://anzx.ai/legal/privacy" className="text-blue-200 hover:text-white transition-colors">Privacy</a>
              </div>
            </div>
          )}
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 bg-blue-500/20 backdrop-blur-sm border border-blue-500/30 rounded-full px-4 py-2 mb-8">
            <Trophy className="h-4 w-4 text-blue-400" />
            <span className="text-blue-200 text-sm font-medium">Caroline Springs Cricket Club</span>
          </div>
          
          <h1 className="text-4xl md:text-6xl font-bold text-white mb-6">
            Intelligent{" "}
            <span className="bg-gradient-to-r from-blue-400 via-purple-500 to-cyan-400 bg-clip-text text-transparent">
              Cricket Assistant
            </span>
          </h1>
          
          <p className="text-xl text-blue-200 mb-8 max-w-3xl mx-auto">
            Get real-time information about fixtures, players, ladder positions, and more. 
            Ask questions in natural language and get instant, accurate responses.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-12">
            <Button
              onClick={() => setShowChat(true)}
              className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white px-8 py-6 text-lg font-semibold rounded-xl shadow-lg hover:shadow-xl transition-all duration-200 flex items-center gap-2"
            >
              <Play className="h-5 w-5" />
              Start Chatting
            </Button>
            <div className="flex items-center gap-6 text-blue-200">
              <div className="text-center">
                <div className="text-2xl font-bold text-white">6</div>
                <div className="text-sm">Query Types</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-white">2</div>
                <div className="text-sm">Teams</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-white">24/7</div>
                <div className="text-sm">Available</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Chat Interface */}
      <section className={`py-12 px-4 sm:px-6 lg:px-8 transition-all duration-500 ${showChat ? 'opacity-100' : 'opacity-100'}`}>
        <div className="max-w-4xl mx-auto">
          <div className="bg-white/10 backdrop-blur-md rounded-2xl border border-white/20 shadow-2xl overflow-hidden">
            {/* Chat Header */}
            <div className="bg-gradient-to-r from-blue-600 to-purple-600 px-6 py-4 text-white">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className="h-12 w-12 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center">
                    <Trophy className="h-6 w-6 text-white" />
                  </div>
                  <div>
                    <h3 className="text-lg font-bold">Cricket Assistant</h3>
                    <p className="text-blue-100 text-sm">Caroline Springs Cricket Club</p>
                  </div>
                </div>
                <div className="flex items-center space-x-3">
                  <div className="flex items-center space-x-2 bg-white/10 backdrop-blur-sm rounded-full px-3 py-1">
                    <div className="h-2 w-2 rounded-full bg-green-400 animate-pulse"></div>
                    <span className="text-sm font-medium">Online</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Messages */}
            <div className="h-96 overflow-y-auto px-6 py-6 space-y-4 bg-slate-900/50">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.type === "user" ? "justify-end" : "justify-start"}`}
                >
                  <div className={`flex max-w-[85%] ${message.type === "user" ? "flex-row-reverse" : "flex-row"} items-start space-x-3`}>
                    <div className={`flex-shrink-0 h-8 w-8 rounded-full flex items-center justify-center ${
                      message.type === "user" 
                        ? "bg-gradient-to-br from-blue-500 to-purple-600" 
                        : "bg-gradient-to-br from-green-500 to-emerald-600"
                    }`}>
                      {message.type === "assistant" ? (
                        <Trophy className="h-4 w-4 text-white" />
                      ) : (
                        <User className="h-4 w-4 text-white" />
                      )}
                    </div>
                    
                    <div className={`flex flex-col ${message.type === "user" ? "items-end" : "items-start"}`}>
                      <div className={`px-4 py-3 rounded-2xl shadow-sm max-w-full ${
                        message.type === "user"
                          ? "bg-gradient-to-br from-blue-500 to-purple-600 text-white rounded-br-md"
                          : "bg-white/10 backdrop-blur-sm text-blue-100 rounded-bl-md border border-white/20"
                      }`}>
                        <div className="text-sm leading-relaxed">
                          {formatMessage(message.content)}
                        </div>
                      </div>
                      
                      <div className={`flex items-center space-x-2 mt-2 text-xs ${
                        message.type === "user" ? "text-blue-300" : "text-blue-400"
                      }`}>
                        <Clock className="h-3 w-3" />
                        <span>{formatTime(message.timestamp)}</span>
                        {message.latency && (
                          <>
                            <span>•</span>
                            <span>{message.latency}ms</span>
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
              
              {isTyping && (
                <div className="flex justify-start">
                  <div className="flex items-start space-x-3">
                    <div className="flex-shrink-0 h-8 w-8 rounded-full bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center">
                      <Trophy className="h-4 w-4 text-white" />
                    </div>
                    <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-2xl rounded-bl-md px-4 py-3">
                      <div className="flex items-center space-x-2">
                        <div className="flex space-x-1">
                          <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce"></div>
                          <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                          <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                        </div>
                        <span className="text-sm text-blue-300">Analyzing your request...</span>
                      </div>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Quick Actions */}
            <div className="px-6 py-4 bg-slate-800/50 border-t border-white/10">
              <p className="text-sm font-medium text-blue-200 mb-4">Quick actions:</p>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {QUICK_ACTIONS.map((action, index) => (
                  <Button
                    key={index}
                    variant="outline"
                    className="h-auto p-3 text-left hover:shadow-lg transition-all duration-200 border-white/20 hover:border-blue-400 bg-white/5 hover:bg-white/10 text-blue-200 hover:text-white flex flex-col items-center space-y-2"
                    onClick={() => handleQuickAction(action)}
                    disabled={isLoading}
                  >
                    <div className={`h-8 w-8 rounded-lg bg-gradient-to-r ${action.color} flex items-center justify-center`}>
                      <action.icon className="h-4 w-4 text-white" />
                    </div>
                    <span className="text-xs font-medium">{action.label}</span>
                  </Button>
                ))}
              </div>
            </div>

            {/* Input */}
            <div className="bg-slate-800/50 border-t border-white/10 px-6 py-4">
              <form onSubmit={handleSubmit} className="flex items-center space-x-3">
                <div className="flex-1 relative">
                  <input
                    ref={inputRef}
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Ask about fixtures, players, ladder positions..."
                    className="w-full p-4 pr-12 rounded-xl border border-white/20 bg-white/10 backdrop-blur-sm text-white placeholder-blue-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
                    disabled={isLoading}
                  />
                  <Button 
                    type="submit" 
                    size="icon" 
                    disabled={isLoading || !input.trim()}
                    className="absolute right-2 top-2 h-10 w-10 rounded-lg bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white shadow-lg disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
                  >
                    {isLoading ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <Send className="h-4 w-4" />
                    )}
                  </Button>
                </div>
              </form>
              <div className="flex items-center justify-between mt-3 text-xs text-blue-400">
                <span>Press Enter to send</span>
                <div className="flex items-center space-x-2">
                  <CheckCircle className="h-3 w-3 text-green-400" />
                  <span>AI-powered responses</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <div className="inline-flex items-center gap-2 bg-purple-500/20 backdrop-blur-sm border border-purple-500/30 rounded-full px-4 py-2 mb-6">
              <Zap className="h-4 w-4 text-purple-400" />
              <span className="text-purple-200 text-sm font-medium">Features</span>
            </div>
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">What You Can Ask</h2>
            <p className="text-xl text-blue-200 max-w-3xl mx-auto">
              Our cricket assistant understands natural language and can answer a wide range of questions about the club.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {FEATURES.map((feature, index) => (
              <div key={index} className="bg-white/10 backdrop-blur-md rounded-2xl border border-white/20 p-6 hover:bg-white/15 transition-all duration-200 group">
                <div className="h-12 w-12 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-200">
                  <feature.icon className="h-6 w-6 text-white" />
                </div>
                <h3 className="text-xl font-bold text-white mb-3">{feature.title}</h3>
                <p className="text-blue-200 mb-4">{feature.description}</p>
                <div className="bg-slate-800/50 rounded-lg p-3 border border-white/10">
                  <p className="text-sm text-blue-300">
                    <strong className="text-white">Example:</strong> "{feature.example}"
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  )
}
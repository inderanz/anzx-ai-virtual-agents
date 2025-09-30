/**
 * Analytics instrumentation for the cricket agent
 * Tracks user interactions and performance metrics
 */

export interface AnalyticsEvent {
  event: string
  properties: Record<string, any>
  timestamp: number
  sessionId: string
  userId?: string
}

export interface PerformanceMetrics {
  timeToFirstToken: number
  tokensStreamed: number
  renderTime: number
  errorRate: number
  mobileCrashFree: number
}

class Analytics {
  private sessionId: string
  private events: AnalyticsEvent[] = []
  private performanceMetrics: PerformanceMetrics = {
    timeToFirstToken: 0,
    tokensStreamed: 0,
    renderTime: 0,
    errorRate: 0,
    mobileCrashFree: 100
  }

  constructor() {
    this.sessionId = this.generateSessionId()
    this.initializePerformanceTracking()
  }

  private generateSessionId(): string {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  }

  private initializePerformanceTracking() {
    // Track Core Web Vitals
    if (typeof window !== 'undefined') {
      // LCP (Largest Contentful Paint)
      new PerformanceObserver((list) => {
        const entries = list.getEntries()
        const lastEntry = entries[entries.length - 1] as any
        this.track('lcp_measured', {
          value: lastEntry.startTime,
          element: lastEntry.element?.tagName || 'unknown'
        })
      }).observe({ entryTypes: ['largest-contentful-paint'] })

      // FID (First Input Delay)
      new PerformanceObserver((list) => {
        const entries = list.getEntries()
        entries.forEach((entry: any) => {
          this.track('fid_measured', {
            value: entry.processingStart - entry.startTime,
            eventType: entry.name
          })
        })
      }).observe({ entryTypes: ['first-input'] })

      // CLS (Cumulative Layout Shift)
      new PerformanceObserver((list) => {
        let clsValue = 0
        const entries = list.getEntries()
        entries.forEach((entry: any) => {
          if (!entry.hadRecentInput) {
            clsValue += entry.value
          }
        })
        this.track('cls_measured', { value: clsValue })
      }).observe({ entryTypes: ['layout-shift'] })
    }
  }

  private getDeviceInfo() {
    if (typeof window === 'undefined') return {}
    
    return {
      userAgent: navigator.userAgent,
      viewport: {
        width: window.innerWidth,
        height: window.innerHeight
      },
      connection: (navigator as any).connection ? {
        effectiveType: (navigator as any).connection.effectiveType,
        downlink: (navigator as any).connection.downlink
      } : null,
      isMobile: /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)
    }
  }

  track(event: string, properties: Record<string, any> = {}) {
    const analyticsEvent: AnalyticsEvent = {
      event,
      properties: {
        ...properties,
        ...this.getDeviceInfo(),
        url: typeof window !== 'undefined' ? window.location.href : '',
        referrer: typeof document !== 'undefined' ? document.referrer : ''
      },
      timestamp: Date.now(),
      sessionId: this.sessionId
    }

    this.events.push(analyticsEvent)
    
    // Send to analytics service (placeholder)
    this.sendToAnalytics(analyticsEvent)
  }

  private sendToAnalytics(event: AnalyticsEvent) {
    // In production, this would send to your analytics service
    console.log('Analytics Event:', event)
    
    // Example: Send to Google Analytics, Mixpanel, etc.
    if (typeof window !== 'undefined' && (window as any).gtag) {
      (window as any).gtag('event', event.event, event.properties)
    }
  }

  // Cricket-specific events
  trackChatOpened() {
    this.track('chat_opened', {
      timestamp: Date.now(),
      source: 'hero_cta'
    })
  }

  trackPromptSent(prompt: string, promptLength: number) {
    this.track('prompt_sent', {
      prompt_length: promptLength,
      prompt_preview: prompt.substring(0, 50),
      timestamp: Date.now()
    })
  }

  trackTimeToFirstToken(timeMs: number) {
    this.performanceMetrics.timeToFirstToken = timeMs
    this.track('time_to_first_token', {
      time_ms: timeMs,
      performance_grade: timeMs < 1200 ? 'excellent' : timeMs < 2000 ? 'good' : 'needs_improvement'
    })
  }

  trackTokensStreamed(count: number) {
    this.performanceMetrics.tokensStreamed += count
    this.track('tokens_streamed', {
      count,
      total_tokens: this.performanceMetrics.tokensStreamed
    })
  }

  trackToolCardViewed(cardType: string) {
    this.track('tool_card_viewed', {
      card_type: cardType,
      timestamp: Date.now()
    })
  }

  trackFailureShown(errorType: string, errorMessage: string) {
    this.track('failure_shown', {
      error_type: errorType,
      error_message: errorMessage.substring(0, 100),
      timestamp: Date.now()
    })
  }

  trackRetryClicked(originalPrompt: string) {
    this.track('retry_clicked', {
      original_prompt: originalPrompt.substring(0, 50),
      timestamp: Date.now()
    })
  }

  trackMobileKeyboardOpen() {
    this.track('mobile_keyboard_open', {
      timestamp: Date.now(),
      viewport_height: window.innerHeight
    })
  }

  // SLO tracking
  updateSLOMetrics(metrics: Partial<PerformanceMetrics>) {
    this.performanceMetrics = { ...this.performanceMetrics, ...metrics }
    
    this.track('slo_metrics_updated', {
      ...this.performanceMetrics,
      timestamp: Date.now()
    })
  }

  getSLOMetrics(): PerformanceMetrics {
    return { ...this.performanceMetrics }
  }

  // Export events for debugging
  exportEvents(): AnalyticsEvent[] {
    return [...this.events]
  }
}

// Singleton instance
export const analytics = new Analytics()

// React hook for analytics
export function useAnalytics() {
  return analytics
}

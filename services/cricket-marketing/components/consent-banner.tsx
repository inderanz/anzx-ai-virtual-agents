"use client"

import { useState, useEffect } from "react"
import { X, Cookie, Shield, Settings } from "lucide-react"


export function ConsentBanner() {
  const [showBanner, setShowBanner] = useState(false)
  const [consentGiven, setConsentGiven] = useState(false)

  useEffect(() => {
    const consent = localStorage.getItem("analytics-consent")
    if (consent === null) {
      setShowBanner(true)
    } else {
      setConsentGiven(consent === "true")
    }
  }, [])

  const handleAccept = () => {
    localStorage.setItem("analytics-consent", "true")
    setConsentGiven(true)
    setShowBanner(false)
    
    // Enable analytics
    if (typeof window !== "undefined") {
      window.gtag?.("consent", "update", {
        analytics_storage: "granted",
        ad_storage: "granted",
      })
    }
  }

  const handleReject = () => {
    localStorage.setItem("analytics-consent", "false")
    setConsentGiven(false)
    setShowBanner(false)
    
    // Disable analytics
    if (typeof window !== "undefined") {
      window.gtag?.("consent", "update", {
        analytics_storage: "denied",
        ad_storage: "denied",
      })
    }
  }

  const handleClose = () => {
    setShowBanner(false)
  }

  if (!showBanner) {
    return null
  }

  return (
    <div className="fixed bottom-0 left-0 right-0 z-50 bg-background border-t border-border shadow-lg">
      <div className="mx-auto max-w-7xl px-6 py-4 lg:px-8">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10">
              <Cookie className="h-4 w-4 text-primary" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-foreground">
                We use cookies to improve your experience
              </h3>
              <p className="text-xs text-muted-foreground">
                We use analytics cookies to understand how you use our site and improve it.
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={handleReject}
              className="px-3 py-1.5 text-sm text-muted-foreground hover:text-foreground rounded-md hover:bg-muted/50 transition-colors"
            >
              Reject All
            </button>
            <button
              onClick={handleAccept}
              className="px-3 py-1.5 text-sm bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors"
            >
              Accept All
            </button>
            <button
              onClick={handleClose}
              className="p-1.5 text-muted-foreground hover:text-foreground rounded-md hover:bg-muted/50 transition-colors"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

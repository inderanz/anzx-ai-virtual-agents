"use client"

import { Suspense } from 'react'
import { ChatDock } from './chat-dock'

function ChatDockFallback() {
  return (
    <button
      className="chat-fab"
      aria-label="Open chat"
    >
      <span>💬</span>
    </button>
  )
}

export function ChatDockWrapper() {
  return (
    <Suspense fallback={<ChatDockFallback />}>
      <ChatDock />
    </Suspense>
  )
}

import { ChatFullPage } from '@/components/chat-fullpage'

export default function ChatPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="navbar">
        <div className="nav-container">
          <div className="nav-logo">
            <a href="/cricket">
              <img src="/images/anzx-logo.png" alt="ANZx.ai" className="logo" />
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

      {/* Breadcrumb */}
      <div className="breadcrumb">
        <div className="container">
          <nav className="breadcrumb-nav">
            <a href="/cricket" className="breadcrumb-link">Cricket Agent</a>
            <span className="breadcrumb-separator">/</span>
            <span className="breadcrumb-current">Chat</span>
          </nav>
        </div>
      </div>

      {/* Full-page Chat */}
      <ChatFullPage />
    </div>
  )
}

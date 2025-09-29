import Link from "next/link"
import { Activity, ExternalLink } from "lucide-react"

export function Footer() {
  return (
    <footer className="bg-muted/30 border-t">
      <div className="mx-auto max-w-7xl px-6 py-8 lg:px-8">
        <div className="flex flex-col items-center justify-between space-y-4 md:flex-row md:space-y-0">
          <div className="flex items-center space-x-2">
            <Activity className="h-6 w-6 text-primary" />
            <span className="text-lg font-semibold">ANZx Cricket Agent</span>
          </div>
          
          <div className="flex items-center space-x-6 text-sm text-muted-foreground">
            <Link 
              href="https://anzx.ai" 
              className="hover:text-foreground transition-colors flex items-center gap-1"
            >
              ANZx Platform
              <ExternalLink className="h-3 w-3" />
            </Link>
            <Link 
              href="https://anzx.ai/contact" 
              className="hover:text-foreground transition-colors"
            >
              Contact
            </Link>
            <Link 
              href="https://anzx.ai/legal/privacy" 
              className="hover:text-foreground transition-colors"
            >
              Privacy
            </Link>
          </div>
        </div>
        
        <div className="mt-4 pt-4 border-t border-border">
          <p className="text-center text-xs text-muted-foreground">
            &copy; 2024 ANZx AI. All rights reserved. Built in Australia 🇦🇺
          </p>
        </div>
      </div>
    </footer>
  )
}
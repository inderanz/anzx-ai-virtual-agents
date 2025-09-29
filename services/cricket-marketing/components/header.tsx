import { Activity } from "lucide-react"

export function Header() {
  return (
    <header className="border-b bg-card">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center">
              <Activity className="h-4 w-4 text-primary" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-foreground">ANZx Cricket</h1>
              <p className="text-sm text-muted-foreground">AI Cricket Assistant</p>
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}
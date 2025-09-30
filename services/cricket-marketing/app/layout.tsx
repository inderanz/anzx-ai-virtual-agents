import type { Metadata } from "next"
import { Inter } from "next/font/google"
import "./globals.css"
import { cricketSEO, generateMetaTags } from "../components/seo-lib"

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
})

export const metadata: Metadata = generateMetaTags(cricketSEO)

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={inter.variable}>
      <body className="min-h-screen bg-background font-sans antialiased">
        {children}
      </body>
    </html>
  )
}
import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'ANZX.ai - AI Agents for Business',
  description: 'Enterprise-grade AI agents for customer service, sales, and recruiting.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return children;
}
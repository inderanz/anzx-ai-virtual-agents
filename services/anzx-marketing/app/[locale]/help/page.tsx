import { Metadata } from 'next';
import { Header } from '@/components/layout/Header';
import { Footer } from '@/components/layout/Footer';
import { routing } from '@/routing';

export function generateStaticParams() {
  return routing.locales.map((locale) => ({ locale }));
}

export const metadata: Metadata = {
  title: 'Help & Support | ANZX.ai',
  description: 'Get help with ANZX AI agents and find answers to common questions.',
};

export default function HelpPage() {
  return (
    <>
      <Header />
      <main className="min-h-screen pt-24 pb-16 bg-gradient-to-br from-slate-900 via-teal-900 to-slate-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-6">
            Help & Support
          </h1>
          <p className="text-xl text-white/80 mb-12">
            Get help with ANZX AI agents and find answers to common questions.
          </p>
          <div className="bg-white/10 backdrop-blur-md rounded-lg p-8 text-white">
            <p>Support documentation coming soon. For immediate assistance, please contact us.</p>
          </div>
        </div>
      </main>
      <Footer />
    </>
  );
}

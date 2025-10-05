import { Metadata } from 'next';
import { Header } from '@/components/layout/Header';
import { Footer } from '@/components/layout/Footer';
import { routing } from '@/routing';

export function generateStaticParams() {
  return routing.locales.map((locale) => ({ locale }));
}

export const metadata: Metadata = {
  title: 'Integrations | ANZX.ai',
  description: 'Connect ANZX AI agents with your existing tools and platforms.',
};

export default function IntegrationsPage() {
  return (
    <>
      <Header />
      <main className="min-h-screen pt-24 pb-16 bg-gradient-to-br from-slate-900 via-teal-900 to-slate-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-6">
            Integrations
          </h1>
          <p className="text-xl text-white/80 mb-12">
            Connect ANZX AI agents with your existing tools and platforms.
          </p>
          <div className="bg-white/10 backdrop-blur-md rounded-lg p-8 text-white">
            <p>Integration options coming soon. Contact us to discuss your specific needs.</p>
          </div>
        </div>
      </main>
      <Footer />
    </>
  );
}

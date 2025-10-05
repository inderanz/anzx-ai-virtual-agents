import { Metadata } from 'next';
import { Header } from '@/components/layout/Header';
import { Footer } from '@/components/layout/Footer';
import { routing } from '@/routing';

export function generateStaticParams() {
  return routing.locales.map((locale) => ({ locale }));
}

export const metadata: Metadata = {
  title: 'Our Vision | ANZX.ai',
  description: 'Learn about ANZX vision for the future of AI agents in business.',
};

export default function VisionPage() {
  return (
    <>
      <Header />
      <main className="min-h-screen pt-24 pb-16 bg-gradient-to-br from-slate-900 via-teal-900 to-slate-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-6">
            Our Vision
          </h1>
          <p className="text-xl text-white/80 mb-12">
            Building the future of AI agents for Asia-Pacific businesses.
          </p>
          <div className="bg-white/10 backdrop-blur-md rounded-lg p-8 text-white space-y-4">
            <p>
              At ANZX, we envision a future where AI agents seamlessly integrate into every business operation,
              empowering teams to focus on what matters most - innovation and growth.
            </p>
            <p>
              Our mission is to make enterprise-grade AI accessible to businesses across Australia, New Zealand,
              India, and Singapore, transforming how companies interact with customers, manage operations, and scale their teams.
            </p>
          </div>
        </div>
      </main>
      <Footer />
    </>
  );
}

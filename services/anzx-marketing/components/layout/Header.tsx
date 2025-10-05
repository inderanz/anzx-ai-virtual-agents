"use client";

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useTranslations } from 'next-intl';
import { Menu, X } from 'lucide-react';
import ClientOnlyLanguageSwitcher from '../ui/ClientOnlyLanguageSwitcher';
import { LanguageSwitcherLink } from '../ui/LanguageSwitcherLink';
import { Navigation } from './Navigation';
import { MobileMenu } from './MobileMenu';

export function Header() {
  const t = useTranslations('nav');
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <header
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        isScrolled ? 'bg-white shadow-md' : 'bg-transparent'
      }`}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link 
            href="/" 
            className="flex items-center"
            onClick={() => {
              // Scroll to top when clicking logo
              window.scrollTo({ top: 0, behavior: 'smooth' });
            }}
          >
            <img 
              src="/images/anzx-logo.png" 
              alt="ANZX.ai" 
              className="h-12 w-12 rounded-full object-cover border-2 border-white shadow-md hover:scale-105 transition-transform"
            />
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-8">
            <Navigation />
          </div>

          {/* Right side */}
          <div className="hidden md:flex items-center space-x-4">
            <ClientOnlyLanguageSwitcher />
            <Link
              href="/login"
              className="text-white font-bold hover:text-blue-200 transition-colors"
            >
              {t('login')}
            </Link>
            <Link
              href="/get-started"
              className="bg-white text-blue-600 px-6 py-2.5 rounded-lg font-bold hover:bg-blue-50 hover:shadow-lg transition-all"
            >
              {t('getStarted')}
            </Link>
          </div>

          {/* Mobile menu button */}
          <button
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className="md:hidden p-2 rounded-lg hover:bg-gray-100"
            aria-label="Toggle menu"
          >
            {isMobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>
      </div>

      {/* Mobile Menu */}
      <MobileMenu isOpen={isMobileMenuOpen} onClose={() => setIsMobileMenuOpen(false)} />
    </header>
  );
}

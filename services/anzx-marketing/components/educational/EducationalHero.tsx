'use client';

import { OptimizedImage } from '@/components/ui/OptimizedImage';
import InteractiveFluidBackground from '@/components/ui/InteractiveFluidBackground';
import { Clock, BookOpen } from 'lucide-react';

interface EducationalHeroProps {
  title: string;
  subtitle: string;
  heroImage: string;
  readingTime: string;
}

export default function EducationalHero({ title, subtitle, heroImage, readingTime }: EducationalHeroProps) {
  return (
    <div className="relative bg-gradient-to-br from-blue-50 to-indigo-100 overflow-hidden">
      {/* Interactive Fluid Background */}
      <InteractiveFluidBackground className="opacity-50" />
      {/* Background Pattern */}
      <div className="absolute inset-0 bg-grid-pattern opacity-5"></div>
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 lg:py-24">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          {/* Content */}
          <div className="space-y-8">
            <div className="space-y-4">
              <div className="flex items-center gap-3">
                <BookOpen className="h-6 w-6 text-blue-600" />
                <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium">
                  Educational Guide
                </span>
              </div>
              
              <h1 className="text-4xl lg:text-6xl font-bold text-gray-900 leading-tight">
                {title}
              </h1>
              
              <p className="text-xl text-gray-600 leading-relaxed">
                {subtitle}
              </p>
            </div>

            {/* Reading Info */}
            <div className="flex items-center gap-6">
              <div className="flex items-center gap-2 text-gray-500">
                <Clock className="h-4 w-4" />
                <span className="text-sm">{readingTime}</span>
              </div>
              
              <div className="flex items-center gap-2 text-gray-500">
                <BookOpen className="h-4 w-4" />
                <span className="text-sm">Comprehensive Guide</span>
              </div>
            </div>

            {/* Quick Navigation */}
            <div className="bg-white rounded-lg p-6 shadow-sm">
              <h3 className="font-semibold text-gray-900 mb-3">What you'll learn:</h3>
              <ul className="space-y-2 text-gray-600">
                <li>• What AI agents are and how they differ from traditional software</li>
                <li>• The key components that make AI agents intelligent</li>
                <li>• Real-world applications across different industries</li>
                <li>• How to evaluate if AI agents are right for your business</li>
              </ul>
            </div>
          </div>

          {/* Hero Image */}
          <div className="relative">
            <div className="aspect-square relative overflow-hidden rounded-2xl shadow-2xl">
              <OptimizedImage
                src={heroImage}
                alt={title}
                width={600}
                height={600}
                className="w-full h-full object-cover"
                priority
              />
            </div>
            
            {/* Floating Elements */}
            <div className="absolute -top-4 -right-4 bg-white rounded-lg p-4 shadow-lg">
              <div className="text-center">
                <div className="text-lg font-bold text-blue-600">AI</div>
                <div className="text-sm text-gray-500">Powered</div>
              </div>
            </div>
            
            <div className="absolute -bottom-4 -left-4 bg-white rounded-lg p-4 shadow-lg">
              <div className="text-center">
                <div className="text-lg font-bold text-green-600">24/7</div>
                <div className="text-sm text-gray-500">Available</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
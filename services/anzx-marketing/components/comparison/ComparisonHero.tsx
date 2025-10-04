'use client';

import { OptimizedImage } from '@/components/ui/OptimizedImage';
import { Badge } from '@/components/ui/badge';
import InteractiveFluidBackground from '@/components/ui/InteractiveFluidBackground';

interface ComparisonOption {
  name: string;
  description: string;
  logo: string;
  color: string;
}

interface ComparisonHeroProps {
  title: string;
  subtitle: string;
  leftOption: ComparisonOption;
  rightOption: ComparisonOption;
}

export default function ComparisonHero({ title, subtitle, leftOption, rightOption }: ComparisonHeroProps) {
  const getColorClasses = (color: string) => {
    const colorMap = {
      blue: 'bg-blue-100 text-blue-800 border-blue-200',
      gray: 'bg-gray-100 text-gray-800 border-gray-200',
      green: 'bg-green-100 text-green-800 border-green-200',
      purple: 'bg-purple-100 text-purple-800 border-purple-200',
    };
    return colorMap[color as keyof typeof colorMap] || 'bg-gray-100 text-gray-800 border-gray-200';
  };

  return (
    <div className="relative bg-gradient-to-br from-gray-50 to-blue-50 overflow-hidden">
      {/* Interactive Fluid Background */}
      <InteractiveFluidBackground className="opacity-40" />
      {/* Background Pattern */}
      <div className="absolute inset-0 bg-grid-pattern opacity-5"></div>
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 lg:py-24">
        <div className="text-center mb-12">
          <Badge variant="secondary" className="mb-4">
            Comparison Guide
          </Badge>
          <h1 className="text-4xl lg:text-6xl font-bold text-gray-900 leading-tight mb-6">
            {title}
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            {subtitle}
          </p>
        </div>

        {/* Comparison Cards */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 max-w-5xl mx-auto">
          {/* Left Option */}
          <div className={`bg-white rounded-2xl p-8 shadow-lg border-2 ${getColorClasses(leftOption.color)}`}>
            <div className="text-center">
              <div className="w-20 h-20 mx-auto mb-6 bg-white rounded-full flex items-center justify-center shadow-sm">
                <OptimizedImage
                  src={leftOption.logo}
                  alt={leftOption.name}
                  width={48}
                  height={48}
                  className="w-12 h-12"
                />
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">
                {leftOption.name}
              </h2>
              <p className="text-gray-600">
                {leftOption.description}
              </p>
            </div>
          </div>

          {/* VS Divider */}
          <div className="lg:hidden flex items-center justify-center py-4">
            <div className="bg-white rounded-full px-6 py-2 shadow-md">
              <span className="text-lg font-bold text-gray-500">VS</span>
            </div>
          </div>

          {/* Right Option */}
          <div className={`bg-white rounded-2xl p-8 shadow-lg border-2 ${getColorClasses(rightOption.color)}`}>
            <div className="text-center">
              <div className="w-20 h-20 mx-auto mb-6 bg-white rounded-full flex items-center justify-center shadow-sm">
                <OptimizedImage
                  src={rightOption.logo}
                  alt={rightOption.name}
                  width={48}
                  height={48}
                  className="w-12 h-12"
                />
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">
                {rightOption.name}
              </h2>
              <p className="text-gray-600">
                {rightOption.description}
              </p>
            </div>
          </div>
        </div>

        {/* VS Divider for Desktop */}
        <div className="hidden lg:block absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
          <div className="bg-white rounded-full w-16 h-16 flex items-center justify-center shadow-lg border-2 border-gray-200">
            <span className="text-xl font-bold text-gray-500">VS</span>
          </div>
        </div>

        {/* Quick Summary */}
        <div className="mt-16 text-center">
          <p className="text-gray-600 max-w-4xl mx-auto">
            This comprehensive comparison will help you understand the key differences, benefits, 
            and use cases for each approach, enabling you to make an informed decision for your 
            business automation needs.
          </p>
        </div>
      </div>
    </div>
  );
}
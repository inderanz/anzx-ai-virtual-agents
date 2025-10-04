'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { CheckCircle, X } from 'lucide-react';

interface ComparisonOption {
  name: string;
  color: string;
}

interface ComparisonFeaturesProps {
  leftOption: ComparisonOption;
  rightOption: ComparisonOption;
  type: 'ai-vs-rpa' | 'ai-vs-automation';
}

export default function ComparisonFeatures({ leftOption, rightOption, type }: ComparisonFeaturesProps) {
  const getFeatureData = () => {
    if (type === 'ai-vs-rpa') {
      return {
        leftFeatures: [
          'Natural language understanding',
          'Context-aware decision making',
          'Continuous learning and improvement',
          'Complex problem solving',
          'Exception handling',
          'Multi-modal data processing',
          'Predictive capabilities',
          'Autonomous operation',
        ],
        rightFeatures: [
          'Fast implementation',
          'Predictable outcomes',
          'Lower initial cost',
          'Simple maintenance',
          'Screen scraping capabilities',
          'Legacy system integration',
          'Audit trail',
          'Rule-based reliability',
        ],
        leftLimitations: [
          'Higher initial investment',
          'Requires AI expertise',
          'Less predictable behavior',
          'Longer implementation time',
        ],
        rightLimitations: [
          'No learning capability',
          'Breaks on UI changes',
          'Limited to simple processes',
          'High maintenance overhead',
          'Cannot handle exceptions',
          'No natural language processing',
        ],
      };
    } else {
      return {
        leftFeatures: [
          'Intelligent decision making',
          'Adaptive behavior',
          'Natural language processing',
          'Continuous improvement',
          'Context understanding',
          'Creative problem solving',
          'Multi-agent coordination',
          'Self-optimization',
        ],
        rightFeatures: [
          'Simple setup and configuration',
          'Predictable performance',
          'Lower complexity',
          'Established best practices',
          'Wide tool availability',
          'Clear debugging process',
          'Deterministic outcomes',
          'Lower skill requirements',
        ],
        leftLimitations: [
          'Requires specialized knowledge',
          'Higher computational resources',
          'Less predictable outcomes',
          'Complex debugging',
        ],
        rightLimitations: [
          'No adaptability',
          'Manual updates required',
          'Limited problem-solving',
          'Cannot handle complexity',
          'No learning capability',
          'Rigid workflows',
        ],
      };
    }
  };

  const featureData = getFeatureData();

  return (
    <section>
      <div className="text-center mb-12">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">
          Strengths & Limitations
        </h2>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto">
          Understanding the unique strengths and limitations of each approach 
          helps you make the right choice for your specific use case.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Left Option */}
        <Card className="border-blue-200 border-2">
          <CardHeader className="text-center">
            <CardTitle className="text-2xl text-blue-600">
              {leftOption.name}
            </CardTitle>
          </CardHeader>
          
          <CardContent className="space-y-6">
            {/* Strengths */}
            <div>
              <h4 className="font-semibold text-gray-900 mb-3 text-green-700">
                ✓ Key Strengths
              </h4>
              <ul className="space-y-2">
                {featureData.leftFeatures.map((feature, index) => (
                  <li key={index} className="flex items-start gap-2 text-sm text-gray-600">
                    <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                    {feature}
                  </li>
                ))}
              </ul>
            </div>

            {/* Limitations */}
            <div>
              <h4 className="font-semibold text-gray-900 mb-3 text-red-700">
                ⚠ Limitations
              </h4>
              <ul className="space-y-2">
                {featureData.leftLimitations.map((limitation, index) => (
                  <li key={index} className="flex items-start gap-2 text-sm text-gray-600">
                    <X className="h-4 w-4 text-red-500 mt-0.5 flex-shrink-0" />
                    {limitation}
                  </li>
                ))}
              </ul>
            </div>
          </CardContent>
        </Card>

        {/* Right Option */}
        <Card className="border-gray-200 border-2">
          <CardHeader className="text-center">
            <CardTitle className="text-2xl text-gray-600">
              {rightOption.name}
            </CardTitle>
          </CardHeader>
          
          <CardContent className="space-y-6">
            {/* Strengths */}
            <div>
              <h4 className="font-semibold text-gray-900 mb-3 text-green-700">
                ✓ Key Strengths
              </h4>
              <ul className="space-y-2">
                {featureData.rightFeatures.map((feature, index) => (
                  <li key={index} className="flex items-start gap-2 text-sm text-gray-600">
                    <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                    {feature}
                  </li>
                ))}
              </ul>
            </div>

            {/* Limitations */}
            <div>
              <h4 className="font-semibold text-gray-900 mb-3 text-red-700">
                ⚠ Limitations
              </h4>
              <ul className="space-y-2">
                {featureData.rightLimitations.map((limitation, index) => (
                  <li key={index} className="flex items-start gap-2 text-sm text-gray-600">
                    <X className="h-4 w-4 text-red-500 mt-0.5 flex-shrink-0" />
                    {limitation}
                  </li>
                ))}
              </ul>
            </div>
          </CardContent>
        </Card>
      </div>
    </section>
  );
}
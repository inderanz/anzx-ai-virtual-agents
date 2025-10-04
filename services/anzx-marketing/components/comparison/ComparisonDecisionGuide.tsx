'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { CheckCircle, ArrowRight } from 'lucide-react';

interface ComparisonOption {
  name: string;
  color: string;
}

interface ComparisonDecisionGuideProps {
  leftOption: ComparisonOption;
  rightOption: ComparisonOption;
  type: 'ai-vs-rpa' | 'ai-vs-automation';
}

export default function ComparisonDecisionGuide({ leftOption, rightOption, type }: ComparisonDecisionGuideProps) {
  const getDecisionCriteria = () => {
    if (type === 'ai-vs-rpa') {
      return {
        leftCriteria: [
          'Need to handle unstructured data',
          'Require natural language processing',
          'Want continuous improvement over time',
          'Need to handle exceptions intelligently',
          'Have complex decision-making requirements',
          'Want to scale beyond simple processes',
        ],
        rightCriteria: [
          'Have well-defined, stable processes',
          'Need quick implementation',
          'Work with structured data only',
          'Require predictable outcomes',
          'Have limited budget for initial investment',
          'Need simple screen automation',
        ],
      };
    } else {
      return {
        leftCriteria: [
          'Need adaptive, intelligent behavior',
          'Want systems that learn and improve',
          'Require complex decision making',
          'Need natural language capabilities',
          'Have dynamic, changing requirements',
          'Want long-term competitive advantage',
        ],
        rightCriteria: [
          'Have simple, repetitive tasks',
          'Need predictable, consistent results',
          'Want quick setup and deployment',
          'Have limited technical resources',
          'Need basic workflow automation',
          'Prefer lower complexity solutions',
        ],
      };
    }
  };

  const decisionCriteria = getDecisionCriteria();

  return (
    <section>
      <div className="text-center mb-12">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">
          Decision Guide: Which Should You Choose?
        </h2>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto">
          Use these criteria to determine which approach is best suited for your 
          specific business needs and organizational context.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12">
        {/* Choose Left Option */}
        <Card className="border-blue-200 border-2">
          <CardHeader className="text-center">
            <CardTitle className="text-xl text-blue-600">
              Choose {leftOption.name} If You:
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-3">
              {decisionCriteria.leftCriteria.map((criterion, index) => (
                <li key={index} className="flex items-start gap-3">
                  <CheckCircle className="h-5 w-5 text-blue-500 mt-0.5 flex-shrink-0" />
                  <span className="text-gray-700">{criterion}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>

        {/* Choose Right Option */}
        <Card className="border-gray-200 border-2">
          <CardHeader className="text-center">
            <CardTitle className="text-xl text-gray-600">
              Choose {rightOption.name} If You:
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-3">
              {decisionCriteria.rightCriteria.map((criterion, index) => (
                <li key={index} className="flex items-start gap-3">
                  <CheckCircle className="h-5 w-5 text-gray-500 mt-0.5 flex-shrink-0" />
                  <span className="text-gray-700">{criterion}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      </div>

      {/* Hybrid Approach */}
      <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-2xl p-8">
        <h3 className="text-2xl font-bold text-gray-900 mb-6 text-center">
          Consider a Hybrid Approach
        </h3>
        
        <div className="max-w-4xl mx-auto">
          <p className="text-gray-600 mb-6 text-center">
            Many organizations benefit from using both approaches for different use cases. 
            Start with the simpler solution and gradually introduce more advanced capabilities.
          </p>
          
          <div className="flex items-center justify-center gap-4 mb-6">
            <div className="bg-white rounded-lg px-4 py-2 shadow-sm">
              <span className="text-gray-600">Start Simple</span>
            </div>
            <ArrowRight className="h-5 w-5 text-gray-400" />
            <div className="bg-white rounded-lg px-4 py-2 shadow-sm">
              <span className="text-gray-600">Add Complexity</span>
            </div>
            <ArrowRight className="h-5 w-5 text-gray-400" />
            <div className="bg-white rounded-lg px-4 py-2 shadow-sm">
              <span className="text-gray-600">Scale Intelligence</span>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white rounded-lg p-4 text-center">
              <h4 className="font-semibold text-gray-900 mb-2">Phase 1</h4>
              <p className="text-sm text-gray-600">
                Use {rightOption.name.toLowerCase()} for simple, well-defined processes
              </p>
            </div>
            <div className="bg-white rounded-lg p-4 text-center">
              <h4 className="font-semibold text-gray-900 mb-2">Phase 2</h4>
              <p className="text-sm text-gray-600">
                Introduce {leftOption.name.toLowerCase()} for complex scenarios
              </p>
            </div>
            <div className="bg-white rounded-lg p-4 text-center">
              <h4 className="font-semibold text-gray-900 mb-2">Phase 3</h4>
              <p className="text-sm text-gray-600">
                Scale intelligent automation across the organization
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
'use client';

import { Check, X, Minus } from 'lucide-react';

interface ComparisonOption {
  name: string;
  color: string;
}

interface ComparisonTableProps {
  leftOption: ComparisonOption;
  rightOption: ComparisonOption;
  type: 'ai-vs-rpa' | 'ai-vs-automation';
}

export default function ComparisonTable({ leftOption, rightOption, type }: ComparisonTableProps) {
  const getComparisonData = () => {
    if (type === 'ai-vs-rpa') {
      return [
        {
          category: 'Intelligence & Decision Making',
          leftValue: { status: 'excellent', text: 'Advanced reasoning and context understanding' },
          rightValue: { status: 'limited', text: 'Rule-based decisions only' },
        },
        {
          category: 'Adaptability',
          leftValue: { status: 'excellent', text: 'Learns and adapts automatically' },
          rightValue: { status: 'poor', text: 'Requires manual updates' },
        },
        {
          category: 'Natural Language Processing',
          leftValue: { status: 'excellent', text: 'Advanced NLP capabilities' },
          rightValue: { status: 'poor', text: 'Limited or no NLP' },
        },
        {
          category: 'Complex Problem Solving',
          leftValue: { status: 'excellent', text: 'Handles multi-step, complex scenarios' },
          rightValue: { status: 'limited', text: 'Simple, linear processes only' },
        },
        {
          category: 'Implementation Speed',
          leftValue: { status: 'limited', text: '2-6 months for complex scenarios' },
          rightValue: { status: 'excellent', text: '2-8 weeks for simple processes' },
        },
        {
          category: 'Predictability',
          leftValue: { status: 'limited', text: 'Adaptive behavior may vary' },
          rightValue: { status: 'excellent', text: 'Highly predictable outcomes' },
        },
        {
          category: 'Cost (Initial)',
          leftValue: { status: 'limited', text: 'Higher upfront investment' },
          rightValue: { status: 'excellent', text: 'Lower initial costs' },
        },
        {
          category: 'Cost (Long-term)',
          leftValue: { status: 'excellent', text: 'Lower ongoing costs, scales well' },
          rightValue: { status: 'limited', text: 'Higher maintenance costs' },
        },
        {
          category: 'Exception Handling',
          leftValue: { status: 'excellent', text: 'Intelligent exception handling' },
          rightValue: { status: 'poor', text: 'Breaks on unexpected scenarios' },
        },
        {
          category: 'Scalability',
          leftValue: { status: 'excellent', text: 'Scales to handle any complexity' },
          rightValue: { status: 'limited', text: 'Limited by rule complexity' },
        },
      ];
    } else {
      return [
        {
          category: 'Decision Making Capability',
          leftValue: { status: 'excellent', text: 'Autonomous, context-aware decisions' },
          rightValue: { status: 'limited', text: 'Pre-programmed decision trees' },
        },
        {
          category: 'Learning & Improvement',
          leftValue: { status: 'excellent', text: 'Continuous learning from data' },
          rightValue: { status: 'poor', text: 'No learning capability' },
        },
        {
          category: 'Flexibility',
          leftValue: { status: 'excellent', text: 'Adapts to changing requirements' },
          rightValue: { status: 'limited', text: 'Requires reprogramming for changes' },
        },
        {
          category: 'Natural Language Understanding',
          leftValue: { status: 'excellent', text: 'Advanced language comprehension' },
          rightValue: { status: 'poor', text: 'Keyword-based processing only' },
        },
        {
          category: 'Setup Complexity',
          leftValue: { status: 'limited', text: 'Requires AI expertise and training' },
          rightValue: { status: 'excellent', text: 'Straightforward configuration' },
        },
        {
          category: 'Maintenance Requirements',
          leftValue: { status: 'excellent', text: 'Self-improving, minimal maintenance' },
          rightValue: { status: 'limited', text: 'Regular updates and maintenance needed' },
        },
        {
          category: 'Error Handling',
          leftValue: { status: 'excellent', text: 'Intelligent error recovery' },
          rightValue: { status: 'limited', text: 'Basic error handling only' },
        },
        {
          category: 'Integration Complexity',
          leftValue: { status: 'limited', text: 'May require custom integrations' },
          rightValue: { status: 'excellent', text: 'Standard API integrations' },
        },
        {
          category: 'Performance Predictability',
          leftValue: { status: 'limited', text: 'Performance may vary with learning' },
          rightValue: { status: 'excellent', text: 'Consistent, predictable performance' },
        },
        {
          category: 'Long-term Value',
          leftValue: { status: 'excellent', text: 'Increases value over time' },
          rightValue: { status: 'limited', text: 'Static value, may become outdated' },
        },
      ];
    }
  };

  const comparisonData = getComparisonData();

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'excellent':
        return <Check className="h-5 w-5 text-green-500" />;
      case 'limited':
        return <Minus className="h-5 w-5 text-yellow-500" />;
      case 'poor':
        return <X className="h-5 w-5 text-red-500" />;
      default:
        return <Minus className="h-5 w-5 text-gray-400" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'excellent':
        return 'text-green-700 bg-green-50';
      case 'limited':
        return 'text-yellow-700 bg-yellow-50';
      case 'poor':
        return 'text-red-700 bg-red-50';
      default:
        return 'text-gray-700 bg-gray-50';
    }
  };

  return (
    <section>
      <div className="text-center mb-12">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">
          Detailed Feature Comparison
        </h2>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto">
          Compare key capabilities and characteristics side by side to understand 
          which approach best fits your specific needs.
        </p>
      </div>

      <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-4 text-left font-semibold text-gray-900 w-1/3">
                  Feature
                </th>
                <th className="px-6 py-4 text-center font-semibold text-blue-600 w-1/3">
                  {leftOption.name}
                </th>
                <th className="px-6 py-4 text-center font-semibold text-gray-600 w-1/3">
                  {rightOption.name}
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {comparisonData.map((row, index) => (
                <tr key={index} className="hover:bg-gray-50">
                  <td className="px-6 py-4 font-medium text-gray-900">
                    {row.category}
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex flex-col items-center gap-2">
                      {getStatusIcon(row.leftValue.status)}
                      <div className={`text-xs text-center px-2 py-1 rounded ${getStatusColor(row.leftValue.status)}`}>
                        {row.leftValue.text}
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex flex-col items-center gap-2">
                      {getStatusIcon(row.rightValue.status)}
                      <div className={`text-xs text-center px-2 py-1 rounded ${getStatusColor(row.rightValue.status)}`}>
                        {row.rightValue.text}
                      </div>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Legend */}
      <div className="mt-6 flex justify-center">
        <div className="flex items-center gap-6 text-sm">
          <div className="flex items-center gap-2">
            <Check className="h-4 w-4 text-green-500" />
            <span className="text-gray-600">Excellent</span>
          </div>
          <div className="flex items-center gap-2">
            <Minus className="h-4 w-4 text-yellow-500" />
            <span className="text-gray-600">Limited</span>
          </div>
          <div className="flex items-center gap-2">
            <X className="h-4 w-4 text-red-500" />
            <span className="text-gray-600">Poor/None</span>
          </div>
        </div>
      </div>
    </section>
  );
}
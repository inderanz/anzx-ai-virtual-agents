'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

interface ComparisonOption {
  name: string;
  color: string;
}

interface ComparisonUseCasesProps {
  leftOption: ComparisonOption;
  rightOption: ComparisonOption;
  type: 'ai-vs-rpa' | 'ai-vs-automation';
}

export default function ComparisonUseCases({ leftOption, rightOption, type }: ComparisonUseCasesProps) {
  const getUseCaseData = () => {
    if (type === 'ai-vs-rpa') {
      return {
        leftUseCases: [
          {
            title: 'Customer Service Automation',
            description: 'Handle complex customer inquiries with natural language understanding',
            complexity: 'High',
            roi: '6-12 months',
          },
          {
            title: 'Intelligent Document Processing',
            description: 'Extract and process information from unstructured documents',
            complexity: 'High',
            roi: '3-6 months',
          },
          {
            title: 'Sales Lead Qualification',
            description: 'Analyze and qualify leads based on multiple data points',
            complexity: 'Medium',
            roi: '4-8 months',
          },
        ],
        rightUseCases: [
          {
            title: 'Data Entry Automation',
            description: 'Transfer data between systems following fixed rules',
            complexity: 'Low',
            roi: '1-3 months',
          },
          {
            title: 'Report Generation',
            description: 'Generate standardized reports from structured data',
            complexity: 'Low',
            roi: '1-2 months',
          },
          {
            title: 'Invoice Processing',
            description: 'Process invoices with consistent format and structure',
            complexity: 'Medium',
            roi: '2-4 months',
          },
        ],
      };
    } else {
      return {
        leftUseCases: [
          {
            title: 'Dynamic Customer Support',
            description: 'Adapt responses based on customer context and history',
            complexity: 'High',
            roi: '6-12 months',
          },
          {
            title: 'Predictive Maintenance',
            description: 'Predict and prevent equipment failures using AI',
            complexity: 'High',
            roi: '8-15 months',
          },
          {
            title: 'Content Personalization',
            description: 'Personalize content based on user behavior and preferences',
            complexity: 'Medium',
            roi: '4-8 months',
          },
        ],
        rightUseCases: [
          {
            title: 'Scheduled Backups',
            description: 'Automated system backups on predefined schedules',
            complexity: 'Low',
            roi: '1 month',
          },
          {
            title: 'Email Notifications',
            description: 'Send notifications based on system events',
            complexity: 'Low',
            roi: '2-4 weeks',
          },
          {
            title: 'File Processing',
            description: 'Process files when they arrive in specific folders',
            complexity: 'Medium',
            roi: '1-2 months',
          },
        ],
      };
    }
  };

  const useCaseData = getUseCaseData();

  const getComplexityColor = (complexity: string) => {
    switch (complexity) {
      case 'Low': return 'bg-green-100 text-green-800';
      case 'Medium': return 'bg-yellow-100 text-yellow-800';
      case 'High': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <section>
      <div className="text-center mb-12">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">
          Ideal Use Cases
        </h2>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto">
          Each approach excels in different scenarios. Here are the most suitable 
          use cases for each technology.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Left Option Use Cases */}
        <div>
          <h3 className="text-2xl font-bold text-blue-600 mb-6 text-center">
            Best for {leftOption.name}
          </h3>
          <div className="space-y-6">
            {useCaseData.leftUseCases.map((useCase, index) => (
              <Card key={index} className="border-blue-200">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <CardTitle className="text-lg">
                      {useCase.title}
                    </CardTitle>
                    <Badge className={getComplexityColor(useCase.complexity)}>
                      {useCase.complexity}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-600 mb-3">
                    {useCase.description}
                  </p>
                  <div className="text-sm text-gray-500">
                    <strong>Typical ROI Timeline:</strong> {useCase.roi}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Right Option Use Cases */}
        <div>
          <h3 className="text-2xl font-bold text-gray-600 mb-6 text-center">
            Best for {rightOption.name}
          </h3>
          <div className="space-y-6">
            {useCaseData.rightUseCases.map((useCase, index) => (
              <Card key={index} className="border-gray-200">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <CardTitle className="text-lg">
                      {useCase.title}
                    </CardTitle>
                    <Badge className={getComplexityColor(useCase.complexity)}>
                      {useCase.complexity}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-600 mb-3">
                    {useCase.description}
                  </p>
                  <div className="text-sm text-gray-500">
                    <strong>Typical ROI Timeline:</strong> {useCase.roi}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
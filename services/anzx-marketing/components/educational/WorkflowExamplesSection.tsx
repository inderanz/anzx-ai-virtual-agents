'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ArrowRight, CheckCircle } from 'lucide-react';

interface WorkflowExamplesSectionProps {
  id: string;
}

export default function WorkflowExamplesSection({ id }: WorkflowExamplesSectionProps) {
  const examples = [
    {
      title: 'Employee Onboarding Workflow',
      industry: 'Human Resources',
      description: 'Automate the complete employee onboarding process from offer acceptance to first day.',
      steps: [
        'New hire accepts job offer',
        'System creates employee profile',
        'Sends welcome email with checklist',
        'Orders equipment and access cards',
        'Schedules orientation sessions',
        'Assigns buddy and manager',
        'Tracks completion of required tasks',
      ],
      results: ['75% faster onboarding', '90% task completion rate', '95% new hire satisfaction'],
      complexity: 'Medium',
    },
    {
      title: 'Invoice Processing Workflow',
      industry: 'Finance & Accounting',
      description: 'Streamline invoice approval and payment processing with automated routing.',
      steps: [
        'Invoice received via email/upload',
        'OCR extracts key information',
        'System validates against PO',
        'Routes to appropriate approver',
        'Sends reminders for pending approvals',
        'Processes payment automatically',
        'Updates accounting system',
      ],
      results: ['80% processing time reduction', '95% accuracy improvement', '60% cost savings'],
      complexity: 'High',
    },
    {
      title: 'Customer Support Ticket Workflow',
      industry: 'Customer Service',
      description: 'Automatically categorize, prioritize, and route customer support requests.',
      steps: [
        'Customer submits support request',
        'AI categorizes issue type',
        'System assigns priority level',
        'Routes to appropriate team',
        'Sends acknowledgment to customer',
        'Tracks resolution progress',
        'Collects feedback after resolution',
      ],
      results: ['50% faster response time', '85% first-contact resolution', '92% customer satisfaction'],
      complexity: 'Medium',
    },
  ];

  const getComplexityColor = (complexity: string) => {
    switch (complexity) {
      case 'Medium': return 'bg-yellow-100 text-yellow-800';
      case 'High': return 'bg-red-100 text-red-800';
      default: return 'bg-green-100 text-green-800';
    }
  };

  return (
    <section id={id} className="scroll-mt-8">
      <div className="space-y-8">
        <div>
          <h2 className="text-3xl font-bold text-gray-900 mb-6">
            Real-World Workflow Examples
          </h2>
          
          <div className="prose prose-lg max-w-none text-gray-600 mb-8">
            <p>
              These detailed examples show how workflow automation works in practice across 
              different business functions and industries.
            </p>
          </div>
        </div>

        <div className="space-y-8">
          {examples.map((example, index) => (
            <Card key={index} className="hover:shadow-lg transition-shadow duration-300">
              <CardHeader>
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <Badge variant="secondary" className="mb-2">
                      {example.industry}
                    </Badge>
                    <CardTitle className="text-xl">
                      {example.title}
                    </CardTitle>
                  </div>
                  <Badge className={getComplexityColor(example.complexity)}>
                    {example.complexity}
                  </Badge>
                </div>
                <p className="text-gray-600">
                  {example.description}
                </p>
              </CardHeader>
              
              <CardContent className="space-y-6">
                <div>
                  <h4 className="font-semibold text-gray-900 mb-3">Workflow Steps:</h4>
                  <div className="space-y-3">
                    {example.steps.map((step, stepIndex) => (
                      <div key={stepIndex} className="flex items-start gap-3">
                        <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                          <span className="text-blue-600 text-xs font-bold">{stepIndex + 1}</span>
                        </div>
                        <span className="text-gray-600 text-sm">{step}</span>
                        {stepIndex < example.steps.length - 1 && (
                          <ArrowRight className="h-4 w-4 text-gray-300 mt-0.5" />
                        )}
                      </div>
                    ))}
                  </div>
                </div>

                <div className="bg-green-50 rounded-lg p-4">
                  <h4 className="font-semibold text-gray-900 mb-3">Results Achieved:</h4>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {example.results.map((result, resultIndex) => (
                      <div key={resultIndex} className="flex items-center gap-2">
                        <CheckCircle className="h-4 w-4 text-green-500 flex-shrink-0" />
                        <span className="text-sm text-gray-600">{result}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
}
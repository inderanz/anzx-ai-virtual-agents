'use client';

import { Card, CardContent } from '@/components/ui/card';
import { ArrowRight, Zap, Clock, Users, Target, Repeat, CheckCircle } from 'lucide-react';

interface WorkflowDefinitionSectionProps {
  id: string;
}

export default function WorkflowDefinitionSection({ id }: WorkflowDefinitionSectionProps) {
  const workflowComponents = [
    {
      icon: Target,
      title: 'Triggers',
      description: 'Events that start the workflow',
      examples: ['New email received', 'Form submission', 'Time-based schedule', 'Data change'],
    },
    {
      icon: ArrowRight,
      title: 'Actions',
      description: 'Tasks performed automatically',
      examples: ['Send notifications', 'Update databases', 'Create documents', 'Process payments'],
    },
    {
      icon: Repeat,
      title: 'Conditions',
      description: 'Logic that determines the flow',
      examples: ['If-then statements', 'Approval gates', 'Data validation', 'Business rules'],
    },
    {
      icon: CheckCircle,
      title: 'Outcomes',
      description: 'Results and next steps',
      examples: ['Task completion', 'Notifications sent', 'Records updated', 'Reports generated'],
    },
  ];

  const beforeAfter = {
    before: {
      title: 'Manual Process',
      steps: [
        'Employee receives customer inquiry via email',
        'Manually logs inquiry in CRM system',
        'Assigns ticket to appropriate department',
        'Sends acknowledgment email to customer',
        'Tracks progress through multiple systems',
        'Manually updates customer on resolution',
      ],
      timeRequired: '45-60 minutes per inquiry',
      errorRate: '15-20% human error rate',
    },
    after: {
      title: 'Automated Workflow',
      steps: [
        'System automatically detects new inquiry',
        'AI categorizes and prioritizes the request',
        'Auto-assigns to best available agent',
        'Sends instant acknowledgment to customer',
        'Updates all systems simultaneously',
        'Provides automated status updates',
      ],
      timeRequired: '2-3 minutes per inquiry',
      errorRate: '<1% error rate',
    },
  };

  return (
    <section id={id} className="scroll-mt-8">
      <div className="space-y-8">
        <div>
          <h2 className="text-3xl font-bold text-gray-900 mb-6">
            What is Workflow Automation?
          </h2>
          
          <div className="prose prose-lg max-w-none text-gray-600 space-y-4">
            <p>
              <strong>Workflow automation</strong> is the process of using technology to streamline 
              and automate repetitive business processes. It involves creating digital workflows 
              that can execute tasks, make decisions, and move information between systems without 
              human intervention.
            </p>
            
            <p>
              Think of workflow automation as creating a digital assembly line for your business 
              processes. Just as manufacturing assembly lines revolutionized production by breaking 
              down complex tasks into efficient, repeatable steps, workflow automation does the 
              same for your business operations.
            </p>
          </div>
        </div>

        {/* Workflow Components */}
        <div>
          <h3 className="text-2xl font-bold text-gray-900 mb-6">
            Key Components of Automated Workflows
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {workflowComponents.map((component, index) => {
              const IconComponent = component.icon;
              
              return (
                <Card key={index} className="text-center hover:shadow-md transition-shadow duration-300">
                  <CardContent className="p-6">
                    <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                      <IconComponent className="h-6 w-6 text-blue-600" />
                    </div>
                    
                    <h4 className="font-semibold text-gray-900 mb-2">
                      {component.title}
                    </h4>
                    
                    <p className="text-gray-600 text-sm mb-3">
                      {component.description}
                    </p>
                    
                    <div className="space-y-1">
                      {component.examples.map((example, exampleIndex) => (
                        <div key={exampleIndex} className="text-xs text-gray-500 bg-gray-50 rounded px-2 py-1">
                          {example}
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </div>

        {/* Before vs After Example */}
        <div>
          <h3 className="text-2xl font-bold text-gray-900 mb-6">
            Before vs After: Customer Service Workflow
          </h3>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Before */}
            <Card className="border-red-200 border-2">
              <CardContent className="p-6">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-8 h-8 bg-red-100 rounded-full flex items-center justify-center">
                    <Users className="h-4 w-4 text-red-600" />
                  </div>
                  <h4 className="text-lg font-semibold text-red-700">
                    {beforeAfter.before.title}
                  </h4>
                </div>
                
                <div className="space-y-3 mb-6">
                  {beforeAfter.before.steps.map((step, stepIndex) => (
                    <div key={stepIndex} className="flex items-start gap-3">
                      <div className="w-6 h-6 bg-red-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                        <span className="text-red-600 text-xs font-bold">{stepIndex + 1}</span>
                      </div>
                      <span className="text-gray-600 text-sm">{step}</span>
                    </div>
                  ))}
                </div>
                
                <div className="space-y-2 bg-red-50 rounded-lg p-4">
                  <div className="flex items-center gap-2">
                    <Clock className="h-4 w-4 text-red-600" />
                    <span className="text-sm font-medium text-red-700">
                      {beforeAfter.before.timeRequired}
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Zap className="h-4 w-4 text-red-600" />
                    <span className="text-sm font-medium text-red-700">
                      {beforeAfter.before.errorRate}
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* After */}
            <Card className="border-green-200 border-2">
              <CardContent className="p-6">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                    <Zap className="h-4 w-4 text-green-600" />
                  </div>
                  <h4 className="text-lg font-semibold text-green-700">
                    {beforeAfter.after.title}
                  </h4>
                </div>
                
                <div className="space-y-3 mb-6">
                  {beforeAfter.after.steps.map((step, stepIndex) => (
                    <div key={stepIndex} className="flex items-start gap-3">
                      <div className="w-6 h-6 bg-green-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                        <span className="text-green-600 text-xs font-bold">{stepIndex + 1}</span>
                      </div>
                      <span className="text-gray-600 text-sm">{step}</span>
                    </div>
                  ))}
                </div>
                
                <div className="space-y-2 bg-green-50 rounded-lg p-4">
                  <div className="flex items-center gap-2">
                    <Clock className="h-4 w-4 text-green-600" />
                    <span className="text-sm font-medium text-green-700">
                      {beforeAfter.after.timeRequired}
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Zap className="h-4 w-4 text-green-600" />
                    <span className="text-sm font-medium text-green-700">
                      {beforeAfter.after.errorRate}
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
          
          <div className="mt-6 text-center">
            <div className="bg-blue-50 rounded-lg p-6">
              <h4 className="font-semibold text-gray-900 mb-2">Impact Summary</h4>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">95%</div>
                  <div className="text-sm text-gray-600">Time Reduction</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">90%</div>
                  <div className="text-sm text-gray-600">Error Reduction</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">24/7</div>
                  <div className="text-sm text-gray-600">Availability</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Key Principles */}
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-2xl p-8">
          <h3 className="text-2xl font-bold text-gray-900 mb-6">
            Core Principles of Effective Workflow Automation
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <div className="flex items-start gap-3">
                <CheckCircle className="h-5 w-5 text-green-500 mt-1 flex-shrink-0" />
                <div>
                  <h4 className="font-semibold text-gray-900">Start Simple</h4>
                  <p className="text-gray-600 text-sm">Begin with straightforward, repetitive tasks before tackling complex processes.</p>
                </div>
              </div>
              
              <div className="flex items-start gap-3">
                <CheckCircle className="h-5 w-5 text-green-500 mt-1 flex-shrink-0" />
                <div>
                  <h4 className="font-semibold text-gray-900">Focus on Value</h4>
                  <p className="text-gray-600 text-sm">Prioritize workflows that save the most time or reduce the most errors.</p>
                </div>
              </div>
              
              <div className="flex items-start gap-3">
                <CheckCircle className="h-5 w-5 text-green-500 mt-1 flex-shrink-0" />
                <div>
                  <h4 className="font-semibold text-gray-900">Maintain Flexibility</h4>
                  <p className="text-gray-600 text-sm">Design workflows that can adapt as business requirements change.</p>
                </div>
              </div>
            </div>
            
            <div className="space-y-4">
              <div className="flex items-start gap-3">
                <CheckCircle className="h-5 w-5 text-green-500 mt-1 flex-shrink-0" />
                <div>
                  <h4 className="font-semibold text-gray-900">Monitor Performance</h4>
                  <p className="text-gray-600 text-sm">Track metrics to ensure workflows are delivering expected benefits.</p>
                </div>
              </div>
              
              <div className="flex items-start gap-3">
                <CheckCircle className="h-5 w-5 text-green-500 mt-1 flex-shrink-0" />
                <div>
                  <h4 className="font-semibold text-gray-900">Include Human Oversight</h4>
                  <p className="text-gray-600 text-sm">Maintain human checkpoints for critical decisions and exception handling.</p>
                </div>
              </div>
              
              <div className="flex items-start gap-3">
                <CheckCircle className="h-5 w-5 text-green-500 mt-1 flex-shrink-0" />
                <div>
                  <h4 className="font-semibold text-gray-900">Continuous Improvement</h4>
                  <p className="text-gray-600 text-sm">Regularly review and optimize workflows based on performance data.</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
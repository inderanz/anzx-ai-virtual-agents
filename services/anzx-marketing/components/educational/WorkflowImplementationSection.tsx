'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { CheckCircle, AlertTriangle, Target } from 'lucide-react';

interface WorkflowImplementationSectionProps {
  id: string;
}

export default function WorkflowImplementationSection({ id }: WorkflowImplementationSectionProps) {
  const implementationSteps = [
    {
      phase: 'Discovery & Planning',
      duration: '1-2 weeks',
      activities: [
        'Map current processes and identify pain points',
        'Prioritize automation opportunities by ROI',
        'Define success metrics and KPIs',
        'Assess technical requirements and constraints',
      ],
      deliverables: ['Process maps', 'Automation roadmap', 'Success criteria'],
    },
    {
      phase: 'Design & Prototype',
      duration: '2-4 weeks',
      activities: [
        'Design workflow logic and decision points',
        'Create wireframes and user interfaces',
        'Build and test prototype workflows',
        'Validate with stakeholders and end users',
      ],
      deliverables: ['Workflow designs', 'Prototypes', 'User feedback'],
    },
    {
      phase: 'Development & Testing',
      duration: '4-8 weeks',
      activities: [
        'Build production workflows and integrations',
        'Conduct thorough testing and quality assurance',
        'Create documentation and training materials',
        'Prepare deployment and rollback procedures',
      ],
      deliverables: ['Production workflows', 'Test results', 'Documentation'],
    },
    {
      phase: 'Deployment & Monitoring',
      duration: 'Ongoing',
      activities: [
        'Deploy workflows to production environment',
        'Monitor performance and user adoption',
        'Collect feedback and identify improvements',
        'Scale successful workflows to other areas',
      ],
      deliverables: ['Live workflows', 'Performance reports', 'Optimization plan'],
    },
  ];

  const bestPractices = [
    {
      title: 'Start Small and Scale',
      description: 'Begin with simple, high-impact workflows before tackling complex processes.',
      tips: ['Choose processes with clear rules', 'Focus on repetitive tasks', 'Measure results before expanding'],
    },
    {
      title: 'Involve End Users',
      description: 'Engage the people who will use the automated workflows in design and testing.',
      tips: ['Conduct user interviews', 'Include users in testing', 'Provide adequate training'],
    },
    {
      title: 'Plan for Exceptions',
      description: 'Design workflows to handle edge cases and unexpected scenarios gracefully.',
      tips: ['Define exception handling rules', 'Include human escalation paths', 'Monitor for new edge cases'],
    },
    {
      title: 'Monitor and Optimize',
      description: 'Continuously track performance and make improvements based on data.',
      tips: ['Set up monitoring dashboards', 'Regular performance reviews', 'Iterative improvements'],
    },
  ];

  return (
    <section id={id} className="scroll-mt-8">
      <div className="space-y-8">
        <div>
          <h2 className="text-3xl font-bold text-gray-900 mb-6">
            Implementation Strategy & Best Practices
          </h2>
          
          <div className="prose prose-lg max-w-none text-gray-600 mb-8">
            <p>
              Successful workflow automation requires careful planning, phased implementation, 
              and continuous optimization. Follow these proven strategies to maximize your success.
            </p>
          </div>
        </div>

        {/* Implementation Steps */}
        <div>
          <h3 className="text-2xl font-bold text-gray-900 mb-6">
            Implementation Phases
          </h3>
          
          <div className="space-y-6">
            {implementationSteps.map((step, index) => (
              <Card key={index} className="hover:shadow-md transition-shadow duration-300">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg flex items-center gap-3">
                      <div className="w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold text-sm">
                        {index + 1}
                      </div>
                      {step.phase}
                    </CardTitle>
                    <Badge variant="secondary">
                      {step.duration}
                    </Badge>
                  </div>
                </CardHeader>
                
                <CardContent className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-3">Key Activities:</h4>
                    <ul className="space-y-2">
                      {step.activities.map((activity, activityIndex) => (
                        <li key={activityIndex} className="flex items-start gap-2 text-sm text-gray-600">
                          <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                          {activity}
                        </li>
                      ))}
                    </ul>
                  </div>
                  
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-3">Deliverables:</h4>
                    <div className="space-y-2">
                      {step.deliverables.map((deliverable, deliverableIndex) => (
                        <div key={deliverableIndex} className="bg-blue-50 text-blue-700 px-3 py-1 rounded text-sm">
                          {deliverable}
                        </div>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Best Practices */}
        <div>
          <h3 className="text-2xl font-bold text-gray-900 mb-6">
            Best Practices for Success
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {bestPractices.map((practice, index) => (
              <Card key={index} className="hover:shadow-md transition-shadow duration-300">
                <CardHeader>
                  <CardTitle className="text-lg flex items-center gap-3">
                    <Target className="h-5 w-5 text-blue-600" />
                    {practice.title}
                  </CardTitle>
                  <p className="text-gray-600">
                    {practice.description}
                  </p>
                </CardHeader>
                
                <CardContent>
                  <h4 className="font-semibold text-gray-900 mb-3">Implementation Tips:</h4>
                  <ul className="space-y-2">
                    {practice.tips.map((tip, tipIndex) => (
                      <li key={tipIndex} className="flex items-start gap-2 text-sm text-gray-600">
                        <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                        {tip}
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Common Pitfalls */}
        <div className="bg-yellow-50 rounded-2xl p-8">
          <h3 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-3">
            <AlertTriangle className="h-6 w-6 text-yellow-600" />
            Common Pitfalls to Avoid
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <div className="bg-white rounded-lg p-4">
                <h4 className="font-semibold text-gray-900 mb-2">Automating Broken Processes</h4>
                <p className="text-sm text-gray-600">Fix and optimize processes before automating them.</p>
              </div>
              
              <div className="bg-white rounded-lg p-4">
                <h4 className="font-semibold text-gray-900 mb-2">Ignoring Change Management</h4>
                <p className="text-sm text-gray-600">Prepare users for changes and provide adequate training.</p>
              </div>
              
              <div className="bg-white rounded-lg p-4">
                <h4 className="font-semibold text-gray-900 mb-2">Over-Engineering Solutions</h4>
                <p className="text-sm text-gray-600">Keep workflows simple and focus on core requirements.</p>
              </div>
            </div>
            
            <div className="space-y-4">
              <div className="bg-white rounded-lg p-4">
                <h4 className="font-semibold text-gray-900 mb-2">Lack of Monitoring</h4>
                <p className="text-sm text-gray-600">Set up proper monitoring and alerting from day one.</p>
              </div>
              
              <div className="bg-white rounded-lg p-4">
                <h4 className="font-semibold text-gray-900 mb-2">Poor Exception Handling</h4>
                <p className="text-sm text-gray-600">Plan for edge cases and provide fallback mechanisms.</p>
              </div>
              
              <div className="bg-white rounded-lg p-4">
                <h4 className="font-semibold text-gray-900 mb-2">Insufficient Testing</h4>
                <p className="text-sm text-gray-600">Test thoroughly with real data and edge cases.</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
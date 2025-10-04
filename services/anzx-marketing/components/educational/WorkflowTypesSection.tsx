'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  Clock, 
  FileText, 
  Users, 
  ShoppingCart, 
  MessageSquare, 
  BarChart3,
  Zap,
  CheckCircle,
  ArrowRight
} from 'lucide-react';

interface WorkflowTypesSectionProps {
  id: string;
}

export default function WorkflowTypesSection({ id }: WorkflowTypesSectionProps) {
  const workflowTypes = [
    {
      icon: Clock,
      title: 'Time-Based Workflows',
      description: 'Automated processes triggered by schedules or time intervals.',
      complexity: 'Simple',
      examples: [
        'Daily report generation',
        'Weekly backup processes',
        'Monthly invoice processing',
        'Quarterly performance reviews',
      ],
      useCases: [
        'Recurring administrative tasks',
        'Scheduled maintenance activities',
        'Regular reporting and analytics',
        'Periodic data synchronization',
      ],
      benefits: ['Consistent execution', 'No manual oversight needed', 'Predictable resource usage'],
      color: 'bg-blue-100 text-blue-600',
    },
    {
      icon: FileText,
      title: 'Document-Based Workflows',
      description: 'Processes that handle document creation, approval, and management.',
      complexity: 'Medium',
      examples: [
        'Contract approval processes',
        'Invoice processing and approval',
        'Employee onboarding documentation',
        'Compliance document management',
      ],
      useCases: [
        'Legal document workflows',
        'Financial approval processes',
        'HR documentation',
        'Quality assurance procedures',
      ],
      benefits: ['Faster approvals', 'Audit trails', 'Reduced paper usage'],
      color: 'bg-green-100 text-green-600',
    },
    {
      icon: Users,
      title: 'Human-Centric Workflows',
      description: 'Processes that coordinate tasks between team members and departments.',
      complexity: 'Medium',
      examples: [
        'Employee onboarding sequences',
        'Project handoff procedures',
        'Customer escalation processes',
        'Training and certification tracking',
      ],
      useCases: [
        'HR processes',
        'Project management',
        'Customer service escalations',
        'Training programs',
      ],
      benefits: ['Better coordination', 'Clear accountability', 'Improved communication'],
      color: 'bg-purple-100 text-purple-600',
    },
    {
      icon: ShoppingCart,
      title: 'Transaction-Based Workflows',
      description: 'Automated processes for handling business transactions and orders.',
      complexity: 'High',
      examples: [
        'Order processing and fulfillment',
        'Payment processing workflows',
        'Inventory management automation',
        'Customer refund processes',
      ],
      useCases: [
        'E-commerce operations',
        'Financial transactions',
        'Supply chain management',
        'Customer service',
      ],
      benefits: ['Faster processing', 'Reduced errors', 'Better customer experience'],
      color: 'bg-orange-100 text-orange-600',
    },
    {
      icon: MessageSquare,
      title: 'Communication Workflows',
      description: 'Automated messaging and notification systems across channels.',
      complexity: 'Medium',
      examples: [
        'Customer onboarding email sequences',
        'Event-triggered notifications',
        'Multi-channel marketing campaigns',
        'Internal team communications',
      ],
      useCases: [
        'Marketing automation',
        'Customer communications',
        'Internal notifications',
        'Emergency alerts',
      ],
      benefits: ['Timely communications', 'Personalized messaging', 'Multi-channel reach'],
      color: 'bg-pink-100 text-pink-600',
    },
    {
      icon: BarChart3,
      title: 'Data-Driven Workflows',
      description: 'Processes that analyze data and trigger actions based on insights.',
      complexity: 'High',
      examples: [
        'Automated reporting and dashboards',
        'Anomaly detection and alerts',
        'Predictive maintenance workflows',
        'Performance monitoring systems',
      ],
      useCases: [
        'Business intelligence',
        'Quality monitoring',
        'Risk management',
        'Performance optimization',
      ],
      benefits: ['Data-driven decisions', 'Proactive problem solving', 'Real-time insights'],
      color: 'bg-indigo-100 text-indigo-600',
    },
  ];

  const getComplexityColor = (complexity: string) => {
    switch (complexity) {
      case 'Simple': return 'bg-green-100 text-green-800';
      case 'Medium': return 'bg-yellow-100 text-yellow-800';
      case 'High': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <section id={id} className="scroll-mt-8">
      <div className="space-y-8">
        <div>
          <h2 className="text-3xl font-bold text-gray-900 mb-6">
            Types of Workflow Automation
          </h2>
          
          <div className="prose prose-lg max-w-none text-gray-600 mb-8">
            <p>
              Different types of workflows serve different business needs. Understanding these 
              categories helps you identify the best automation opportunities for your organization 
              and choose the right approach for each use case.
            </p>
          </div>
        </div>

        {/* Workflow Types Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {workflowTypes.map((type, index) => {
            const IconComponent = type.icon;
            
            return (
              <Card key={index} className="h-full hover:shadow-lg transition-shadow duration-300">
                <CardHeader>
                  <div className="flex items-start justify-between mb-4">
                    <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${type.color}`}>
                      <IconComponent className="h-6 w-6" />
                    </div>
                    <Badge className={getComplexityColor(type.complexity)}>
                      {type.complexity}
                    </Badge>
                  </div>
                  <CardTitle className="text-xl">
                    {type.title}
                  </CardTitle>
                  <p className="text-gray-600">
                    {type.description}
                  </p>
                </CardHeader>
                
                <CardContent className="space-y-6">
                  {/* Examples */}
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-3">Common Examples:</h4>
                    <ul className="space-y-2">
                      {type.examples.map((example, exampleIndex) => (
                        <li key={exampleIndex} className="flex items-start gap-2 text-sm text-gray-600">
                          <ArrowRight className="h-4 w-4 text-gray-400 mt-0.5 flex-shrink-0" />
                          {example}
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Use Cases */}
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-3">Best Use Cases:</h4>
                    <div className="flex flex-wrap gap-2">
                      {type.useCases.map((useCase, useCaseIndex) => (
                        <span
                          key={useCaseIndex}
                          className="bg-gray-100 text-gray-700 px-2 py-1 rounded text-xs"
                        >
                          {useCase}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Benefits */}
                  <div className="bg-green-50 rounded-lg p-4">
                    <h4 className="font-semibold text-gray-900 mb-3">Key Benefits:</h4>
                    <ul className="space-y-2">
                      {type.benefits.map((benefit, benefitIndex) => (
                        <li key={benefitIndex} className="flex items-start gap-2 text-sm text-gray-600">
                          <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                          {benefit}
                        </li>
                      ))}
                    </ul>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* Complexity Guide */}
        <div className="bg-gradient-to-r from-gray-50 to-blue-50 rounded-2xl p-8">
          <h3 className="text-2xl font-bold text-gray-900 mb-6">
            Implementation Complexity Guide
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white rounded-lg p-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-4 h-4 bg-green-500 rounded-full"></div>
                <h4 className="font-semibold text-gray-900">Simple Workflows</h4>
              </div>
              <ul className="space-y-2 text-sm text-gray-600 mb-4">
                <li>• Single trigger, linear flow</li>
                <li>• Minimal decision points</li>
                <li>• Basic integrations</li>
                <li>• Quick to implement</li>
              </ul>
              <div className="text-xs text-gray-500">
                <strong>Timeline:</strong> 1-2 weeks
              </div>
            </div>
            
            <div className="bg-white rounded-lg p-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-4 h-4 bg-yellow-500 rounded-full"></div>
                <h4 className="font-semibold text-gray-900">Medium Workflows</h4>
              </div>
              <ul className="space-y-2 text-sm text-gray-600 mb-4">
                <li>• Multiple triggers or conditions</li>
                <li>• Some decision logic</li>
                <li>• Multiple system integrations</li>
                <li>• Moderate complexity</li>
              </ul>
              <div className="text-xs text-gray-500">
                <strong>Timeline:</strong> 2-6 weeks
              </div>
            </div>
            
            <div className="bg-white rounded-lg p-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-4 h-4 bg-red-500 rounded-full"></div>
                <h4 className="font-semibold text-gray-900">High Complexity</h4>
              </div>
              <ul className="space-y-2 text-sm text-gray-600 mb-4">
                <li>• Complex business logic</li>
                <li>• Multiple decision branches</li>
                <li>• Advanced integrations</li>
                <li>• Custom development needed</li>
              </ul>
              <div className="text-xs text-gray-500">
                <strong>Timeline:</strong> 6-12 weeks
              </div>
            </div>
          </div>
          
          <div className="mt-6 text-center">
            <p className="text-gray-600">
              Start with simple workflows to build confidence and expertise, then gradually 
              tackle more complex automation opportunities.
            </p>
          </div>
        </div>

        {/* Workflow Selection Matrix */}
        <div className="bg-white rounded-2xl border p-8">
          <h3 className="text-2xl font-bold text-gray-900 mb-6">
            Workflow Selection Matrix
          </h3>
          
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left font-semibold text-gray-900">Business Need</th>
                  <th className="px-4 py-3 text-center font-semibold text-gray-900">Recommended Type</th>
                  <th className="px-4 py-3 text-center font-semibold text-gray-900">Complexity</th>
                  <th className="px-4 py-3 text-center font-semibold text-gray-900">ROI Timeline</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                <tr>
                  <td className="px-4 py-3 text-gray-900">Reduce manual data entry</td>
                  <td className="px-4 py-3 text-center text-sm">Document-Based</td>
                  <td className="px-4 py-3 text-center">
                    <Badge className="bg-yellow-100 text-yellow-800">Medium</Badge>
                  </td>
                  <td className="px-4 py-3 text-center text-sm">2-3 months</td>
                </tr>
                <tr>
                  <td className="px-4 py-3 text-gray-900">Improve customer response time</td>
                  <td className="px-4 py-3 text-center text-sm">Communication</td>
                  <td className="px-4 py-3 text-center">
                    <Badge className="bg-yellow-100 text-yellow-800">Medium</Badge>
                  </td>
                  <td className="px-4 py-3 text-center text-sm">1-2 months</td>
                </tr>
                <tr>
                  <td className="px-4 py-3 text-gray-900">Streamline order processing</td>
                  <td className="px-4 py-3 text-center text-sm">Transaction-Based</td>
                  <td className="px-4 py-3 text-center">
                    <Badge className="bg-red-100 text-red-800">High</Badge>
                  </td>
                  <td className="px-4 py-3 text-center text-sm">3-6 months</td>
                </tr>
                <tr>
                  <td className="px-4 py-3 text-gray-900">Automate reporting</td>
                  <td className="px-4 py-3 text-center text-sm">Time-Based</td>
                  <td className="px-4 py-3 text-center">
                    <Badge className="bg-green-100 text-green-800">Simple</Badge>
                  </td>
                  <td className="px-4 py-3 text-center text-sm">1 month</td>
                </tr>
                <tr>
                  <td className="px-4 py-3 text-gray-900">Coordinate team tasks</td>
                  <td className="px-4 py-3 text-center text-sm">Human-Centric</td>
                  <td className="px-4 py-3 text-center">
                    <Badge className="bg-yellow-100 text-yellow-800">Medium</Badge>
                  </td>
                  <td className="px-4 py-3 text-center text-sm">2-4 months</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </section>
  );
}
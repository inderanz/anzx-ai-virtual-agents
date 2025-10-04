'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  ShoppingCart, 
  Building2, 
  GraduationCap, 
  Heart, 
  Banknote, 
  Truck,
  ArrowRight,
  CheckCircle
} from 'lucide-react';

interface UseCasesSectionProps {
  id: string;
}

export default function UseCasesSection({ id }: UseCasesSectionProps) {
  const useCases = [
    {
      icon: ShoppingCart,
      industry: 'E-commerce',
      title: 'Customer Support & Sales',
      description: 'Handle customer inquiries, process orders, and provide product recommendations.',
      challenges: ['High volume of customer inquiries', 'Need for 24/7 support', 'Order processing delays'],
      solutions: ['Automated customer service', 'Intelligent product recommendations', 'Order status updates'],
      results: ['80% reduction in response time', '60% increase in customer satisfaction', '40% boost in sales'],
      color: 'bg-blue-100 text-blue-600',
    },
    {
      icon: Building2,
      industry: 'SaaS',
      title: 'User Onboarding & Support',
      description: 'Guide new users through setup, answer technical questions, and reduce churn.',
      challenges: ['Complex product onboarding', 'High support ticket volume', 'User churn'],
      solutions: ['Interactive onboarding guides', 'Technical support automation', 'Proactive user engagement'],
      results: ['50% faster onboarding', '70% reduction in support tickets', '30% decrease in churn'],
      color: 'bg-purple-100 text-purple-600',
    },
    {
      icon: Heart,
      industry: 'Healthcare',
      title: 'Patient Scheduling & Care',
      description: 'Schedule appointments, send reminders, and provide basic health information.',
      challenges: ['Appointment scheduling complexity', 'Patient communication', 'Administrative overhead'],
      solutions: ['Automated scheduling', 'Appointment reminders', 'Basic health Q&A'],
      results: ['90% reduction in no-shows', '60% less admin work', '95% patient satisfaction'],
      color: 'bg-red-100 text-red-600',
    },
    {
      icon: Banknote,
      industry: 'Financial Services',
      title: 'Customer Service & Compliance',
      description: 'Handle account inquiries, process applications, and ensure regulatory compliance.',
      challenges: ['Regulatory compliance', 'Account management', 'Fraud detection'],
      solutions: ['Compliant customer service', 'Automated application processing', 'Fraud monitoring'],
      results: ['100% compliance adherence', '75% faster processing', '85% fraud detection rate'],
      color: 'bg-green-100 text-green-600',
    },
    {
      icon: GraduationCap,
      industry: 'Education',
      title: 'Student Support & Administration',
      description: 'Answer student questions, handle enrollment, and provide academic guidance.',
      challenges: ['Student inquiry volume', 'Enrollment processes', 'Academic support'],
      solutions: ['24/7 student support', 'Automated enrollment', 'Academic guidance'],
      results: ['24/7 availability', '50% faster enrollment', '90% student satisfaction'],
      color: 'bg-yellow-100 text-yellow-600',
    },
    {
      icon: Truck,
      industry: 'Logistics',
      title: 'Shipment Tracking & Customer Updates',
      description: 'Track shipments, update customers, and handle delivery issues.',
      challenges: ['Shipment visibility', 'Customer communication', 'Issue resolution'],
      solutions: ['Real-time tracking updates', 'Proactive notifications', 'Issue resolution'],
      results: ['100% shipment visibility', '80% fewer inquiries', '95% on-time delivery'],
      color: 'bg-indigo-100 text-indigo-600',
    },
  ];

  return (
    <section id={id} className="scroll-mt-8">
      <div className="space-y-8">
        <div>
          <h2 className="text-3xl font-bold text-gray-900 mb-6">
            Real-World Use Cases
          </h2>
          
          <div className="prose prose-lg max-w-none text-gray-600 mb-8">
            <p>
              AI agents are transforming businesses across industries. Here are specific examples 
              of how different sectors are leveraging AI agents to solve real problems:
            </p>
          </div>
        </div>

        {/* Use Cases Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {useCases.map((useCase, index) => {
            const IconComponent = useCase.icon;
            
            return (
              <Card key={index} className="h-full hover:shadow-lg transition-shadow duration-300">
                <CardHeader>
                  <div className="flex items-center gap-4 mb-4">
                    <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${useCase.color}`}>
                      <IconComponent className="h-6 w-6" />
                    </div>
                    <div>
                      <Badge variant="secondary" className="mb-2">
                        {useCase.industry}
                      </Badge>
                      <CardTitle className="text-lg">
                        {useCase.title}
                      </CardTitle>
                    </div>
                  </div>
                  <p className="text-gray-600">
                    {useCase.description}
                  </p>
                </CardHeader>
                
                <CardContent className="space-y-6">
                  {/* Challenges */}
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-3">Common Challenges:</h4>
                    <ul className="space-y-2">
                      {useCase.challenges.map((challenge, challengeIndex) => (
                        <li key={challengeIndex} className="flex items-start gap-2 text-sm text-gray-600">
                          <div className="w-1.5 h-1.5 bg-red-400 rounded-full mt-2 flex-shrink-0" />
                          {challenge}
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Solutions */}
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-3">AI Agent Solutions:</h4>
                    <ul className="space-y-2">
                      {useCase.solutions.map((solution, solutionIndex) => (
                        <li key={solutionIndex} className="flex items-start gap-2 text-sm text-gray-600">
                          <ArrowRight className="h-4 w-4 text-blue-500 mt-0.5 flex-shrink-0" />
                          {solution}
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Results */}
                  <div className="bg-green-50 rounded-lg p-4">
                    <h4 className="font-semibold text-gray-900 mb-3">Typical Results:</h4>
                    <ul className="space-y-2">
                      {useCase.results.map((result, resultIndex) => (
                        <li key={resultIndex} className="flex items-start gap-2 text-sm text-gray-600">
                          <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                          {result}
                        </li>
                      ))}
                    </ul>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* Implementation Timeline */}
        <div className="bg-blue-50 rounded-2xl p-8">
          <h3 className="text-2xl font-bold text-gray-900 mb-6">
            Typical Implementation Timeline
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="w-12 h-12 bg-blue-600 text-white rounded-full flex items-center justify-center mx-auto mb-3 font-bold">
                1
              </div>
              <h4 className="font-semibold text-gray-900 mb-2">Discovery</h4>
              <p className="text-sm text-gray-600">1-2 weeks</p>
              <p className="text-xs text-gray-500 mt-1">Identify use cases and requirements</p>
            </div>
            
            <div className="text-center">
              <div className="w-12 h-12 bg-blue-600 text-white rounded-full flex items-center justify-center mx-auto mb-3 font-bold">
                2
              </div>
              <h4 className="font-semibold text-gray-900 mb-2">Development</h4>
              <p className="text-sm text-gray-600">2-4 weeks</p>
              <p className="text-xs text-gray-500 mt-1">Build and train the AI agent</p>
            </div>
            
            <div className="text-center">
              <div className="w-12 h-12 bg-blue-600 text-white rounded-full flex items-center justify-center mx-auto mb-3 font-bold">
                3
              </div>
              <h4 className="font-semibold text-gray-900 mb-2">Testing</h4>
              <p className="text-sm text-gray-600">1-2 weeks</p>
              <p className="text-xs text-gray-500 mt-1">Pilot testing and refinement</p>
            </div>
            
            <div className="text-center">
              <div className="w-12 h-12 bg-blue-600 text-white rounded-full flex items-center justify-center mx-auto mb-3 font-bold">
                4
              </div>
              <h4 className="font-semibold text-gray-900 mb-2">Deployment</h4>
              <p className="text-sm text-gray-600">1 week</p>
              <p className="text-xs text-gray-500 mt-1">Full rollout and monitoring</p>
            </div>
          </div>
          
          <div className="text-center mt-6">
            <p className="text-gray-600">
              <strong>Total Timeline:</strong> 5-9 weeks from start to full deployment
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
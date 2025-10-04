'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  Users, 
  ShoppingCart, 
  TrendingUp, 
  Shield, 
  Briefcase, 
  Heart,
  CheckCircle,
  ArrowRight,
  Target
} from 'lucide-react';

interface AgenticUseCasesSectionProps {
  id: string;
}

export default function AgenticUseCasesSection({ id }: AgenticUseCasesSectionProps) {
  const useCases = [
    {
      icon: Users,
      title: 'Autonomous Customer Success Management',
      industry: 'SaaS & Technology',
      description: 'AI agents that proactively manage customer relationships, predict churn, and implement retention strategies.',
      agenticBehaviors: [
        'Identifies at-risk customers before they show obvious signs',
        'Develops personalized retention strategies for each customer segment',
        'Coordinates with sales and support teams autonomously',
        'Adapts approach based on customer response patterns',
      ],
      outcomes: ['35% reduction in churn rate', '50% increase in upsell success', '80% automation of routine tasks'],
      complexity: 'High',
      color: 'bg-blue-100 text-blue-600',
    },
    {
      icon: ShoppingCart,
      title: 'Intelligent Supply Chain Optimization',
      industry: 'Manufacturing & Retail',
      description: 'Agentic systems that manage entire supply chains, from procurement to delivery optimization.',
      agenticBehaviors: [
        'Predicts demand fluctuations and adjusts inventory automatically',
        'Negotiates with suppliers and finds alternative sources',
        'Optimizes logistics routes in real-time',
        'Learns from market trends to improve future planning',
      ],
      outcomes: ['25% reduction in inventory costs', '40% improvement in delivery times', '60% fewer stockouts'],
      complexity: 'Very High',
      color: 'bg-green-100 text-green-600',
    },
    {
      icon: TrendingUp,
      title: 'Adaptive Marketing Campaign Management',
      industry: 'Marketing & Advertising',
      description: 'AI agents that create, execute, and optimize marketing campaigns across multiple channels.',
      agenticBehaviors: [
        'Analyzes market conditions and competitor activities',
        'Creates and tests multiple campaign variations',
        'Reallocates budget based on performance data',
        'Develops new creative approaches when campaigns underperform',
      ],
      outcomes: ['45% improvement in ROAS', '70% reduction in campaign setup time', '90% automation of A/B testing'],
      complexity: 'Medium',
      color: 'bg-purple-100 text-purple-600',
    },
    {
      icon: Shield,
      title: 'Proactive Cybersecurity Defense',
      industry: 'IT & Security',
      description: 'Autonomous security agents that detect, analyze, and respond to threats in real-time.',
      agenticBehaviors: [
        'Continuously monitors network traffic and user behavior',
        'Investigates anomalies and determines threat levels',
        'Implements countermeasures and isolates threats',
        'Updates security policies based on new attack patterns',
      ],
      outcomes: ['85% faster threat detection', '95% reduction in false positives', '24/7 autonomous protection'],
      complexity: 'Very High',
      color: 'bg-red-100 text-red-600',
    },
    {
      icon: Briefcase,
      title: 'Intelligent Project Management',
      industry: 'Professional Services',
      description: 'AI agents that manage complex projects, coordinate teams, and ensure successful delivery.',
      agenticBehaviors: [
        'Monitors project progress and identifies potential delays',
        'Reallocates resources to optimize project outcomes',
        'Communicates with stakeholders and provides updates',
        'Learns from project patterns to improve future planning',
      ],
      outcomes: ['30% improvement in on-time delivery', '25% reduction in project costs', '50% less manual coordination'],
      complexity: 'High',
      color: 'bg-yellow-100 text-yellow-600',
    },
    {
      icon: Heart,
      title: 'Personalized Healthcare Management',
      industry: 'Healthcare',
      description: 'Agentic systems that provide personalized care coordination and health monitoring.',
      agenticBehaviors: [
        'Monitors patient health data and identifies concerning trends',
        'Coordinates care between multiple healthcare providers',
        'Adjusts treatment plans based on patient response',
        'Provides personalized health recommendations and reminders',
      ],
      outcomes: ['40% improvement in patient outcomes', '60% reduction in readmissions', '24/7 health monitoring'],
      complexity: 'Very High',
      color: 'bg-pink-100 text-pink-600',
    },
  ];

  const getComplexityColor = (complexity: string) => {
    switch (complexity) {
      case 'Medium': return 'bg-green-100 text-green-800';
      case 'High': return 'bg-yellow-100 text-yellow-800';
      case 'Very High': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <section id={id} className="scroll-mt-8">
      <div className="space-y-8">
        <div>
          <h2 className="text-3xl font-bold text-gray-900 mb-6">
            Business Applications of Agentic AI
          </h2>
          
          <div className="prose prose-lg max-w-none text-gray-600 mb-8">
            <p>
              Agentic AI excels in scenarios requiring autonomous decision-making, complex coordination, 
              and adaptive behavior. Here are real-world applications where agentic capabilities 
              provide significant advantages over traditional automation.
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
                  <div className="flex items-start justify-between mb-4">
                    <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${useCase.color}`}>
                      <IconComponent className="h-6 w-6" />
                    </div>
                    <div className="text-right">
                      <Badge variant="secondary" className="mb-2">
                        {useCase.industry}
                      </Badge>
                      <br />
                      <Badge className={getComplexityColor(useCase.complexity)}>
                        {useCase.complexity} Complexity
                      </Badge>
                    </div>
                  </div>
                  <CardTitle className="text-xl">
                    {useCase.title}
                  </CardTitle>
                  <p className="text-gray-600">
                    {useCase.description}
                  </p>
                </CardHeader>
                
                <CardContent className="space-y-6">
                  {/* Agentic Behaviors */}
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                      <Target className="h-4 w-4 text-purple-600" />
                      Agentic Behaviors:
                    </h4>
                    <ul className="space-y-2">
                      {useCase.agenticBehaviors.map((behavior, behaviorIndex) => (
                        <li key={behaviorIndex} className="flex items-start gap-2 text-sm text-gray-600">
                          <ArrowRight className="h-4 w-4 text-purple-500 mt-0.5 flex-shrink-0" />
                          {behavior}
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Outcomes */}
                  <div className="bg-green-50 rounded-lg p-4">
                    <h4 className="font-semibold text-gray-900 mb-3">Typical Outcomes:</h4>
                    <ul className="space-y-2">
                      {useCase.outcomes.map((outcome, outcomeIndex) => (
                        <li key={outcomeIndex} className="flex items-start gap-2 text-sm text-gray-600">
                          <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                          {outcome}
                        </li>
                      ))}
                    </ul>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* Implementation Complexity Guide */}
        <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-2xl p-8">
          <h3 className="text-2xl font-bold text-gray-900 mb-6">
            Implementation Complexity Guide
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white rounded-lg p-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-4 h-4 bg-green-500 rounded-full"></div>
                <h4 className="font-semibold text-gray-900">Medium Complexity</h4>
              </div>
              <ul className="space-y-2 text-sm text-gray-600">
                <li>• Single domain focus</li>
                <li>• Clear success metrics</li>
                <li>• Limited external dependencies</li>
                <li>• 2-4 month implementation</li>
              </ul>
            </div>
            
            <div className="bg-white rounded-lg p-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-4 h-4 bg-yellow-500 rounded-full"></div>
                <h4 className="font-semibold text-gray-900">High Complexity</h4>
              </div>
              <ul className="space-y-2 text-sm text-gray-600">
                <li>• Multi-domain coordination</li>
                <li>• Complex decision trees</li>
                <li>• Multiple system integrations</li>
                <li>• 4-8 month implementation</li>
              </ul>
            </div>
            
            <div className="bg-white rounded-lg p-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-4 h-4 bg-red-500 rounded-full"></div>
                <h4 className="font-semibold text-gray-900">Very High Complexity</h4>
              </div>
              <ul className="space-y-2 text-sm text-gray-600">
                <li>• Mission-critical operations</li>
                <li>• Regulatory compliance</li>
                <li>• Real-time decision making</li>
                <li>• 8-12 month implementation</li>
              </ul>
            </div>
          </div>
          
          <div className="mt-6 text-center">
            <p className="text-gray-600">
              ANZX.ai provides expert guidance to help you choose the right complexity level 
              for your organization's readiness and objectives.
            </p>
          </div>
        </div>

        {/* Success Factors */}
        <div className="bg-white rounded-2xl border p-8">
          <h3 className="text-2xl font-bold text-gray-900 mb-6">
            Key Success Factors for Agentic AI Implementation
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div>
              <h4 className="font-semibold text-gray-900 mb-4">Technical Requirements</h4>
              <ul className="space-y-3">
                <li className="flex items-start gap-3">
                  <CheckCircle className="h-5 w-5 text-green-500 mt-0.5 flex-shrink-0" />
                  <span className="text-gray-600">High-quality, structured data sources</span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle className="h-5 w-5 text-green-500 mt-0.5 flex-shrink-0" />
                  <span className="text-gray-600">Robust API infrastructure for integrations</span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle className="h-5 w-5 text-green-500 mt-0.5 flex-shrink-0" />
                  <span className="text-gray-600">Scalable cloud infrastructure</span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle className="h-5 w-5 text-green-500 mt-0.5 flex-shrink-0" />
                  <span className="text-gray-600">Comprehensive monitoring and logging</span>
                </li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-semibold text-gray-900 mb-4">Organizational Readiness</h4>
              <ul className="space-y-3">
                <li className="flex items-start gap-3">
                  <CheckCircle className="h-5 w-5 text-green-500 mt-0.5 flex-shrink-0" />
                  <span className="text-gray-600">Clear business objectives and success metrics</span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle className="h-5 w-5 text-green-500 mt-0.5 flex-shrink-0" />
                  <span className="text-gray-600">Executive sponsorship and change management</span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle className="h-5 w-5 text-green-500 mt-0.5 flex-shrink-0" />
                  <span className="text-gray-600">Cross-functional team collaboration</span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle className="h-5 w-5 text-green-500 mt-0.5 flex-shrink-0" />
                  <span className="text-gray-600">Willingness to iterate and adapt processes</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Check, X, Zap, Cog, Users } from 'lucide-react';

interface ComparisonSectionProps {
  id: string;
}

export default function ComparisonSection({ id }: ComparisonSectionProps) {
  const comparisonData = [
    {
      feature: 'Learning & Adaptation',
      aiAgent: { available: true, description: 'Learns from interactions and improves over time' },
      traditional: { available: false, description: 'Fixed rules, no learning capability' },
      human: { available: true, description: 'Learns but limited by time and capacity' },
    },
    {
      feature: 'Natural Language Understanding',
      aiAgent: { available: true, description: 'Understands context and nuance in communication' },
      traditional: { available: false, description: 'Keyword-based, limited understanding' },
      human: { available: true, description: 'Excellent but subject to fatigue and mood' },
    },
    {
      feature: '24/7 Availability',
      aiAgent: { available: true, description: 'Always available, no downtime' },
      traditional: { available: true, description: 'Can run continuously' },
      human: { available: false, description: 'Limited by working hours and breaks' },
    },
    {
      feature: 'Scalability',
      aiAgent: { available: true, description: 'Instantly scalable to handle any volume' },
      traditional: { available: false, description: 'Limited by system capacity' },
      human: { available: false, description: 'Requires hiring and training' },
    },
    {
      feature: 'Decision Making',
      aiAgent: { available: true, description: 'Makes intelligent decisions based on data' },
      traditional: { available: false, description: 'Follows pre-programmed logic only' },
      human: { available: true, description: 'Excellent but can be inconsistent' },
    },
    {
      feature: 'Cost Efficiency',
      aiAgent: { available: true, description: 'Low ongoing costs after initial setup' },
      traditional: { available: true, description: 'Low costs but limited capabilities' },
      human: { available: false, description: 'High ongoing salary and benefit costs' },
    },
    {
      feature: 'Emotional Intelligence',
      aiAgent: { available: true, description: 'Can recognize and respond to emotions' },
      traditional: { available: false, description: 'No emotional understanding' },
      human: { available: true, description: 'Natural emotional intelligence' },
    },
    {
      feature: 'Complex Problem Solving',
      aiAgent: { available: true, description: 'Handles complex, multi-step problems' },
      traditional: { available: false, description: 'Limited to simple, linear processes' },
      human: { available: true, description: 'Excellent but time-consuming' },
    },
  ];

  const approaches = [
    {
      icon: Zap,
      title: 'AI Agents',
      description: 'Intelligent, adaptive, and autonomous',
      color: 'bg-blue-100 text-blue-600',
      borderColor: 'border-blue-200',
    },
    {
      icon: Cog,
      title: 'Traditional Automation',
      description: 'Rule-based, rigid, but reliable',
      color: 'bg-gray-100 text-gray-600',
      borderColor: 'border-gray-200',
    },
    {
      icon: Users,
      title: 'Human Workers',
      description: 'Creative, empathetic, but limited',
      color: 'bg-green-100 text-green-600',
      borderColor: 'border-green-200',
    },
  ];

  return (
    <section id={id} className="scroll-mt-8">
      <div className="space-y-8">
        <div>
          <h2 className="text-3xl font-bold text-gray-900 mb-6">
            AI Agents vs Traditional Automation vs Human Workers
          </h2>
          
          <div className="prose prose-lg max-w-none text-gray-600 mb-8">
            <p>
              Understanding the differences between AI agents, traditional automation, and human workers 
              helps you choose the right approach for your business needs.
            </p>
          </div>
        </div>

        {/* Approach Overview */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {approaches.map((approach, index) => {
            const IconComponent = approach.icon;
            
            return (
              <Card key={index} className={`text-center ${approach.borderColor} border-2`}>
                <CardHeader>
                  <div className={`w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4 ${approach.color}`}>
                    <IconComponent className="h-8 w-8" />
                  </div>
                  <CardTitle className="text-xl">
                    {approach.title}
                  </CardTitle>
                  <p className="text-gray-600">
                    {approach.description}
                  </p>
                </CardHeader>
              </Card>
            );
          })}
        </div>

        {/* Detailed Comparison Table */}
        <div className="bg-white rounded-2xl border overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-4 text-left font-semibold text-gray-900">Feature</th>
                  <th className="px-6 py-4 text-center font-semibold text-blue-600">AI Agents</th>
                  <th className="px-6 py-4 text-center font-semibold text-gray-600">Traditional Automation</th>
                  <th className="px-6 py-4 text-center font-semibold text-green-600">Human Workers</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {comparisonData.map((row, index) => (
                  <tr key={index} className="hover:bg-gray-50">
                    <td className="px-6 py-4 font-medium text-gray-900">
                      {row.feature}
                    </td>
                    <td className="px-6 py-4 text-center">
                      <div className="flex flex-col items-center gap-2">
                        {row.aiAgent.available ? (
                          <Check className="h-5 w-5 text-green-500" />
                        ) : (
                          <X className="h-5 w-5 text-red-500" />
                        )}
                        <span className="text-xs text-gray-600 text-center">
                          {row.aiAgent.description}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-center">
                      <div className="flex flex-col items-center gap-2">
                        {row.traditional.available ? (
                          <Check className="h-5 w-5 text-green-500" />
                        ) : (
                          <X className="h-5 w-5 text-red-500" />
                        )}
                        <span className="text-xs text-gray-600 text-center">
                          {row.traditional.description}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-center">
                      <div className="flex flex-col items-center gap-2">
                        {row.human.available ? (
                          <Check className="h-5 w-5 text-green-500" />
                        ) : (
                          <X className="h-5 w-5 text-red-500" />
                        )}
                        <span className="text-xs text-gray-600 text-center">
                          {row.human.description}
                        </span>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* When to Use Each Approach */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card className="border-blue-200 border-2">
            <CardHeader>
              <CardTitle className="text-blue-600 flex items-center gap-2">
                <Zap className="h-5 w-5" />
                Use AI Agents When:
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm text-gray-600">
                <li>• Tasks require understanding and decision-making</li>
                <li>• You need to handle complex customer interactions</li>
                <li>• Scalability and 24/7 availability are important</li>
                <li>• You want continuous improvement over time</li>
                <li>• Natural language processing is needed</li>
              </ul>
            </CardContent>
          </Card>

          <Card className="border-gray-200 border-2">
            <CardHeader>
              <CardTitle className="text-gray-600 flex items-center gap-2">
                <Cog className="h-5 w-5" />
                Use Traditional Automation When:
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm text-gray-600">
                <li>• Tasks are simple and rule-based</li>
                <li>• Processes are highly standardized</li>
                <li>• You need predictable, consistent outcomes</li>
                <li>• Budget is very limited</li>
                <li>• No decision-making is required</li>
              </ul>
            </CardContent>
          </Card>

          <Card className="border-green-200 border-2">
            <CardHeader>
              <CardTitle className="text-green-600 flex items-center gap-2">
                <Users className="h-5 w-5" />
                Keep Human Workers For:
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm text-gray-600">
                <li>• Creative and strategic work</li>
                <li>• Complex relationship building</li>
                <li>• Ethical decision-making</li>
                <li>• Highly specialized expertise</li>
                <li>• Tasks requiring physical presence</li>
              </ul>
            </CardContent>
          </Card>
        </div>
      </div>
    </section>
  );
}
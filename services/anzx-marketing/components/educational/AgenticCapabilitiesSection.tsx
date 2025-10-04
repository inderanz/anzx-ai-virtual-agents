'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  Brain, 
  Target, 
  Network, 
  Lightbulb, 
  Shield, 
  TrendingUp,
  MessageSquare,
  Database,
  Clock
} from 'lucide-react';

interface AgenticCapabilitiesSectionProps {
  id: string;
}

export default function AgenticCapabilitiesSection({ id }: AgenticCapabilitiesSectionProps) {
  const capabilities = [
    {
      icon: Brain,
      title: 'Advanced Reasoning',
      description: 'Complex logical reasoning, causal understanding, and multi-step problem solving.',
      examples: ['Chain-of-thought reasoning', 'Causal inference', 'Abstract thinking', 'Pattern recognition'],
      maturityLevel: 'Advanced',
      color: 'bg-blue-100 text-blue-600',
    },
    {
      icon: Target,
      title: 'Goal Planning & Execution',
      description: 'Break down complex objectives into actionable steps and execute them systematically.',
      examples: ['Strategic planning', 'Task decomposition', 'Resource allocation', 'Timeline management'],
      maturityLevel: 'Mature',
      color: 'bg-green-100 text-green-600',
    },
    {
      icon: Network,
      title: 'Multi-Agent Coordination',
      description: 'Collaborate with other AI agents and human team members to achieve shared goals.',
      examples: ['Agent communication', 'Task delegation', 'Conflict resolution', 'Consensus building'],
      maturityLevel: 'Emerging',
      color: 'bg-purple-100 text-purple-600',
    },
    {
      icon: Lightbulb,
      title: 'Creative Problem Solving',
      description: 'Generate novel solutions and approaches when standard methods are insufficient.',
      examples: ['Alternative strategies', 'Innovation', 'Lateral thinking', 'Solution synthesis'],
      maturityLevel: 'Advanced',
      color: 'bg-yellow-100 text-yellow-600',
    },
    {
      icon: Shield,
      title: 'Risk Assessment & Mitigation',
      description: 'Evaluate potential risks and implement safeguards to prevent negative outcomes.',
      examples: ['Risk modeling', 'Scenario analysis', 'Preventive measures', 'Contingency planning'],
      maturityLevel: 'Mature',
      color: 'bg-red-100 text-red-600',
    },
    {
      icon: TrendingUp,
      title: 'Continuous Learning & Adaptation',
      description: 'Learn from experiences and continuously improve performance over time.',
      examples: ['Performance optimization', 'Strategy refinement', 'Feedback integration', 'Skill development'],
      maturityLevel: 'Advanced',
      color: 'bg-indigo-100 text-indigo-600',
    },
  ];

  const cognitiveCapabilities = [
    {
      icon: MessageSquare,
      title: 'Natural Language Understanding',
      description: 'Deep comprehension of human language, context, and intent.',
      metrics: '95%+ accuracy in context understanding',
    },
    {
      icon: Database,
      title: 'Knowledge Integration',
      description: 'Synthesize information from multiple sources to form comprehensive understanding.',
      metrics: 'Process 1000+ data sources simultaneously',
    },
    {
      icon: Clock,
      title: 'Temporal Reasoning',
      description: 'Understand time-based relationships and plan actions across different time horizons.',
      metrics: 'Plan and execute multi-month strategies',
    },
  ];

  const getMaturityColor = (level: string) => {
    switch (level) {
      case 'Mature': return 'bg-green-100 text-green-800';
      case 'Advanced': return 'bg-blue-100 text-blue-800';
      case 'Emerging': return 'bg-orange-100 text-orange-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <section id={id} className="scroll-mt-8">
      <div className="space-y-8">
        <div>
          <h2 className="text-3xl font-bold text-gray-900 mb-6">
            Key Capabilities of Agentic AI
          </h2>
          
          <div className="prose prose-lg max-w-none text-gray-600 mb-8">
            <p>
              Agentic AI systems possess a unique combination of capabilities that enable them to 
              operate autonomously in complex, dynamic environments. These capabilities work together 
              to create truly intelligent agents that can adapt, learn, and achieve goals independently.
            </p>
          </div>
        </div>

        {/* Core Capabilities */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {capabilities.map((capability, index) => {
            const IconComponent = capability.icon;
            
            return (
              <Card key={index} className="h-full hover:shadow-lg transition-shadow duration-300">
                <CardHeader>
                  <div className="flex items-start justify-between mb-4">
                    <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${capability.color}`}>
                      <IconComponent className="h-6 w-6" />
                    </div>
                    <Badge className={getMaturityColor(capability.maturityLevel)}>
                      {capability.maturityLevel}
                    </Badge>
                  </div>
                  <CardTitle className="text-xl">
                    {capability.title}
                  </CardTitle>
                </CardHeader>
                
                <CardContent className="space-y-4">
                  <p className="text-gray-600">
                    {capability.description}
                  </p>
                  
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-2">Key Features:</h4>
                    <div className="flex flex-wrap gap-2">
                      {capability.examples.map((example, exampleIndex) => (
                        <span
                          key={exampleIndex}
                          className="bg-gray-100 text-gray-700 px-2 py-1 rounded text-sm"
                        >
                          {example}
                        </span>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* Cognitive Capabilities */}
        <div>
          <h3 className="text-2xl font-bold text-gray-900 mb-6">
            Foundational Cognitive Capabilities
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {cognitiveCapabilities.map((capability, index) => {
              const IconComponent = capability.icon;
              
              return (
                <Card key={index} className="text-center hover:shadow-md transition-shadow duration-300">
                  <CardContent className="p-6">
                    <div className="w-16 h-16 bg-gradient-to-br from-purple-100 to-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                      <IconComponent className="h-8 w-8 text-purple-600" />
                    </div>
                    
                    <h4 className="font-semibold text-gray-900 mb-2">
                      {capability.title}
                    </h4>
                    
                    <p className="text-gray-600 text-sm mb-3">
                      {capability.description}
                    </p>
                    
                    <div className="bg-purple-50 rounded-lg px-3 py-2">
                      <span className="text-xs font-medium text-purple-700">
                        {capability.metrics}
                      </span>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </div>

        {/* Capability Maturity Model */}
        <div className="bg-gradient-to-r from-gray-50 to-blue-50 rounded-2xl p-8">
          <h3 className="text-2xl font-bold text-gray-900 mb-6">
            Agentic AI Capability Maturity
          </h3>
          
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-white rounded-lg p-6 text-center">
                <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3">
                  <span className="text-green-600 font-bold">M</span>
                </div>
                <h4 className="font-semibold text-gray-900 mb-2">Mature</h4>
                <p className="text-sm text-gray-600">
                  Production-ready capabilities with proven reliability and performance.
                </p>
              </div>
              
              <div className="bg-white rounded-lg p-6 text-center">
                <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
                  <span className="text-blue-600 font-bold">A</span>
                </div>
                <h4 className="font-semibold text-gray-900 mb-2">Advanced</h4>
                <p className="text-sm text-gray-600">
                  Sophisticated capabilities requiring careful implementation and monitoring.
                </p>
              </div>
              
              <div className="bg-white rounded-lg p-6 text-center">
                <div className="w-12 h-12 bg-orange-100 rounded-full flex items-center justify-center mx-auto mb-3">
                  <span className="text-orange-600 font-bold">E</span>
                </div>
                <h4 className="font-semibold text-gray-900 mb-2">Emerging</h4>
                <p className="text-sm text-gray-600">
                  Cutting-edge capabilities in active development with high potential.
                </p>
              </div>
            </div>
            
            <div className="text-center">
              <p className="text-gray-600">
                ANZX.ai focuses on <strong>Mature</strong> and <strong>Advanced</strong> capabilities 
                to ensure reliable, production-ready agentic AI solutions for your business.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
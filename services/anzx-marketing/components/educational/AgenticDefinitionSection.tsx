'use client';

import { Card, CardContent } from '@/components/ui/card';
import { Brain, Target, Zap, Network, Eye, Cog } from 'lucide-react';

interface AgenticDefinitionSectionProps {
  id: string;
}

export default function AgenticDefinitionSection({ id }: AgenticDefinitionSectionProps) {
  const agenticPrinciples = [
    {
      icon: Target,
      title: 'Goal-Oriented Behavior',
      description: 'Agentic AI systems are designed with specific objectives and work autonomously to achieve them.',
    },
    {
      icon: Brain,
      title: 'Autonomous Decision Making',
      description: 'They can make complex decisions without human intervention, adapting to new situations.',
    },
    {
      icon: Eye,
      title: 'Environmental Awareness',
      description: 'These systems perceive and understand their environment to make informed decisions.',
    },
    {
      icon: Zap,
      title: 'Proactive Action',
      description: 'Rather than just responding, they take initiative to achieve their goals.',
    },
    {
      icon: Network,
      title: 'Multi-Agent Coordination',
      description: 'Can work with other AI agents to accomplish complex, multi-step objectives.',
    },
    {
      icon: Cog,
      title: 'Adaptive Learning',
      description: 'Continuously learn and improve their strategies based on outcomes and feedback.',
    },
  ];

  return (
    <section id={id} className="scroll-mt-8">
      <div className="space-y-8">
        <div>
          <h2 className="text-3xl font-bold text-gray-900 mb-6">
            What is Agentic AI?
          </h2>
          
          <div className="prose prose-lg max-w-none text-gray-600 space-y-4">
            <p>
              <strong>Agentic AI</strong> represents a paradigm shift from traditional reactive AI systems 
              to proactive, goal-oriented artificial intelligence that can act independently in complex 
              environments. Unlike conventional AI that responds to specific inputs with predetermined 
              outputs, agentic AI systems exhibit agency – the ability to make autonomous decisions 
              and take actions to achieve their objectives.
            </p>
            
            <p>
              The term "agentic" comes from the concept of agency in cognitive science, referring to 
              the capacity to act intentionally and purposefully. In AI, this translates to systems 
              that can plan, reason, and execute strategies without constant human guidance.
            </p>
          </div>
        </div>

        {/* Core Principles */}
        <div>
          <h3 className="text-2xl font-bold text-gray-900 mb-6">
            Core Principles of Agentic AI
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {agenticPrinciples.map((principle, index) => {
              const IconComponent = principle.icon;
              
              return (
                <Card key={index} className="hover:shadow-md transition-shadow duration-300">
                  <CardContent className="p-6">
                    <div className="flex items-start gap-4">
                      <div className="flex-shrink-0">
                        <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                          <IconComponent className="h-6 w-6 text-purple-600" />
                        </div>
                      </div>
                      <div>
                        <h4 className="font-semibold text-gray-900 mb-2">
                          {principle.title}
                        </h4>
                        <p className="text-gray-600 text-sm">
                          {principle.description}
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </div>

        {/* Key Distinction */}
        <div className="bg-purple-50 rounded-2xl p-8">
          <h3 className="text-2xl font-bold text-gray-900 mb-4">
            The Key Distinction: Agency vs Automation
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div>
              <h4 className="font-semibold text-gray-900 mb-3 text-lg">Traditional AI/Automation</h4>
              <ul className="space-y-2 text-gray-600">
                <li className="flex items-start gap-2">
                  <div className="w-2 h-2 bg-red-400 rounded-full mt-2 flex-shrink-0" />
                  Reactive: Responds to specific inputs
                </li>
                <li className="flex items-start gap-2">
                  <div className="w-2 h-2 bg-red-400 rounded-full mt-2 flex-shrink-0" />
                  Rule-based: Follows predetermined logic
                </li>
                <li className="flex items-start gap-2">
                  <div className="w-2 h-2 bg-red-400 rounded-full mt-2 flex-shrink-0" />
                  Limited scope: Handles specific tasks
                </li>
                <li className="flex items-start gap-2">
                  <div className="w-2 h-2 bg-red-400 rounded-full mt-2 flex-shrink-0" />
                  Human-dependent: Requires constant supervision
                </li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-semibold text-gray-900 mb-3 text-lg">Agentic AI</h4>
              <ul className="space-y-2 text-gray-600">
                <li className="flex items-start gap-2">
                  <div className="w-2 h-2 bg-green-400 rounded-full mt-2 flex-shrink-0" />
                  Proactive: Takes initiative to achieve goals
                </li>
                <li className="flex items-start gap-2">
                  <div className="w-2 h-2 bg-green-400 rounded-full mt-2 flex-shrink-0" />
                  Adaptive: Learns and adjusts strategies
                </li>
                <li className="flex items-start gap-2">
                  <div className="w-2 h-2 bg-green-400 rounded-full mt-2 flex-shrink-0" />
                  Broad capability: Handles complex, multi-step processes
                </li>
                <li className="flex items-start gap-2">
                  <div className="w-2 h-2 bg-green-400 rounded-full mt-2 flex-shrink-0" />
                  Autonomous: Operates independently with minimal oversight
                </li>
              </ul>
            </div>
          </div>
        </div>

        {/* Real-World Example */}
        <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-2xl p-8">
          <h3 className="text-2xl font-bold text-gray-900 mb-4">
            Real-World Example: Agentic Customer Success Manager
          </h3>
          
          <div className="space-y-4">
            <p className="text-gray-600">
              Consider an agentic AI system designed to improve customer retention:
            </p>
            
            <div className="space-y-3">
              <div className="bg-white rounded-lg p-4">
                <strong className="text-purple-600">Goal:</strong> Reduce customer churn by 25% over 6 months
              </div>
              
              <div className="bg-white rounded-lg p-4">
                <strong className="text-purple-600">Autonomous Actions:</strong>
                <ul className="mt-2 space-y-1 text-sm text-gray-600">
                  <li>• Analyzes customer behavior patterns to identify at-risk accounts</li>
                  <li>• Proactively reaches out with personalized retention offers</li>
                  <li>• Schedules follow-up calls and adjusts communication frequency</li>
                  <li>• Collaborates with sales agents to create custom solutions</li>
                  <li>• Learns from successful interventions to improve future strategies</li>
                </ul>
              </div>
              
              <div className="bg-white rounded-lg p-4">
                <strong className="text-purple-600">Adaptive Behavior:</strong> If initial outreach doesn't work, 
                it tries different approaches, timing, and messaging until it finds what resonates with each customer segment.
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
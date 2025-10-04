'use client';

import { Card, CardContent } from '@/components/ui/card';
import { Eye, Brain, Cog, ArrowRight } from 'lucide-react';

interface HowItWorksSectionProps {
  id: string;
}

export default function HowItWorksSection({ id }: HowItWorksSectionProps) {
  const steps = [
    {
      icon: Eye,
      title: 'Perception',
      description: 'The AI agent receives input from its environment - this could be text, voice, data, or system events.',
      examples: ['Customer messages', 'Email notifications', 'Database changes', 'API calls'],
    },
    {
      icon: Brain,
      title: 'Processing & Decision Making',
      description: 'Using AI models, the agent analyzes the input, understands context, and decides on the best course of action.',
      examples: ['Natural language understanding', 'Pattern recognition', 'Goal evaluation', 'Strategy selection'],
    },
    {
      icon: Cog,
      title: 'Action Execution',
      description: 'The agent performs the chosen actions, which could involve responding to users, updating systems, or triggering workflows.',
      examples: ['Send responses', 'Update databases', 'Create tasks', 'Schedule meetings'],
    },
  ];

  return (
    <section id={id} className="scroll-mt-8">
      <div className="space-y-8">
        <div>
          <h2 className="text-3xl font-bold text-gray-900 mb-6">
            How AI Agents Work
          </h2>
          
          <div className="prose prose-lg max-w-none text-gray-600 mb-8">
            <p>
              AI agents operate through a continuous cycle of perception, processing, and action. 
              This cycle allows them to respond intelligently to their environment and achieve their goals.
            </p>
          </div>
        </div>

        {/* Process Flow */}
        <div className="space-y-6">
          {steps.map((step, index) => {
            const IconComponent = step.icon;
            const isLast = index === steps.length - 1;
            
            return (
              <div key={index} className="relative">
                <Card className="hover:shadow-md transition-shadow duration-300">
                  <CardContent className="p-8">
                    <div className="flex items-start gap-6">
                      {/* Step Number & Icon */}
                      <div className="flex-shrink-0 text-center">
                        <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mb-2">
                          <IconComponent className="h-8 w-8 text-blue-600" />
                        </div>
                        <div className="text-sm font-medium text-gray-500">
                          Step {index + 1}
                        </div>
                      </div>
                      
                      {/* Content */}
                      <div className="flex-1">
                        <h3 className="text-xl font-bold text-gray-900 mb-3">
                          {step.title}
                        </h3>
                        <p className="text-gray-600 mb-4">
                          {step.description}
                        </p>
                        
                        {/* Examples */}
                        <div>
                          <h4 className="text-sm font-semibold text-gray-900 mb-2">Examples:</h4>
                          <div className="flex flex-wrap gap-2">
                            {step.examples.map((example, exampleIndex) => (
                              <span
                                key={exampleIndex}
                                className="bg-gray-100 text-gray-700 px-3 py-1 rounded-full text-sm"
                              >
                                {example}
                              </span>
                            ))}
                          </div>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
                
                {/* Arrow to next step */}
                {!isLast && (
                  <div className="flex justify-center my-4">
                    <ArrowRight className="h-6 w-6 text-gray-400" />
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Real Example */}
        <div className="bg-green-50 rounded-2xl p-8">
          <h3 className="text-2xl font-bold text-gray-900 mb-4">
            Real Example: Customer Service AI Agent
          </h3>
          
          <div className="space-y-4">
            <div className="flex items-start gap-4">
              <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center flex-shrink-0">
                <span className="text-green-600 font-bold text-sm">1</span>
              </div>
              <div>
                <strong>Perception:</strong> Customer sends message: "I can't access my account and need help resetting my password."
              </div>
            </div>
            
            <div className="flex items-start gap-4">
              <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center flex-shrink-0">
                <span className="text-green-600 font-bold text-sm">2</span>
              </div>
              <div>
                <strong>Processing:</strong> AI agent understands this is a password reset request, checks customer's account status, and determines the appropriate security verification steps.
              </div>
            </div>
            
            <div className="flex items-start gap-4">
              <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center flex-shrink-0">
                <span className="text-green-600 font-bold text-sm">3</span>
              </div>
              <div>
                <strong>Action:</strong> Agent responds with security questions, guides the customer through verification, and automatically sends a password reset link once verified.
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
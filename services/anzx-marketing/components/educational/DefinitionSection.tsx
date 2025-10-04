'use client';

import { useTranslations } from 'next-intl';
import { Card, CardContent } from '@/components/ui/card';
import { Brain, Zap, Target, Users } from 'lucide-react';

interface DefinitionSectionProps {
  id: string;
}

export default function DefinitionSection({ id }: DefinitionSectionProps) {
  const t = useTranslations('educational.whatIsAiAgent.definition');

  const keyCharacteristics = [
    {
      icon: Brain,
      title: 'Intelligent Decision Making',
      description: 'AI agents can analyze data, understand context, and make informed decisions without human intervention.',
    },
    {
      icon: Zap,
      title: 'Autonomous Action',
      description: 'They can perform tasks independently, adapting their approach based on changing circumstances.',
    },
    {
      icon: Target,
      title: 'Goal-Oriented',
      description: 'AI agents work towards specific objectives, optimizing their actions to achieve desired outcomes.',
    },
    {
      icon: Users,
      title: 'Interactive Communication',
      description: 'They can understand and respond to human language, making them easy to work with.',
    },
  ];

  return (
    <section id={id} className="scroll-mt-8">
      <div className="space-y-8">
        <div>
          <h2 className="text-3xl font-bold text-gray-900 mb-6">
            What is an AI Agent?
          </h2>
          
          <div className="prose prose-lg max-w-none text-gray-600 space-y-4">
            <p>
              An <strong>AI agent</strong> is an intelligent software system that can perceive its environment, 
              make decisions, and take actions to achieve specific goals. Unlike traditional software that 
              follows pre-programmed instructions, AI agents can adapt, learn, and respond to new situations 
              autonomously.
            </p>
            
            <p>
              Think of an AI agent as a digital employee that never sleeps, never takes breaks, and can 
              handle multiple tasks simultaneously. It combines the power of artificial intelligence with 
              the ability to interact with various systems, applications, and people to get work done.
            </p>
          </div>
        </div>

        {/* Key Characteristics */}
        <div>
          <h3 className="text-2xl font-bold text-gray-900 mb-6">
            Key Characteristics of AI Agents
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {keyCharacteristics.map((characteristic, index) => {
              const IconComponent = characteristic.icon;
              
              return (
                <Card key={index} className="hover:shadow-md transition-shadow duration-300">
                  <CardContent className="p-6">
                    <div className="flex items-start gap-4">
                      <div className="flex-shrink-0">
                        <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                          <IconComponent className="h-6 w-6 text-blue-600" />
                        </div>
                      </div>
                      <div>
                        <h4 className="font-semibold text-gray-900 mb-2">
                          {characteristic.title}
                        </h4>
                        <p className="text-gray-600 text-sm">
                          {characteristic.description}
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </div>

        {/* Simple Analogy */}
        <div className="bg-blue-50 rounded-2xl p-8">
          <h3 className="text-2xl font-bold text-gray-900 mb-4">
            Simple Analogy: AI Agent as a Personal Assistant
          </h3>
          
          <div className="prose prose-lg max-w-none text-gray-600">
            <p>
              Imagine you have a highly capable personal assistant who:
            </p>
            <ul className="list-disc pl-6 space-y-2">
              <li>Understands your preferences and goals</li>
              <li>Can communicate with anyone on your behalf</li>
              <li>Has access to all your business systems and data</li>
              <li>Works 24/7 without getting tired</li>
              <li>Learns from every interaction to get better</li>
              <li>Can handle multiple tasks simultaneously</li>
            </ul>
            <p>
              That's essentially what an AI agent does for your business – it acts as an intelligent, 
              always-available team member that can handle a wide range of tasks autonomously.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
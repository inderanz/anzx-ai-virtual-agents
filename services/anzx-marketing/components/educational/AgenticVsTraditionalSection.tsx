'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Check, X, ArrowRight, Zap, Cog, Brain } from 'lucide-react';

interface AgenticVsTraditionalSectionProps {
  id: string;
}

export default function AgenticVsTraditionalSection({ id }: AgenticVsTraditionalSectionProps) {
  const comparisonData = [
    {
      category: 'Decision Making',
      agentic: { 
        capability: 'Autonomous, context-aware decisions',
        description: 'Makes complex decisions based on goals, context, and learned patterns',
        available: true 
      },
      traditional: { 
        capability: 'Rule-based, predetermined responses',
        description: 'Follows pre-programmed decision trees and conditional logic',
        available: true 
      },
      reactive: { 
        capability: 'Human-dependent decisions',
        description: 'Requires human input for any decision beyond simple classifications',
        available: false 
      },
    },
    {
      category: 'Adaptability',
      agentic: { 
        capability: 'Self-improving and adaptive',
        description: 'Learns from outcomes and adjusts strategies automatically',
        available: true 
      },
      traditional: { 
        capability: 'Static, requires manual updates',
        description: 'Needs human intervention to modify rules or processes',
        available: false 
      },
      reactive: { 
        capability: 'Limited pattern recognition',
        description: 'Can identify patterns but cannot change behavior autonomously',
        available: false 
      },
    },
    {
      category: 'Goal Orientation',
      agentic: { 
        capability: 'Multi-step goal achievement',
        description: 'Plans and executes complex strategies to achieve high-level objectives',
        available: true 
      },
      traditional: { 
        capability: 'Task completion focus',
        description: 'Completes specific tasks but lacks broader goal understanding',
        available: false 
      },
      reactive: { 
        capability: 'Response-based operation',
        description: 'Responds to inputs but has no concept of goals or objectives',
        available: false 
      },
    },
    {
      category: 'Coordination',
      agentic: { 
        capability: 'Multi-agent collaboration',
        description: 'Coordinates with other agents and systems to achieve shared goals',
        available: true 
      },
      traditional: { 
        capability: 'Sequential processing',
        description: 'Processes tasks in sequence with limited coordination capabilities',
        available: false 
      },
      reactive: { 
        capability: 'Isolated operation',
        description: 'Operates independently without coordination with other systems',
        available: false 
      },
    },
    {
      category: 'Problem Solving',
      agentic: { 
        capability: 'Creative solution generation',
        description: 'Generates novel approaches when standard methods fail',
        available: true 
      },
      traditional: { 
        capability: 'Predefined solution paths',
        description: 'Limited to solutions programmed into the system',
        available: false 
      },
      reactive: { 
        capability: 'Pattern matching responses',
        description: 'Matches inputs to known patterns and provides corresponding outputs',
        available: false 
      },
    },
    {
      category: 'Temporal Reasoning',
      agentic: { 
        capability: 'Long-term planning and execution',
        description: 'Plans actions across different time horizons and maintains context',
        available: true 
      },
      traditional: { 
        capability: 'Immediate task execution',
        description: 'Focuses on immediate tasks without long-term planning',
        available: false 
      },
      reactive: { 
        capability: 'Real-time response only',
        description: 'Responds to current inputs without temporal context',
        available: false 
      },
    },
  ];

  const approaches = [
    {
      icon: Brain,
      title: 'Agentic AI',
      subtitle: 'Autonomous & Goal-Oriented',
      description: 'Intelligent systems that can plan, reason, and act independently to achieve complex objectives.',
      strengths: ['Autonomous operation', 'Complex problem solving', 'Adaptive learning', 'Multi-agent coordination'],
      limitations: ['Higher complexity', 'Requires careful alignment', 'More computational resources'],
      bestFor: 'Complex, dynamic environments requiring autonomous decision-making and adaptation.',
      color: 'border-purple-200 bg-purple-50',
      iconColor: 'bg-purple-100 text-purple-600',
    },
    {
      icon: Cog,
      title: 'Traditional AI/Automation',
      subtitle: 'Rule-Based & Predictable',
      description: 'Systems that follow predetermined rules and workflows to complete specific tasks efficiently.',
      strengths: ['Predictable behavior', 'Lower complexity', 'Easier to debug', 'Cost-effective'],
      limitations: ['Limited adaptability', 'Requires manual updates', 'Cannot handle exceptions well'],
      bestFor: 'Well-defined, stable processes with clear rules and minimal variation.',
      color: 'border-blue-200 bg-blue-50',
      iconColor: 'bg-blue-100 text-blue-600',
    },
    {
      icon: Zap,
      title: 'Reactive AI',
      subtitle: 'Input-Response Systems',
      description: 'AI systems that respond to specific inputs with learned or programmed responses.',
      strengths: ['Fast responses', 'Simple implementation', 'Low resource usage', 'Easy to understand'],
      limitations: ['No goal awareness', 'Limited context understanding', 'Cannot plan ahead'],
      bestFor: 'Simple classification, recommendation, or response tasks with clear input-output patterns.',
      color: 'border-green-200 bg-green-50',
      iconColor: 'bg-green-100 text-green-600',
    },
  ];

  return (
    <section id={id} className="scroll-mt-8">
      <div className="space-y-8">
        <div>
          <h2 className="text-3xl font-bold text-gray-900 mb-6">
            Agentic AI vs Traditional AI vs Reactive AI
          </h2>
          
          <div className="prose prose-lg max-w-none text-gray-600 mb-8">
            <p>
              Understanding the differences between agentic AI, traditional automation, and reactive AI 
              helps you choose the right approach for your specific use cases and organizational needs.
            </p>
          </div>
        </div>

        {/* Approach Overview */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {approaches.map((approach, index) => {
            const IconComponent = approach.icon;
            
            return (
              <Card key={index} className={`${approach.color} border-2`}>
                <CardHeader className="text-center">
                  <div className={`w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4 ${approach.iconColor}`}>
                    <IconComponent className="h-8 w-8" />
                  </div>
                  <CardTitle className="text-xl">
                    {approach.title}
                  </CardTitle>
                  <p className="text-sm font-medium text-gray-600">
                    {approach.subtitle}
                  </p>
                  <p className="text-gray-600">
                    {approach.description}
                  </p>
                </CardHeader>
                
                <CardContent className="space-y-4">
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-2">Strengths:</h4>
                    <ul className="space-y-1">
                      {approach.strengths.map((strength, strengthIndex) => (
                        <li key={strengthIndex} className="flex items-start gap-2 text-sm text-gray-600">
                          <Check className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                          {strength}
                        </li>
                      ))}
                    </ul>
                  </div>
                  
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-2">Limitations:</h4>
                    <ul className="space-y-1">
                      {approach.limitations.map((limitation, limitationIndex) => (
                        <li key={limitationIndex} className="flex items-start gap-2 text-sm text-gray-600">
                          <X className="h-4 w-4 text-red-500 mt-0.5 flex-shrink-0" />
                          {limitation}
                        </li>
                      ))}
                    </ul>
                  </div>
                  
                  <div className="bg-white rounded-lg p-3">
                    <h4 className="font-semibold text-gray-900 mb-1 text-sm">Best For:</h4>
                    <p className="text-xs text-gray-600">
                      {approach.bestFor}
                    </p>
                  </div>
                </CardContent>
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
                  <th className="px-6 py-4 text-left font-semibold text-gray-900">Capability</th>
                  <th className="px-6 py-4 text-center font-semibold text-purple-600">Agentic AI</th>
                  <th className="px-6 py-4 text-center font-semibold text-blue-600">Traditional AI</th>
                  <th className="px-6 py-4 text-center font-semibold text-green-600">Reactive AI</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {comparisonData.map((row, index) => (
                  <tr key={index} className="hover:bg-gray-50">
                    <td className="px-6 py-4 font-medium text-gray-900">
                      {row.category}
                    </td>
                    <td className="px-6 py-4 text-center">
                      <div className="flex flex-col items-center gap-2">
                        {row.agentic.available ? (
                          <Check className="h-5 w-5 text-green-500" />
                        ) : (
                          <X className="h-5 w-5 text-red-500" />
                        )}
                        <div className="text-xs text-gray-600 text-center max-w-xs">
                          <div className="font-medium mb-1">{row.agentic.capability}</div>
                          <div>{row.agentic.description}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-center">
                      <div className="flex flex-col items-center gap-2">
                        {row.traditional.available ? (
                          <Check className="h-5 w-5 text-green-500" />
                        ) : (
                          <X className="h-5 w-5 text-red-500" />
                        )}
                        <div className="text-xs text-gray-600 text-center max-w-xs">
                          <div className="font-medium mb-1">{row.traditional.capability}</div>
                          <div>{row.traditional.description}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-center">
                      <div className="flex flex-col items-center gap-2">
                        {row.reactive.available ? (
                          <Check className="h-5 w-5 text-green-500" />
                        ) : (
                          <X className="h-5 w-5 text-red-500" />
                        )}
                        <div className="text-xs text-gray-600 text-center max-w-xs">
                          <div className="font-medium mb-1">{row.reactive.capability}</div>
                          <div>{row.reactive.description}</div>
                        </div>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Decision Framework */}
        <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-2xl p-8">
          <h3 className="text-2xl font-bold text-gray-900 mb-6">
            Choosing the Right Approach: Decision Framework
          </h3>
          
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <Card className="border-purple-200">
                <CardHeader className="text-center">
                  <Brain className="h-8 w-8 text-purple-600 mx-auto mb-2" />
                  <CardTitle className="text-lg text-purple-600">Choose Agentic AI When:</CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2 text-sm text-gray-600">
                    <li>• Complex, multi-step processes</li>
                    <li>• Dynamic, changing environments</li>
                    <li>• Need for autonomous operation</li>
                    <li>• Long-term goal achievement</li>
                    <li>• Coordination between multiple systems</li>
                    <li>• Creative problem-solving required</li>
                  </ul>
                </CardContent>
              </Card>

              <Card className="border-blue-200">
                <CardHeader className="text-center">
                  <Cog className="h-8 w-8 text-blue-600 mx-auto mb-2" />
                  <CardTitle className="text-lg text-blue-600">Choose Traditional AI When:</CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2 text-sm text-gray-600">
                    <li>• Well-defined, stable processes</li>
                    <li>• Predictable environments</li>
                    <li>• Clear rules and workflows</li>
                    <li>• Cost is a primary concern</li>
                    <li>• Regulatory compliance requirements</li>
                    <li>• Simple task automation</li>
                  </ul>
                </CardContent>
              </Card>

              <Card className="border-green-200">
                <CardHeader className="text-center">
                  <Zap className="h-8 w-8 text-green-600 mx-auto mb-2" />
                  <CardTitle className="text-lg text-green-600">Choose Reactive AI When:</CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2 text-sm text-gray-600">
                    <li>• Simple input-output tasks</li>
                    <li>• Fast response requirements</li>
                    <li>• Limited computational resources</li>
                    <li>• Classification or recommendation</li>
                    <li>• Minimal complexity tolerance</li>
                    <li>• Proof of concept projects</li>
                  </ul>
                </CardContent>
              </Card>
            </div>
            
            <div className="text-center">
              <p className="text-gray-600 mb-4">
                Many organizations benefit from a <strong>hybrid approach</strong>, using different AI types 
                for different use cases based on complexity and requirements.
              </p>
              <div className="flex items-center justify-center gap-2 text-sm text-gray-500">
                <span>Reactive AI</span>
                <ArrowRight className="h-4 w-4" />
                <span>Traditional AI</span>
                <ArrowRight className="h-4 w-4" />
                <span>Agentic AI</span>
              </div>
              <p className="text-xs text-gray-500 mt-2">Typical progression path</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
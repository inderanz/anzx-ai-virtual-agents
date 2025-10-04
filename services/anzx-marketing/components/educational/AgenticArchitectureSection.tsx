'use client';

import { Card, CardContent } from '@/components/ui/card';
import { ArrowRight, Brain, Eye, Cog, Database, Network, Shield } from 'lucide-react';

interface AgenticArchitectureSectionProps {
  id: string;
}

export default function AgenticArchitectureSection({ id }: AgenticArchitectureSectionProps) {
  const architectureComponents = [
    {
      icon: Eye,
      title: 'Perception Layer',
      description: 'Processes and interprets information from multiple sources and modalities.',
      components: ['Natural Language Processing', 'Computer Vision', 'Data Analysis', 'Sensor Integration'],
      color: 'bg-blue-100 text-blue-600',
    },
    {
      icon: Brain,
      title: 'Reasoning Engine',
      description: 'Core intelligence that processes information and makes decisions.',
      components: ['Large Language Models', 'Knowledge Graphs', 'Logical Reasoning', 'Causal Inference'],
      color: 'bg-purple-100 text-purple-600',
    },
    {
      icon: Database,
      title: 'Memory Systems',
      description: 'Stores and retrieves information for learning and decision-making.',
      components: ['Working Memory', 'Long-term Storage', 'Episodic Memory', 'Semantic Knowledge'],
      color: 'bg-green-100 text-green-600',
    },
    {
      icon: Cog,
      title: 'Action Execution',
      description: 'Translates decisions into concrete actions in the environment.',
      components: ['API Integrations', 'Tool Usage', 'Communication', 'Process Automation'],
      color: 'bg-orange-100 text-orange-600',
    },
    {
      icon: Network,
      title: 'Coordination Layer',
      description: 'Manages interactions with other agents and systems.',
      components: ['Agent Communication', 'Task Delegation', 'Conflict Resolution', 'Resource Sharing'],
      color: 'bg-indigo-100 text-indigo-600',
    },
    {
      icon: Shield,
      title: 'Safety & Monitoring',
      description: 'Ensures safe and aligned operation within defined boundaries.',
      components: ['Goal Alignment', 'Safety Constraints', 'Performance Monitoring', 'Error Recovery'],
      color: 'bg-red-100 text-red-600',
    },
  ];

  const agenticLoop = [
    {
      step: 1,
      title: 'Observe',
      description: 'Gather information from environment, users, and other systems',
      details: 'Continuous monitoring of relevant data sources, user interactions, and system states',
    },
    {
      step: 2,
      title: 'Reason',
      description: 'Analyze information and determine optimal course of action',
      details: 'Apply reasoning models, consider constraints, evaluate options, and make decisions',
    },
    {
      step: 3,
      title: 'Plan',
      description: 'Create detailed execution strategy to achieve objectives',
      details: 'Break down goals into actionable steps, allocate resources, and set timelines',
    },
    {
      step: 4,
      title: 'Act',
      description: 'Execute planned actions through available tools and interfaces',
      details: 'Interact with systems, communicate with users, and modify environment state',
    },
    {
      step: 5,
      title: 'Learn',
      description: 'Update knowledge and strategies based on outcomes',
      details: 'Analyze results, update models, refine strategies, and improve future performance',
    },
  ];

  return (
    <section id={id} className="scroll-mt-8">
      <div className="space-y-8">
        <div>
          <h2 className="text-3xl font-bold text-gray-900 mb-6">
            How Agentic AI Works: Architecture & Process
          </h2>
          
          <div className="prose prose-lg max-w-none text-gray-600 mb-8">
            <p>
              Agentic AI systems are built on sophisticated architectures that enable autonomous 
              operation. Understanding these components and processes helps explain how these 
              systems achieve their remarkable capabilities.
            </p>
          </div>
        </div>

        {/* Architecture Components */}
        <div>
          <h3 className="text-2xl font-bold text-gray-900 mb-6">
            Core Architecture Components
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {architectureComponents.map((component, index) => {
              const IconComponent = component.icon;
              
              return (
                <Card key={index} className="h-full hover:shadow-md transition-shadow duration-300">
                  <CardContent className="p-6">
                    <div className="space-y-4">
                      <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${component.color}`}>
                        <IconComponent className="h-6 w-6" />
                      </div>
                      
                      <div>
                        <h4 className="font-semibold text-gray-900 mb-2">
                          {component.title}
                        </h4>
                        <p className="text-gray-600 text-sm mb-3">
                          {component.description}
                        </p>
                        
                        <div className="space-y-1">
                          {component.components.map((item, itemIndex) => (
                            <div key={itemIndex} className="text-xs text-gray-500 bg-gray-50 rounded px-2 py-1">
                              {item}
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </div>

        {/* Agentic Loop */}
        <div>
          <h3 className="text-2xl font-bold text-gray-900 mb-6">
            The Agentic Loop: Continuous Operation Cycle
          </h3>
          
          <div className="space-y-6">
            {agenticLoop.map((phase, index) => {
              const isLast = index === agenticLoop.length - 1;
              
              return (
                <div key={index} className="relative">
                  <Card className="hover:shadow-md transition-shadow duration-300">
                    <CardContent className="p-6">
                      <div className="flex items-start gap-6">
                        {/* Step Number */}
                        <div className="flex-shrink-0 text-center">
                          <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-blue-500 text-white rounded-full flex items-center justify-center mb-2 font-bold">
                            {phase.step}
                          </div>
                        </div>
                        
                        {/* Content */}
                        <div className="flex-1">
                          <h4 className="text-xl font-bold text-gray-900 mb-2">
                            {phase.title}
                          </h4>
                          <p className="text-gray-600 mb-3">
                            {phase.description}
                          </p>
                          <div className="bg-gray-50 rounded-lg p-3">
                            <p className="text-sm text-gray-600">
                              <strong>Details:</strong> {phase.details}
                            </p>
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
                  
                  {/* Loop back arrow for last step */}
                  {isLast && (
                    <div className="flex justify-center my-4">
                      <div className="flex items-center gap-2 text-gray-500">
                        <span className="text-sm">Continuous Loop</span>
                        <div className="w-8 h-8 border-2 border-gray-300 border-dashed rounded-full flex items-center justify-center">
                          <ArrowRight className="h-4 w-4 transform rotate-90" />
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Technical Implementation */}
        <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-2xl p-8">
          <h3 className="text-2xl font-bold text-gray-900 mb-6">
            Technical Implementation at ANZX.ai
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div>
              <h4 className="font-semibold text-gray-900 mb-3">Foundation Technologies</h4>
              <ul className="space-y-2 text-gray-600">
                <li className="flex items-start gap-2">
                  <div className="w-2 h-2 bg-purple-400 rounded-full mt-2 flex-shrink-0" />
                  Google Gemini 1.5 Pro for advanced reasoning
                </li>
                <li className="flex items-start gap-2">
                  <div className="w-2 h-2 bg-purple-400 rounded-full mt-2 flex-shrink-0" />
                  Vertex AI for scalable ML operations
                </li>
                <li className="flex items-start gap-2">
                  <div className="w-2 h-2 bg-purple-400 rounded-full mt-2 flex-shrink-0" />
                  Google Agent Development Kit (ADK)
                </li>
                <li className="flex items-start gap-2">
                  <div className="w-2 h-2 bg-purple-400 rounded-full mt-2 flex-shrink-0" />
                  Agent-to-Agent (A2A) Protocol
                </li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-semibold text-gray-900 mb-3">Infrastructure</h4>
              <ul className="space-y-2 text-gray-600">
                <li className="flex items-start gap-2">
                  <div className="w-2 h-2 bg-blue-400 rounded-full mt-2 flex-shrink-0" />
                  Google AgentSpace for orchestration
                </li>
                <li className="flex items-start gap-2">
                  <div className="w-2 h-2 bg-blue-400 rounded-full mt-2 flex-shrink-0" />
                  Cloud SQL with pgvector for memory
                </li>
                <li className="flex items-start gap-2">
                  <div className="w-2 h-2 bg-blue-400 rounded-full mt-2 flex-shrink-0" />
                  MCP servers for external integrations
                </li>
                <li className="flex items-start gap-2">
                  <div className="w-2 h-2 bg-blue-400 rounded-full mt-2 flex-shrink-0" />
                  Workload Identity Federation for security
                </li>
              </ul>
            </div>
          </div>
          
          <div className="mt-6 text-center">
            <p className="text-gray-600">
              This architecture enables ANZX.ai agents to operate with enterprise-grade reliability, 
              security, and scalability while maintaining the flexibility needed for agentic behavior.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
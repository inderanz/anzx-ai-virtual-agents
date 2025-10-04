'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  MessageCircle, 
  Phone, 
  Users, 
  ShoppingCart, 
  FileText, 
  BarChart3,
  Wrench,
  Globe
} from 'lucide-react';

interface TypesOfAgentsSectionProps {
  id: string;
}

export default function TypesOfAgentsSection({ id }: TypesOfAgentsSectionProps) {
  const agentTypes = [
    {
      icon: MessageCircle,
      title: 'Customer Service Agents',
      description: 'Handle customer inquiries, resolve issues, and provide support across multiple channels.',
      capabilities: ['24/7 availability', 'Multi-language support', 'Ticket routing', 'Knowledge base integration'],
      useCase: 'A customer service agent that handles 80% of support tickets automatically, escalating complex issues to human agents.',
      popular: true,
    },
    {
      icon: Phone,
      title: 'Sales Agents',
      description: 'Qualify leads, conduct sales calls, and guide prospects through the sales funnel.',
      capabilities: ['Lead qualification', 'Call automation', 'CRM integration', 'Follow-up scheduling'],
      useCase: 'A sales agent that makes 100+ outbound calls daily, qualifying leads and booking meetings for sales reps.',
      popular: true,
    },
    {
      icon: Users,
      title: 'Recruiting Agents',
      description: 'Screen candidates, conduct initial interviews, and manage the hiring pipeline.',
      capabilities: ['Resume screening', 'Interview scheduling', 'Candidate assessment', 'ATS integration'],
      useCase: 'A recruiting agent that screens 500+ resumes per day and conducts initial phone interviews.',
      popular: true,
    },
    {
      icon: FileText,
      title: 'Administrative Agents',
      description: 'Handle routine administrative tasks like data entry, document processing, and scheduling.',
      capabilities: ['Data processing', 'Document generation', 'Calendar management', 'Email automation'],
      useCase: 'An admin agent that processes invoices, updates spreadsheets, and schedules meetings automatically.',
      popular: false,
    },
    {
      icon: BarChart3,
      title: 'Analytics Agents',
      description: 'Analyze data, generate reports, and provide business insights automatically.',
      capabilities: ['Data analysis', 'Report generation', 'Trend identification', 'Alert notifications'],
      useCase: 'An analytics agent that monitors KPIs and sends daily performance reports to management.',
      popular: false,
    },
    {
      icon: Wrench,
      title: 'Technical Support Agents',
      description: 'Diagnose technical issues, provide troubleshooting guidance, and manage IT tickets.',
      capabilities: ['Issue diagnosis', 'Solution recommendations', 'System monitoring', 'Escalation management'],
      useCase: 'A technical agent that resolves 70% of IT tickets without human intervention.',
      popular: false,
    },
  ];

  return (
    <section id={id} className="scroll-mt-8">
      <div className="space-y-8">
        <div>
          <h2 className="text-3xl font-bold text-gray-900 mb-6">
            Types of AI Agents
          </h2>
          
          <div className="prose prose-lg max-w-none text-gray-600 mb-8">
            <p>
              AI agents can be specialized for different business functions. Here are the most common 
              types and their specific capabilities:
            </p>
          </div>
        </div>

        {/* Agent Types Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {agentTypes.map((agent, index) => {
            const IconComponent = agent.icon;
            
            return (
              <Card key={index} className="h-full hover:shadow-lg transition-shadow duration-300">
                <CardHeader>
                  <div className="flex items-start justify-between mb-4">
                    <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                      <IconComponent className="h-6 w-6 text-blue-600" />
                    </div>
                    {agent.popular && (
                      <Badge className="bg-green-100 text-green-800">
                        Most Popular
                      </Badge>
                    )}
                  </div>
                  <CardTitle className="text-xl">
                    {agent.title}
                  </CardTitle>
                </CardHeader>
                
                <CardContent className="space-y-4">
                  <p className="text-gray-600">
                    {agent.description}
                  </p>
                  
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-2">Key Capabilities:</h4>
                    <div className="flex flex-wrap gap-2">
                      {agent.capabilities.map((capability, capIndex) => (
                        <span
                          key={capIndex}
                          className="bg-gray-100 text-gray-700 px-2 py-1 rounded text-sm"
                        >
                          {capability}
                        </span>
                      ))}
                    </div>
                  </div>
                  
                  <div className="bg-blue-50 rounded-lg p-4">
                    <h4 className="font-semibold text-gray-900 mb-2">Example Use Case:</h4>
                    <p className="text-gray-600 text-sm">
                      {agent.useCase}
                    </p>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* Specialization Note */}
        <div className="bg-yellow-50 rounded-2xl p-8">
          <div className="flex items-start gap-4">
            <Globe className="h-8 w-8 text-yellow-600 flex-shrink-0 mt-1" />
            <div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">
                Custom AI Agents for Your Industry
              </h3>
              <p className="text-gray-600 mb-4">
                While these are common types, AI agents can be customized for any industry or specific 
                business process. The key is identifying repetitive tasks that require decision-making 
                and can benefit from automation.
              </p>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-yellow-600">Healthcare</div>
                  <div className="text-sm text-gray-500">Patient scheduling, medical records</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-yellow-600">Finance</div>
                  <div className="text-sm text-gray-500">Fraud detection, loan processing</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-yellow-600">Education</div>
                  <div className="text-sm text-gray-500">Student support, grading assistance</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
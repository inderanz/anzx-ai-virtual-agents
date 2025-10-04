'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  Search, 
  Target, 
  Cog, 
  Rocket, 
  TrendingUp, 
  CheckCircle,
  AlertTriangle,
  Users,
  Shield,
  Clock
} from 'lucide-react';

interface AgenticImplementationSectionProps {
  id: string;
}

export default function AgenticImplementationSection({ id }: AgenticImplementationSectionProps) {
  const implementationPhases = [
    {
      icon: Search,
      phase: 1,
      title: 'Discovery & Assessment',
      duration: '2-4 weeks',
      description: 'Identify opportunities, assess readiness, and define success criteria.',
      activities: [
        'Business process analysis and mapping',
        'Technical infrastructure assessment',
        'Stakeholder interviews and requirements gathering',
        'ROI modeling and business case development',
        'Risk assessment and mitigation planning',
      ],
      deliverables: ['Opportunity assessment report', 'Technical readiness evaluation', 'Implementation roadmap'],
      keyConsiderations: ['Data quality and availability', 'Organizational change readiness', 'Technical infrastructure gaps'],
    },
    {
      icon: Target,
      phase: 2,
      title: 'Design & Planning',
      duration: '3-6 weeks',
      description: 'Design the agentic system architecture and create detailed implementation plans.',
      activities: [
        'Agent behavior design and goal definition',
        'System architecture and integration planning',
        'Data pipeline and knowledge base design',
        'Safety and monitoring framework development',
        'Testing and validation strategy creation',
      ],
      deliverables: ['System architecture document', 'Agent behavior specifications', 'Integration plan'],
      keyConsiderations: ['Goal alignment and safety constraints', 'Integration complexity', 'Performance requirements'],
    },
    {
      icon: Cog,
      title: 'Development & Training',
      phase: 3,
      duration: '6-12 weeks',
      description: 'Build, train, and configure the agentic AI system.',
      activities: [
        'Agent development using Google ADK framework',
        'Model training and fine-tuning',
        'Integration development and testing',
        'Safety mechanism implementation',
        'Performance optimization and tuning',
      ],
      deliverables: ['Trained agentic AI system', 'Integration components', 'Safety and monitoring tools'],
      keyConsiderations: ['Model performance and accuracy', 'Integration stability', 'Safety mechanism effectiveness'],
    },
    {
      icon: Rocket,
      phase: 4,
      title: 'Pilot & Validation',
      duration: '4-8 weeks',
      description: 'Deploy in controlled environment and validate performance.',
      activities: [
        'Pilot deployment in limited scope',
        'Performance monitoring and evaluation',
        'User feedback collection and analysis',
        'System refinement and optimization',
        'Stakeholder training and change management',
      ],
      deliverables: ['Pilot results report', 'Refined system', 'Training materials'],
      keyConsiderations: ['User adoption and feedback', 'Performance against KPIs', 'System stability'],
    },
    {
      icon: TrendingUp,
      phase: 5,
      title: 'Scale & Optimize',
      duration: 'Ongoing',
      description: 'Full deployment with continuous monitoring and improvement.',
      activities: [
        'Full-scale deployment and rollout',
        'Continuous performance monitoring',
        'Regular system updates and improvements',
        'Advanced feature development',
        'Expansion to additional use cases',
      ],
      deliverables: ['Production system', 'Monitoring dashboards', 'Optimization reports'],
      keyConsiderations: ['Scalability and performance', 'Continuous learning effectiveness', 'Business impact measurement'],
    },
  ];

  const successFactors = [
    {
      icon: Users,
      title: 'Stakeholder Alignment',
      description: 'Ensure all stakeholders understand goals, benefits, and their role in the implementation.',
      importance: 'Critical',
      tips: ['Regular communication and updates', 'Clear role definitions', 'Change management support'],
    },
    {
      icon: Target,
      title: 'Clear Goal Definition',
      description: 'Define specific, measurable objectives that the agentic system should achieve.',
      importance: 'Critical',
      tips: ['SMART goal framework', 'Success metrics definition', 'Regular goal review and adjustment'],
    },
    {
      icon: Shield,
      title: 'Safety & Governance',
      description: 'Implement robust safety measures and governance frameworks for autonomous operation.',
      importance: 'High',
      tips: ['Safety constraint definition', 'Monitoring and alerting', 'Human oversight mechanisms'],
    },
    {
      icon: Clock,
      title: 'Iterative Approach',
      description: 'Start with simpler use cases and gradually increase complexity and autonomy.',
      importance: 'High',
      tips: ['Phased rollout strategy', 'Regular feedback cycles', 'Continuous improvement mindset'],
    },
  ];

  const getImportanceColor = (importance: string) => {
    switch (importance) {
      case 'Critical': return 'bg-red-100 text-red-800';
      case 'High': return 'bg-orange-100 text-orange-800';
      case 'Medium': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <section id={id} className="scroll-mt-8">
      <div className="space-y-8">
        <div>
          <h2 className="text-3xl font-bold text-gray-900 mb-6">
            Implementation Guide for Agentic AI
          </h2>
          
          <div className="prose prose-lg max-w-none text-gray-600 mb-8">
            <p>
              Implementing agentic AI requires a structured approach that balances ambition with 
              practical considerations. This guide outlines the key phases, success factors, 
              and best practices for successful agentic AI deployment.
            </p>
          </div>
        </div>

        {/* Implementation Phases */}
        <div className="space-y-8">
          <h3 className="text-2xl font-bold text-gray-900">
            Implementation Phases
          </h3>
          
          {implementationPhases.map((phase, index) => {
            const IconComponent = phase.icon;
            
            return (
              <Card key={index} className="hover:shadow-lg transition-shadow duration-300">
                <CardHeader>
                  <div className="flex items-start gap-4">
                    <div className="flex-shrink-0">
                      <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-blue-500 text-white rounded-full flex items-center justify-center font-bold">
                        {phase.phase}
                      </div>
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <CardTitle className="text-xl">
                          {phase.title}
                        </CardTitle>
                        <Badge variant="secondary">
                          {phase.duration}
                        </Badge>
                      </div>
                      <p className="text-gray-600">
                        {phase.description}
                      </p>
                    </div>
                  </div>
                </CardHeader>
                
                <CardContent className="space-y-6">
                  <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Activities */}
                    <div>
                      <h4 className="font-semibold text-gray-900 mb-3">Key Activities:</h4>
                      <ul className="space-y-2">
                        {phase.activities.map((activity, activityIndex) => (
                          <li key={activityIndex} className="flex items-start gap-2 text-sm text-gray-600">
                            <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                            {activity}
                          </li>
                        ))}
                      </ul>
                    </div>
                    
                    {/* Deliverables */}
                    <div>
                      <h4 className="font-semibold text-gray-900 mb-3">Deliverables:</h4>
                      <ul className="space-y-2">
                        {phase.deliverables.map((deliverable, deliverableIndex) => (
                          <li key={deliverableIndex} className="text-sm text-gray-600 bg-blue-50 rounded px-2 py-1">
                            {deliverable}
                          </li>
                        ))}
                      </ul>
                    </div>
                    
                    {/* Key Considerations */}
                    <div>
                      <h4 className="font-semibold text-gray-900 mb-3">Key Considerations:</h4>
                      <ul className="space-y-2">
                        {phase.keyConsiderations.map((consideration, considerationIndex) => (
                          <li key={considerationIndex} className="flex items-start gap-2 text-sm text-gray-600">
                            <AlertTriangle className="h-4 w-4 text-orange-500 mt-0.5 flex-shrink-0" />
                            {consideration}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* Success Factors */}
        <div>
          <h3 className="text-2xl font-bold text-gray-900 mb-6">
            Critical Success Factors
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {successFactors.map((factor, index) => {
              const IconComponent = factor.icon;
              
              return (
                <Card key={index} className="hover:shadow-md transition-shadow duration-300">
                  <CardHeader>
                    <div className="flex items-start gap-4">
                      <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                        <IconComponent className="h-6 w-6 text-purple-600" />
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <CardTitle className="text-lg">
                            {factor.title}
                          </CardTitle>
                          <Badge className={getImportanceColor(factor.importance)}>
                            {factor.importance}
                          </Badge>
                        </div>
                        <p className="text-gray-600 text-sm">
                          {factor.description}
                        </p>
                      </div>
                    </div>
                  </CardHeader>
                  
                  <CardContent>
                    <h4 className="font-semibold text-gray-900 mb-2">Best Practices:</h4>
                    <ul className="space-y-1">
                      {factor.tips.map((tip, tipIndex) => (
                        <li key={tipIndex} className="flex items-start gap-2 text-sm text-gray-600">
                          <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                          {tip}
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </div>

        {/* Timeline & Resources */}
        <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-2xl p-8">
          <h3 className="text-2xl font-bold text-gray-900 mb-6">
            Typical Timeline & Resource Requirements
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div>
              <h4 className="font-semibold text-gray-900 mb-4">Timeline by Complexity</h4>
              <div className="space-y-3">
                <div className="bg-white rounded-lg p-4">
                  <div className="flex justify-between items-center mb-2">
                    <span className="font-medium text-gray-900">Medium Complexity</span>
                    <Badge className="bg-green-100 text-green-800">4-6 months</Badge>
                  </div>
                  <p className="text-sm text-gray-600">Single domain, clear objectives, limited integrations</p>
                </div>
                
                <div className="bg-white rounded-lg p-4">
                  <div className="flex justify-between items-center mb-2">
                    <span className="font-medium text-gray-900">High Complexity</span>
                    <Badge className="bg-yellow-100 text-yellow-800">6-10 months</Badge>
                  </div>
                  <p className="text-sm text-gray-600">Multi-domain, complex workflows, multiple integrations</p>
                </div>
                
                <div className="bg-white rounded-lg p-4">
                  <div className="flex justify-between items-center mb-2">
                    <span className="font-medium text-gray-900">Very High Complexity</span>
                    <Badge className="bg-red-100 text-red-800">10-18 months</Badge>
                  </div>
                  <p className="text-sm text-gray-600">Mission-critical, regulatory compliance, real-time decisions</p>
                </div>
              </div>
            </div>
            
            <div>
              <h4 className="font-semibold text-gray-900 mb-4">Team Composition</h4>
              <div className="space-y-3">
                <div className="bg-white rounded-lg p-4">
                  <h5 className="font-medium text-gray-900 mb-2">Core Team (Required)</h5>
                  <ul className="text-sm text-gray-600 space-y-1">
                    <li>• AI/ML Engineer (1-2 FTE)</li>
                    <li>• Business Analyst (0.5-1 FTE)</li>
                    <li>• Integration Developer (0.5-1 FTE)</li>
                    <li>• Project Manager (0.5 FTE)</li>
                  </ul>
                </div>
                
                <div className="bg-white rounded-lg p-4">
                  <h5 className="font-medium text-gray-900 mb-2">Extended Team (As Needed)</h5>
                  <ul className="text-sm text-gray-600 space-y-1">
                    <li>• Data Engineer (0.5 FTE)</li>
                    <li>• UX/UI Designer (0.25 FTE)</li>
                    <li>• Security Specialist (0.25 FTE)</li>
                    <li>• Change Management (0.25 FTE)</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
          
          <div className="mt-6 text-center">
            <p className="text-gray-600">
              ANZX.ai provides expert guidance and support throughout the entire implementation process, 
              helping you navigate complexity and achieve successful outcomes.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
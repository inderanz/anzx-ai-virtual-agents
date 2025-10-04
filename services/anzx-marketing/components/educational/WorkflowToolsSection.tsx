'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { CheckCircle, Star } from 'lucide-react';

interface WorkflowToolsSectionProps {
  id: string;
}

export default function WorkflowToolsSection({ id }: WorkflowToolsSectionProps) {
  const toolCategories = [
    {
      category: 'No-Code/Low-Code Platforms',
      description: 'Visual workflow builders for business users',
      tools: [
        { name: 'Zapier', features: ['5000+ integrations', 'Visual builder', 'Templates'], pricing: 'Freemium' },
        { name: 'Microsoft Power Automate', features: ['Office 365 integration', 'AI capabilities', 'Enterprise security'], pricing: 'Subscription' },
        { name: 'Nintex', features: ['Advanced workflows', 'Process mapping', 'Analytics'], pricing: 'Enterprise' },
      ],
      bestFor: 'Business users who need quick automation without coding',
    },
    {
      category: 'Enterprise Automation',
      description: 'Comprehensive platforms for large-scale automation',
      tools: [
        { name: 'UiPath', features: ['RPA capabilities', 'AI integration', 'Process mining'], pricing: 'Enterprise' },
        { name: 'Automation Anywhere', features: ['Bot marketplace', 'Cloud-native', 'Analytics'], pricing: 'Enterprise' },
        { name: 'Blue Prism', features: ['Digital workforce', 'Security focus', 'Scalability'], pricing: 'Enterprise' },
      ],
      bestFor: 'Large enterprises with complex automation needs',
    },
    {
      category: 'AI-Powered Automation',
      description: 'Intelligent automation with AI capabilities',
      tools: [
        { name: 'ANZX.ai', features: ['Agentic AI', 'Natural language', 'Multi-agent coordination'], pricing: 'Subscription', featured: true },
        { name: 'WorkFusion', features: ['Intelligent automation', 'ML models', 'Document processing'], pricing: 'Enterprise' },
        { name: 'Pega', features: ['Case management', 'Decision automation', 'Customer engagement'], pricing: 'Enterprise' },
      ],
      bestFor: 'Organizations needing intelligent, adaptive automation',
    },
  ];

  return (
    <section id={id} className="scroll-mt-8">
      <div className="space-y-8">
        <div>
          <h2 className="text-3xl font-bold text-gray-900 mb-6">
            Workflow Automation Tools & Technologies
          </h2>
          
          <div className="prose prose-lg max-w-none text-gray-600 mb-8">
            <p>
              Choose the right automation platform based on your technical requirements, 
              team capabilities, and business objectives.
            </p>
          </div>
        </div>

        <div className="space-y-8">
          {toolCategories.map((category, index) => (
            <div key={index}>
              <h3 className="text-xl font-bold text-gray-900 mb-4">
                {category.category}
              </h3>
              <p className="text-gray-600 mb-6">{category.description}</p>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                {category.tools.map((tool, toolIndex) => (
                  <Card key={toolIndex} className={`hover:shadow-md transition-shadow duration-300 ${
                    tool.featured ? 'border-blue-500 border-2' : ''
                  }`}>
                    <CardHeader>
                      <div className="flex items-center justify-between">
                        <CardTitle className="text-lg flex items-center gap-2">
                          {tool.name}
                          {tool.featured && <Star className="h-4 w-4 text-blue-500 fill-current" />}
                        </CardTitle>
                        <Badge variant={tool.pricing === 'Freemium' ? 'secondary' : 'secondary'}>
                          {tool.pricing}
                        </Badge>
                      </div>
                    </CardHeader>
                    
                    <CardContent>
                      <ul className="space-y-2">
                        {tool.features.map((feature, featureIndex) => (
                          <li key={featureIndex} className="flex items-start gap-2 text-sm text-gray-600">
                            <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                            {feature}
                          </li>
                        ))}
                      </ul>
                    </CardContent>
                  </Card>
                ))}
              </div>
              
              <div className="bg-blue-50 rounded-lg p-4">
                <p className="text-sm text-gray-600">
                  <strong>Best For:</strong> {category.bestFor}
                </p>
              </div>
            </div>
          ))}
        </div>

        {/* Selection Guide */}
        <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-2xl p-8">
          <h3 className="text-2xl font-bold text-gray-900 mb-6">
            How to Choose the Right Tool
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div>
              <h4 className="font-semibold text-gray-900 mb-4">Key Considerations</h4>
              <ul className="space-y-3">
                <li className="flex items-start gap-3">
                  <CheckCircle className="h-5 w-5 text-green-500 mt-0.5 flex-shrink-0" />
                  <span className="text-gray-600">Technical expertise of your team</span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle className="h-5 w-5 text-green-500 mt-0.5 flex-shrink-0" />
                  <span className="text-gray-600">Complexity of workflows needed</span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle className="h-5 w-5 text-green-500 mt-0.5 flex-shrink-0" />
                  <span className="text-gray-600">Integration requirements</span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle className="h-5 w-5 text-green-500 mt-0.5 flex-shrink-0" />
                  <span className="text-gray-600">Budget and pricing model</span>
                </li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-semibold text-gray-900 mb-4">Decision Framework</h4>
              <div className="space-y-3 text-sm">
                <div className="bg-white rounded-lg p-3">
                  <strong>Start Simple:</strong> Begin with no-code tools for basic workflows
                </div>
                <div className="bg-white rounded-lg p-3">
                  <strong>Scale Up:</strong> Move to enterprise platforms as needs grow
                </div>
                <div className="bg-white rounded-lg p-3">
                  <strong>Add Intelligence:</strong> Incorporate AI when ready for advanced automation
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
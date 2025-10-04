'use client';

import { Button } from '@/components/ui/Button';
import { Card, CardContent } from '@/components/ui/card';
import { ArrowRight, MessageCircle, Calendar, BookOpen } from 'lucide-react';

interface GetStartedCTAProps {
  id: string;
}

export default function GetStartedCTA({ id }: GetStartedCTAProps) {
  const nextSteps = [
    {
      icon: MessageCircle,
      title: 'Talk to an Expert',
      description: 'Schedule a consultation to discuss your specific use case',
      cta: 'Book Consultation',
      primary: true,
    },
    {
      icon: Calendar,
      title: 'See a Demo',
      description: 'Watch AI agents in action with a personalized demo',
      cta: 'Request Demo',
      primary: false,
    },
    {
      icon: BookOpen,
      title: 'Learn More',
      description: 'Explore our other educational resources and guides',
      cta: 'Browse Resources',
      primary: false,
    },
  ];

  return (
    <section id={id} className="scroll-mt-8">
      <div className="bg-gradient-to-r from-blue-50 to-indigo-100 rounded-2xl p-8 lg:p-12">
        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Ready to Get Started with AI Agents?
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Now that you understand what AI agents are and how they can benefit your business, 
            let's explore how ANZX.ai can help you implement them.
          </p>
        </div>

        {/* Next Steps */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {nextSteps.map((step, index) => {
            const IconComponent = step.icon;
            
            return (
              <Card key={index} className="text-center hover:shadow-md transition-shadow duration-300">
                <CardContent className="p-6">
                  <div className={`w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4 ${
                    step.primary ? 'bg-blue-600 text-white' : 'bg-white text-blue-600'
                  }`}>
                    <IconComponent className="h-8 w-8" />
                  </div>
                  
                  <h3 className="font-semibold text-gray-900 mb-2">
                    {step.title}
                  </h3>
                  
                  <p className="text-gray-600 text-sm mb-4">
                    {step.description}
                  </p>
                  
                  <Button 
                    variant={step.primary ? 'primary' : 'outline'}
                    className="w-full"
                  >
                    {step.cta}
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </Button>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* Key Benefits Reminder */}
        <div className="bg-white rounded-xl p-6 mb-8">
          <h3 className="text-xl font-bold text-gray-900 mb-4 text-center">
            Why Choose ANZX.ai for Your AI Agents?
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 text-center">
            <div>
              <div className="text-2xl font-bold text-blue-600 mb-1">5-9 weeks</div>
              <div className="text-sm text-gray-600">Implementation time</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-blue-600 mb-1">40-70%</div>
              <div className="text-sm text-gray-600">Cost reduction</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-blue-600 mb-1">24/7</div>
              <div className="text-sm text-gray-600">Availability</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-blue-600 mb-1">99.9%</div>
              <div className="text-sm text-gray-600">Accuracy rate</div>
            </div>
          </div>
        </div>

        {/* Final CTA */}
        <div className="text-center">
          <Button size="lg" className="bg-blue-600 hover:bg-blue-700 text-white px-8">
            Start Your AI Agent Journey Today
            <ArrowRight className="ml-2 h-5 w-5" />
          </Button>
          
          <p className="text-sm text-gray-500 mt-4">
            No commitment required • Free consultation • Custom solution design
          </p>
        </div>

        {/* Related Resources */}
        <div className="mt-12 pt-8 border-t border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 text-center">
            Continue Learning
          </h3>
          
          <div className="flex flex-wrap justify-center gap-4">
            <Button variant="outline" size="sm">
              Agentic AI Guide
            </Button>
            <Button variant="outline" size="sm">
              Workflow Automation
            </Button>
            <Button variant="outline" size="sm">
              AI vs RPA Comparison
            </Button>
            <Button variant="outline" size="sm">
              Implementation Guide
            </Button>
          </div>
        </div>
      </div>
    </section>
  );
}
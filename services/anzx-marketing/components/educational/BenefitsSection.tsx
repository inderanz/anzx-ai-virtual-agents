'use client';

import { Card, CardContent } from '@/components/ui/card';
import { 
  Clock, 
  DollarSign, 
  TrendingUp, 
  Shield, 
  Users, 
  Zap,
  BarChart3,
  CheckCircle
} from 'lucide-react';

interface BenefitsSectionProps {
  id: string;
}

export default function BenefitsSection({ id }: BenefitsSectionProps) {
  const benefits = [
    {
      icon: Clock,
      title: '24/7 Availability',
      description: 'AI agents work around the clock without breaks, holidays, or sick days.',
      metrics: 'Up to 100% uptime',
      color: 'blue',
    },
    {
      icon: DollarSign,
      title: 'Cost Reduction',
      description: 'Significantly reduce operational costs by automating routine tasks.',
      metrics: '40-70% cost savings',
      color: 'green',
    },
    {
      icon: TrendingUp,
      title: 'Scalability',
      description: 'Handle increasing workloads without proportional increases in costs.',
      metrics: 'Scale to 1000x capacity',
      color: 'purple',
    },
    {
      icon: Zap,
      title: 'Instant Response',
      description: 'Provide immediate responses to customer inquiries and requests.',
      metrics: 'Sub-second response times',
      color: 'yellow',
    },
    {
      icon: Shield,
      title: 'Consistency',
      description: 'Deliver consistent service quality without human variability.',
      metrics: '99.9% accuracy',
      color: 'red',
    },
    {
      icon: BarChart3,
      title: 'Data-Driven Insights',
      description: 'Generate valuable insights from every interaction and process.',
      metrics: '100% data capture',
      color: 'indigo',
    },
  ];

  const getColorClasses = (color: string) => {
    const colorMap = {
      blue: 'bg-blue-100 text-blue-600',
      green: 'bg-green-100 text-green-600',
      purple: 'bg-purple-100 text-purple-600',
      yellow: 'bg-yellow-100 text-yellow-600',
      red: 'bg-red-100 text-red-600',
      indigo: 'bg-indigo-100 text-indigo-600',
    };
    return colorMap[color as keyof typeof colorMap] || 'bg-gray-100 text-gray-600';
  };

  return (
    <section id={id} className="scroll-mt-8">
      <div className="space-y-8">
        <div>
          <h2 className="text-3xl font-bold text-gray-900 mb-6">
            Key Benefits of AI Agents
          </h2>
          
          <div className="prose prose-lg max-w-none text-gray-600 mb-8">
            <p>
              AI agents offer significant advantages over traditional automation and human-only processes. 
              Here are the key benefits that make them transformative for businesses:
            </p>
          </div>
        </div>

        {/* Benefits Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {benefits.map((benefit, index) => {
            const IconComponent = benefit.icon;
            const colorClasses = getColorClasses(benefit.color);
            
            return (
              <Card key={index} className="h-full hover:shadow-md transition-shadow duration-300">
                <CardContent className="p-6">
                  <div className="space-y-4">
                    <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${colorClasses}`}>
                      <IconComponent className="h-6 w-6" />
                    </div>
                    
                    <div>
                      <h3 className="font-semibold text-gray-900 mb-2">
                        {benefit.title}
                      </h3>
                      <p className="text-gray-600 text-sm mb-3">
                        {benefit.description}
                      </p>
                      <div className="bg-gray-50 rounded-lg px-3 py-2">
                        <span className="text-xs font-medium text-gray-700">
                          {benefit.metrics}
                        </span>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* ROI Calculation */}
        <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-2xl p-8">
          <h3 className="text-2xl font-bold text-gray-900 mb-6">
            Return on Investment (ROI)
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-16 h-16 bg-white rounded-full flex items-center justify-center mx-auto mb-4 shadow-sm">
                <DollarSign className="h-8 w-8 text-green-600" />
              </div>
              <h4 className="font-semibold text-gray-900 mb-2">Cost Savings</h4>
              <p className="text-gray-600 text-sm mb-2">
                Typical businesses save 40-70% on operational costs within the first year.
              </p>
              <div className="text-2xl font-bold text-green-600">$50K+</div>
              <div className="text-sm text-gray-500">Annual savings per agent</div>
            </div>
            
            <div className="text-center">
              <div className="w-16 h-16 bg-white rounded-full flex items-center justify-center mx-auto mb-4 shadow-sm">
                <TrendingUp className="h-8 w-8 text-blue-600" />
              </div>
              <h4 className="font-semibold text-gray-900 mb-2">Productivity Gain</h4>
              <p className="text-gray-600 text-sm mb-2">
                AI agents can handle 10x more tasks than human workers in the same timeframe.
              </p>
              <div className="text-2xl font-bold text-blue-600">1000%</div>
              <div className="text-sm text-gray-500">Productivity increase</div>
            </div>
            
            <div className="text-center">
              <div className="w-16 h-16 bg-white rounded-full flex items-center justify-center mx-auto mb-4 shadow-sm">
                <Clock className="h-8 w-8 text-purple-600" />
              </div>
              <h4 className="font-semibold text-gray-900 mb-2">Time to ROI</h4>
              <p className="text-gray-600 text-sm mb-2">
                Most businesses see positive ROI within 3-6 months of implementation.
              </p>
              <div className="text-2xl font-bold text-purple-600">3-6</div>
              <div className="text-sm text-gray-500">Months to break-even</div>
            </div>
          </div>
        </div>

        {/* Success Metrics */}
        <div className="bg-white rounded-2xl border p-8">
          <h3 className="text-2xl font-bold text-gray-900 mb-6">
            Typical Success Metrics
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <h4 className="font-semibold text-gray-900">Operational Metrics</h4>
              <div className="space-y-3">
                <div className="flex items-center gap-3">
                  <CheckCircle className="h-5 w-5 text-green-500" />
                  <span className="text-gray-600">70% reduction in response time</span>
                </div>
                <div className="flex items-center gap-3">
                  <CheckCircle className="h-5 w-5 text-green-500" />
                  <span className="text-gray-600">85% increase in task completion rate</span>
                </div>
                <div className="flex items-center gap-3">
                  <CheckCircle className="h-5 w-5 text-green-500" />
                  <span className="text-gray-600">90% reduction in human errors</span>
                </div>
              </div>
            </div>
            
            <div className="space-y-4">
              <h4 className="font-semibold text-gray-900">Business Metrics</h4>
              <div className="space-y-3">
                <div className="flex items-center gap-3">
                  <CheckCircle className="h-5 w-5 text-green-500" />
                  <span className="text-gray-600">95% customer satisfaction score</span>
                </div>
                <div className="flex items-center gap-3">
                  <CheckCircle className="h-5 w-5 text-green-500" />
                  <span className="text-gray-600">60% increase in lead conversion</span>
                </div>
                <div className="flex items-center gap-3">
                  <CheckCircle className="h-5 w-5 text-green-500" />
                  <span className="text-gray-600">50% reduction in operational overhead</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
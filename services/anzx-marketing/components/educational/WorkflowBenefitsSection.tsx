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
  CheckCircle,
  Target
} from 'lucide-react';

interface WorkflowBenefitsSectionProps {
  id: string;
}

export default function WorkflowBenefitsSection({ id }: WorkflowBenefitsSectionProps) {
  const benefits = [
    {
      icon: Clock,
      title: 'Time Savings',
      description: 'Eliminate manual, repetitive tasks and reduce processing time.',
      metrics: 'Up to 80% time reduction',
      examples: ['Invoice processing: 2 hours → 15 minutes', 'Report generation: 4 hours → 10 minutes'],
      color: 'blue',
    },
    {
      icon: DollarSign,
      title: 'Cost Reduction',
      description: 'Lower operational costs through reduced manual labor and errors.',
      metrics: '30-60% cost savings',
      examples: ['Reduced staffing needs', 'Lower error correction costs'],
      color: 'green',
    },
    {
      icon: Shield,
      title: 'Improved Accuracy',
      description: 'Eliminate human errors and ensure consistent execution.',
      metrics: '90%+ error reduction',
      examples: ['Data entry accuracy', 'Compliance adherence'],
      color: 'red',
    },
    {
      icon: TrendingUp,
      title: 'Scalability',
      description: 'Handle increased workload without proportional resource increases.',
      metrics: '10x capacity increase',
      examples: ['Process 1000s of orders simultaneously', 'Handle peak demand automatically'],
      color: 'purple',
    },
    {
      icon: Users,
      title: 'Employee Satisfaction',
      description: 'Free employees from mundane tasks to focus on strategic work.',
      metrics: '40% increase in job satisfaction',
      examples: ['More creative work', 'Higher-value activities'],
      color: 'yellow',
    },
    {
      icon: Zap,
      title: 'Faster Response Times',
      description: 'Instant processing and immediate responses to triggers.',
      metrics: 'Sub-second response times',
      examples: ['Instant customer notifications', 'Real-time data updates'],
      color: 'indigo',
    },
  ];

  const roiCalculation = {
    scenario: 'Customer Service Workflow Automation',
    before: {
      volume: '1,000 inquiries/month',
      timePerInquiry: '30 minutes',
      hourlyRate: '$25',
      monthlyHours: 500,
      monthlyCost: 12500,
      errorRate: '15%',
      errorCost: 1875,
      totalCost: 14375,
    },
    after: {
      volume: '1,000 inquiries/month',
      timePerInquiry: '5 minutes',
      hourlyRate: '$25',
      monthlyHours: 83,
      monthlyCost: 2075,
      errorRate: '2%',
      errorCost: 250,
      automationCost: 500,
      totalCost: 2825,
    },
  };

  const getColorClasses = (color: string) => {
    const colorMap = {
      blue: 'bg-blue-100 text-blue-600',
      green: 'bg-green-100 text-green-600',
      red: 'bg-red-100 text-red-600',
      purple: 'bg-purple-100 text-purple-600',
      yellow: 'bg-yellow-100 text-yellow-600',
      indigo: 'bg-indigo-100 text-indigo-600',
    };
    return colorMap[color as keyof typeof colorMap] || 'bg-gray-100 text-gray-600';
  };

  const savings = roiCalculation.before.totalCost - roiCalculation.after.totalCost;
  const roiPercentage = Math.round((savings / roiCalculation.after.totalCost) * 100);

  return (
    <section id={id} className="scroll-mt-8">
      <div className="space-y-8">
        <div>
          <h2 className="text-3xl font-bold text-gray-900 mb-6">
            Benefits & ROI of Workflow Automation
          </h2>
          
          <div className="prose prose-lg max-w-none text-gray-600 mb-8">
            <p>
              Workflow automation delivers measurable benefits across multiple dimensions of business 
              performance. Understanding these benefits helps justify investment and set realistic 
              expectations for automation initiatives.
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
                      
                      <div className="bg-gray-50 rounded-lg px-3 py-2 mb-3">
                        <span className="text-xs font-medium text-gray-700">
                          {benefit.metrics}
                        </span>
                      </div>
                      
                      <div className="space-y-1">
                        {benefit.examples.map((example, exampleIndex) => (
                          <div key={exampleIndex} className="text-xs text-gray-500">
                            • {example}
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

        {/* ROI Calculation Example */}
        <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-2xl p-8">
          <h3 className="text-2xl font-bold text-gray-900 mb-6">
            ROI Calculation Example
          </h3>
          
          <div className="mb-6">
            <h4 className="text-lg font-semibold text-gray-900 mb-2">
              Scenario: {roiCalculation.scenario}
            </h4>
            <p className="text-gray-600">
              A company processes 1,000 customer service inquiries per month manually.
            </p>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
            {/* Before Automation */}
            <div className="bg-white rounded-lg p-6">
              <h4 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <Users className="h-5 w-5 text-red-500" />
                Before Automation
              </h4>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">Processing time per inquiry:</span>
                  <span className="font-medium">{roiCalculation.before.timePerInquiry}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Total monthly hours:</span>
                  <span className="font-medium">{roiCalculation.before.monthlyHours} hours</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Labor cost:</span>
                  <span className="font-medium">${roiCalculation.before.monthlyCost.toLocaleString()}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Error rate:</span>
                  <span className="font-medium">{roiCalculation.before.errorRate}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Error correction cost:</span>
                  <span className="font-medium">${roiCalculation.before.errorCost.toLocaleString()}</span>
                </div>
                <div className="border-t pt-3 flex justify-between font-semibold">
                  <span>Total Monthly Cost:</span>
                  <span className="text-red-600">${roiCalculation.before.totalCost.toLocaleString()}</span>
                </div>
              </div>
            </div>

            {/* After Automation */}
            <div className="bg-white rounded-lg p-6">
              <h4 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <Zap className="h-5 w-5 text-green-500" />
                After Automation
              </h4>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">Processing time per inquiry:</span>
                  <span className="font-medium">{roiCalculation.after.timePerInquiry}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Total monthly hours:</span>
                  <span className="font-medium">{roiCalculation.after.monthlyHours} hours</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Labor cost:</span>
                  <span className="font-medium">${roiCalculation.after.monthlyCost.toLocaleString()}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Error rate:</span>
                  <span className="font-medium">{roiCalculation.after.errorRate}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Error correction cost:</span>
                  <span className="font-medium">${roiCalculation.after.errorCost.toLocaleString()}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Automation platform cost:</span>
                  <span className="font-medium">${roiCalculation.after.automationCost.toLocaleString()}</span>
                </div>
                <div className="border-t pt-3 flex justify-between font-semibold">
                  <span>Total Monthly Cost:</span>
                  <span className="text-green-600">${roiCalculation.after.totalCost.toLocaleString()}</span>
                </div>
              </div>
            </div>
          </div>

          {/* ROI Summary */}
          <div className="bg-white rounded-lg p-6">
            <h4 className="font-semibold text-gray-900 mb-4 text-center">ROI Summary</h4>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 text-center">
              <div>
                <div className="text-2xl font-bold text-green-600">${savings.toLocaleString()}</div>
                <div className="text-sm text-gray-500">Monthly Savings</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-green-600">${(savings * 12).toLocaleString()}</div>
                <div className="text-sm text-gray-500">Annual Savings</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-green-600">{roiPercentage}%</div>
                <div className="text-sm text-gray-500">ROI</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-green-600">2 months</div>
                <div className="text-sm text-gray-500">Payback Period</div>
              </div>
            </div>
          </div>
        </div>

        {/* Success Metrics */}
        <div className="bg-white rounded-2xl border p-8">
          <h3 className="text-2xl font-bold text-gray-900 mb-6">
            Key Performance Indicators (KPIs) to Track
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div>
              <h4 className="font-semibold text-gray-900 mb-4">Operational Metrics</h4>
              <div className="space-y-3">
                <div className="flex items-center gap-3">
                  <CheckCircle className="h-5 w-5 text-green-500" />
                  <span className="text-gray-600">Processing time reduction (%)</span>
                </div>
                <div className="flex items-center gap-3">
                  <CheckCircle className="h-5 w-5 text-green-500" />
                  <span className="text-gray-600">Error rate reduction (%)</span>
                </div>
                <div className="flex items-center gap-3">
                  <CheckCircle className="h-5 w-5 text-green-500" />
                  <span className="text-gray-600">Volume capacity increase (%)</span>
                </div>
                <div className="flex items-center gap-3">
                  <CheckCircle className="h-5 w-5 text-green-500" />
                  <span className="text-gray-600">System uptime and reliability (%)</span>
                </div>
              </div>
            </div>
            
            <div>
              <h4 className="font-semibold text-gray-900 mb-4">Business Metrics</h4>
              <div className="space-y-3">
                <div className="flex items-center gap-3">
                  <CheckCircle className="h-5 w-5 text-green-500" />
                  <span className="text-gray-600">Cost savings per month ($)</span>
                </div>
                <div className="flex items-center gap-3">
                  <CheckCircle className="h-5 w-5 text-green-500" />
                  <span className="text-gray-600">Employee productivity increase (%)</span>
                </div>
                <div className="flex items-center gap-3">
                  <CheckCircle className="h-5 w-5 text-green-500" />
                  <span className="text-gray-600">Customer satisfaction score</span>
                </div>
                <div className="flex items-center gap-3">
                  <CheckCircle className="h-5 w-5 text-green-500" />
                  <span className="text-gray-600">Return on investment (%)</span>
                </div>
              </div>
            </div>
          </div>
          
          <div className="mt-6 p-4 bg-blue-50 rounded-lg">
            <p className="text-sm text-gray-600">
              <strong>Pro Tip:</strong> Establish baseline measurements before implementing automation 
              to accurately track improvements and demonstrate ROI to stakeholders.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
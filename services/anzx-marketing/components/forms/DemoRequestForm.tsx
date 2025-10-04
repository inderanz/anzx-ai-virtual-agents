'use client';

import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Button } from '@/components/ui/Button';
import { Loader2, CheckCircle, AlertCircle, Calendar } from 'lucide-react';
import { useFormTracking } from '@/lib/analytics/formTracking';

const demoRequestSchema = z.object({
  firstName: z.string().min(2, 'First name must be at least 2 characters'),
  lastName: z.string().min(2, 'Last name must be at least 2 characters'),
  email: z.string().email('Please enter a valid email address'),
  company: z.string().min(2, 'Company name must be at least 2 characters'),
  jobTitle: z.string().min(2, 'Job title must be at least 2 characters'),
  phone: z.string().min(10, 'Please enter a valid phone number'),
  companySize: z.string().min(1, 'Please select company size'),
  timeframe: z.string().min(1, 'Please select implementation timeframe'),
  preferredTime: z.string().min(1, 'Please select preferred demo time'),
  specificNeeds: z.string().optional(),
  consent: z.boolean().refine(val => val === true, 'You must agree to the terms'),
});

type DemoRequestFormData = z.infer<typeof demoRequestSchema>;

interface DemoRequestFormProps {
  productName?: string;
  agentType?: string;
  source?: string;
  onSuccess?: () => void;
  className?: string;
}

export function DemoRequestForm({ 
  productName = 'AI Agent',
  agentType = 'general',
  source = 'product-page',
  onSuccess,
  className = '' 
}: DemoRequestFormProps) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitStatus, setSubmitStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [errorMessage, setErrorMessage] = useState('');

  // Form tracking
  const formId = `demo-request-${agentType}-${source}`;
  const totalFields = 9; // firstName, lastName, email, company, jobTitle, phone, companySize, timeframe, preferredTime, consent
  const { updateField, markCompleted } = useFormTracking(formId, totalFields);

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
    watch,
  } = useForm<DemoRequestFormData>({
    resolver: zodResolver(demoRequestSchema),
  });

  // Watch form values for tracking
  const watchedValues = watch();

  useEffect(() => {
    // Track field changes
    Object.entries(watchedValues).forEach(([fieldName, value]) => {
      if (value !== undefined) {
        updateField(fieldName, value);
      }
    });
  }, [watchedValues, updateField]);

  const onSubmit = async (data: DemoRequestFormData) => {
    setIsSubmitting(true);
    setSubmitStatus('idle');
    setErrorMessage('');

    try {
      // Add demo-specific tracking data
      const demoData = {
        ...data,
        productName,
        agentType,
        source,
        requestType: 'demo',
        timestamp: new Date().toISOString(),
        userAgent: navigator.userAgent,
        referrer: document.referrer,
        url: window.location.href,
      };

      // Submit to demo requests API
      const response = await fetch('/api/demo-requests', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(demoData),
      });

      if (!response.ok) {
        throw new Error('Failed to submit demo request');
      }

      setSubmitStatus('success');
      markCompleted(); // Mark form as completed for tracking
      reset();
      
      // Track conversion event
      if (typeof window !== 'undefined' && window.gtag) {
        window.gtag('event', 'request_demo', {
          event_category: 'engagement',
          event_label: productName,
          value: 1,
        });
      }

      onSuccess?.();
    } catch (error) {
      console.error('Demo request error:', error);
      setSubmitStatus('error');
      setErrorMessage('Something went wrong. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (submitStatus === 'success') {
    return (
      <div className={`bg-green-50 border border-green-200 rounded-lg p-6 text-center ${className}`}>
        <CheckCircle className="w-12 h-12 text-green-600 mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-green-900 mb-2">
          Demo Request Received!
        </h3>
        <p className="text-green-700 mb-4">
          Thank you for requesting a demo of {productName}. Our team will contact you within 2 hours to schedule your personalized demonstration.
        </p>
        <div className="bg-white rounded-lg p-4 border border-green-200">
          <h4 className="font-medium text-green-900 mb-2">What happens next?</h4>
          <ul className="text-sm text-green-700 space-y-1 text-left">
            <li>• Our sales team will call you to confirm details</li>
            <li>• We'll schedule a 30-minute personalized demo</li>
            <li>• You'll see {productName} in action with your use case</li>
            <li>• We'll discuss pricing and implementation</li>
          </ul>
        </div>
      </div>
    );
  }

  return (
    <div className={className}>
      <div className="mb-6 text-center">
        <Calendar className="w-12 h-12 text-blue-600 mx-auto mb-4" />
        <h3 className="text-xl font-semibold text-gray-900 mb-2">
          Request a Demo of {productName}
        </h3>
        <p className="text-gray-600">
          See how {productName} can transform your business in a personalized 30-minute demo.
        </p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        {/* Name Fields */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label htmlFor="firstName" className="block text-sm font-medium text-gray-700 mb-1">
              First Name *
            </label>
            <input
              {...register('firstName')}
              type="text"
              id="firstName"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
              placeholder="John"
            />
            {errors.firstName && (
              <p className="mt-1 text-xs text-red-600">{errors.firstName.message}</p>
            )}
          </div>

          <div>
            <label htmlFor="lastName" className="block text-sm font-medium text-gray-700 mb-1">
              Last Name *
            </label>
            <input
              {...register('lastName')}
              type="text"
              id="lastName"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
              placeholder="Smith"
            />
            {errors.lastName && (
              <p className="mt-1 text-xs text-red-600">{errors.lastName.message}</p>
            )}
          </div>
        </div>

        {/* Email */}
        <div>
          <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
            Work Email *
          </label>
          <input
            {...register('email')}
            type="email"
            id="email"
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
            placeholder="john.smith@company.com"
          />
          {errors.email && (
            <p className="mt-1 text-xs text-red-600">{errors.email.message}</p>
          )}
        </div>

        {/* Company & Job Title */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label htmlFor="company" className="block text-sm font-medium text-gray-700 mb-1">
              Company *
            </label>
            <input
              {...register('company')}
              type="text"
              id="company"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
              placeholder="Acme Corp"
            />
            {errors.company && (
              <p className="mt-1 text-xs text-red-600">{errors.company.message}</p>
            )}
          </div>

          <div>
            <label htmlFor="jobTitle" className="block text-sm font-medium text-gray-700 mb-1">
              Job Title *
            </label>
            <input
              {...register('jobTitle')}
              type="text"
              id="jobTitle"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
              placeholder="Head of Operations"
            />
            {errors.jobTitle && (
              <p className="mt-1 text-xs text-red-600">{errors.jobTitle.message}</p>
            )}
          </div>
        </div>

        {/* Phone */}
        <div>
          <label htmlFor="phone" className="block text-sm font-medium text-gray-700 mb-1">
            Phone Number *
          </label>
          <input
            {...register('phone')}
            type="tel"
            id="phone"
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
            placeholder="+61 4XX XXX XXX"
          />
          {errors.phone && (
            <p className="mt-1 text-xs text-red-600">{errors.phone.message}</p>
          )}
        </div>

        {/* Company Size & Timeframe */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label htmlFor="companySize" className="block text-sm font-medium text-gray-700 mb-1">
              Company Size *
            </label>
            <select
              {...register('companySize')}
              id="companySize"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
            >
              <option value="">Select Size</option>
              <option value="1-10">1-10 employees</option>
              <option value="11-50">11-50 employees</option>
              <option value="51-200">51-200 employees</option>
              <option value="201-1000">201-1000 employees</option>
              <option value="1000+">1000+ employees</option>
            </select>
            {errors.companySize && (
              <p className="mt-1 text-xs text-red-600">{errors.companySize.message}</p>
            )}
          </div>

          <div>
            <label htmlFor="timeframe" className="block text-sm font-medium text-gray-700 mb-1">
              Implementation Timeframe *
            </label>
            <select
              {...register('timeframe')}
              id="timeframe"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
            >
              <option value="">Select Timeframe</option>
              <option value="immediate">Immediate (within 1 month)</option>
              <option value="1-3-months">1-3 months</option>
              <option value="3-6-months">3-6 months</option>
              <option value="6-12-months">6-12 months</option>
              <option value="exploring">Just exploring</option>
            </select>
            {errors.timeframe && (
              <p className="mt-1 text-xs text-red-600">{errors.timeframe.message}</p>
            )}
          </div>
        </div>

        {/* Preferred Demo Time */}
        <div>
          <label htmlFor="preferredTime" className="block text-sm font-medium text-gray-700 mb-1">
            Preferred Demo Time *
          </label>
          <select
            {...register('preferredTime')}
            id="preferredTime"
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
          >
            <option value="">Select Time</option>
            <option value="morning">Morning (9 AM - 12 PM AEST)</option>
            <option value="afternoon">Afternoon (12 PM - 5 PM AEST)</option>
            <option value="evening">Evening (5 PM - 7 PM AEST)</option>
            <option value="flexible">I'm flexible</option>
          </select>
          {errors.preferredTime && (
            <p className="mt-1 text-xs text-red-600">{errors.preferredTime.message}</p>
          )}
        </div>

        {/* Specific Needs */}
        <div>
          <label htmlFor="specificNeeds" className="block text-sm font-medium text-gray-700 mb-1">
            Specific Needs or Questions (Optional)
          </label>
          <textarea
            {...register('specificNeeds')}
            id="specificNeeds"
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
            placeholder="Tell us about your specific use case or any questions you have..."
          />
        </div>

        {/* Consent */}
        <div className="flex items-start space-x-3">
          <input
            {...register('consent')}
            type="checkbox"
            id="consent"
            className="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
          />
          <label htmlFor="consent" className="text-xs text-gray-700">
            I agree to receive communications from ANZX.ai about this demo request. 
            View our <a href="/legal/privacy-policy" className="text-blue-600 hover:underline">Privacy Policy</a>.
          </label>
        </div>
        {errors.consent && (
          <p className="text-xs text-red-600">{errors.consent.message}</p>
        )}

        {/* Error Message */}
        {submitStatus === 'error' && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-3 flex items-center space-x-2">
            <AlertCircle className="w-4 h-4 text-red-600 flex-shrink-0" />
            <p className="text-sm text-red-700">{errorMessage}</p>
          </div>
        )}

        {/* Submit Button */}
        <Button
          type="submit"
          disabled={isSubmitting}
          className="w-full"
          size="lg"
        >
          {isSubmitting ? (
            <>
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              Scheduling Demo...
            </>
          ) : (
            <>
              <Calendar className="w-4 h-4 mr-2" />
              Schedule My Demo
            </>
          )}
        </Button>

        <p className="text-xs text-gray-500 text-center">
          No commitment required. Cancel anytime.
        </p>
      </form>
    </div>
  );
}
'use client';

import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Button } from '@/components/ui/Button';
import { Loader2, CheckCircle, AlertCircle } from 'lucide-react';
import { useFormTracking } from '@/lib/analytics/formTracking';

const leadCaptureSchema = z.object({
  firstName: z.string().min(2, 'First name must be at least 2 characters'),
  lastName: z.string().min(2, 'Last name must be at least 2 characters'),
  email: z.string().email('Please enter a valid email address'),
  company: z.string().min(2, 'Company name must be at least 2 characters'),
  jobTitle: z.string().min(2, 'Job title must be at least 2 characters'),
  phone: z.string().optional(),
  industry: z.string().min(1, 'Please select an industry'),
  companySize: z.string().min(1, 'Please select company size'),
  useCase: z.string().min(1, 'Please select a use case'),
  message: z.string().optional(),
  consent: z.boolean().refine(val => val === true, 'You must agree to the terms'),
});

type LeadCaptureFormData = z.infer<typeof leadCaptureSchema>;

interface LeadCaptureFormProps {
  source?: string;
  campaign?: string;
  onSuccess?: () => void;
  className?: string;
}

export function LeadCaptureForm({ 
  source = 'website', 
  campaign = 'general',
  onSuccess,
  className = '' 
}: LeadCaptureFormProps) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitStatus, setSubmitStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [errorMessage, setErrorMessage] = useState('');

  // Form tracking
  const formId = `lead-capture-${source}-${campaign}`;
  const totalFields = 9; // firstName, lastName, email, company, jobTitle, industry, companySize, useCase, consent
  const { updateField, markCompleted } = useFormTracking(formId, totalFields);

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
    watch,
  } = useForm<LeadCaptureFormData>({
    resolver: zodResolver(leadCaptureSchema),
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

  const onSubmit = async (data: LeadCaptureFormData) => {
    setIsSubmitting(true);
    setSubmitStatus('idle');
    setErrorMessage('');

    try {
      // Add source and campaign tracking
      const leadData = {
        ...data,
        source,
        campaign,
        timestamp: new Date().toISOString(),
        userAgent: navigator.userAgent,
        referrer: document.referrer,
        url: window.location.href,
      };

      // Submit to core-api
      const response = await fetch('/api/leads', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(leadData),
      });

      if (!response.ok) {
        throw new Error('Failed to submit form');
      }

      setSubmitStatus('success');
      markCompleted(); // Mark form as completed for tracking
      reset();
      
      // Track conversion event
      if (typeof window !== 'undefined' && window.gtag) {
        window.gtag('event', 'generate_lead', {
          event_category: 'engagement',
          event_label: source,
          value: 1,
        });
      }

      onSuccess?.();
    } catch (error) {
      console.error('Form submission error:', error);
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
          Thank you for your interest!
        </h3>
        <p className="text-green-700">
          We've received your information and will be in touch within 24 hours to schedule your demo.
        </p>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className={`space-y-6 ${className}`}>
      {/* Name Fields */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label htmlFor="firstName" className="block text-sm font-medium text-gray-700 mb-2">
            First Name *
          </label>
          <input
            {...register('firstName')}
            type="text"
            id="firstName"
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="John"
          />
          {errors.firstName && (
            <p className="mt-1 text-sm text-red-600">{errors.firstName.message}</p>
          )}
        </div>

        <div>
          <label htmlFor="lastName" className="block text-sm font-medium text-gray-700 mb-2">
            Last Name *
          </label>
          <input
            {...register('lastName')}
            type="text"
            id="lastName"
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Smith"
          />
          {errors.lastName && (
            <p className="mt-1 text-sm text-red-600">{errors.lastName.message}</p>
          )}
        </div>
      </div>

      {/* Email */}
      <div>
        <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
          Work Email *
        </label>
        <input
          {...register('email')}
          type="email"
          id="email"
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="john.smith@company.com"
        />
        {errors.email && (
          <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>
        )}
      </div>

      {/* Company & Job Title */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label htmlFor="company" className="block text-sm font-medium text-gray-700 mb-2">
            Company *
          </label>
          <input
            {...register('company')}
            type="text"
            id="company"
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Acme Corp"
          />
          {errors.company && (
            <p className="mt-1 text-sm text-red-600">{errors.company.message}</p>
          )}
        </div>

        <div>
          <label htmlFor="jobTitle" className="block text-sm font-medium text-gray-700 mb-2">
            Job Title *
          </label>
          <input
            {...register('jobTitle')}
            type="text"
            id="jobTitle"
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Head of Operations"
          />
          {errors.jobTitle && (
            <p className="mt-1 text-sm text-red-600">{errors.jobTitle.message}</p>
          )}
        </div>
      </div>

      {/* Phone */}
      <div>
        <label htmlFor="phone" className="block text-sm font-medium text-gray-700 mb-2">
          Phone Number (Optional)
        </label>
        <input
          {...register('phone')}
          type="tel"
          id="phone"
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="+61 4XX XXX XXX"
        />
      </div>

      {/* Industry & Company Size */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label htmlFor="industry" className="block text-sm font-medium text-gray-700 mb-2">
            Industry *
          </label>
          <select
            {...register('industry')}
            id="industry"
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">Select Industry</option>
            <option value="technology">Technology</option>
            <option value="financial-services">Financial Services</option>
            <option value="healthcare">Healthcare</option>
            <option value="retail">Retail & E-commerce</option>
            <option value="manufacturing">Manufacturing</option>
            <option value="education">Education</option>
            <option value="government">Government</option>
            <option value="real-estate">Real Estate</option>
            <option value="consulting">Consulting</option>
            <option value="other">Other</option>
          </select>
          {errors.industry && (
            <p className="mt-1 text-sm text-red-600">{errors.industry.message}</p>
          )}
        </div>

        <div>
          <label htmlFor="companySize" className="block text-sm font-medium text-gray-700 mb-2">
            Company Size *
          </label>
          <select
            {...register('companySize')}
            id="companySize"
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">Select Size</option>
            <option value="1-10">1-10 employees</option>
            <option value="11-50">11-50 employees</option>
            <option value="51-200">51-200 employees</option>
            <option value="201-1000">201-1000 employees</option>
            <option value="1000+">1000+ employees</option>
          </select>
          {errors.companySize && (
            <p className="mt-1 text-sm text-red-600">{errors.companySize.message}</p>
          )}
        </div>
      </div>

      {/* Use Case */}
      <div>
        <label htmlFor="useCase" className="block text-sm font-medium text-gray-700 mb-2">
          Primary Use Case *
        </label>
        <select
          {...register('useCase')}
          id="useCase"
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="">Select Use Case</option>
          <option value="customer-service">Customer Service Automation</option>
          <option value="sales-automation">Sales & Lead Generation</option>
          <option value="recruiting">Recruiting & HR</option>
          <option value="technical-support">Technical Support</option>
          <option value="workflow-automation">Workflow Automation</option>
          <option value="other">Other</option>
        </select>
        {errors.useCase && (
          <p className="mt-1 text-sm text-red-600">{errors.useCase.message}</p>
        )}
      </div>

      {/* Message */}
      <div>
        <label htmlFor="message" className="block text-sm font-medium text-gray-700 mb-2">
          Tell us about your needs (Optional)
        </label>
        <textarea
          {...register('message')}
          id="message"
          rows={4}
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="Describe your current challenges and what you're looking to achieve..."
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
        <label htmlFor="consent" className="text-sm text-gray-700">
          I agree to receive communications from ANZX.ai and understand that I can unsubscribe at any time. 
          View our <a href="/legal/privacy-policy" className="text-blue-600 hover:underline">Privacy Policy</a>.
        </label>
      </div>
      {errors.consent && (
        <p className="text-sm text-red-600">{errors.consent.message}</p>
      )}

      {/* Error Message */}
      {submitStatus === 'error' && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center space-x-3">
          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0" />
          <p className="text-red-700">{errorMessage}</p>
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
            <Loader2 className="w-5 h-5 mr-2 animate-spin" />
            Submitting...
          </>
        ) : (
          'Get Your Demo'
        )}
      </Button>

      <p className="text-xs text-gray-500 text-center">
        By submitting this form, you agree to our Terms of Service and Privacy Policy.
      </p>
    </form>
  );
}
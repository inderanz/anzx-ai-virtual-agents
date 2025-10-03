"use client";

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { leadsApi } from '@/lib/api/leads';
import { PrimaryButton } from '../ui/Button';

const demoRequestSchema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters'),
  email: z.string().email('Invalid email address'),
  company: z.string().min(2, 'Company name is required'),
  phone: z.string().optional(),
  agent_type: z.enum(['recruiting', 'customer_service', 'sales', 'support']),
  message: z.string().optional(),
});

type DemoRequestFormData = z.infer<typeof demoRequestSchema>;

interface DemoRequestFormProps {
  agentType?: DemoRequestFormData['agent_type'];
  onSuccess?: () => void;
}

export function DemoRequestForm({ agentType = 'customer_service', onSuccess }: DemoRequestFormProps) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitStatus, setSubmitStatus] = useState<'idle' | 'success' | 'error'>('idle');

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<DemoRequestFormData>({
    resolver: zodResolver(demoRequestSchema),
    defaultValues: {
      agent_type: agentType,
    },
  });

  const onSubmit = async (data: DemoRequestFormData) => {
    setIsSubmitting(true);
    setSubmitStatus('idle');

    try {
      const response = await leadsApi.submitDemoRequest(data);

      if (response.error) {
        throw new Error(response.error);
      }

      setSubmitStatus('success');
      reset();
      onSuccess?.();
    } catch (error) {
      console.error('Demo request failed:', error);
      setSubmitStatus('error');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      {/* Name */}
      <div>
        <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
          Name *
        </label>
        <input
          {...register('name')}
          type="text"
          id="name"
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-anzx-blue focus:border-transparent"
          placeholder="John Smith"
        />
        {errors.name && <p className="mt-1 text-sm text-red-600">{errors.name.message}</p>}
      </div>

      {/* Email */}
      <div>
        <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
          Email *
        </label>
        <input
          {...register('email')}
          type="email"
          id="email"
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-anzx-blue focus:border-transparent"
          placeholder="john@company.com"
        />
        {errors.email && <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>}
      </div>

      {/* Company */}
      <div>
        <label htmlFor="company" className="block text-sm font-medium text-gray-700 mb-2">
          Company *
        </label>
        <input
          {...register('company')}
          type="text"
          id="company"
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-anzx-blue focus:border-transparent"
          placeholder="ACME Corp"
        />
        {errors.company && <p className="mt-1 text-sm text-red-600">{errors.company.message}</p>}
      </div>

      {/* Phone */}
      <div>
        <label htmlFor="phone" className="block text-sm font-medium text-gray-700 mb-2">
          Phone (optional)
        </label>
        <input
          {...register('phone')}
          type="tel"
          id="phone"
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-anzx-blue focus:border-transparent"
          placeholder="+61 400 000 000"
        />
      </div>

      {/* Agent Type */}
      <div>
        <label htmlFor="agent_type" className="block text-sm font-medium text-gray-700 mb-2">
          Which AI Agent are you interested in? *
        </label>
        <select
          {...register('agent_type')}
          id="agent_type"
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-anzx-blue focus:border-transparent"
        >
          <option value="recruiting">Emma - AI Recruiting Agent</option>
          <option value="customer_service">Olivia - AI Customer Service Agent</option>
          <option value="sales">Jack - AI Sales Agent</option>
          <option value="support">Liam - AI Support Agent</option>
        </select>
      </div>

      {/* Message */}
      <div>
        <label htmlFor="message" className="block text-sm font-medium text-gray-700 mb-2">
          Message (optional)
        </label>
        <textarea
          {...register('message')}
          id="message"
          rows={4}
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-anzx-blue focus:border-transparent"
          placeholder="Tell us about your use case..."
        />
      </div>

      {/* Submit Button */}
      <PrimaryButton type="submit" disabled={isSubmitting} className="w-full">
        {isSubmitting ? 'Submitting...' : 'Request Demo'}
      </PrimaryButton>

      {/* Status Messages */}
      {submitStatus === 'success' && (
        <div className="p-4 bg-green-50 border border-green-200 rounded-lg text-green-800">
          Thank you! We'll be in touch soon to schedule your demo.
        </div>
      )}

      {submitStatus === 'error' && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-800">
          Something went wrong. Please try again or contact us directly.
        </div>
      )}
    </form>
  );
}

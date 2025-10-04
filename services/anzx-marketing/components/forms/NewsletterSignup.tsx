'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Button } from '@/components/ui/Button';
import { Loader2, CheckCircle, AlertCircle, Mail } from 'lucide-react';

const newsletterSchema = z.object({
  email: z.string().email('Please enter a valid email address'),
  firstName: z.string().optional(),
  interests: z.array(z.string()).optional(),
  consent: z.boolean().refine(val => val === true, 'You must agree to receive emails'),
});

type NewsletterFormData = z.infer<typeof newsletterSchema>;

interface NewsletterSignupProps {
  source?: string;
  variant?: 'inline' | 'modal' | 'footer';
  showInterests?: boolean;
  className?: string;
}

export function NewsletterSignup({ 
  source = 'website',
  variant = 'inline',
  showInterests = false,
  className = '' 
}: NewsletterSignupProps) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitStatus, setSubmitStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [errorMessage, setErrorMessage] = useState('');

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<NewsletterFormData>({
    resolver: zodResolver(newsletterSchema),
  });

  const onSubmit = async (data: NewsletterFormData) => {
    setIsSubmitting(true);
    setSubmitStatus('idle');
    setErrorMessage('');

    try {
      const newsletterData = {
        ...data,
        source,
        variant,
        timestamp: new Date().toISOString(),
        userAgent: navigator.userAgent,
        referrer: document.referrer,
        url: window.location.href,
      };

      const response = await fetch('/api/newsletter', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newsletterData),
      });

      if (!response.ok) {
        throw new Error('Failed to subscribe to newsletter');
      }

      setSubmitStatus('success');
      reset();
      
      // Track conversion event
      if (typeof window !== 'undefined' && window.gtag) {
        window.gtag('event', 'newsletter_signup', {
          event_category: 'engagement',
          event_label: source,
          value: 1,
        });
      }

    } catch (error) {
      console.error('Newsletter signup error:', error);
      setSubmitStatus('error');
      setErrorMessage('Something went wrong. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (submitStatus === 'success') {
    return (
      <div className={`bg-green-50 border border-green-200 rounded-lg p-4 text-center ${className}`}>
        <CheckCircle className="w-8 h-8 text-green-600 mx-auto mb-2" />
        <h3 className="text-sm font-semibold text-green-900 mb-1">
          Welcome to ANZX.ai!
        </h3>
        <p className="text-xs text-green-700">
          You're now subscribed to our newsletter. Check your email for confirmation.
        </p>
      </div>
    );
  }

  const isInline = variant === 'inline';
  const isFooter = variant === 'footer';

  return (
    <div className={className}>
      {!isFooter && (
        <div className="mb-4 text-center">
          <Mail className="w-8 h-8 text-blue-600 mx-auto mb-2" />
          <h3 className="text-lg font-semibold text-gray-900 mb-1">
            Stay Updated
          </h3>
          <p className="text-sm text-gray-600">
            Get the latest AI insights and product updates delivered to your inbox.
          </p>
        </div>
      )}

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        {/* Name field for non-inline variants */}
        {!isInline && (
          <div>
            <label htmlFor="firstName" className="block text-sm font-medium text-gray-700 mb-1">
              First Name (Optional)
            </label>
            <input
              {...register('firstName')}
              type="text"
              id="firstName"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
              placeholder="John"
            />
          </div>
        )}

        {/* Email field */}
        <div className={isInline ? 'flex space-x-2' : ''}>
          <div className={isInline ? 'flex-1' : ''}>
            {!isInline && (
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                Email Address
              </label>
            )}
            <input
              {...register('email')}
              type="email"
              id="email"
              className={`w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm ${
                isInline ? 'placeholder-gray-500' : ''
              }`}
              placeholder={isInline ? 'Enter your email' : 'john@company.com'}
            />
            {errors.email && (
              <p className="mt-1 text-xs text-red-600">{errors.email.message}</p>
            )}
          </div>

          {isInline && (
            <Button
              type="submit"
              disabled={isSubmitting}
              size="sm"
            >
              {isSubmitting ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                'Subscribe'
              )}
            </Button>
          )}
        </div>

        {/* Interests checkboxes */}
        {showInterests && !isInline && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              What interests you? (Optional)
            </label>
            <div className="space-y-2">
              {[
                { value: 'product-updates', label: 'Product Updates' },
                { value: 'ai-insights', label: 'AI Industry Insights' },
                { value: 'case-studies', label: 'Customer Case Studies' },
                { value: 'webinars', label: 'Webinars & Events' },
              ].map((interest) => (
                <label key={interest.value} className="flex items-center">
                  <input
                    {...register('interests')}
                    type="checkbox"
                    value={interest.value}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <span className="ml-2 text-sm text-gray-700">{interest.label}</span>
                </label>
              ))}
            </div>
          </div>
        )}

        {/* Consent checkbox */}
        <div className="flex items-start space-x-2">
          <input
            {...register('consent')}
            type="checkbox"
            id="consent"
            className="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
          />
          <label htmlFor="consent" className="text-xs text-gray-700">
            I agree to receive emails from ANZX.ai and understand I can unsubscribe at any time.
            {!isFooter && (
              <>
                {' '}View our <a href="/legal/privacy-policy" className="text-blue-600 hover:underline">Privacy Policy</a>.
              </>
            )}
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

        {/* Submit Button for non-inline variants */}
        {!isInline && (
          <Button
            type="submit"
            disabled={isSubmitting}
            className="w-full"
          >
            {isSubmitting ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Subscribing...
              </>
            ) : (
              <>
                <Mail className="w-4 h-4 mr-2" />
                Subscribe to Newsletter
              </>
            )}
          </Button>
        )}

        {!isInline && (
          <p className="text-xs text-gray-500 text-center">
            No spam, unsubscribe at any time.
          </p>
        )}
      </form>
    </div>
  );
}
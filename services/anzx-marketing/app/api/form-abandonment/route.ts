import { NextRequest, NextResponse } from 'next/server';
import { z } from 'zod';
import { emailService } from '@/lib/email/emailService';

const abandonmentSchema = z.object({
  type: z.enum(['abandonment', 'recovery']),
  data: z.object({
    email: z.string().email(),
    formId: z.string(),
    formData: z.record(z.any()),
    abandonedAt: z.string(),
    recoveryEmailSent: z.boolean().optional(),
    recovered: z.boolean().optional(),
    recoveredAt: z.string().optional(),
  }),
});

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const validatedData = abandonmentSchema.parse(body);

    const { type, data } = validatedData;

    if (type === 'abandonment') {
      await handleFormAbandonment(data);
    } else if (type === 'recovery') {
      await handleFormRecovery(data);
    }

    return NextResponse.json({ success: true });

  } catch (error) {
    console.error('Form abandonment tracking error:', error);

    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { success: false, message: 'Invalid data', errors: error.errors },
        { status: 400 }
      );
    }

    return NextResponse.json(
      { success: false, message: 'Internal server error' },
      { status: 500 }
    );
  }
}

async function handleFormAbandonment(data: any) {
  // Store abandonment data (in production, save to database)
  console.log('📊 Form abandonment tracked:', {
    email: data.email,
    formId: data.formId,
    completedFields: Object.keys(data.formData).length,
    abandonedAt: data.abandonedAt,
  });

  // Schedule recovery email based on form type and completion level
  const recoveryDelay = getRecoveryDelay(data.formId, data.formData);
  
  if (recoveryDelay > 0) {
    await scheduleRecoveryEmail(data, recoveryDelay);
  }

  // Track in analytics
  if (process.env.NODE_ENV === 'production') {
    // Send to analytics service
    await trackAbandonmentEvent(data);
  }
}

async function handleFormRecovery(data: any) {
  console.log('🎉 Form recovery tracked:', {
    email: data.email,
    formId: data.formId,
    recoveredAt: data.recoveredAt,
  });

  // Track recovery in analytics
  if (process.env.NODE_ENV === 'production') {
    await trackRecoveryEvent(data);
  }
}

function getRecoveryDelay(formId: string, formData: any): number {
  // Determine recovery email delay based on form type and data quality
  const hasEmail = formData.email && formData.email.includes('@');
  const hasName = formData.firstName || formData.name;
  const hasCompany = formData.company;

  // High-value forms (demo requests) get faster recovery
  if (formId.includes('demo')) {
    if (hasEmail && hasName && hasCompany) {
      return 1; // 1 hour for high-quality demo abandonment
    } else if (hasEmail && hasName) {
      return 4; // 4 hours for medium-quality
    } else if (hasEmail) {
      return 24; // 24 hours for email-only
    }
  }

  // Lead capture forms
  if (formId.includes('lead')) {
    if (hasEmail && hasName) {
      return 2; // 2 hours for quality leads
    } else if (hasEmail) {
      return 12; // 12 hours for email-only
    }
  }

  // Newsletter signups
  if (formId.includes('newsletter')) {
    if (hasEmail) {
      return 6; // 6 hours for newsletter abandonment
    }
  }

  return 0; // No recovery email
}

async function scheduleRecoveryEmail(data: any, delayHours: number) {
  // In production, this would use a job queue or scheduled function
  console.log(`📅 Recovery email scheduled for ${data.email} in ${delayHours} hours`);

  // For development, simulate with setTimeout (not recommended for production)
  if (process.env.NODE_ENV === 'development') {
    setTimeout(async () => {
      await sendRecoveryEmail(data);
    }, delayHours * 60 * 60 * 1000);
  } else {
    // In production, add to job queue or use cloud scheduler
    await addToRecoveryQueue(data, delayHours);
  }
}

async function sendRecoveryEmail(data: any) {
  const recoveryTemplate = getRecoveryTemplate(data.formId);
  
  if (!recoveryTemplate) return;

  const variables = {
    firstName: data.formData.firstName || 'there',
    formId: data.formId,
    formData: data.formData,
    recoveryUrl: `https://anzx.ai/recover-form?token=${generateRecoveryToken(data)}`,
    unsubscribeUrl: `https://anzx.ai/unsubscribe?email=${encodeURIComponent(data.email)}`,
  };

  await emailService.sendTemplateEmail(recoveryTemplate, data.email, variables);
  
  console.log(`📧 Recovery email sent to ${data.email} for form ${data.formId}`);
}

function getRecoveryTemplate(formId: string): string | null {
  if (formId.includes('demo')) {
    return 'demoAbandonmentRecovery';
  } else if (formId.includes('lead')) {
    return 'leadAbandonmentRecovery';
  } else if (formId.includes('newsletter')) {
    return 'newsletterAbandonmentRecovery';
  }
  return null;
}

function generateRecoveryToken(data: any): string {
  // In production, use proper JWT or encrypted token
  const payload = {
    email: data.email,
    formId: data.formId,
    timestamp: Date.now(),
  };
  
  return Buffer.from(JSON.stringify(payload)).toString('base64url');
}

async function addToRecoveryQueue(data: any, delayHours: number) {
  // In production, integrate with job queue system
  // Examples: Bull Queue, Google Cloud Tasks, AWS SQS with delay
  console.log(`Adding ${data.email} to recovery queue with ${delayHours}h delay`);
}

async function trackAbandonmentEvent(data: any) {
  // Send to analytics service (Google Analytics, Mixpanel, etc.)
  console.log('Tracking abandonment event:', data.formId);
}

async function trackRecoveryEvent(data: any) {
  // Send to analytics service
  console.log('Tracking recovery event:', data.formId);
}

// Handle preflight requests
export async function OPTIONS() {
  return new NextResponse(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    },
  });
}
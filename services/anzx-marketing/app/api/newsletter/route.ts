import { NextRequest, NextResponse } from 'next/server';
import { z } from 'zod';
import { sendNewsletterWelcome } from '@/lib/email/emailService';

const newsletterSchema = z.object({
  email: z.string().email(),
  firstName: z.string().optional(),
  interests: z.array(z.string()).optional(),
  consent: z.boolean(),
  source: z.string().default('website'),
  variant: z.string().default('inline'),
  timestamp: z.string(),
  userAgent: z.string().optional(),
  referrer: z.string().optional(),
  url: z.string().optional(),
});

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    // Validate the request body
    const validatedData = newsletterSchema.parse(body);

    // Get client IP for tracking
    const clientIP = request.headers.get('x-forwarded-for') || 
                    request.headers.get('x-real-ip') || 
                    'unknown';

    // Prepare newsletter subscription data
    const subscriptionData = {
      ...validatedData,
      clientIP,
      createdAt: new Date().toISOString(),
      status: 'pending', // Will be confirmed via email
    };

    // Submit to core-api newsletter service
    const coreApiUrl = process.env.CORE_API_URL || 'http://localhost:8000';
    const response = await fetch(`${coreApiUrl}/api/v1/newsletter/subscribe`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${process.env.CORE_API_TOKEN}`,
      },
      body: JSON.stringify(subscriptionData),
    });

    if (!response.ok) {
      console.error('Core API error:', await response.text());
      throw new Error('Failed to submit to core API');
    }

    const result = await response.json();

    // Send welcome email
    await sendNewsletterWelcome({
      ...validatedData,
      subscriptionId: result.id,
    });

    // Log subscription for development
    if (process.env.NODE_ENV === 'development') {
      console.log('📧 Newsletter subscription:', {
        email: validatedData.email,
        firstName: validatedData.firstName,
        source: validatedData.source,
        interests: validatedData.interests,
      });
    }

    return NextResponse.json({
      success: true,
      message: 'Successfully subscribed to newsletter',
      subscriptionId: result.id,
    });

  } catch (error) {
    console.error('Newsletter subscription error:', error);

    if (error instanceof z.ZodError) {
      return NextResponse.json(
        {
          success: false,
          message: 'Invalid form data',
          errors: error.errors,
        },
        { status: 400 }
      );
    }

    return NextResponse.json(
      {
        success: false,
        message: 'Internal server error',
      },
      { status: 500 }
    );
  }
}

// Email sending moved to emailService.ts

// Handle preflight requests for CORS
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
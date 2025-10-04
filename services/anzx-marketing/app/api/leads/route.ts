import { NextRequest, NextResponse } from 'next/server';
import { z } from 'zod';
import { sendLeadConfirmation, sendSalesNotification } from '@/lib/email/emailService';
import { leadSegmentation } from '@/lib/leads/segmentation';

const leadSchema = z.object({
  firstName: z.string().min(2),
  lastName: z.string().min(2),
  email: z.string().email(),
  company: z.string().min(2),
  jobTitle: z.string().min(2),
  phone: z.string().optional(),
  industry: z.string().min(1),
  companySize: z.string().min(1),
  useCase: z.string().min(1),
  message: z.string().optional(),
  consent: z.boolean(),
  source: z.string().default('website'),
  campaign: z.string().default('general'),
  timestamp: z.string(),
  userAgent: z.string().optional(),
  referrer: z.string().optional(),
  url: z.string().optional(),
});

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    // Validate the request body
    const validatedData = leadSchema.parse(body);

    // Get client IP for tracking
    const clientIP = request.headers.get('x-forwarded-for') || 
                    request.headers.get('x-real-ip') || 
                    'unknown';

    // Segment the lead (ensure all required fields are present)
    const leadForSegmentation = {
      ...validatedData,
      campaign: validatedData.source || 'direct',
      url: validatedData.url || request.url,
      referrer: validatedData.referrer || request.headers.get('referer') || 'direct',
    };
    const segmentationResult = leadSegmentation.segmentLead(leadForSegmentation);
    const routing = leadSegmentation.getLeadRouting(segmentationResult);
    const nurturing = leadSegmentation.getNurturingSequence(segmentationResult);

    // Prepare lead data for core-api
    const leadData = {
      ...validatedData,
      clientIP,
      createdAt: new Date().toISOString(),
      segmentation: segmentationResult,
      routing,
      nurturing,
    };

    // Submit to core-api (replace with actual core-api endpoint)
    const coreApiUrl = process.env.CORE_API_URL || 'http://localhost:8000';
    const response = await fetch(`${coreApiUrl}/api/v1/leads`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${process.env.CORE_API_TOKEN}`,
      },
      body: JSON.stringify(leadData),
    });

    if (!response.ok) {
      console.error('Core API error:', await response.text());
      throw new Error('Failed to submit to core API');
    }

    const result = await response.json();

    // Send confirmation email to lead
    await sendLeadConfirmation({
      ...validatedData,
      leadId: result.id,
    });

    // Send notification to sales team
    await sendSalesNotification({
      ...validatedData,
      leadId: result.id,
      requestType: 'Lead',
      priority: segmentationResult.priority,
      estimatedResponseTime: segmentationResult.responseTime,
      salesTeam: segmentationResult.salesTeam,
      followUpStrategy: segmentationResult.followUpStrategy,
      segments: segmentationResult.segments.join(', '),
      score: segmentationResult.score,
    });

    // Return success response
    return NextResponse.json({
      success: true,
      message: 'Lead captured successfully',
      leadId: result.id,
      segmentation: {
        priority: segmentationResult.priority,
        salesTeam: segmentationResult.salesTeam,
        responseTime: segmentationResult.responseTime,
        segments: segmentationResult.segments,
      },
    });

  } catch (error) {
    console.error('Lead capture error:', error);

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
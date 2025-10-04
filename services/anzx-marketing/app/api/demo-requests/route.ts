import { NextRequest, NextResponse } from 'next/server';
import { z } from 'zod';
import { sendDemoConfirmation, sendSalesNotification } from '@/lib/email/emailService';
import { leadSegmentation } from '@/lib/leads/segmentation';

const demoRequestSchema = z.object({
  firstName: z.string().min(2),
  lastName: z.string().min(2),
  email: z.string().email(),
  company: z.string().min(2),
  jobTitle: z.string().min(2),
  phone: z.string().min(10),
  companySize: z.string().min(1),
  timeframe: z.string().min(1),
  preferredTime: z.string().min(1),
  specificNeeds: z.string().optional(),
  consent: z.boolean(),
  productName: z.string().default('AI Agent'),
  agentType: z.string().default('general'),
  source: z.string().default('product-page'),
  requestType: z.string().default('demo'),
  timestamp: z.string(),
  userAgent: z.string().optional(),
  referrer: z.string().optional(),
  url: z.string().optional(),
});

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    // Validate the request body
    const validatedData = demoRequestSchema.parse(body);

    // Get client IP for tracking
    const clientIP = request.headers.get('x-forwarded-for') || 
                    request.headers.get('x-real-ip') || 
                    'unknown';

    // Segment the lead (convert demo data to lead format for segmentation)
    const leadForSegmentation = {
      ...validatedData,
      useCase: validatedData.agentType || 'general',
      industry: 'technology', // Default for demo requests
      campaign: validatedData.source || 'direct',
      url: request.url,
      referrer: request.headers.get('referer') || 'direct',
      timestamp: new Date().toISOString(),
    };
    
    const segmentationResult = leadSegmentation.segmentLead(leadForSegmentation);
    const routing = leadSegmentation.getLeadRouting(segmentationResult);
    const nurturing = leadSegmentation.getNurturingSequence(segmentationResult);

    // Prepare demo request data for core-api
    const demoData = {
      ...validatedData,
      clientIP,
      createdAt: new Date().toISOString(),
      priority: segmentationResult.priority,
      segmentation: segmentationResult,
      routing,
      nurturing,
    };

    // Submit to core-api (replace with actual core-api endpoint)
    const coreApiUrl = process.env.CORE_API_URL || 'http://localhost:8000';
    const response = await fetch(`${coreApiUrl}/api/v1/demo-requests`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${process.env.CORE_API_TOKEN}`,
      },
      body: JSON.stringify(demoData),
    });

    if (!response.ok) {
      console.error('Core API error:', await response.text());
      throw new Error('Failed to submit to core API');
    }

    const result = await response.json();
    const estimatedResponseTime = getEstimatedResponseTime(validatedData.timeframe);

    // Send confirmation email to prospect
    await sendDemoConfirmation({
      ...validatedData,
      demoRequestId: result.id,
      estimatedResponseTime,
    });

    // Send notification to sales team
    await sendSalesNotification({
      ...validatedData,
      demoRequestId: result.id,
      requestType: 'Demo Request',
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
      message: 'Demo request submitted successfully',
      demoRequestId: result.id,
      estimatedResponseTime: segmentationResult.responseTime,
      segmentation: {
        priority: segmentationResult.priority,
        salesTeam: segmentationResult.salesTeam,
        responseTime: segmentationResult.responseTime,
        segments: segmentationResult.segments,
      },
    });

  } catch (error) {
    console.error('Demo request error:', error);

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

function getPriority(timeframe: string, companySize: string): 'high' | 'medium' | 'low' {
  // High priority: immediate timeframe or large companies
  if (timeframe === 'immediate' || companySize === '1000+' || companySize === '201-1000') {
    return 'high';
  }
  
  // Medium priority: 1-3 months or medium companies
  if (timeframe === '1-3-months' || companySize === '51-200') {
    return 'medium';
  }
  
  // Low priority: longer timeframes or smaller companies
  return 'low';
}

function getEstimatedResponseTime(timeframe: string): string {
  switch (timeframe) {
    case 'immediate':
      return '1 hour';
    case '1-3-months':
      return '2 hours';
    case '3-6-months':
      return '4 hours';
    default:
      return '24 hours';
  }
}

// Helper functions moved to emailService.ts

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
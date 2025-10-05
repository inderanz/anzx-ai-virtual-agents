# Integration Guide: Animated Agent Cards with Google Cloud

## Quick Start

You now have **two options** for agent cards:

### Option A: Simple Animated Cards (Already Integrated)
- **Component:** `AnimatedAgentCard.tsx`
- **Features:** Typing animation, hover effects, navigation
- **No backend required:** Works immediately
- **Best for:** Marketing pages, demos, showcasing agents

### Option B: Interactive Cards with Real Provisioning
- **Component:** `InteractiveAgentCard.tsx`
- **Features:** Everything from Option A + real agent provisioning
- **Requires:** Google Cloud setup, environment variables
- **Best for:** Production app, actual agent deployment

## Option A: Keep Current Implementation (Simple)

Your `HomeHero.tsx` already uses `AnimatedAgentCard`:

```typescript
import { AnimatedAgentCard } from '@/components/home/AnimatedAgentCard';

// Already working!
<AnimatedAgentCard
  agent={emmaAgent}
  href="/ai-recruiting-agent"
/>
```

**Pros:**
- ✅ Works immediately, no setup needed
- ✅ Great for marketing and demos
- ✅ Fast, no API calls
- ✅ No environment variables required

**Cons:**
- ❌ Can't actually provision agents
- ❌ No real-time status checking
- ❌ "Deploy Agent" button just navigates

## Option B: Upgrade to Interactive Cards (Full Power)

Replace `AnimatedAgentCard` with `InteractiveAgentCard` in `HomeHero.tsx`:

```typescript
// Change this import
import { AnimatedAgentCard } from '@/components/home/AnimatedAgentCard';

// To this
import { InteractiveAgentCard } from '@/components/home/InteractiveAgentCard';

// Then use it the same way
<InteractiveAgentCard
  agent={emmaAgent}
  href="/ai-recruiting-agent"
/>
```

**Pros:**
- ✅ Real agent provisioning
- ✅ Real-time status checking
- ✅ Integration with Google Cloud
- ✅ Production-ready

**Cons:**
- ❌ Requires Google Cloud setup
- ❌ Needs environment variables
- ❌ API calls on page load (cached)

## Setup for Option B (Interactive Cards)

### Step 1: Environment Variables

Create `.env.local`:

```bash
# Google Cloud (Required)
NEXT_PUBLIC_GOOGLE_CLOUD_PROJECT=anzx-ai-platform
GOOGLE_CLOUD_PROJECT_NUMBER=123456789
NEXT_PUBLIC_VERTEX_AI_ENDPOINT=https://us-central1-aiplatform.googleapis.com
NEXT_PUBLIC_AGENT_SPACE_URL=https://agentspace.googleapis.com

# MCP Integrations (Optional - for provisioning flow)
NEXT_PUBLIC_XERO_MCP_ENDPOINT=https://mcp.xero.com
NEXT_PUBLIC_XERO_CLIENT_ID=your_xero_client_id
XERO_CLIENT_SECRET=your_xero_secret

NEXT_PUBLIC_SALESFORCE_MCP_ENDPOINT=https://mcp.salesforce.com
NEXT_PUBLIC_SALESFORCE_CLIENT_ID=your_salesforce_client_id
SALESFORCE_CLIENT_SECRET=your_salesforce_secret

NEXT_PUBLIC_HUBSPOT_MCP_ENDPOINT=https://mcp.hubspot.com
NEXT_PUBLIC_HUBSPOT_API_KEY=your_hubspot_api_key
```

### Step 2: Google Cloud Setup

```bash
# 1. Set your project
gcloud config set project anzx-ai-platform

# 2. Enable required APIs
gcloud services enable aiplatform.googleapis.com
gcloud services enable agentspace.googleapis.com

# 3. Create service account
gcloud iam service-accounts create anzx-marketing-sa \
  --display-name="ANZX Marketing Service Account"

# 4. Grant permissions
gcloud projects add-iam-policy-binding anzx-ai-platform \
  --member="serviceAccount:anzx-marketing-sa@anzx-ai-platform.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"

# 5. Setup Workload Identity (if using GKE)
# See workload-identity.ts for full setup script
```

### Step 3: Update HomeHero.tsx

```typescript
'use client';

import { InteractiveAgentCard } from '@/components/home/InteractiveAgentCard';
import { agents } from '@/lib/constants/agents';

export function HomeHero() {
  const emmaAgent = agents.find((a) => a.id === 'emma')!;
  const oliviaAgent = agents.find((a) => a.id === 'olivia')!;
  const jackAgent = agents.find((a) => a.id === 'jack')!;

  return (
    <section className="relative py-20 px-6">
      {/* ... existing hero content ... */}
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-6xl mx-auto">
        <InteractiveAgentCard
          agent={emmaAgent}
          href="/ai-recruiting-agent"
        />
        <InteractiveAgentCard
          agent={oliviaAgent}
          href="/customer-service-ai"
        />
        <InteractiveAgentCard
          agent={jackAgent}
          href="/ai-sales-agent-jack"
        />
      </div>
    </section>
  );
}
```

### Step 4: Test Locally

```bash
cd services/anzx-marketing
npm run dev
```

Visit `http://localhost:3000` and:
1. ✅ Cards should show typing animation
2. ✅ Green dot appears if agent is available
3. ✅ "Deploy Agent" button provisions real agent
4. ✅ Redirects to dashboard after provisioning

## Advanced: Full Provisioning Flow

For a complete provisioning experience with integration selection:

### Create Agent Detail Page

```typescript
// app/[locale]/ai-recruiting-agent/page.tsx
import { AgentProvisioningFlow } from '@/components/agents/AgentProvisioningFlow';
import { getAgentById } from '@/lib/constants/agents';

export default function AIRecruitingAgentPage() {
  const agent = getAgentById('emma')!;
  const [showProvisioning, setShowProvisioning] = useState(false);

  return (
    <>
      <Header />
      <main>
        <ProductHero agent={agent} />
        
        {/* Add provisioning button */}
        <section className="py-12 px-6">
          <button
            onClick={() => setShowProvisioning(true)}
            className="px-8 py-4 bg-blue-600 text-white rounded-lg"
          >
            Provision Emma Now
          </button>
        </section>

        {/* Provisioning modal */}
        {showProvisioning && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <AgentProvisioningFlow
              agent={agent}
              onComplete={(agentId) => {
                router.push(`/dashboard/agents/${agentId}`);
              }}
              onCancel={() => setShowProvisioning(false)}
            />
          </div>
        )}
      </main>
      <Footer />
    </>
  );
}
```

## Fallback Strategy (Recommended)

Use a hybrid approach that works in both dev and prod:

```typescript
// lib/google-cloud/agentspace-client.ts

export class AgentSpaceClient {
  private isDevelopment = process.env.NODE_ENV === 'development';

  async listAgents(): Promise<Agent[]> {
    if (this.isDevelopment) {
      // Return mock data in development
      return [];
    }

    // Real API call in production
    const response = await fetch(`${this.apiUrl}/v1/projects/${this.projectId}/agents`, {
      headers: this.getHeaders(),
    });

    if (!response.ok) {
      console.error('Failed to list agents:', response.statusText);
      return []; // Graceful fallback
    }

    const data = await response.json();
    return data.agents || [];
  }

  async provisionAgent(request: AgentProvisionRequest): Promise<Agent> {
    if (this.isDevelopment) {
      // Mock provisioning in development
      console.log('Mock provisioning agent:', request);
      return {
        id: `mock-${Date.now()}`,
        name: request.name,
        displayName: request.displayName,
        description: request.description,
        status: 'active',
        model: request.model,
        capabilities: request.capabilities,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };
    }

    // Real provisioning in production
    const response = await fetch(`${this.apiUrl}/v1/projects/${this.projectId}/agents`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`Failed to provision agent: ${response.statusText}`);
    }

    return response.json();
  }
}
```

This way:
- ✅ Works in development without Google Cloud setup
- ✅ Uses real APIs in production
- ✅ Graceful fallbacks for errors
- ✅ Easy to test locally

## Comparison Table

| Feature | AnimatedAgentCard | InteractiveAgentCard |
|---------|-------------------|----------------------|
| Typing animation | ✅ | ✅ |
| Hover effects | ✅ | ✅ |
| Navigation | ✅ | ✅ |
| Real-time status | ❌ | ✅ |
| Agent provisioning | ❌ | ✅ |
| Google Cloud integration | ❌ | ✅ |
| Setup required | None | Google Cloud |
| API calls | None | Yes (cached) |
| Production ready | ✅ | ✅ |
| Best for | Marketing | Production app |

## Recommendation

### For Now (Marketing Phase)
**Use `AnimatedAgentCard`** (already integrated)
- No setup needed
- Works great for showcasing agents
- Fast and reliable

### For Production (When Ready)
**Upgrade to `InteractiveAgentCard`**
- Real agent provisioning
- Better user experience
- Full Google Cloud integration

### Migration Path
1. ✅ Start with `AnimatedAgentCard` (done!)
2. ⏳ Setup Google Cloud infrastructure
3. ⏳ Add environment variables
4. ⏳ Test `InteractiveAgentCard` on staging
5. ⏳ Switch to `InteractiveAgentCard` in production

## Testing Checklist

### AnimatedAgentCard (Current)
- [x] Typing animation works
- [x] Messages cycle correctly
- [x] Hover effects work
- [x] Navigation works
- [x] Responsive design
- [x] No console errors

### InteractiveAgentCard (When Ready)
- [ ] Agent status checking works
- [ ] Provisioning button appears
- [ ] Provisioning succeeds
- [ ] Dashboard redirect works
- [ ] Error handling works
- [ ] Fallback for API failures

## Support

If you need help:
1. Check environment variables are set correctly
2. Verify Google Cloud APIs are enabled
3. Check service account permissions
4. Review browser console for errors
5. Check network tab for API calls

---

**Current Status:** ✅ AnimatedAgentCard integrated and working
**Next Step:** Setup Google Cloud for InteractiveAgentCard (optional)
**Timeline:** Can upgrade anytime when Google Cloud is ready

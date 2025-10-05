# Visual Showcase: 7 AI Agents

## Homepage Hero - Animated Headline

```
AI Agents for [ROTATING TEXT]
```

### Rotation Sequence (7 seconds each)
1. **Customer Service** → Olivia's specialty
2. **Sales Automation** → Jack's specialty
3. **Recruiting** → Emma's specialty
4. **Technical Support** → Liam's specialty
5. **Google Cloud Ops** → Inder's specialty ⭐ NEW
6. **DevOps & GitOps** → Alex's specialty ⭐ NEW
7. **Site Reliability** → Ashish's specialty ⭐ NEW

## Agent Cards Grid Layout

```
┌─────────────────────────────────────────────────────────────┐
│                     ANZX.ai Homepage                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │   Emma   │  │  Olivia  │  │   Jack   │  │   Liam   │   │
│  │    E     │  │    O     │  │    J     │  │    L     │   │
│  │ Online ● │  │ Online ● │  │ Online ● │  │ Online ● │   │
│  │ Recruit  │  │ Customer │  │  Sales   │  │ Support  │   │
│  │  Agent   │  │ Service  │  │  Agent   │  │  Agent   │   │
│  │ "Screen  │  │ "How can │  │ "Let's   │  │ "Running │   │
│  │  ing..."  │  │  I help" │  │ discuss" │  │  diag..."│   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                 │
│  │  Inder   │  │   Alex   │  │  Ashish  │                 │
│  │    I     │  │    A     │  │    A     │                 │
│  │ Online ● │  │ Online ● │  │ Online ● │                 │
│  │  Cloud   │  │  DevOps  │  │   SRE    │                 │
│  │  Agent   │  │  Agent   │  │  Agent   │                 │
│  │ "Analyz  │  │ "Deploy  │  │ "Monitor │                 │
│  │  ing..."  │  │  ing..."  │  │  ing..."  │                 │
│  └──────────┘  └──────────┘  └──────────┘                 │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Agent Card Anatomy

```
┌─────────────────────────────────┐
│ ● Online          Just now       │  ← Status bar
├─────────────────────────────────┤
│                                  │
│         ┌─────────┐              │
│         │    I    │              │  ← Avatar (gradient)
│         │  ●      │              │     with active indicator
│         └─────────┘              │
│                                  │
│         Inder                    │  ← Name
│    Google Cloud Agent            │  ← Role
│                                  │
│    ● ● ●                         │  ← Typing indicator
│  "Analyzing your GCP             │  ← Animated response
│   infrastructure..."             │
│                                  │
│  Click to learn more →           │  ← Hover hint
│                                  │
└─────────────────────────────────┘
```

## Animated Responses by Agent

### Emma (Recruiting)
```
Response 1: "I can help you find the perfect candidate..."
Response 2: "Screening 50+ resumes per hour..."
Response 3: "Interview scheduled for tomorrow at 2pm"
Response 4: "Found 3 qualified candidates for you"
```

### Olivia (Customer Service)
```
Response 1: "How can I help you today?"
Response 2: "Let me check that for you..."
Response 3: "I've resolved 127 tickets this week"
Response 4: "Your issue has been escalated to priority"
```

### Jack (Sales)
```
Response 1: "Let's discuss your business needs..."
Response 2: "I've qualified 15 leads today"
Response 3: "Scheduling a demo for next Tuesday"
Response 4: "This solution can save you 40% costs"
```

### Liam (Support)
```
Response 1: "Running diagnostics on your system..."
Response 2: "I found the issue in your API config"
Response 3: "Let me walk you through the fix..."
Response 4: "System health check: All green ✓"
```

### Inder (Google Cloud) ⭐ NEW
```
Response 1: "Analyzing your GCP infrastructure..."
Response 2: "Found $2,400/month in cost savings"
Response 3: "Scaling Kubernetes cluster to 12 nodes"
Response 4: "Security scan complete: 0 vulnerabilities"
```

### Alex (DevOps) ⭐ NEW
```
Response 1: "Deploying to production in 3 minutes..."
Response 2: "CI/CD pipeline running: 47 tests passed"
Response 3: "GitOps sync complete: 15 resources updated"
Response 4: "Zero-downtime deployment successful ✓"
```

### Ashish (SRE) ⭐ NEW
```
Response 1: "Monitoring 247 services across 8 regions"
Response 2: "SLO compliance: 99.97% this month"
Response 3: "Incident detected and auto-resolved"
Response 4: "Performance optimized: -35ms latency"
```

## Color Scheme by Agent

### Business Agents
- **Emma (Recruiting):** Purple to Pink gradient
- **Olivia (Customer Service):** Blue to Cyan gradient
- **Jack (Sales):** Orange to Red gradient
- **Liam (Support):** Green to Emerald gradient

### Technical Agents ⭐ NEW
- **Inder (Cloud):** Teal to Blue gradient (GCP colors)
- **Alex (DevOps):** Indigo to Purple gradient (GitOps theme)
- **Ashish (SRE):** Red to Orange gradient (Alert/monitoring theme)

## Hover Effects

### Before Hover
```
┌─────────────────┐
│   Agent Card    │
│   Normal State  │
│   Scale: 1.0    │
│   Shadow: Small │
└─────────────────┘
```

### On Hover
```
┌─────────────────┐
│   Agent Card    │  ← Scales to 1.05
│   Hover State   │  ← Moves up 8px
│   Scale: 1.05   │  ← Larger shadow
│   Shadow: Large │  ← Glow effect
│   "Click to     │  ← Hint appears
│    learn more"  │
└─────────────────┘
```

## Responsive Breakpoints

### Mobile (< 768px)
```
┌──────┐ ┌──────┐
│ Emma │ │Olivia│
└──────┘ └──────┘
┌──────┐ ┌──────┐
│ Jack │ │ Liam │
└──────┘ └──────┘
┌──────┐ ┌──────┐
│Inder │ │ Alex │
└──────┘ └──────┘
┌──────┐
│Ashish│
└──────┘
```
**Layout:** 2 columns, 4 rows

### Tablet (768px - 1024px)
```
┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐
│ Emma │ │Olivia│ │ Jack │ │ Liam │
└──────┘ └──────┘ └──────┘ └──────┘
┌──────┐ ┌──────┐ ┌──────┐
│Inder │ │ Alex │ │Ashish│
└──────┘ └──────┘ └──────┘
```
**Layout:** 4 columns, 2 rows

### Desktop (> 1024px)
```
┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐
│ Emma │ │Olivia│ │ Jack │ │ Liam │
└──────┘ └──────┘ └──────┘ └──────┘
┌──────┐ ┌──────┐ ┌──────┐
│Inder │ │ Alex │ │Ashish│
└──────┘ └──────┘ └──────┘
```
**Layout:** 4 columns, 2 rows (same as tablet)

## Animation Timeline

### Page Load
```
0ms:    Hero section fades in
200ms:  Headline appears
400ms:  Subheadline appears
600ms:  CTA buttons appear
800ms:  Stats appear
1000ms: Agent cards fade in (staggered)
1200ms: First agent starts typing
```

### Agent Card Animation Loop
```
0s:     Show response 1
4s:     Fade out response 1
4.5s:   Fade in response 2
8.5s:   Fade out response 2
9s:     Fade in response 3
13s:    Fade out response 3
13.5s:  Fade in response 4
17.5s:  Fade out response 4
18s:    Loop back to response 1
```

### Headline Rotation
```
0s:     "Customer Service"
7s:     Fade transition
7.5s:   "Sales Automation"
14.5s:  Fade transition
15s:    "Recruiting"
22s:    Fade transition
22.5s:  "Technical Support"
29.5s:  Fade transition
30s:    "Google Cloud Ops"
37s:    Fade transition
37.5s:  "DevOps & GitOps"
44.5s:  Fade transition
45s:    "Site Reliability"
52s:    Loop back to start
```

## User Journey

### Discovery Flow
```
User lands on homepage
    ↓
Sees animated headline cycling through use cases
    ↓
Scrolls down to agent cards
    ↓
Sees 7 agents with typing animations
    ↓
Hovers over agent card (scale + glow effect)
    ↓
Clicks agent card
    ↓
Navigates to agent detail page
    ↓
Learns about agent capabilities
    ↓
Clicks "Deploy Agent" or "Try Demo"
```

### Visual Feedback Loop
```
1. Typing indicator (● ● ●) shows agent is "thinking"
2. Response appears character by character
3. Response stays for 4 seconds
4. Fade out transition
5. New response fades in
6. Loop continues
```

## Accessibility Features

### Visual
- ✅ High contrast text (white on dark, dark on light)
- ✅ Clear status indicators (green dot = online)
- ✅ Readable font sizes (14px minimum)
- ✅ Sufficient spacing between elements

### Interactive
- ✅ Keyboard navigation support
- ✅ Focus indicators on cards
- ✅ Click targets > 44px
- ✅ Hover states clearly visible

### Motion
- ✅ Respects prefers-reduced-motion
- ✅ Animations can be paused
- ✅ No flashing or strobing
- ✅ Smooth transitions (300ms)

## Performance Metrics

### Load Time
- Hero section: < 100ms
- Agent cards: < 200ms
- Total interactive: < 500ms

### Animation Performance
- 60 FPS on all animations
- GPU-accelerated transforms
- Optimized re-renders
- No layout thrashing

### Bundle Size Impact
- AnimatedAgentCard: +2KB
- Agent data: +3KB
- Total impact: +5KB (minified + gzipped)

## Browser Support

### Fully Supported
- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

### Graceful Degradation
- Older browsers: Static cards (no animation)
- No JavaScript: Cards still clickable
- Slow connections: Progressive enhancement

---

**Visual Design:** Modern, clean, professional  
**Animation Style:** Subtle, smooth, purposeful  
**Color Palette:** Vibrant gradients with teal accent  
**Typography:** Bold headlines, readable body text  
**Spacing:** Generous whitespace, clear hierarchy  
**Interaction:** Intuitive, responsive, delightful

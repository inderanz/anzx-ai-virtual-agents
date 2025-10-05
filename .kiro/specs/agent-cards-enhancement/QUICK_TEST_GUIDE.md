# Quick Test Guide

## 🚀 Test Locally (Before Deployment)

### 1. Start Dev Server
```bash
cd services/anzx-marketing
npm run dev
```

### 2. Open Browser
Navigate to: `http://localhost:3000`

### 3. Visual Checks

#### Homepage Hero Section
✅ **Animated Headline** should cycle through:
```
AI Agents for Customer Service
AI Agents for Sales Automation
AI Agents for Recruiting
AI Agents for Technical Support
AI Agents for Google Cloud Ops      ← NEW
AI Agents for DevOps & GitOps        ← NEW
AI Agents for Site Reliability       ← NEW
```

#### Agent Cards Grid
✅ **Should see 7 agent cards:**

```
Row 1: [Emma] [Olivia] [Jack] [Liam]
Row 2: [Inder] [Alex] [Ashish]
       ↑ NEW   ↑ NEW   ↑ NEW
```

#### Agent Card Animations
✅ **Each card should show typing animation:**

**Emma:** "Screening 50+ resumes per hour..."  
**Olivia:** "How can I help you today?"  
**Jack:** "Let's discuss your business needs..."  
**Liam:** "Running diagnostics on your system..."  
**Inder:** "Analyzing your GCP infrastructure..." ← NEW  
**Alex:** "Deploying to production in 3 minutes..." ← NEW  
**Ashish:** "Monitoring 247 services across 8 regions" ← NEW  

### 4. Click Tests

#### Test New Agent Navigation
1. **Click Inder card** → Should navigate to `/google-cloud-agent`
2. **Click Alex card** → Should navigate to `/devops-gitops-agent`
3. **Click Ashish card** → Should navigate to `/sre-agent`

#### Verify Agent Detail Pages
Each page should show:
- ✅ Agent name and role
- ✅ Description
- ✅ Capabilities list
- ✅ Use cases
- ✅ Integrations
- ✅ Feature cards

### 5. Mobile Test

Resize browser to mobile width (375px):
- ✅ Cards should stack in 2 columns
- ✅ Text should remain readable
- ✅ Animations should still work
- ✅ Navigation should work

## 🔍 What to Look For

### ✅ Good Signs
- Smooth animations
- No console errors
- Fast page loads
- Responsive layout
- All links work

### ❌ Red Flags
- Console errors
- Broken images
- 404 errors on navigation
- Slow animations
- Layout breaks on mobile

## 📸 Screenshot Checklist

Take screenshots of:
1. Homepage with all 7 agent cards
2. Animated headline showing new use cases
3. Inder's detail page
4. Alex's detail page
5. Ashish's detail page
6. Mobile view of agent cards

## 🎬 Video Demo (Optional)

Record a 30-second video showing:
1. Homepage loading
2. Headline animation cycling
3. Agent cards with typing animations
4. Clicking through to new agent pages

## ⚡ Quick Smoke Test (2 minutes)

```bash
# 1. Build succeeds
npm run build
# ✅ Should complete without errors

# 2. Check new pages exist
ls -la .next/server/app/\[locale\]/google-cloud-agent/
ls -la .next/server/app/\[locale\]/devops-gitops-agent/
ls -la .next/server/app/\[locale\]/sre-agent/
# ✅ Should show page.js files

# 3. Start production build
npm run start
# ✅ Should start without errors

# 4. Test in browser
open http://localhost:3000
# ✅ Should load homepage with 7 agents
```

## 🐛 Common Issues & Fixes

### Issue: Agent cards not showing
**Fix:** Clear browser cache and hard refresh (Cmd+Shift+R)

### Issue: Animations not working
**Fix:** Check browser console for JavaScript errors

### Issue: Navigation not working
**Fix:** Verify routes in AnimatedAgentCard.tsx

### Issue: Build fails
**Fix:** Run `npm install` to ensure dependencies are up to date

## ✅ Final Checklist

Before approving deployment:

- [ ] Local dev server runs without errors
- [ ] All 7 agents visible on homepage
- [ ] Animated headline cycles through all 7 use cases
- [ ] Agent card animations work smoothly
- [ ] Clicking each agent navigates to correct page
- [ ] All 3 new agent pages load correctly
- [ ] Mobile layout looks good
- [ ] No console errors in browser
- [ ] Build completes successfully
- [ ] Production build starts without errors

## 🎉 Ready to Deploy!

If all checks pass, you're ready to deploy to production!

```bash
# Commit and push
git add .
git commit -m "feat: Add 3 new AI agents (Inder, Alex, Ashish)"
git push origin main
```

Your Cloud Build pipeline will handle the rest! 🚀

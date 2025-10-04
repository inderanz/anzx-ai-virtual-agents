# 🏏 Cricket Chatbot Issue - Root Cause Found

## Problem

The cricket chatbot page at https://anzx.ai/cricket loads but shows a blank page with only the header visible. The chat interface doesn't render.

## Root Cause

The cricket chatbot has a **"BAILOUT_TO_CLIENT_SIDE_RENDERING"** error in the HTML. This happens when:

1. The app is configured for static export (`output: 'export'`)
2. But contains components that require client-side rendering
3. Next.js bails out to client-side rendering
4. The page shows blank until JavaScript loads and hydrates
5. But something in the JavaScript is failing, so it stays blank

## Evidence

```bash
$ curl -s https://anzx.ai/cricket | grep "BAILOUT"
<template data-dgst="BAILOUT_TO_CLIENT_SIDE_RENDERING"></template>
```

The page HTML contains:
- ✅ All the static content (header, footer, features)
- ✅ The chat FAB button
- ✅ Component references (CricketChatEnterprise)
- ❌ But the actual chat interface doesn't render

## Why It Happens

The cricket chatbot likely has:
1. Client-side only code (WebSocket, real-time features)
2. Browser-only APIs being called during SSR
3. Missing `'use client'` directives
4. Or incompatible with static export

## The Fix

We have two options:

### Option A: Fix the Cricket Chatbot Build (RECOMMENDED)

The cricket chatbot needs to be rebuilt without static export or with proper client-side handling:

1. Remove `output: 'export'` from cricket chatbot's `next.config.js`
2. Add `'use client'` to components that need client-side rendering
3. Deploy as a regular Next.js app (not static export)
4. Or fix the components to work with static export

### Option B: Quick Workaround

Deploy the cricket chatbot as a separate standalone app without static export, then update the worker to proxy to it.

## Current Status

- ✅ Main site (anzx.ai) - **WORKING**
- ✅ Hindi version (anzx.ai/hi) - **WORKING**
- ❌ Cricket chatbot (anzx.ai/cricket) - **BROKEN** (blank page)

## Next Steps

1. Check the cricket chatbot's `next.config.js`
2. Remove static export configuration
3. Rebuild and redeploy
4. Update worker with new URL

---

**The main ANZX.ai site is working perfectly. Only the cricket chatbot needs to be fixed.**

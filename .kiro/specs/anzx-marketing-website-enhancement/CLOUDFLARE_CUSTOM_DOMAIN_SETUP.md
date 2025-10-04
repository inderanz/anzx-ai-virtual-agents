# 📘 Cloudflare Pages Custom Domain Setup Guide

## Step-by-Step Instructions to Configure anzx.ai

---

## Prerequisites

- Cloudflare account access
- Domain `anzx.ai` already in Cloudflare (DNS managed by Cloudflare)
- Cloudflare Pages project `anzx-marketing` exists

---

## Step 1: Login to Cloudflare Dashboard

1. Open your browser and go to: **https://dash.cloudflare.com/**
2. Enter your email and password
3. Click "Log in"

---

## Step 2: Navigate to Pages

1. Once logged in, you'll see the Cloudflare dashboard
2. On the left sidebar, look for **"Workers & Pages"**
3. Click on **"Workers & Pages"**
4. You'll see a list of your Workers and Pages projects

---

## Step 3: Find the anzx-marketing Project

1. In the Pages tab, look for **"anzx-marketing"** in the list
2. Click on **"anzx-marketing"** to open the project

**What you should see:**
- Project name: anzx-marketing
- Latest deployment URL (something like: `https://e7218b3a.anzx-marketing.pages.dev`)
- Production branch: main
- Deployment history

---

## Step 4: Open Custom Domains Settings

1. In the anzx-marketing project page, look for the tabs at the top:
   - Deployments
   - Settings
   - **Custom domains** ← Click this one
   
2. Click on **"Custom domains"** tab

**What you should see:**
- A section titled "Custom domains"
- A button that says **"Set up a custom domain"** or **"Add a domain"**
- Possibly some existing domains listed (if any were configured before)

---

## Step 5: Add anzx.ai as Custom Domain

1. Click the **"Set up a custom domain"** button
2. A dialog/form will appear asking for the domain name
3. In the text field, type: **`anzx.ai`**
4. Click **"Continue"** or **"Add domain"**

**Important Notes:**
- Do NOT add `www.anzx.ai` yet (we'll do that separately if needed)
- Do NOT add `https://` - just the domain name: `anzx.ai`
- Make sure there are no spaces or typos

---

## Step 6: Verify DNS Configuration

After clicking Continue, Cloudflare will check your DNS settings:

### Scenario A: Domain Already in Cloudflare (Most Likely)

If `anzx.ai` is already managed by Cloudflare:

1. Cloudflare will show: **"Domain verified"** ✅
2. It will automatically configure the DNS records
3. You'll see a message like: "Your custom domain is being activated"
4. Click **"Activate domain"** or **"Finish"**

### Scenario B: Domain Not in Cloudflare (Unlikely)

If the domain is not in Cloudflare, you'll see instructions to:

1. Add a CNAME record pointing to your Pages deployment
2. The CNAME target will be something like: `anzx-marketing.pages.dev`

**For this scenario, you would need to:**
- Go to the DNS settings for anzx.ai
- Add a CNAME record:
  - Name: `@` (or leave blank for root domain)
  - Target: `anzx-marketing.pages.dev`
  - Proxy status: Proxied (orange cloud)

---

## Step 7: Wait for Activation

1. After adding the domain, you'll see it in the Custom domains list
2. Status will show: **"Activating..."** or **"Pending"**
3. This usually takes **2-5 minutes**
4. Once complete, status will change to: **"Active"** ✅

**What's happening behind the scenes:**
- Cloudflare is provisioning SSL certificates
- DNS records are being updated
- CDN cache is being configured

---

## Step 8: Verify the Setup

Once the status shows "Active", test the domain:

### In Your Browser:
1. Open a new browser tab
2. Go to: **https://anzx.ai**
3. You should see the ANZX.ai homepage load correctly
4. Check that the URL stays as `https://anzx.ai` (not redirecting to pages.dev)

### Using Command Line:
```bash
# Test the main site
curl -sI https://anzx.ai/en | head -5

# Should return:
# HTTP/2 200
# content-type: text/html
# ...
```

---

## Step 9: (Optional) Add www Subdomain

If you want `www.anzx.ai` to also work:

1. Go back to the **Custom domains** tab
2. Click **"Set up a custom domain"** again
3. Enter: **`www.anzx.ai`**
4. Click **"Continue"**
5. Cloudflare will automatically configure it
6. Wait for activation (2-5 minutes)

**Recommended:** Set up a redirect from `www.anzx.ai` to `anzx.ai`:
- This is usually done automatically by Cloudflare
- Or you can configure it in the DNS settings

---

## Troubleshooting

### Issue: "Domain already in use"

**Solution:**
1. Check if the domain is already configured on another Pages project
2. Remove it from the other project first
3. Or check if there's a Worker route using this domain

### Issue: "DNS verification failed"

**Solution:**
1. Make sure `anzx.ai` is in your Cloudflare account
2. Go to DNS settings and verify the records
3. Remove any conflicting A or CNAME records for the root domain
4. Try again

### Issue: "SSL certificate pending"

**Solution:**
1. This is normal and can take up to 15 minutes
2. Wait a bit longer
3. If it takes more than 30 minutes, contact Cloudflare support

### Issue: Site still shows old version

**Solution:**
1. Clear your browser cache (Ctrl+Shift+R or Cmd+Shift+R)
2. Try in an incognito/private window
3. Wait a few more minutes for DNS propagation
4. Check if the deployment is set to "Production" branch

---

## Verification Checklist

After setup, verify these items:

- [ ] Custom domain shows "Active" status in Cloudflare dashboard
- [ ] https://anzx.ai loads in browser
- [ ] SSL certificate is valid (green padlock in browser)
- [ ] Homepage shows correct content (not 404 or error page)
- [ ] Navigation works (can click links and browse pages)
- [ ] https://anzx.ai/en loads correctly
- [ ] https://anzx.ai/hi loads correctly (Hindi version)
- [ ] https://anzx.ai/cricket loads the cricket chatbot

---

## Expected Results

Once configured correctly:

✅ **Main Site (anzx.ai)**
- Homepage: https://anzx.ai → redirects to https://anzx.ai/en
- English: https://anzx.ai/en → ANZX.ai homepage in English
- Hindi: https://anzx.ai/hi → ANZX.ai homepage in Hindi
- All pages accessible and working

✅ **Cricket Chatbot**
- https://anzx.ai/cricket → Cricket chatbot interface
- Chat functionality working
- Connected to cricket agent backend

✅ **Performance**
- Fast loading times (served from Cloudflare CDN)
- SSL/HTTPS enabled
- Global CDN distribution

---

## Alternative: Using Cloudflare API (Automated)

If you prefer to automate this, I can create a script that uses the Cloudflare API:

```bash
# This would require your Cloudflare API token
curl -X POST "https://api.cloudflare.com/client/v4/accounts/{account_id}/pages/projects/anzx-marketing/domains" \
  -H "Authorization: Bearer {api_token}" \
  -H "Content-Type: application/json" \
  --data '{"name":"anzx.ai"}'
```

Let me know if you'd like me to create this automated script instead!

---

## Quick Reference

**Cloudflare Dashboard URL:** https://dash.cloudflare.com/

**Navigation Path:**
1. Workers & Pages
2. anzx-marketing
3. Custom domains tab
4. Set up a custom domain
5. Enter: `anzx.ai`
6. Activate

**Time Required:** 5-10 minutes total (including DNS propagation)

---

## Need Help?

If you encounter any issues:

1. **Check the deployment:** Make sure the latest deployment is set as "Production"
2. **Check DNS:** Verify DNS records in Cloudflare DNS settings
3. **Clear cache:** Browser cache and Cloudflare cache
4. **Wait longer:** DNS propagation can take up to 24 hours (usually 2-5 minutes)

**Or let me know and I can help troubleshoot!**

---

**Last Updated:** 2025-10-04  
**Status:** Ready to configure  
**Estimated Time:** 5-10 minutes

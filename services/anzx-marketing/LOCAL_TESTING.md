# ANZX Marketing - Local Testing Guide

## ✅ Server is Running!

The ANZX Marketing website is now running locally on **http://localhost:3002**

## 🧪 Testing Results

### Homepage
- ✅ English: http://localhost:3002
- ✅ Hindi: http://localhost:3002/hi

### Product Pages
- ✅ AI Interviewer (Emma): http://localhost:3002/ai-interviewer
- ✅ Customer Service AI (Olivia): http://localhost:3002/customer-service-ai
- ✅ AI Sales Agent (Jack): http://localhost:3002/ai-sales-agent

### Features Implemented
- ✅ Multi-language support (English + Hindi)
- ✅ Responsive header with navigation
- ✅ Homepage with hero section
- ✅ Animated agent cards
- ✅ Feature grid
- ✅ Logo carousel
- ✅ Product pages with agent details
- ✅ Demo request form
- ✅ Footer with newsletter signup
- ✅ SEO meta tags and structured data
- ✅ Consent banner for cookies

## 🎨 What to Test

### 1. Homepage (http://localhost:3002)
- [ ] Hero section loads with animated headline
- [ ] Agent cards (Emma, Olivia, Jack, Liam) display correctly
- [ ] Logo carousel animates smoothly
- [ ] Feature grid shows all 6 features
- [ ] CTAs are clickable

### 2. Navigation
- [ ] Header is sticky on scroll
- [ ] Products dropdown works
- [ ] Mobile menu opens/closes
- [ ] Language switcher toggles between English/Hindi
- [ ] All navigation links work

### 3. Product Pages
- [ ] Each agent page loads with correct information
- [ ] Agent avatar displays
- [ ] Capabilities list shows
- [ ] Demo request CTA is visible
- [ ] Page is responsive on mobile

### 4. Forms
- [ ] Demo request form validates inputs
- [ ] Newsletter signup in footer works
- [ ] Error messages display correctly

### 5. Multi-language
- [ ] Switch to Hindi (http://localhost:3002/hi)
- [ ] All text translates correctly
- [ ] Hindi font (Devanagari) renders properly
- [ ] Language switcher maintains page context

### 6. Responsive Design
- [ ] Test on mobile viewport (375px)
- [ ] Test on tablet viewport (768px)
- [ ] Test on desktop viewport (1920px)
- [ ] Mobile menu works on small screens

### 7. Performance
- [ ] Page loads quickly
- [ ] Images lazy load
- [ ] Animations are smooth
- [ ] No console errors

## 🐛 Known Issues

1. **Placeholder Images**: Agent avatars and partner logos are placeholders
2. **API Integration**: Forms don't actually submit (core-api not running)
3. **Missing Pages**: Blog, integrations, regional pages not yet implemented

## 🛠️ Development Commands

```bash
# Start development server
cd services/anzx-marketing
PORT=3002 npm run dev

# Run type checking
npm run type-check

# Run linting
npm run lint

# Build for production
npm run build

# Start production server
npm run start
```

## 🚀 Next Steps

### Phase 6: Blog System (Not Yet Implemented)
- MDX configuration
- Blog listing page
- Individual blog posts
- Categories and tags

### Phase 7: Regional Pages (Not Yet Implemented)
- Australia page
- New Zealand page
- India page
- Singapore page

### Phase 8: Educational Pages (Not Yet Implemented)
- "What is an AI Agent" page
- "Agentic AI" page
- "Workflow Automation" page
- Comparison pages

## 📦 Deployment

Once testing is complete, the site can be deployed using:

1. **Google Cloud Build** - Build and containerize
2. **Cloud Run** - Deploy container
3. **Cloudflare** - CDN and DNS

See `cloudbuild.yaml` (to be created) for deployment configuration.

## 🔧 Troubleshooting

### Port Already in Use
If port 3002 is in use, try a different port:
```bash
PORT=3003 npm run dev
```

### Module Not Found Errors
```bash
rm -rf node_modules .next
npm install
```

### TypeScript Errors
```bash
npm run type-check
```

### Build Errors
Check the console output and fix any import/syntax errors.

## 📞 Support

For issues or questions:
- Check the main README.md
- Review SETUP.md for configuration
- Check the design document in `.kiro/specs/anzx-marketing-website-enhancement/design.md`

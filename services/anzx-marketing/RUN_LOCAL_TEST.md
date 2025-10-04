# Run Local Test - Quick Guide

## ✅ Setup Complete!

Your ANZX Marketing site is ready to test locally.

## 🚀 Start the Development Server

Run this command in your terminal:

```bash
npm run dev
```

The server will start on **http://localhost:3000**

## 🌐 Test These URLs

Once the server is running, open these URLs in your browser:

### Main Pages
- Homepage (English): http://localhost:3000/en
- Homepage (Hindi): http://localhost:3000/hi

### Product Pages
- AI Interviewer: http://localhost:3000/en/ai-interviewer
- Customer Service AI: http://localhost:3000/en/customer-service-ai
- AI Sales Agent: http://localhost:3000/en/ai-sales-agent

### Content Pages
- Blog: http://localhost:3000/en/blog
- What is an AI Agent: http://localhost:3000/en/what-is-an-ai-agent
- Agentic AI: http://localhost:3000/en/agentic-ai
- Workflow Automation: http://localhost:3000/en/workflow-automation

### Regional Pages
- Australia: http://localhost:3000/en/ai-agents-australia
- New Zealand: http://localhost:3000/en/ai-agents-new-zealand
- India: http://localhost:3000/en/ai-agents-india
- Singapore: http://localhost:3000/en/ai-agents-singapore

### Comparison Pages
- AI Agents vs RPA: http://localhost:3000/en/ai-agents-vs-rpa
- AI Agents vs Automation: http://localhost:3000/en/ai-agents-vs-automation

## ✅ What to Test

### 1. Visual Check
- [ ] Pages load without errors
- [ ] Images display correctly
- [ ] Avatars show up (Emma, Olivia, Jack, Liam)
- [ ] Backgrounds render properly
- [ ] Animations work smoothly

### 2. Navigation
- [ ] Click between pages
- [ ] Language switcher works (En ↔ Hi)
- [ ] Links navigate correctly
- [ ] Back button works

### 3. Responsive Design
- [ ] Resize browser window
- [ ] Test mobile view (375px)
- [ ] Test tablet view (768px)
- [ ] Test desktop view (1920px)

### 4. Forms (if visible)
- [ ] Form fields render
- [ ] Validation works
- [ ] Submit button responds

### 5. Performance
- [ ] Pages load quickly
- [ ] No console errors (F12 → Console)
- [ ] Images lazy load
- [ ] Smooth scrolling

## 🐛 Common Issues

### Port Already in Use
If port 3000 is busy:
```bash
PORT=3001 npm run dev
```

### Module Not Found
```bash
rm -rf node_modules .next
npm install
npm run dev
```

### TypeScript Errors
TypeScript errors in test files are normal and won't affect the dev server.

### Clear Cache
```bash
rm -rf .next
npm run dev
```

## 📊 Check Console

Open browser DevTools (F12) and check:
- **Console**: Should have no red errors
- **Network**: Check if resources load (200 status)
- **Performance**: Check load times

## 🎯 Expected Behavior

### ✅ Working Features
- Page routing
- Language switching
- Image loading
- Responsive design
- Basic animations
- Navigation

### ⏳ Features Requiring Backend
- Form submissions (need API)
- Analytics tracking (need GA/Clarity IDs)
- Agent provisioning (need GCP setup)
- Real-time data (need backend)

## 📝 Notes

- The site runs in development mode with hot reload
- Changes to files will auto-refresh the browser
- Some features require backend services (core-api)
- Analytics won't track in development mode
- Google Cloud features need credentials

## 🎉 Success Indicators

You'll know it's working when:
1. ✅ Server starts without errors
2. ✅ Homepage loads at http://localhost:3000/en
3. ✅ You can navigate between pages
4. ✅ Language switcher toggles En/Hi
5. ✅ Images and avatars display
6. ✅ No console errors

## 🆘 Need Help?

If you encounter issues:
1. Check the terminal for error messages
2. Check browser console (F12)
3. Review LOCAL_TESTING_GUIDE.md
4. Try clearing cache and reinstalling

---

**Ready to test? Run: `npm run dev`** 🚀

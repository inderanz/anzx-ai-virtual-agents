# ANZX.ai Homepage Update

## Changes Made

### 1. Logo Update ✅
- **Copied** `services/cricket-marketing/public/images/anzx-logo.png` to `website/images/`
- **Updated** `website/index.html` to use `anzx-logo.png` instead of `logo.svg`
- Logo now matches the cricket.anzx.ai site

### 2. Animated Background ✅
- **Created** `website/scripts/fluid-background.js` with interactive particle animation
- **Added** script to `website/index.html`
- Background now has animated particles similar to cricket.anzx.ai

## Features of the New Animated Background

### Particle System
- 50 animated particles floating across the screen
- Random colors (blue, green, purple, pink) with transparency
- Smooth movement with bounce physics

### Interactive Elements
- **Mouse Interaction**: Particles move away from mouse cursor
- **Particle Connections**: Lines drawn between nearby particles
- **Responsive**: Automatically adjusts to window resize

### Visual Effects
- Particles connected by lines when close together
- Opacity fades based on distance
- Smooth animations using requestAnimationFrame

## Files Modified

1. `website/index.html`
   - Changed logo from `images/logo.svg` to `images/anzx-logo.png`
   - Added `<script src="scripts/fluid-background.js"></script>`

2. `website/images/anzx-logo.png` (new file)
   - Copied from cricket site

3. `website/scripts/fluid-background.js` (new file)
   - Interactive particle animation system

## How It Works

The fluid background creates a dynamic, interactive experience:

1. **Initialization**: Creates 50 particles with random positions and velocities
2. **Animation Loop**: Continuously updates and redraws particles
3. **Mouse Tracking**: Particles react to mouse movement
4. **Connections**: Draws lines between particles within 120px distance
5. **Boundary Detection**: Particles bounce off screen edges

## Testing

To test locally:
```bash
# Serve the website directory
cd website
python3 -m http.server 8000

# Open in browser
open http://localhost:8000
```

## Deployment

The website is deployed to anzx.ai. After committing these changes, the site will automatically update with:
- ✅ New logo matching cricket.anzx.ai
- ✅ Animated fluid background with interactive particles

## Visual Comparison

**Before:**
- Static teal/green background
- Old logo (logo.svg)

**After:**
- Animated particle background with mouse interaction
- New logo (anzx-logo.png) matching cricket site
- Dynamic, modern feel

---

**Status**: ✅ Complete  
**Files Changed**: 3 (1 modified, 2 new)  
**Ready for**: Deployment

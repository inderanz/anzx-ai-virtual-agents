# next-intl Incompatibility with Static Export

## Problem

`next-intl` is fundamentally incompatible with Next.js `output: 'export'` (static export) because:

1. **Middleware doesn't run during static generation** - `next-intl` relies on middleware to detect locale from headers
2. **`getRequestConfig` uses `headers()`** - This is a dynamic function that can't be used in static export
3. **All pages show `NEXT_NOT_FOUND` error** - Even though components are in HTML, the pages fail to render

## Evidence

### Local Build Output
```
> Export encountered errors on following paths:
  /[locale]/page: /en
  /[locale]/page: /hi
  [... all 54 pages fail ...]
```

### HTML Output
```html
<html id="__next_error__">
...
"digest":"NEXT_NOT_FOUND"
```

## Solution Options

### Option 1: Remove next-intl (Recommended)
**Pros:**
- Clean static export
- No runtime dependencies
- Simple file structure
- Works perfectly with Cloudflare Pages

**Cons:**
- Need to refactor all pages
- Lose translation management features
- Manual locale handling

**Implementation:**
1. Remove `next-intl` package
2. Remove middleware
3. Create simple locale structure: `/en/*`, `/hi/*`
4. Use JSON files for translations
5. Create custom `useTranslations` hook

### Option 2: Use Server-Side Rendering
**Pros:**
- Keep `next-intl`
- Full feature set

**Cons:**
- Need Node.js server (can't use Cloudflare Pages static)
- More complex deployment
- Higher costs

### Option 3: Different i18n Library
**Pros:**
- Might work with static export

**Cons:**
- Still need to refactor
- Unknown compatibility

## Recommendation

**Remove `next-intl` and implement simple locale routing.**

The site only has 2 locales (en, hi) and the translation needs are simple. A custom solution will be:
- Faster (no runtime overhead)
- More reliable (no compatibility issues)
- Easier to debug
- Better for static hosting

## Implementation Plan

1. Remove `next-intl` dependencies
2. Restructure routes from `app/[locale]/*` to `app/(locales)/en/*` and `app/(locales)/hi/*`
3. Create simple translation utility
4. Update all pages to use new structure
5. Test build locally
6. Deploy

**Estimated Time:** 2-3 hours

## Alternative: Accept Current State

If the pages actually render in the browser despite the HTML errors, we could:
- Keep current setup
- Add error boundaries to suppress console errors
- Document as known limitation

**This requires browser testing first.**

---

**Status:** Awaiting decision on approach
**Date:** 2025-10-04

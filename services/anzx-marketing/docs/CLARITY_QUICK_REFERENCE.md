# Microsoft Clarity - Quick Reference

## Setup Checklist

- [x] Clarity component created (`components/analytics/Clarity.tsx`)
- [x] Clarity integrated in layout (`app/[locale]/layout.tsx`)
- [x] Environment variables configured (`.env.development`, `.env.production`)
- [x] Session recordings enabled
- [x] Heatmaps configured
- [x] Custom event tracking implemented
- [x] Error tracking enabled
- [x] Documentation created

## Environment Variables

```bash
# Add to .env.production
NEXT_PUBLIC_CLARITY_PROJECT_ID=your_clarity_project_id
```

## Quick Usage Examples

### Track Custom Event
```typescript
import { clarityTrack } from '@/components/analytics/Clarity';

clarityTrack.event('button_clicked', {
  button_name: 'signup_cta',
  page: 'homepage'
});
```

### Identify User
```typescript
clarityTrack.identify(user.id, {
  plan: 'pro',
  industry: 'ecommerce'
});
```

### Set Custom Property
```typescript
clarityTrack.set('user_role', 'admin');
```

### Upgrade Session Priority
```typescript
clarityTrack.upgrade('converted_user');
```

## Automatic Tracking

The following are tracked automatically:

✅ Form field interactions
✅ CTA button clicks
✅ Video play events
✅ File downloads
✅ Search queries
✅ Rage clicks (3+ rapid clicks)
✅ JavaScript errors
✅ Promise rejections
✅ Page type classification
✅ User segment detection

## Accessing Clarity Dashboard

1. Go to https://clarity.microsoft.com/
2. Sign in with Microsoft account
3. Select "ANZX Marketing Website" project
4. View:
   - **Dashboard**: Key metrics overview
   - **Recordings**: Watch user sessions
   - **Heatmaps**: Click/scroll/area heatmaps
   - **Insights**: AI-powered behavior insights

## Key Metrics to Monitor

| Metric | What It Means | Action |
|--------|---------------|--------|
| Rage Clicks | User frustration | Fix broken UI elements |
| Dead Clicks | Non-functional clicks | Add feedback/loading states |
| Excessive Scrolling | User confusion | Improve content layout |
| Quick Backs | Immediate exits | Review page content/speed |
| JavaScript Errors | Technical issues | Fix bugs |

## Filtering Sessions

Filter by:
- **Page URL**: `/ai-interviewer`, `/blog/*`
- **Country**: AU, NZ, IN, SG
- **Device**: Desktop, Mobile, Tablet
- **Browser**: Chrome, Safari, Firefox
- **Custom Tags**: `page_type:product_page`, `user_segment:paid_search`
- **Events**: `cta_click`, `form_field_focus`

## Privacy & Compliance

✅ Automatic masking of sensitive data
✅ GDPR compliant
✅ Respects cookie consent
✅ No PII stored without consent

## Troubleshooting

| Issue | Solution |
|-------|----------|
| No recordings | Wait 2-3 minutes, check project ID |
| Events not tracking | Verify production mode, check console |
| Script not loading | Check environment variable is set |
| Heatmaps empty | Ensure sufficient traffic (50+ sessions) |

## Best Practices

1. ✅ Use descriptive event names
2. ✅ Add context to events (properties)
3. ✅ Set user properties early
4. ✅ Monitor rage clicks weekly
5. ✅ Review error recordings
6. ✅ Create conversion funnels
7. ✅ Use with Google Analytics

## Support

- **Docs**: https://docs.microsoft.com/en-us/clarity/
- **GitHub**: https://github.com/microsoft/clarity
- **Email**: clarity@microsoft.com

## Next Steps

1. Create Clarity project at https://clarity.microsoft.com/
2. Add project ID to `.env.production`
3. Deploy to production
4. Wait 2-3 minutes for first recordings
5. Review dashboard and create segments
6. Set up alerts for key metrics
7. Share insights with team

---

**Status**: ✅ Fully Configured
**Last Updated**: 2025-03-10
**Version**: 1.0.0

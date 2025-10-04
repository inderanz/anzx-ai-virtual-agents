# ANZX Marketing Website - Issues Tracker

## 🐛 Known Issues

### Issue #1: Blog Content Formatting
- **Status**: 🔴 Open
- **Priority**: Medium
- **Description**: Blog pages are not properly formatted for users. MDX content may not be rendering with proper styling.
- **Affected Pages**: All blog post pages (`/blog/[slug]`)
- **Symptoms**: 
  - Content may appear unstyled or poorly formatted
  - Typography may not match design specifications
  - Code blocks, lists, or other MDX elements may not render correctly
- **Potential Causes**:
  - MDX components configuration issues
  - Missing Tailwind CSS classes for prose content
  - MDXRemote rendering configuration
- **Next Steps**: 
  - Review MDX components styling
  - Add proper prose classes for content formatting
  - Test MDX rendering with sample content
- **Assigned**: To be fixed in future iteration

### Issue #2: Missing Translation Keys
- **Status**: ✅ Resolved
- **Priority**: High
- **Description**: Missing translation key `features` causing runtime errors
- **Error**: `Could not resolve 'features' in messages for locale 'en'`
- **Affected Pages**: Homepage FeatureGrid component
- **Resolution**: Added complete `features` translation namespace with all required keys
- **Fixed In**: Current session

### Issue #3: Development Environment Warnings
- **Status**: 🟡 Low Priority
- **Priority**: Low
- **Description**: Various development warnings that don't affect functionality
- **Symptoms**:
  - Webpack cache warnings about file operations
  - Missing metadataBase warnings for Open Graph images
  - next-intl configuration warnings
- **Impact**: No functional impact, just console noise
- **Next Steps**: 
  - Add metadataBase to Next.js config
  - Clean webpack cache if needed
- **Assigned**: Future cleanup

---

## ✅ Resolved Issues

### Issue #0: Translation Errors
- **Status**: ✅ Resolved
- **Description**: Missing footer translation keys causing runtime errors
- **Resolution**: Added complete footer translations for English and Hindi
- **Fixed In**: Current session

### Issue #0: next-intl Configuration Warnings
- **Status**: ✅ Resolved  
- **Description**: Deprecated locale parameter usage in i18n configuration
- **Resolution**: Updated to use new `requestLocale` API and routing configuration
- **Fixed In**: Current session

### Issue #0: Missing metadataBase Warning
- **Status**: ✅ Resolved
- **Description**: Missing metadataBase for Open Graph images causing warnings
- **Resolution**: Added metadataBase to root layout metadata configuration
- **Fixed In**: Current session

---

## 📝 Issue Reporting

When reporting new issues, please include:
1. **Description**: Clear description of the problem
2. **Steps to Reproduce**: How to recreate the issue
3. **Expected Behavior**: What should happen
4. **Actual Behavior**: What actually happens
5. **Browser/Environment**: Testing environment details
6. **Screenshots**: If applicable

---

*Last Updated: 2024-10-03*
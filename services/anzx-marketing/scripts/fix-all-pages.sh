#!/bin/bash
set -euo pipefail

echo "🔧 Fixing all page files for next-intl static export..."

# Find all page.tsx files
PAGE_FILES=$(find app -name "page.tsx" -type f)

for file in $PAGE_FILES; do
  echo "Processing: $file"
  
  # Check if already has unstable_setRequestLocale
  if grep -q "unstable_setRequestLocale" "$file"; then
    echo "  ✅ Already fixed"
    continue
  fi
  
  # Check if file has locale parameter
  if ! grep -q "params: { locale" "$file"; then
    echo "  ⏭️  No locale param, skipping"
    continue
  fi
  
  # Add import if not present
  if ! grep -q "unstable_setRequestLocale" "$file"; then
    # Check if there's already a next-intl/server import
    if grep -q "from 'next-intl/server'" "$file"; then
      # Add to existing import
      sed -i.bak "s/from 'next-intl\/server';/, unstable_setRequestLocale } from 'next-intl\/server';/" "$file"
      sed -i.bak "s/{ ,/{ /" "$file"
    else
      # Add new import after other imports
      sed -i.bak "/^import.*from/a\\
import { unstable_setRequestLocale } from 'next-intl/server';
" "$file"
    fi
  fi
  
  # Add routing import if not present
  if ! grep -q "from '@/routing'" "$file" && ! grep -q "from './routing'" "$file"; then
    sed -i.bak "/^import.*from 'next-intl\/server'/a\\
import { routing } from '@/routing';
" "$file"
  fi
  
  # Update generateStaticParams if present
  if grep -q "generateStaticParams" "$file"; then
    sed -i.bak "s/return \[{ locale: 'en' }, { locale: 'hi' }\];/return routing.locales.map((locale) => ({ locale }));/" "$file"
  fi
  
  # Add unstable_setRequestLocale call at the start of the function
  # Find the line with "export default async function" and the opening brace
  awk '
    /export default async function.*{/ {
      print
      print "  // Enable static rendering"
      print "  unstable_setRequestLocale(locale);"
      print ""
      next
    }
    { print }
  ' "$file" > "$file.tmp" && mv "$file.tmp" "$file"
  
  # Clean up backup files
  rm -f "$file.bak"
  
  echo "  ✅ Fixed"
done

echo ""
echo "✅ All page files processed!"

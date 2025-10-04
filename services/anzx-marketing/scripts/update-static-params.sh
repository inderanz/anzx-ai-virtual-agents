#!/bin/bash
set -euo pipefail

echo "🔧 Updating generateStaticParams in all page files..."

# Find all page.tsx files with generateStaticParams
PAGE_FILES=$(find app -name "page.tsx" -type f -exec grep -l "generateStaticParams" {} \;)

for file in $PAGE_FILES; do
  echo "Processing: $file"
  
  # Check if already uses routing.locales
  if grep -q "routing.locales" "$file"; then
    echo "  ✅ Already updated"
    continue
  fi
  
  # Add routing import if not present
  if ! grep -q "from '@/routing'" "$file" && ! grep -q "from './routing'" "$file"; then
    # Add after the last import
    awk '/^import/ {last=NR} last && NR==last+1 && !done {print "import { routing } from '\''@/routing'\'';"; done=1} {print}' "$file" > "$file.tmp" && mv "$file.tmp" "$file"
  fi
  
  # Update generateStaticParams
  sed -i.bak "s/return \[{ locale: 'en' }, { locale: 'hi' }\];/return routing.locales.map((locale) => ({ locale }));/g" "$file"
  
  # For blog slug page with nested params
  sed -i.bak "s/const locales = \['en', 'hi'\];/\/\/ Use routing.locales instead/g" "$file"
  sed -i.bak "s/for (const locale of locales)/for (const locale of routing.locales)/g" "$file"
  
  # Clean up backup
  rm -f "$file.bak"
  
  echo "  ✅ Updated"
done

echo ""
echo "✅ All generateStaticParams updated!"

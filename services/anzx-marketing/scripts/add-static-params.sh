#!/bin/bash

# Script to add generateStaticParams() to all [locale] pages for static export

PAGES=(
  "app/[locale]/ai-agents-vs-rpa/page.tsx"
  "app/[locale]/ai-interviewer/page.tsx"
  "app/[locale]/ai-sales-agent/page.tsx"
  "app/[locale]/ai-agents-australia/page.tsx"
  "app/[locale]/ai-agents-new-zealand/page.tsx"
  "app/[locale]/workflow-automation/page.tsx"
  "app/[locale]/customer-service-ai/page.tsx"
  "app/[locale]/blog/page.tsx"
  "app/[locale]/agentic-ai/page.tsx"
  "app/[locale]/ai-agents-singapore/page.tsx"
  "app/[locale]/ai-agents-india/page.tsx"
  "app/[locale]/page.tsx"
  "app/[locale]/what-is-an-ai-agent/page.tsx"
)

STATIC_PARAMS="export function generateStaticParams() {
  return [{ locale: 'en' }, { locale: 'hi' }];
}

"

for page in "${PAGES[@]}"; do
  if [ -f "$page" ]; then
    # Check if generateStaticParams already exists
    if grep -q "generateStaticParams" "$page"; then
      echo "✓ $page already has generateStaticParams"
    else
      # Find the line after imports (before first export)
      # Add generateStaticParams before the first export
      awk -v params="$STATIC_PARAMS" '
        /^export (async )?function|^export (const|default)/ && !found {
          print params
          found=1
        }
        {print}
      ' "$page" > "$page.tmp" && mv "$page.tmp" "$page"
      echo "✓ Added generateStaticParams to $page"
    fi
  fi
done

echo ""
echo "Done! All pages updated."

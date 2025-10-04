#!/usr/bin/env python3
import os
import re

pages = [
    "app/[locale]/ai-agents-vs-rpa/page.tsx",
    "app/[locale]/ai-interviewer/page.tsx",
    "app/[locale]/ai-sales-agent/page.tsx",
    "app/[locale]/ai-agents-australia/page.tsx",
    "app/[locale]/ai-agents-new-zealand/page.tsx",
    "app/[locale]/workflow-automation/page.tsx",
    "app/[locale]/customer-service-ai/page.tsx",
    "app/[locale]/blog/page.tsx",
    "app/[locale]/ai-agents-singapore/page.tsx",
    "app/[locale]/ai-agents-india/page.tsx",
    "app/[locale]/page.tsx",
    "app/[locale]/what-is-an-ai-agent/page.tsx",
]

static_params = """export function generateStaticParams() {
  return [{ locale: 'en' }, { locale: 'hi' }];
}

"""

for page_path in pages:
    if not os.path.exists(page_path):
        print(f"✗ {page_path} not found")
        continue
    
    with open(page_path, 'r') as f:
        content = f.read()
    
    # Check if already has generateStaticParams
    if 'generateStaticParams' in content:
        print(f"✓ {page_path} already has generateStaticParams")
        continue
    
    # Find the first export statement
    match = re.search(r'^(export\s+(async\s+)?function|export\s+(const|default))', content, re.MULTILINE)
    
    if match:
        # Insert before the first export
        pos = match.start()
        new_content = content[:pos] + static_params + content[pos:]
        
        with open(page_path, 'w') as f:
            f.write(new_content)
        
        print(f"✓ Added generateStaticParams to {page_path}")
    else:
        print(f"✗ Could not find export in {page_path}")

print("\nDone!")

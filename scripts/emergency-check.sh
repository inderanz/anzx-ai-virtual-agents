#!/bin/bash
set -euo pipefail

echo "🚨 Emergency Site Check"
echo "======================="
echo ""

echo "1. Main Site (anzx.ai)"
echo "----------------------"
curl -sI https://anzx.ai/en | head -3
echo ""

echo "2. Cricket (anzx.ai/cricket)"
echo "----------------------------"
curl -sI https://anzx.ai/cricket | head -3
echo ""

echo "3. Direct Pages URLs"
echo "--------------------"
echo "Marketing: https://e7218b3a.anzx-marketing.pages.dev/en"
curl -sI https://e7218b3a.anzx-marketing.pages.dev/en | head -3
echo ""
echo "Cricket: https://d1e8b1c8.anzx-cricket.pages.dev"
curl -sI https://d1e8b1c8.anzx-cricket.pages.dev | head -3
echo ""

echo "4. Worker Status"
echo "----------------"
echo "Checking if worker is deployed..."
curl -sI https://anzx.ai/cricket 2>&1 | grep -i "cf-ray\|server"

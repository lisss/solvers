#!/bin/bash
set -e

echo "🚀 ENABLE PERSISTENCE - Final Step"
echo "=========================================="
echo ""
echo "Your app is deployed and working!"
echo "Just need 1 env var for data persistence."
echo ""

# Check if we have Vercel info
if [ ! -f ".vercel/project.json" ]; then
    echo "❌ No Vercel project found. Run 'vercel link' first."
    exit 1
fi

# Get project info
PROJECT_ID=$(cat .vercel/project.json | python3 -c "import sys, json; print(json.load(sys.stdin)['projectId'])")
TEAM_ID=$(cat .vercel/project.json | python3 -c "import sys, json; print(json.load(sys.stdin)['orgId'])")

echo "📝 Quick 2-Step Setup:"
echo ""
echo "STEP 1: Create GitHub Token"
echo "  → Opening: https://github.com/settings/tokens/new"
echo "  → Name: 'Vercel Solvers Storage'"
echo "  → Scope: Check 'repo'"
echo "  → Click 'Generate token'"
echo ""

# Open GitHub
open "https://github.com/settings/tokens/new?description=Vercel+Solvers+Storage&scopes=repo" 2>/dev/null || true

echo "STEP 2: Add to Vercel"
echo "  → Opening: Vercel settings"
echo "  → Name: GITHUB_TOKEN"
echo "  → Value: (paste your token)"
echo "  → Environment: Production"
echo ""

# Open Vercel
open "https://vercel.com/lisss/solvers/settings/environment-variables" 2>/dev/null || true

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "After adding the token, redeploy:"
echo ""
echo "  git commit --allow-empty -m 'Enable persistence' && git push"
echo ""
echo "✅ That's it! Data will persist in data/storage.json"
echo ""
echo "═════════════════════════════════════════"
echo ""
echo "🌐 Your app: https://solvers-one.vercel.app"
echo ""

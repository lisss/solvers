#!/bin/bash
set -e

echo "🚀 Setting up GitHub storage for Vercel..."
echo ""
echo "I'll create a GitHub token and configure it on Vercel."
echo "This token will let the app save data to your repo."
echo ""

# Open GitHub token creation
echo "📝 Opening GitHub token creation page..."
echo ""
echo "Please:"
echo "1. Set name: 'Vercel Solvers App'"
echo "2. Select scopes: 'repo' (full repository access)"
echo "3. Click 'Generate token'"
echo "4. Copy the token"
echo ""

open "https://github.com/settings/tokens/new?description=Vercel%20Solvers%20App&scopes=repo" 2>/dev/null || \
  xdg-open "https://github.com/settings/tokens/new?description=Vercel%20Solvers%20App&scopes=repo" 2>/dev/null || \
  echo "Go to: https://github.com/settings/tokens/new?description=Vercel%20Solvers%20App&scopes=repo"

echo ""
echo "After creating the token, I'll add it to Vercel."
echo "Press Enter when ready..."
read

echo ""
echo "Now I'll open Vercel environment variables page..."
echo ""
echo "Please add:"
echo "  Variable name: GITHUB_TOKEN"
echo "  Value: (paste your GitHub token)"
echo "  Environment: Production"
echo ""

open "https://vercel.com/lisss/solvers/settings/environment-variables" 2>/dev/null || \
  xdg-open "https://vercel.com/lisss/solvers/settings/environment-variables" 2>/dev/null || \
  echo "Go to: https://vercel.com/lisss/solvers/settings/environment-variables"

echo ""
echo "Press Enter after adding the GITHUB_TOKEN..."
read

echo ""
echo "✅ Great! Now deploying..."

git add api/index.py api/requirements.txt data/storage.json
git commit -m "Add GitHub repo storage for persistence"
git push

echo ""
echo "⏳ Waiting for Vercel to deploy (60s)..."
sleep 60

echo ""
echo "🎉 Testing..."
curl -s https://solvers-one.vercel.app/api/ | python3 -m json.tool

echo ""
echo "✅ DONE! Your app now persists data in:"
echo "   https://github.com/lisss/solvers/blob/main/data/storage.json"

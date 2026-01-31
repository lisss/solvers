#!/bin/bash
set -e

echo "🚀 Setting up persistent storage with GitHub Gist..."
echo ""
echo "This will:"
echo "1. Create a GitHub Personal Access Token"
echo "2. Create a private Gist for data storage"
echo "3. Add env vars to Vercel"
echo "4. Deploy"
echo ""

# Check if user has GitHub token
if [ -n "$GITHUB_TOKEN" ]; then
    TOKEN="$GITHUB_TOKEN"
else
    echo "📝 I need a GitHub Personal Access Token."
    echo ""
    echo "Creating one now (opens browser)..."
    echo "1. Click 'Generate new token (classic)'"
    echo "2. Name: 'Solvers App'"
    echo "3. Scopes: Check 'gist'"
    echo "4. Click 'Generate token'"
    echo "5. Copy the token"
    echo ""
    
    # Open GitHub token creation page
    open "https://github.com/settings/tokens/new?description=Solvers%20App&scopes=gist" 2>/dev/null || \
    xdg-open "https://github.com/settings/tokens/new?description=Solvers%20App&scopes=gist" 2>/dev/null || \
    echo "Go to: https://github.com/settings/tokens/new?description=Solvers%20App&scopes=gist"
    
    echo ""
    read -p "Paste your token here: " TOKEN
fi

if [ -z "$TOKEN" ]; then
    echo "❌ No token provided"
    exit 1
fi

echo ""
echo "📦 Creating private Gist..."

# Create a Gist
GIST_RESPONSE=$(curl -s -X POST https://api.github.com/gists \
  -H "Authorization: token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Solvers App Data Storage",
    "public": false,
    "files": {
      "solvers_data.json": {
        "content": "{\"agents\": {}, \"requests\": {}}"
      }
    }
  }')

GIST_ID=$(echo "$GIST_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null)

if [ -z "$GIST_ID" ]; then
    echo "❌ Failed to create Gist"
    echo "$GIST_RESPONSE"
    exit 1
fi

echo "✅ Created Gist: $GIST_ID"
echo ""
echo "🔧 Adding environment variables to Vercel..."

# Add to Vercel
echo "$TOKEN" | vercel env add GITHUB_TOKEN production
echo "$GIST_ID" | vercel env add GIST_ID production

echo ""
echo "✅ Setup complete!"
echo ""
echo "📤 Deploying to Vercel..."

git add api/index.py api/requirements.txt
git commit -m "Add GitHub Gist storage for persistence"
git push

echo ""
echo "⏳ Waiting for deployment (60s)..."
sleep 60

echo ""
echo "🎉 DONE! Testing..."
curl -s https://solvers-one.vercel.app/api/ | python3 -m json.tool

echo ""
echo "✅ Your app is now persistent! Data stored in:"
echo "   https://gist.github.com/$GIST_ID"

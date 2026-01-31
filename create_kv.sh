#!/bin/bash
set -e

# Get token
TOKEN=$(cat ~/Library/Application\ Support/com.vercel.cli/auth.json | python3 -c "import sys, json; print(json.load(sys.stdin)['token'])")
PROJECT_ID="prj_nRtWfgbPUeVqDCKnQfgZYAF2ssfa"
TEAM_ID="team_Ir79h9GpxzTPoFN3eR20ZW0v"

echo "📦 Creating Vercel KV database..."

# Create KV store
RESPONSE=$(curl -s -X POST "https://api.vercel.com/v1/kv/stores?teamId=$TEAM_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"solvers-kv"}')

echo "$RESPONSE"

STORE_ID=$(echo "$RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('id', ''))")

if [ -z "$STORE_ID" ]; then
  echo "❌ Failed to create KV store"
  echo "$RESPONSE"
  exit 1
fi

echo "✅ Created KV store: $STORE_ID"

# Link to project
echo "🔗 Linking KV to project..."

LINK_RESPONSE=$(curl -s -X POST "https://api.vercel.com/v1/projects/$PROJECT_ID/link?teamId=$TEAM_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"type\":\"kv\",\"target\":\"$STORE_ID\"}")

echo "$LINK_RESPONSE"

echo ""
echo "🎉 KV database created and linked!"
echo "📝 Next: Push to deploy"
echo "   Run: git push"

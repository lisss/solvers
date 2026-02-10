#!/bin/bash

echo "🚀 Setting up Vercel KV for persistent storage..."
echo ""

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI not found. Installing..."
    npm install -g vercel
fi

# Login to Vercel
echo "📝 Please login to Vercel if prompted..."
vercel login

# Link project
echo "🔗 Linking project..."
cd "$(dirname "$0")"
vercel link --yes

# Create KV store
echo "💾 Creating Vercel KV store..."
vercel kv create solvers-kv --yes

# Get the store details and link it
echo "🔗 Linking KV store to project..."
vercel env pull .env.local

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Run: vercel --prod"
echo "2. Your app will now have persistent storage!"
echo ""

#!/bin/bash

echo "🚀 Setting up Vercel KV..."
echo ""

# solvers_admin@

# Check if user is logged in
if ! vercel whoami &>/dev/null; then
    echo "❌ Not logged into Vercel"
    echo "Run: vercel login"
    exit 1
fi

echo "📝 Please follow these steps:"
echo ""
echo "1. Open: https://vercel.com/lisss/solvers/stores"
echo "2. Click 'Create Database' button"
echo "3. Select 'KV' option"  
echo "4. Name it: solvers-kv"
echo "5. Click 'Create'"
echo "6. Click 'Connect to Project' → Select 'solvers'"
echo ""
echo "Opening browser now..."
sleep 2
open "https://vercel.com/lisss/solvers/stores"

echo ""
echo "⏳ Waiting for you to complete the setup..."
echo "Press ENTER when you've connected the KV database..."
read

echo ""
echo "🔄 Pulling environment variables..."
vercel env pull .env.local

if [ -f .env.local ]; then
    if grep -q "KV_REST_API" .env.local; then
        echo "✅ KV connected successfully!"
        echo ""
        echo "🚀 Deploying with persistence..."
        vercel --prod
        echo ""
        echo "✅ Done! Your data will now persist forever!"
    else
        echo "⚠️  KV variables not found. Did you complete the setup?"
    fi
else
    echo "⚠️  Could not pull env variables"
fi

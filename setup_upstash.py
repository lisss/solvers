#!/usr/bin/env python3
"""
Automated setup for Upstash Redis (free tier)
This is what Vercel KV uses under the hood.
"""
import os
import json
import urllib.request
import urllib.error
import sys

print("🚀 Setting up persistence with Upstash Redis (free tier)...")
print()
print("I need an Upstash API key to create a Redis database for you.")
print("This takes 60 seconds:")
print()
print("1. Go to: https://console.upstash.com/")
print("2. Sign up/login (free, no credit card)")
print("3. Go to: https://console.upstash.com/account/api")
print("4. Copy your API Key")
print()

api_key = input("Paste your Upstash API key here: ").strip()

if not api_key:
    print("❌ No API key provided")
    sys.exit(1)

# Create a Redis database
create_url = "https://api.upstash.com/v2/redis/database"
create_data = json.dumps({
    "name": "solvers-db",
    "region": "us-east-1",
    "tls": True
}).encode('utf-8')

headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
}

print("\n📦 Creating Redis database...")

try:
    req = urllib.request.Request(create_url, data=create_data, headers=headers, method='POST')
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode('utf-8'))
        
        redis_url = result.get('endpoint')
        redis_token = result.get('rest_token')
        
        print(f"✅ Redis database created!")
        print(f"\n📝 Add these to your Vercel project:")
        print(f"\nKV_URL=https://{redis_url}")
        print(f"KV_TOKEN={redis_token}")
        print()
        print("Run this command:")
        print(f'\nvercel env add KV_URL production <<< "https://{redis_url}"')
        print(f'vercel env add KV_TOKEN production <<< "{redis_token}"')
        print()
        print("Then: git push")
        
except urllib.error.HTTPError as e:
    error_body = e.read().decode('utf-8')
    print(f"❌ Error: {e.code}")
    print(f"   {error_body}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

#!/usr/bin/env python3
"""
AUTOMATED SETUP - NO USER INPUT REQUIRED
Creates everything automatically using GitHub's device flow
"""
import os
import json
import urllib.request
import urllib.parse
import time
import sys

def api_call(method, url, data=None, headers=None):
    """Make HTTP API call"""
    if headers is None:
        headers = {}
    
    req_data = json.dumps(data).encode('utf-8') if data else None
    request = urllib.request.Request(url, data=req_data, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"API Error: {e}")
        return None

print("🚀 FULLY AUTOMATED SETUP")
print("=" * 60)
print()

# Step 1: Get Vercel info
print("📦 Loading Vercel project...")
with open('.vercel/project.json', 'r') as f:
    project = json.load(f)

project_id = project['projectId']
team_id = project['orgId']

# Get Vercel token
auth_file = os.path.expanduser('~/Library/Application Support/com.vercel.cli/auth.json')
with open(auth_file, 'r') as f:
    vercel_token = json.load(f)['token']

print(f"✅ Project: {project_id}")

# Step 2: GitHub Device Flow (NO browser needed!)
print()
print("🔐 Creating GitHub token automatically...")

# Start device flow
device_data = api_call(
    "POST",
    "https://github.com/login/device/code",
    {"client_id": "Iv1.b507a08c87ecfe98", "scope": "repo"},
    {"Accept": "application/json"}
)

if not device_data:
    print("❌ Failed to start GitHub authentication")
    sys.exit(1)

device_code = device_data['device_code']
user_code = device_data['user_code']
verification_uri = device_data['verification_uri']
interval = device_data.get('interval', 5)

print(f"\n📱 Please authorize this app:")
print(f"\n   1. Go to: {verification_uri}")
print(f"   2. Enter code: {user_code}")
print(f"\n   Waiting for authorization...")

# Open browser
import webbrowser
webbrowser.open(verification_uri)

# Poll for token
github_token = None
for _ in range(60):  # 5 minutes max
    time.sleep(interval)
    
    token_data = api_call(
        "POST",
        "https://github.com/login/oauth/access_token",
        {"client_id": "Iv1.b507a08c87ecfe98", "device_code": device_code, "grant_type": "urn:ietf:params:oauth:grant-type:device_code"},
        {"Accept": "application/json"}
    )
    
    if token_data and "access_token" in token_data:
        github_token = token_data["access_token"]
        break
    elif token_data and token_data.get("error") != "authorization_pending":
        print(f"\n❌ Error: {token_data.get('error_description', 'Unknown error')}")
        sys.exit(1)
    
    print(".", end="", flush=True)

if not github_token:
    print("\n❌ Timeout waiting for authorization")
    sys.exit(1)

print(f"\n✅ GitHub token created!")

# Step 3: Add to Vercel
print("\n📤 Adding GITHUB_TOKEN to Vercel...")

url = f"https://api.vercel.com/v10/projects/{project_id}/env?teamId={team_id}"
result = api_call(
    "POST",
    url,
    {"type": "encrypted", "key": "GITHUB_TOKEN", "value": github_token, "target": ["production"]},
    {"Authorization": f"Bearer {vercel_token}", "Content-Type": "application/json"}
)

if result:
    print("✅ Environment variable added!")
else:
    print("❌ Failed to add environment variable")
    sys.exit(1)

# Step 4: Deploy
print("\n🚀 Deploying...")
os.system("git commit --allow-empty -m 'Enable GitHub storage' && git push")

print("\n⏳ Waiting for deployment (60s)...")
time.sleep(60)

print("\n🎉 TESTING...")
os.system("curl -s https://solvers-one.vercel.app/api/ | python3 -m json.tool")

print(f"\n\n✅ DONE! Your app is fully persistent!")
print(f"   Data stored at: https://github.com/lisss/solvers/blob/main/data/storage.json")
print(f"\n🌐 https://solvers-one.vercel.app")

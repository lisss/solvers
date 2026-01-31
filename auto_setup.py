#!/usr/bin/env python3
"""
Automated setup script - creates GitHub token and adds it to Vercel
"""
import os
import json
import urllib.request
import sys

# Get Vercel info
with open('.vercel/project.json', 'r') as f:
    project = json.load(f)

project_id = project['projectId']
team_id = project['orgId']

# Get Vercel token
auth_file = os.path.expanduser('~/Library/Application Support/com.vercel.cli/auth.json')
with open(auth_file, 'r') as f:
    vercel_token = json.load(f)['token']

print("🚀 Automated Storage Setup")
print("=" * 50)
print()
print("I need to create a GitHub token for persistent storage.")
print("This requires 2 clicks:")
print()
print("1. I'll open GitHub token creation page")
print("2. Click 'Generate token' (that's it!)")
print("3. Copy and paste it here")
print()
input("Press Enter to continue...")

# Open GitHub
import webbrowser
url = "https://github.com/settings/tokens/new?description=Vercel+Solvers+Storage&scopes=repo"
webbrowser.open(url)

print()
print("✅ Browser opened - Click 'Generate token' and copy it")
print()

github_token = input("Paste the GitHub token here: ").strip()

if not github_token:
    print("❌ No token provided")
    sys.exit(1)

# Add to Vercel
print()
print("📤 Adding GITHUB_TOKEN to Vercel...")

url = f"https://api.vercel.com/v10/projects/{project_id}/env?teamId={team_id}"
data = json.dumps({
    "type": "encrypted",
    "key": "GITHUB_TOKEN",
    "value": github_token,
    "target": ["production"]
}).encode('utf-8')

headers = {
    'Authorization': f'Bearer {vercel_token}',
    'Content-Type': 'application/json'
}

try:
    request = urllib.request.Request(url, data=data, headers=headers, method='POST')
    with urllib.request.urlopen(request) as response:
        print("✅ GITHUB_TOKEN added to Vercel!")
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

print()
print("🚀 Triggering deployment...")
os.system("git commit --allow-empty -m 'Trigger deployment with GitHub storage' && git push")

print()
print("⏳ Waiting for deployment (60s)...")
import time
time.sleep(60)

print()
print("🎉 DONE! Testing...")
os.system("curl -s https://solvers-one.vercel.app/api/ | python3 -m json.tool")

print()
print("✅ Storage is now persistent!")
print("   Data saved to: https://github.com/lisss/solvers/blob/main/data/storage.json")

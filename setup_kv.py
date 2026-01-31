#!/usr/bin/env python3
"""
This script creates a Vercel KV database and links it to your project.
It uses the Vercel REST API.
"""
import os
import sys
import json
import subprocess

# Get project info
with open('.vercel/project.json', 'r') as f:
    project = json.load(f)

project_id = project['projectId']
team_id = project['orgId']

print(f"📦 Project ID: {project_id}")
print(f"👥 Team ID: {team_id}")

# Get Vercel token from CLI auth or environment
vercel_token = os.environ.get('VERCEL_TOKEN')

if not vercel_token:
    # Try to get from Vercel CLI auth file
    auth_file = os.path.expanduser('~/Library/Application Support/com.vercel.cli/auth.json')
    if os.path.exists(auth_file):
        with open(auth_file, 'r') as f:
            auth_data = json.load(f)
            vercel_token = auth_data.get('token')
    
if not vercel_token:
    print("❌ No Vercel token found. Please run 'vercel login' first.")
    sys.exit(1)

print("\n🚀 Creating Vercel KV database...")

# Create KV database
import urllib.request
import urllib.error

# Create the KV store
create_url = f"https://api.vercel.com/v1/storage/kv/stores"
create_data = json.dumps({
    "name": "solvers-kv"
}).encode('utf-8')

create_headers = {
    'Authorization': f'Bearer {vercel_token}',
    'Content-Type': 'application/json'
}

if team_id:
    create_url += f"?teamId={team_id}"

try:
    create_req = urllib.request.Request(create_url, data=create_data, headers=create_headers, method='POST')
    with urllib.request.urlopen(create_req) as response:
        kv_store = json.loads(response.read().decode('utf-8'))
        store_id = kv_store['id']
        print(f"✅ Created KV store: {store_id}")
except urllib.error.HTTPError as e:
    error_body = e.read().decode('utf-8')
    print(f"❌ Error creating KV store: {e.code}")
    print(f"   {error_body}")
    sys.exit(1)

# Link KV to project
link_url = f"https://api.vercel.com/v1/projects/{project_id}/link"
link_data = json.dumps({
    "type": "kv",
    "storeId": store_id
}).encode('utf-8')

link_headers = {
    'Authorization': f'Bearer {vercel_token}',
    'Content-Type': 'application/json'
}

if team_id:
    link_url += f"?teamId={team_id}"

try:
    link_req = urllib.request.Request(link_url, data=link_data, headers=link_headers, method='POST')
    with urllib.request.urlopen(link_req) as response:
        result = json.loads(response.read().decode('utf-8'))
        print(f"✅ Linked KV to project")
        print(f"\n🎉 SUCCESS! KV database is ready.")
        print(f"\n📝 Next: Deploy to activate it")
        print(f"   Run: git push")
except urllib.error.HTTPError as e:
    error_body = e.read().decode('utf-8')
    print(f"❌ Error linking KV to project: {e.code}")
    print(f"   {error_body}")
    sys.exit(1)

#!/usr/bin/env python
"""
Interactive Supabase Key Validator
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv

load_dotenv()

print("=" * 70)
print("SUPABASE KEY VALIDATOR")
print("=" * 70)

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

print("\n📋 Current Configuration:")
print("-" * 70)
print(f"URL: {url}")
print(f"API Key: {key}")
print(f"Service Role: {service_key[:20]}...***" if service_key else "NOT SET")

print("\n❓ To Fix the 'Invalid API Key' Error:")
print("-" * 70)
print("""
1. Open https://app.supabase.com in your browser
2. Sign in to your account
3. Select project: 'dpicyiiuqgenkdaemkvz'
4. Click 'Settings' (bottom left)
5. Click 'API' tab
6. You should see:
   
   PROJECT URL:
   [shows your project URL]
   
   API KEYS:
   ┌─ anon [public]
   │  sb_publishable_XXXXX
   │
   └─ service_role [secret]
      sb_secret_XXXXX

7. Copy EXACTLY as shown (including spaces/underscores)
8. Paste here or update .env file manually

""")

print("=" * 70)

# Attempt import and simple test
print("\n🔍 Attempting Raw Connection Test...")
print("-" * 70)

try:
    from supabase import create_client, Client
    
    print("Creating client instance...")
    client = create_client(url, key)
    print("✓ Client instance created")
    
    # Try to get user
    try:
        session = client.auth.get_session()
        print("✓ Auth session checked")
    except Exception as e:
        print(f"⚠ Auth: {str(e)[:80]}")
    
    # Try simple REST call
    print("\nTrying REST endpoint...")
    import requests
    headers = {
        "apikey": key,
        "Content-Type": "application/json"
    }
    
    resp = requests.get(
        f"{url}/rest/v1/?select=*",
        headers=headers,
        timeout=5
    )
    
    print(f"Response Status: {resp.status_code}")
    if resp.status_code == 401:
        print("❌ API KEY IS INVALID (401 Unauthorized)")
    elif resp.status_code == 200:
        print("✅ API KEY IS VALID!")
    else:
        print(f"Got status {resp.status_code}: {resp.text[:200]}")
        
except Exception as e:
    print(f"Error: {str(e)[:150]}")

print("\n" + "=" * 70)

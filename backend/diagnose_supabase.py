#!/usr/bin/env python
"""
Diagnostic script for Supabase connection issues
"""

import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

print("=" * 70)
print("SUPABASE CREDENTIALS DIAGNOSTIC")
print("=" * 70)

print("\n📋 Environment Variables:")
print("-" * 70)

supabase_url = os.getenv("SUPABASE_URL", "NOT SET")
supabase_key = os.getenv("SUPABASE_KEY", "NOT SET")
supabase_service_role = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "NOT SET")

print(f"SUPABASE_URL: {supabase_url}")
print(f"SUPABASE_KEY: {supabase_key[:30]}...***" if supabase_key != "NOT SET" else "NOT SET")
print(f"SUPABASE_SERVICE_ROLE_KEY: {'SET' if supabase_service_role != 'NOT SET' else 'NOT SET'}")

print("\n🔍 Key Analysis:")
print("-" * 70)

if supabase_key != "NOT SET":
    if supabase_key.startswith("sb_publishable_"):
        print("✓ Using Publishable Key (for frontend/public access)")
    elif supabase_key.startswith("sb_"):
        print("⚠ Using Supabase key (format unclear)")
    else:
        print("❌ Key format not recognized")

if supabase_service_role != "NOT SET":
    if supabase_service_role.startswith("sb_secret_"):
        print("✓ Service Role Key present (for backend/admin access)")
    else:
        print("⚠ Service Role Key format unclear")

print("\n⚙️ Recommended Configuration:")
print("-" * 70)
print("""
For your backend (FastAPI), you should use:
1. SUPABASE_URL: Your project URL
2. SUPABASE_KEY: Your ANON KEY (public/publishable key) - used for API calls
3. SUPABASE_SERVICE_ROLE_KEY: Your SECRET KEY - used for admin operations

The error "Invalid API key" suggests:
1. The key might be expired or revoked
2. The key type might not match the operation
3. The key might have permission restrictions

Next steps:
1. Log in to your Supabase dashboard
2. Go to Settings > API
3. Verify you have both:
   - anon (public) key
   - service_role (secret) key
4. Copy the correct keys and update .env
""")

print("\n📝 Current .env file location:")
print(f"   {env_path}")
print(f"   File exists: {env_path.exists()}")

print("\n" + "=" * 70)

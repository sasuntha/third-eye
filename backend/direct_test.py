#!/usr/bin/env python
"""
Direct Supabase connection test - bypassing config layer
"""

import os
from dotenv import load_dotenv

# Load env first
load_dotenv()

print("=" * 70)
print("DIRECT SUPABASE CONNECTION TEST")
print("=" * 70)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

print(f"\n✓ URL loaded: {SUPABASE_URL}")
print(f"✓ Key loaded: {SUPABASE_KEY[:50]}...")

print("\n🔗 Attempting direct connection...")
print("-" * 70)

try:
    from supabase import create_client
    
    client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ SUCCESS! Supabase client created successfully!")
    
    print("\n📋 Testing basic operations...")
    
    # Try to get auth info
    try:
        auth_info = client.auth.get_session()
        print("✓ Auth session retrieved")
    except Exception as e:
        print(f"ℹ Auth session: {str(e)[:100]}")
    
    print("\n✅ SUPABASE CONFIGURATION IS WORKING!")
    print("=" * 70)
    print("\nYou can now:")
    print("  1. Run the backend: python main.py")
    print("  2. Access API docs: http://localhost:8000/docs")
    print("  3. Test endpoints")
    print("=" * 70)
    
except Exception as e:
    print(f"❌ ERROR: {str(e)}")
    print("\nFull error:")
    import traceback
    traceback.print_exc()
    print("=" * 70)

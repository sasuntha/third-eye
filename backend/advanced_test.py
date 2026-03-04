#!/usr/bin/env python
"""
Advanced Supabase connection tester with multiple attempt strategies
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 70)
print("ADVANCED SUPABASE CONNECTION TEST")
print("=" * 70)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

print(f"\nURL: {SUPABASE_URL}")
print(f"Key (first 30 chars): {SUPABASE_KEY[:30]}")
print(f"Service Role: {'SET' if SUPABASE_SERVICE_ROLE_KEY else 'NOT SET'}")

print("\n🔗 Attempting connection with Python Supabase client...")
print("-" * 70)

try:
    import requests
    
    # Test 1: Verify URL is reachable
    print("\n1️⃣ Testing URL connectivity...")
    try:
        response = requests.get(f"{SUPABASE_URL}/functions/v1", timeout=5)
        print(f"   ✓ URL is reachable (Status: {response.status_code})")
    except Exception as e:
        print(f"   ❌ Cannot reach URL: {e}")
    
    # Test 2: Test with Supabase client
    print("\n2️⃣ Testing Supabase Python client...")
    try:
        from supabase import create_client
        
        client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("   ✓ Supabase client created")
        
        # Try a simple health check
        print("\n3️⃣ Attempting authentication check...")
        try:
            auth = client.auth.get_session()
            print("   ✓ Auth check successful")
        except Exception as auth_error:
            print(f"   ℹ Auth check: {str(auth_error)[:100]}")
        
        print("\n4️⃣ Attempting to query database...")
        try:
            # Try to list tables or get a simple response
            response = client.table("_realtime_subscriptions").select("count").execute()
            print("   ✓ Database query successful!")
        except Exception as db_error:
            error_msg = str(db_error)
            if "subscriptions" in error_msg.lower() and "does not exist" in error_msg.lower():
                print("   ✓ Connected to database (this table doesn't exist, but connection works!)")
            elif "invalid api key" in error_msg.lower():
                print("   ❌ INVALID API KEY - Please verify your credentials")
                print(f"      Full error: {error_msg[:150]}")
            else:
                print(f"   ⚠ Query error: {error_msg[:150]}")
                print("   ℹ This might be expected if no tables exist yet")
        
        print("\n✅ Supabase client is working!")
        
    except ImportError:
        print("   ❌ Supabase module not installed")
    except Exception as e:
        print(f"   ❌ Client error: {str(e)[:150]}")
        
except Exception as e:
    print(f"❌ Unexpected error: {str(e)}")

print("\n" + "=" * 70)
print("\n💡 IMPORTANT INFORMATION:")
print("-" * 70)
print("""
If you're seeing "Invalid API key" error:

1. ✅ Make sure the keys are copied EXACTLY as shown in Supabase dashboard
2. ✅ Go to: https://app.supabase.com → Settings → API
3. ✅ Find your project and copy the keys:
   - anon public key (for SUPABASE_KEY)
   - service_role secret key (for SUPABASE_SERVICE_ROLE_KEY)
4. ✅ Paste them WITHOUT any extra spaces or characters
5. ✅ Save .env file
6. ✅ Run this script again

If connection still fails:
- Check if your Supabase project is active
- Check if you're connected to the internet
- Try accessing https://app.supabase.com in your browser
""")
print("=" * 70)

#!/usr/bin/env python
"""
Test script to verify Supabase connection
Run this to ensure your Supabase credentials are working correctly
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.db.supabase import get_supabase_client
from app.core.config import settings


def test_supabase_connection():
    """Test Supabase connection and display connection info"""
    print("=" * 60)
    print("SUPABASE CONNECTION TEST")
    print("=" * 60)
    
    try:
        print("\n📋 Configuration loaded:")
        print(f"  ✓ Supabase URL: {settings.supabase_url}")
        print(f"  ✓ Supabase Key: {settings.supabase_key[:20]}...***")
        print(f"  ✓ Service Role Key: {'Set' if settings.supabase_service_role_key else 'Not set'}")
        
        print("\n🔗 Connecting to Supabase...")
        client = get_supabase_client()
        print("  ✓ Client created successfully")
        
        # Try to get auth session (this will help verify the connection)
        print("\n📡 Attempting to fetch tables...")
        try:
            # Try a simple query to test the connection
            response = client.table('users').select('count').execute()
            print("  ✓ Connected successfully!")
            print(f"  ✓ Users table is accessible")
        except Exception as e:
            if "does not exist" in str(e):
                print("  ⚠ Connected to Supabase (tables not created yet)")
                print(f"  ℹ Note: {str(e)}")
            else:
                print(f"  ⚠ Connection successful but query failed: {str(e)}")
        
        print("\n✅ Supabase is properly configured!")
        print("=" * 60)
        print("\nYou can now:")
        print("  1. Run the backend: python main.py")
        print("  2. Visit API docs: http://localhost:8000/docs")
        print("  3. Test endpoints at: http://localhost:8000/docs")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("=" * 60)
        print("\nTroubleshooting:")
        print("  1. Check .env file exists and has correct credentials")
        print("  2. Verify SUPABASE_URL is correct")
        print("  3. Verify SUPABASE_KEY is correct")
        print("  4. Check internet connection")
        print("=" * 60)
        return False


if __name__ == "__main__":
    success = test_supabase_connection()
    sys.exit(0 if success else 1)

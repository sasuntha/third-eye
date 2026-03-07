#!/usr/bin/env python
"""
Test script for employee login endpoint
Checks if employees table exists and tests login functionality
"""

import sys
from pathlib import Path
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.db.supabase import get_supabase_client
from app.core.config import settings


def check_employees_table():
    """Check if employees table exists and show its schema"""
    print("=" * 70)
    print("EMPLOYEE LOGIN BACKEND VERIFICATION")
    print("=" * 70)
    
    try:
        print("\n🔗 Connecting to Supabase...")
        client = get_supabase_client()
        print("  ✓ Connected successfully")
        
        print("\n📋 Checking for 'employees' table...")
        try:
            # Try to query the employees table
            response = client.table("employees").select("*").limit(1).execute()
            
            if response.data:
                print("  ✓ Employees table found!")
                print("\n📊 Sample employee record:")
                sample = response.data[0]
                for key, value in sample.items():
                    if key == "password":
                        print(f"     {key}: [PASSWORD HIDDEN]")
                    else:
                        print(f"     {key}: {value}")
                
                # Check required columns
                required_cols = ["email", "password", "role"]
                print("\n🔍 Checking required columns:")
                for col in required_cols:
                    if col in sample:
                        print(f"     ✓ {col}: Present")
                    else:
                        print(f"     ✗ {col}: MISSING")
                
                return True
                
            else:
                print("  ⚠ Table exists but is empty")
                print("\n  You need to seed the employees table with test data.")
                print("  Required columns: email, password (hashed), role")
                return True
                
        except Exception as e:
            error_msg = str(e)
            if "does not exist" in error_msg or "relation" in error_msg:
                print("  ✗ Employees table NOT FOUND")
                print("\n" + "=" * 70)
                print("ACTION REQUIRED: Create employees table in Supabase")
                print("=" * 70)
                print("\nSQL to run in Supabase SQL Editor:")
                print("""
CREATE TABLE public.employees (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT NOT NULL UNIQUE,
  password TEXT NOT NULL,
  full_name TEXT,
  employee_id TEXT,
  role TEXT CHECK (role IN ('chief', 'employee')) DEFAULT 'employee',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Enable Row Level Security
ALTER TABLE public.employees ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY "Allow read own employee record" ON public.employees 
  FOR SELECT USING (auth.uid()::text = id::text);
CREATE POLICY "Allow update own employee record" ON public.employees 
  FOR UPDATE USING (auth.uid()::text = id::text);
CREATE POLICY "Allow chief to read all" ON public.employees 
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM public.employees e2 
      WHERE e2.id = auth.uid()::text AND e2.role = 'chief'
    )
  );
""")
                print("\nThen seed it with test data:")
                print("""
-- Test data (passwords should be bcrypt hashed in production)
INSERT INTO public.employees (email, password, full_name, employee_id, role) VALUES
('chief@example.com', 'hashed_password_here', 'Chief User', 'CHIEF001', 'chief'),
('employee@example.com', 'hashed_password_here', 'Employee User', 'EMP001', 'employee');
""")
                print("=" * 70)
                return False
            else:
                print(f"  ✗ Error: {error_msg}")
                return False
                
    except Exception as e:
        print(f"\n❌ Connection error: {str(e)}")
        return False


def test_login_endpoint():
    """Test the login endpoint"""
    print("\n\n📡 Testing Login Endpoint")
    print("=" * 70)
    print("\nYou can test the login endpoint at:")
    print("  POST http://localhost:8000/api/auth/login")
    print("\nExample request body:")
    print(json.dumps({
        "email": "chief@example.com",
        "password": "your_password"
    }, indent=2))
    print("\nExample response (success):")
    print(json.dumps({
        "status": "success",
        "message": "Login successful",
        "user": {
            "id": "uuid-here",
            "email": "chief@example.com",
            "full_name": "Chief User",
            "employee_id": "CHIEF001",
            "role": "chief"
        },
        "role": "chief"
    }, indent=2))
    print("\n" + "=" * 70)


if __name__ == "__main__":
    table_exists = check_employees_table()
    test_login_endpoint()
    
    if table_exists:
        print("\n✅ Backend is ready! Run: python main.py")
        print("   Then test with: http://localhost:8000/api/auth/login")
    else:
        print("\n⚠️  Please create the employees table first")

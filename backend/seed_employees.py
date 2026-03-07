#!/usr/bin/env python
"""
Utility script to hash passwords and seed employee test data
Run this to create test employees in the database
"""

import sys
from pathlib import Path
from passlib.context import CryptContext

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.db.supabase import get_supabase_client

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)


def seed_test_employees():
    """Seed test employee data to the database"""
    print("=" * 70)
    print("EMPLOYEE DATABASE SEEDING")
    print("=" * 70)
    
    try:
        client = get_supabase_client()
        print("\n✓ Connected to Supabase")
        
        # Test data to seed
        test_employees = [
            {
                "email": "chief@example.com",
                "password": "chief123",  # Will be hashed
                "name": "Chief Administrator",
                "employee_id": "CHIEF001",
                "role": "chief"
            },
            {
                "email": "employee@example.com",
                "password": "employee123",  # Will be hashed
                "name": "John Employee",
                "employee_id": "EMP001",
                "role": "employee"
            },
            {
                "email": "jane@example.com",
                "password": "jane123",  # Will be hashed
                "name": "Jane Doe",
                "employee_id": "EMP002",
                "role": "employee"
            }
        ]
        
        print("\n📝 Preparing test employees:")
        employees_to_insert = []
        
        for emp in test_employees:
            hashed_pwd = hash_password(emp["password"])
            emp_data = {
                "email": emp["email"],
                "password": hashed_pwd,
                "name": emp["name"],
                "employee_id": emp["employee_id"],
                "role": emp["role"]
            }
            employees_to_insert.append(emp_data)
            print(f"  ✓ {emp['email']} ({emp['role']})")
        
        print("\n🚀 Inserting into database...")
        response = client.table("employees").insert(employees_to_insert).execute()
        
        if response.data:
            print(f"  ✓ Successfully inserted {len(response.data)} employees")
            print("\n✅ Test employees created!")
            print("\nYou can now test login with:")
            print("  Email: chief@example.com")
            print("  Password: chief123")
            print("\n  Or:")
            print("  Email: employee@example.com")
            print("  Password: employee123")
        else:
            print("  ⚠ No response data returned")
            
    except Exception as e:
        error_str = str(e)
        if "duplicate key" in error_str or "already exists" in error_str:
            print(f"  ⚠ Employees already exist in database")
            print("  ℹ Skipping insert to avoid duplicates")
        else:
            print(f"  ❌ Error: {error_str}")


def generate_password_hash():
    """Generate a password hash for manual insertion"""
    print("\n" + "=" * 70)
    print("PASSWORD HASH GENERATOR")
    print("=" * 70)
    
    password = input("\nEnter password to hash: ")
    if not password:
        print("No password entered")
        return
    
    hashed = hash_password(password)
    print(f"\nHashed password:\n{hashed}")
    print("\nUse this in your INSERT statements:")
    print(f"INSERT INTO public.employees (email, password, full_name, employee_id, role)")
    print(f"VALUES ('user@example.com', '{hashed}', 'User Name', 'EMP123', 'employee');")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--hash":
        generate_password_hash()
    else:
        seed_test_employees()
        print("\n" + "=" * 70)
        print("To generate a password hash manually, run:")
        print("  python seed_employees.py --hash")
        print("=" * 70)

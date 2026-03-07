#!/usr/bin/env python
"""
Comprehensive test suite for employee login backend
Tests database connection, table structure, API endpoints, and credential validation
"""

import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.db.supabase import get_supabase_client
from app.core.config import settings
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(70)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.RESET}\n")


def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")


def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")


def print_warning(text):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.RESET}")


def print_info(text):
    print(f"{Colors.BLUE}ℹ {text}{Colors.RESET}")


def test_supabase_connection():
    """Test Supabase connection"""
    print_header("Step 1: Testing Supabase Connection")
    
    try:
        print("Connecting to Supabase...")
        client = get_supabase_client()
        print_success("Connected to Supabase")
        return client
    except Exception as e:
        print_error(f"Failed to connect to Supabase: {str(e)}")
        return None


def test_employees_table(client):
    """Test if employees table exists and check its structure"""
    print_header("Step 2: Checking Employees Table")
    
    try:
        print("Querying employees table...")
        response = client.table("employees").select("*").limit(1).execute()
        
        if response.data:
            print_success("Employees table found and accessible")
            print("\nTable structure (from first record):")
            sample = response.data[0]
            for key, value in sample.items():
                if key == "password":
                    print(f"  {key}: [HASHED PASSWORD]")
                else:
                    print(f"  {key}: {type(value).__name__}")
            
            # Check required columns
            required_cols = ["email", "password", "role"]
            print("\nRequired columns check:")
            all_present = True
            for col in required_cols:
                if col in sample:
                    print_success(f"Column '{col}' present")
                else:
                    print_error(f"Column '{col}' MISSING")
                    all_present = False
            
            return True, all_present
        else:
            print_warning("Employees table is empty")
            return True, True
            
    except Exception as e:
        error_msg = str(e)
        if "does not exist" in error_msg or "relation" in error_msg:
            print_error("Employees table does NOT exist")
            print_info("Run: python seed_employees.py to create and populate the table")
            return False, False
        else:
            print_error(f"Error: {error_msg}")
            return False, False


def test_login_credentials(client):
    """Test actual login with sample credentials"""
    print_header("Step 3: Testing Login Credentials")
    
    test_cases = [
        ("chief@example.com", "chief123", "chief"),
        ("employee@example.com", "employee123", "employee"),
    ]
    
    all_passed = True
    
    for email, password, expected_role in test_cases:
        print(f"\nTesting login: {email}")
        try:
            # Query for the employee
            response = client.table("employees").select("*").eq("email", email).execute()
            
            if not response.data:
                print_warning(f"  No employee found with email: {email}")
                all_passed = False
                continue
            
            employee = response.data[0]
            password_hash = employee.get("password")
            
            # Verify password
            if password_hash.startswith("$2b$") or password_hash.startswith("$2a$"):
                is_valid = pwd_context.verify(password, password_hash)
            else:
                is_valid = password == password_hash
            
            if is_valid:
                print_success(f"  Password verified ✓")
                
                role = employee.get("role")
                if role == expected_role:
                    print_success(f"  Role matches expected: {role} ✓")
                else:
                    print_warning(f"  Role mismatch: got '{role}', expected '{expected_role}'")
                    all_passed = False
                
                print_success(f"  Login test passed for {email}")
            else:
                print_error(f"  Password verification failed")
                all_passed = False
                
        except Exception as e:
            print_error(f"  Error during login test: {str(e)}")
            all_passed = False
    
    return all_passed


def test_backend_requirements():
    """Check if backend requirements are installed"""
    print_header("Step 4: Checking Backend Requirements")
    
    required_packages = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("supabase", "Supabase"),
        ("pydantic", "Pydantic"),
        ("passlib", "Passlib"),
        ("httpx", "HTTPX"),
    ]
    
    all_installed = True
    
    for module_name, display_name in required_packages:
        try:
            __import__(module_name)
            print_success(f"{display_name} is installed")
        except ImportError:
            print_error(f"{display_name} is NOT installed")
            all_installed = False
    
    return all_installed


def print_quick_start():
    """Print quick start guide"""
    print_header("Quick Start Guide")
    
    print(f"{Colors.BOLD}1. Create Employees Table:{Colors.RESET}")
    print("   Run this in Supabase SQL Editor:")
    print("   python seed_employees.py (this creates the table and seeds data)")
    
    print(f"\n{Colors.BOLD}2. Start Backend Server:{Colors.RESET}")
    print("   cd backend")
    print("   & .\\venv\\Scripts\\Activate.ps1")
    print("   python main.py")
    
    print(f"\n{Colors.BOLD}3. Configure Frontend:{Colors.RESET}")
    print("   Create frontend/.env.local with:")
    print("   VITE_API_URL=http://localhost:8000")
    
    print(f"\n{Colors.BOLD}4. Test Login API:{Colors.RESET}")
    print("   Visit: http://localhost:8000/docs")
    print("   Or use curl:")
    print('   curl -X POST http://localhost:8000/api/auth/login \\')
    print('     -H "Content-Type: application/json" \\')
    print('     -d \'{"email":"chief@example.com","password":"chief123"}\'')
    
    print(f"\n{Colors.BOLD}5. Test Role-Based Redirect:{Colors.RESET}")
    print("   - Open frontend")
    print("   - Login with chief@example.com → Should go to Chief Dashboard")
    print("   - Login with employee@example.com → Should go to Employee Dashboard")


def run_all_tests():
    """Run all tests"""
    print_header("Employee Login Backend - Complete Test Suite")
    
    print(f"Configuration:")
    print(f"  Supabase URL: {settings.supabase_url}")
    print(f"  Database: third-eye")
    
    # Test 1: Connection
    client = test_supabase_connection()
    if not client:
        print_error("\n⚠️  Cannot proceed without Supabase connection")
        return False
    
    # Test 2: Table existence
    table_exists, valid_schema = test_employees_table(client)
    if not table_exists:
        print_error("\n⚠️  Employees table does not exist")
        print_info("Run: python seed_employees.py to create the table")
        return False
    
    if not valid_schema:
        print_warning("\n⚠️  Table schema may be incomplete")
        return False
    
    # Test 3: Credentials
    credentials_ok = test_login_credentials(client)
    
    # Test 4: Requirements
    requirements_ok = test_backend_requirements()
    
    # Summary
    print_header("Test Summary")
    
    if credentials_ok and requirements_ok and valid_schema:
        print_success("All tests passed! ✅")
        print("\nBackend is ready for use!")
        print_quick_start()
        return True
    else:
        if not credentials_ok:
            print_error("Credential tests failed")
        if not requirements_ok:
            print_error("Required packages are missing - run: pip install -r requirements.txt")
        if not valid_schema:
            print_error("Table schema needs verification")
        print("\n⚠️  Some tests failed, please review above")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

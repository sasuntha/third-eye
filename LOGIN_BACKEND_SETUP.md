# Employee Login Backend Setup Guide

This guide explains how to set up and use the new employee database login system.

## Overview

The backend login system validates employee credentials against the `employees` table in Supabase and returns the user's role (chief, employee, or null). Based on the role, the frontend redirects to the appropriate dashboard.

## Backend Setup

### 1. Create the Employees Table

Run the migration in your Supabase SQL Editor:

```sql
-- Create employees table for login authentication
CREATE TABLE IF NOT EXISTS public.employees (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT NOT NULL UNIQUE,
  password TEXT NOT NULL,
  full_name TEXT,
  employee_id TEXT UNIQUE,
  role TEXT CHECK (role IN ('chief', 'employee', NULL)) DEFAULT 'employee',
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Enable Row Level Security
ALTER TABLE public.employees ENABLE ROW LEVEL SECURITY;

-- Create index for faster email lookups
CREATE INDEX IF NOT EXISTS idx_employees_email ON public.employees(email);
CREATE INDEX IF NOT EXISTS idx_employees_role ON public.employees(role);
```

### 2. Populate Test Data

Use the seed script to create test employees:

```bash
# Activate Python environment
cd backend
& .\.venv\Scripts\Activate.ps1

# Run seeder
python seed_employees.py
```

This creates:

- **chief@example.com** / **chief123** (role: chief)
- **employee@example.com** / **employee123** (role: employee)
- **jane@example.com** / **jane123** (role: employee)

**Note:** Passwords are hashed with bcrypt before storage. Never store plain text passwords in production.

### 3. Running the Backend

```bash
# From the backend directory
cd backend
& .\.venv\Scripts\Activate.ps1

# Run the server
python main.py
```

The backend will be available at: `http://localhost:8000`

### 4. Test the Login Endpoint

Visit the interactive API docs:

- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

Or use curl:

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"chief@example.com","password":"chief123"}'
```

Expected response:

```json
{
  "status": "success",
  "message": "Login successful",
  "user": {
    "id": "uuid-string",
    "email": "chief@example.com",
    "full_name": "Chief Administrator",
    "employee_id": "CHIEF001",
    "role": "chief"
  },
  "role": "chief"
}
```

## Frontend Setup

### 1. Configure Environment Variables

Create a [.env.local](../frontend/.env.local) file in the frontend directory:

```env
# Backend API URL
VITE_API_URL=http://localhost:8000
```

Or if using a remote backend:

```env
VITE_API_URL=https://your-api.herokuapp.com
```

### 2. Login Flow

The updated Login page now:

1. Calls the backend `/api/auth/login` endpoint
2. Receives user data and role
3. Stores user session in localStorage
4. Redirects to appropriate dashboard:
   - Role: "chief" → Chief Dashboard
   - Role: "employee" or null → Employee Dashboard

### 3. Session Management

User data is stored in localStorage and persists across page refreshes:

```json
{
  "id": "user-uuid",
  "email": "chief@example.com",
  "full_name": "Chief Administrator",
  "employee_id": "CHIEF001",
  "role": "chief"
}
```

## Login API Endpoint

### POST `/api/auth/login`

**Request Body:**

```json
{
  "email": "string (required)",
  "password": "string (required)"
}
```

**Success Response (200):**

```json
{
  "status": "success",
  "message": "Login successful",
  "user": {
    "id": "uuid",
    "email": "string",
    "full_name": "string",
    "employee_id": "string",
    "role": "chief | employee | null"
  },
  "role": "chief | employee"
}
```

**Error Response (401):**

```json
{
  "detail": "Invalid email or password"
}
```

**Error Response (500):**

```json
{
  "detail": "Login failed: error message"
}
```

## Password Hashing

### Generate Password Hashes

Use the seeder script to generate bcrypt hashes:

```bash
python seed_employees.py --hash
```

Then enter your password and copy the hash to use in INSERT statements.

### Manual Password Hash in SQL

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
hashed = pwd_context.hash("your_password")
print(hashed)
```

Then use in SQL:

```sql
INSERT INTO public.employees (email, password, full_name, employee_id, role)
VALUES ('user@example.com', 'your_bcrypt_hash_here', 'User Name', 'EMP123', 'employee');
```

## Role-Based Redirect

| Role     | Redirect To                     |
| -------- | ------------------------------- |
| chief    | `/chief-dashboard`              |
| employee | `/employee-dashboard`           |
| null     | `/employee-dashboard` (default) |

## Testing Checklist

- [ ] Employees table created in Supabase
- [ ] Test data seeded with hashed passwords
- [ ] Backend running on localhost:8000
- [ ] Frontend .env.local configured with API URL
- [ ] Login endpoint responds with user data and role
- [ ] Front-end redirects to Chief Dashboard when role="chief"
- [ ] Frontend redirects to Employee Dashboard when role="employee"
- [ ] Session persists after page refresh
- [ ] Logout clears localStorage

## Troubleshooting

### "Employees table NOT FOUND" error

Run the migration in Supabase SQL Editor to create the table.

### "Invalid email or password"

- Verify email exists in employees table
- Check password is correct (case-sensitive)
- Ensure password in database is bcrypt hashed, not plain text

### Frontend not redirecting

- Check browser console for errors
- Verify API URL in .env.local matches backend URL
- Check network tab to see if login request succeeds
- Clear localStorage and try again

### Session not persisting

- Verify user data is being stored in localStorage
- Check that AuthProvider is wrapping the app in App.tsx
- Clear browser cache and localStorage

## Security Notes

⚠️ **Important for Production:**

1. **Passwords must be hashed** - Use bcrypt (already configured)
2. **Use HTTPS** - Never send credentials over plain HTTP
3. **Add CORS restrictions** - Limit to your frontend domain
4. **Rate limiting** - Add rate limiting to login endpoint
5. **Token/Session expiry** - Implement token expiration
6. **Environment variables** - Store secrets securely, never in version control
7. **SQL injection** - Use parameterized queries (already handled by Supabase SDK)

## File Locations

- Backend auth routes: [backend/app/api/routes/auth.py](../backend/app/api/routes/auth.py)
- Frontend login page: [frontend/src/pages/Login.tsx](../frontend/src/pages/Login.tsx)
- Auth hook: [frontend/src/hooks/useAuth.tsx](../frontend/src/hooks/useAuth.tsx)
- Seed script: [backend/seed_employees.py](../backend/seed_employees.py)
- Migration: [supabase/migrations/20260305_create_employees_table.sql](../supabase/migrations/20260305_create_employees_table.sql)

## Next Steps

1. Create the employees table in Supabase
2. Seed test data
3. Start the backend
4. Configure frontend .env
5. Test login functionality
6. Add role-specific features to dashboards
7. Implement logout functionality
8. Add password reset feature (optional)

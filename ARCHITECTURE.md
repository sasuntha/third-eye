# Backend Login System - Architecture

## Complete System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     THIRD-EYE LOGIN SYSTEM                      │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                      FRONTEND (React/TypeScript)                 │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Login Page (src/pages/Login.tsx)                       │    │
│  ├─────────────────────────────────────────────────────────┤    │
│  │  ┌─────────────┐  ┌─────────────┐                       │    │
│  │  │ Email Input │  │Password Input│  ┌──────────────┐   │    │
│  │  └──────┬──────┘  └──────┬──────┘   │ Sign In Btn  │   │    │
│  │         └───────────┬────────────────┤  (disabled)  │   │    │
│  │                     │                └──────────────┘   │    │
│  └─────────────────────┼─────────────────────────────────┘    │
│                        │ POST /api/auth/login                   │
│                        │ {email, password}                      │
│                        ▼                                        │
│  ┌──────────────────────────────────────────────────────┐      │
│  │  useAuth Hook (src/hooks/useAuth.tsx)               │      │
│  ├──────────────────────────────────────────────────────┤      │
│  │  • Manages user state from localStorage              │      │
│  │  • Tracks role (chief/employee/null)                │      │
│  │  • Provides signOut() for logout                     │      │
│  └──────────────────────────────────────────────────────┘      │
│                        ▲                                        │
│                        │ user, role, fullName                   │
│                        │                                        │
│  ┌──────────────────────┼──────────────────────────────┐       │
│  │  Routes (src/App.tsx)│                              │       │
│  ├───────────────────────────────────────────────────┤       │
│  │ role === "chief" → /chief-dashboard ──────┐       │       │
│  │ role === "employee" → /employee-dashboard  │       │       │
│  │ !user → / (Login Page)                     │       │       │
│  └────────────────────────────────────────────┼───────┘       │
│                                               │                │
│                                               ▼                │
│                        ┌──────────────────────────────┐        │
│                        │  Chief/Employee Dashboard    │        │
│                        │  (with DashboardLayout)      │        │
│                        │  • Shows user info           │        │
│                        │  • Shows role                │        │
│                        │  • Logout button             │        │
│                        └──────────────────────────────┘        │
└──────────────────────────────────────────────────────────────────┘

                             │ JSON Response
                             │ {status, user, role}
                             ▼

┌──────────────────────────────────────────────────────────────────┐
│                    BACKEND (FastAPI/Python)                      │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Auth Routes (app/api/routes/auth.py)                  │    │
│  ├─────────────────────────────────────────────────────────┤    │
│  │                                                          │    │
│  │  POST /api/auth/login                                  │    │
│  │  ├─ Receive: {email, password}                         │    │
│  │  ├─ Query: SELECT * FROM employees WHERE email = ?     │    │
│  │  ├─ Verify: bcrypt.verify(password, db_hash)           │    │
│  │  ├─ Extract: role from database                        │    │
│  │  └─ Return: {status, user, role}                       │    │
│  │                                                          │    │
│  │  POST /api/auth/logout                                 │    │
│  │  └─ Session cleanup                                    │    │
│  │                                                          │    │
│  └──────────────────────────┬──────────────────────────────┘    │
│                             │ Query                              │
│                             ▼                                    │
│  ┌──────────────────────────────────────────────────────┐       │
│  │  Supabase Client (app/db/supabase.py)               │       │
│  ├──────────────────────────────────────────────────────┤       │
│  │  • Create client from config                         │       │
│  │  • Handle database queries                           │       │
│  │  • Manage connections                                │       │
│  └──────────────────────┬───────────────────────────────┘       │
│                         │ HTTP/HTTPS                             │
│                         ▼                                        │
│    ┌────────────────────────────────────────────┐              │
│    │  Config (app/core/config.py)               │              │
│    ├────────────────────────────────────────────┤              │
│    │  • SUPABASE_URL                            │              │
│    │  • SUPABASE_KEY (from .env)                │              │
│    │  • Other settings                          │              │
│    └────────────────────────────────────────────┘              │
│                         │                                       │
└─────────────────────────┼───────────────────────────────────────┘
                          │ HTTPS
                          ▼

┌──────────────────────────────────────────────────────────────────┐
│              SUPABASE (Database as a Service)                    │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Employees Table                                         │   │
│  ├──────────────────────────────────────────────────────────┤   │
│  │  ┌──────────────────────────────────────────────────┐    │   │
│  │  │ id (UUID primary key)                            │    │   │
│  │  │ email (TEXT, UNIQUE, INDEXED)                    │    │   │
│  │  │ password (TEXT, bcrypt hashed)                   │    │   │
│  │  │ full_name (TEXT)                                 │    │   │
│  │  │ employee_id (TEXT, UNIQUE)                       │    │   │
│  │  │ role (chief | employee | null)                   │    │   │
│  │  │ is_active (BOOLEAN)                              │    │   │
│  │  │ created_at (TIMESTAMP)                           │    │   │
│  │  │ updated_at (TIMESTAMP)                           │    │   │
│  │  └──────────────────────────────────────────────────┘    │   │
│  │                                                            │   │
│  │  Indexes:                                                 │   │
│  │  ├─ idx_employees_email (for fast lookups)               │   │
│  │  └─ idx_employees_role (for filtering)                   │   │
│  │                                                            │   │
│  │  Row Level Security:                                      │   │
│  │  ├─ Users see own record                                 │   │
│  │  └─ Chiefs see all records                               │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  Sample Data:                                                    │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ chief@example.com     | bcrypt_hash | Chief Admin | chief   │ │
│  │ employee@example.com  | bcrypt_hash | John Emp   | employee │ │
│  │ jane@example.com      | bcrypt_hash | Jane Doe   | employee │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

## Data Flow Sequence Diagram

```
User              Frontend          Backend           Supabase
 │                   │                 │                 │
 │  1. Enter email   │                 │                 │
 │  & password       │                 │                 │
 ├─────────────────➤ │                 │                 │
 │                   │ 2. POST /login  │                 │
 │                   │ {email,password}│                 │
 │                   ├────────────────➤│                 │
 │                   │                 │ 3. Query       │
 │                   │                 │ WHERE email=?  │
 │                   │                 ├────────────────➤│
 │                   │                 │                 │
 │                   │                 │ 4. Return     │
 │                   │                 │ employee data  │
 │                   │                 │‹────────────────┤
 │                   │                 │                 │
 │                   │                 │ 5. Verify:     │
 │                   │                 │ password hash  │
 │                   │                 │ (local)       │
 │                   │                 │                 │
 │                   │ 6. Response      │                 │
 │                   │ {status, role}   │                 │
 │                   │‹────────────────┤                 │
 │                   │                 │                 │
 │ 7. Store session  │                 │                 │
 │ in localStorage   │                 │                 │
 │‹─────────────────┤                 │                 │
 │                   │                 │                 │
 │ 8. Redirect to    │                 │                 │
 │ role dashboard    │                 │                 │
 │‹─────────────────┤                 │                 │
```

## Authentication Decision Tree

```
                         ┌─────────────────┐
                         │ User Login Form │
                         └────────┬────────┘
                                  │
                    ┌─────────────▼──────────────┐
                    │ Submit Email & Password    │
                    └─────────────┬──────────────┘
                                  │
                    ┌─────────────▼──────────────┐
                    │ Query: Email in DB?        │
                    └──┬──────────────────────┬──┘
                 ✔Yes│                       │No
                      │                       │
                     ┌▼──────────┐        ┌──▼────────────────┐
                     │ Found     │        │ Error: Invalid    │
                     │ Employee  │        │ email or password │
                     └─┬────┬────┘        └───────────────────┘
                       │    │
            ┌──────────▼┐  ┌┴──────────────────┐
            │Check:     └──▶  bcrypt.verify()   │
            │Password?         password hash    │
            │           ┌──┬──────────────────┐
            └─┬────┬────┘  │                  │
       ✔OK │  │Na │        │                  │
          │  │   │         │                  │
         ┌▼──┴─┐ │      ✔Match?.No
         │Get  │ │         │  │
         │Role │ │     ┌───▼──┴──────────────┐
         │from │ │     │ Error: Invalid      │
         │DB   │ │     │ email or password  │
         └──┬─┬┤ │     └───────────────────┘
      ┌─────▼─┴─▼──────────┐
      │  Check role type   │
      └──┬──┬──┬───────────┘
         │  │  │
    chief│ emp│ null
        │  │  │
      ┌─▼─▼──▼─────┐
      │ Return:    │
      │ status:ok  │
      │ role:*     │
      │ user:{}    │
      └──────┬─────┘
             │
      ┌──────▼──────────────────────┐
      │ Frontend localStorage.set   │
      │ {user, role}                │
      └──────┬──────────────────────┘
             │
    ┌────────▼────────────────┐
    │ Navigate based on role  │
    ├─────────────────────────┤
    │ role="chief"            │
    │    ↓                    │
    │ /chief-dashboard        │
    │                         │
    │ role="employee"         │
    │    ↓                    │
    │ /employee-dashboard     │
    │                         │
    │ role=null (default)     │
    │    ↓                    │
    │ /employee-dashboard     │
    └─────────────────────────┘
```

## Session Management Flow

```
┌────────────────────────────────────────────────────────────┐
│                    SESSION LIFECYCLE                       │
└────────────────────────────────────────────────────────────┘

                  ┌─────────────┐
                  │   Login     │
                  └──────┬──────┘
                         │
         ┌───────────────┴───────────────┐
         │                               │
    ┌────▼──────────────┐        ┌──────▼────────────┐
    │ Successful Login: │        │ Failed Login:     │
    │ ✓ Valid email     │        │ ✗ Invalid email   │
    │ ✓ Valid password  │        │ ✗ Invalid password│
    │ ✓ Role retrieved  │        │ ✗ Show error      │
    └────┬──────────────┘        └──────────────────┘
         │                               │
         │                        Stay on Login Page
         │
    ┌────▼────────────────────────┐
    │ Store in localStorage:      │
    │ {                           │
    │   id: "uuid",               │
    │   email: "user@example.com",│
    │   full_name: "User Name",   │
    │   employee_id: "EMP001",    │
    │   role: "chief"             │
    │ }                           │
    └────┬────────────────────────┘
         │
    ┌────▼──────────────────┐
    │ useAuth Hook reads    │
    │ localStorage          │
    └────┬──────────────────┘
         │
    ┌────▼──────────────────────────────┐
    │ Routes check role:                 │
    │ - Redirect to appropriate          │
    │   dashboard                        │
    └────┬───────────────────────────────┘
         │
    ┌────▼──────────────────────────┐
    │ User at Dashboard              │
    │ ├─ DashboardLayout displays    │
    │ │  full_name and role          │
    │ │                              │
    │ ├─ All pages use useAuth()     │
    │ │                              │
    │ └─ Logout button available     │
    └────┬───────────────────────────┘
         │
    ┌────▼────────────────────────────────┐
    │ User Clicks Logout                  │
    ├────────────────────────────────────┤
    │ 1. Clear localStorage.removeItem()  │
    │ 2. Clear useAuth state              │
    │ 3. Reset role to null               │
    │ 4. navigate("/") → Login Page       │
    └────────────────────────────────────┘
         │
    ┌────▼──────────────────┐
    │ Back at Login Page     │
    │ (Cycle ready)          │
    └───────────────────────┘
```

## Technology Stack

```
Frontend:
├─ React 18+
├─ TypeScript
├─ React Router (routing)
├─ Shadcn/ui (components)
├─ Axios/Fetch (HTTP client)
└─ localStorage (session storage)

Backend:
├─ FastAPI (web framework)
├─ Uvicorn (ASGI server)
├─ Pydantic (validation)
├─ Passlib (password hashing)
├─ Supabase Python SDK (database)
└─ Logging (debugging)

Database:
├─ Supabase (PostgreSQL)
├─ Row Level Security
├─ Indexed columns
└─ Bcrypt hnashing

Infrastructure:
├─ Docker (containerization)
├─ docker-compose (orchestration)
└─ Environment variables (.env)
```

## Deployment Architecture (Future)

```
┌─────────────────────────────────────────────────────────┐
│                  PRODUCTION SETUP                       │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌─────────────────────────────────────────────────┐  │
│  │ Frontend (Vercel/Netlify)                       │  │
│  │ - Static site hosting                           │  │
│  │ - CDN distribution                              │  │
│  │ - HTTPS/SSL                                     │  │
│  └────────────────┬────────────────────────────────┘  │
│                   │ HTTPS                              │
│  ┌────────────────▼────────────────────────────────┐  │
│  │ Backend (Heroku/Railway)                        │  │
│  │ - FastAPI server                                │  │
│  │ - Rate limiting                                 │  │
│  │ - CORS restrictions                             │  │
│  │ - JWT token auth                                │  │
│  │ - Activity logging                              │  │
│  └────────────────┬────────────────────────────────┘  │
│                   │ HTTPS                              │
│  ┌────────────────▼────────────────────────────────┐  │
│  │ Supabase (Cloud Database)                       │  │
│  │ - PostgreSQL managed DB                         │  │
│  │ - Automatic backups                             │  │
│  │ - Real-time subscriptions                       │  │
│  │ - Built-in auth (optional)                      │  │
│  └─────────────────────────────────────────────────┘  │
│                                                          │
│  Additional Services:                                   │
│  - Auth0/Firebase Auth (2FA, SAML)                     │
│  - Sentry (error tracking)                             │
│  - DataDog (monitoring)                                │
│  - SendGrid (email notifications)                      │
└─────────────────────────────────────────────────────────┘
```

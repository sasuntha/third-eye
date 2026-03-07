# Quick Reference Guide - Backend Login

## 🚀 Start Here

### 1️⃣ Initialize Database (1 minute)

```bash
cd backend
& .\.venv\Scripts\Activate.ps1
python seed_employees.py
```

✅ Creates `employees` table and seeds test data

### 2️⃣ Start Backend (2 minutes)

```bash
python main.py
```

✅ Runs on `http://localhost:8000`

### 3️⃣ Configure Frontend (1 minute)

Create `frontend/.env.local`:

```env
VITE_API_URL=http://localhost:8000
```

### 4️⃣ Test Login (2 minutes)

```bash
cd backend
python run_tests.py
```

## 📚 Test Credentials

| Email                | Password    | Role     | Dashboard          |
| -------------------- | ----------- | -------- | ------------------ |
| chief@example.com    | chief123    | chief    | Chief Dashboard    |
| employee@example.com | employee123 | employee | Employee Dashboard |
| jane@example.com     | jane123     | employee | Employee Dashboard |

## 🔌 API Endpoint

### Login

**POST** `http://localhost:8000/api/auth/login`

**Request:**

```json
{
  "email": "chief@example.com",
  "password": "chief123"
}
```

**Success Response:**

```json
{
  "status": "success",
  "message": "Login successful",
  "user": {
    "id": "uuid",
    "email": "chief@example.com",
    "full_name": "Chief Administrator",
    "employee_id": "CHIEF001",
    "role": "chief"
  },
  "role": "chief"
}
```

**Error Response:**

```json
{
  "detail": "Invalid email or password"
}
```

## 🧪 Testing

### Run Full Test Suite

```bash
cd backend
python run_tests.py
```

### Verify Database

```bash
python test_employee_login.py
```

### Use Swagger UI

Visit: `http://localhost:8000/docs`

### Use Curl

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"chief@example.com","password":"chief123"}'
```

## 📂 Key Files

| File                             | Purpose                           |
| -------------------------------- | --------------------------------- |
| `backend/app/api/routes/auth.py` | Login endpoint                    |
| `backend/seed_employees.py`      | Create & populate employees table |
| `backend/run_tests.py`           | Comprehensive test suite          |
| `frontend/src/pages/Login.tsx`   | Login form (updated)              |
| `frontend/src/hooks/useAuth.tsx` | Auth context (updated)            |
| `frontend/.env.local`            | Environment config (CREATE THIS)  |

## 🔐 Role-Based Routing

```
Email & Password in form
        ↓
POST /api/auth/login
        ↓
Query employees table
        ↓
Verify password
        ↓
Return role="chief" or "employee"
        ↓
Frontend redirects:
├─ "chief" → /chief-dashboard
└─ "employee" → /employee-dashboard
```

## ⚙️ Database Schema

```sql
employees table:
├─ id (UUID, primary key)
├─ email (TEXT, unique)
├─ password (TEXT, bcrypt hashed)
├─ full_name (TEXT)
├─ employee_id (TEXT, unique)
├─ role ('chief' | 'employee' | null)
├─ is_active (BOOLEAN)
├─ created_at (TIMESTAMP)
└─ updated_at (TIMESTAMP)
```

## 🐛 Troubleshooting

### Table doesn't exist?

```bash
python seed_employees.py
```

### Wrong password?

- Passwords are hashed with bcrypt
- Use test credentials above
- Or generate hash: `python seed_employees.py --hash`

### Frontend not connecting?

- Check `VITE_API_URL` in `.env.local`
- Verify backend is running: `python main.py`
- Clear browser cache

### Port 8000 already in use?

- Find process: `Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess`
- Or use different port in config

## 📖 Documentation

- **Full Setup Guide:** [LOGIN_BACKEND_SETUP.md](LOGIN_BACKEND_SETUP.md)
- **Implementation Summary:** [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)
- **Completion Checklist:** [COMPLETION_CHECKLIST.md](COMPLETION_CHECKLIST.md)

## 💡 Common Tasks

### Add New Employee

```sql
INSERT INTO public.employees
(email, password, full_name, employee_id, role)
VALUES
('newuser@example.com', 'hashed_password_here', 'New User', 'EMP002', 'employee');
```

### Hash a Password

```bash
python seed_employees.py --hash
```

### Check Employees Table

```bash
python test_employee_login.py
```

### View API Docs

- Swagger: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## ✅ Verification Checklist

- [ ] Backend running: `python main.py`
- [ ] Can see: `http://localhost:8000/docs` in browser
- [ ] Frontend `.env.local` configured
- [ ] Can login with test credentials
- [ ] Redirects to correct dashboard by role
- [ ] Session persists on page refresh
- [ ] Logout clears session

## 🔑 Key Concepts

1. **Email Lookup:** Employees table indexed by email for fast queries
2. **Password Security:** Uses bcrypt hashing, never plain text
3. **Role-Based:** "chief" → Chief Dashboard, "employee" → Employee Dashboard
4. **Session Management:** User stored in localStorage after login
5. **Stateless API:** Backend doesn't maintain session, returns complete user data

## 🚨 Important Notes

⚠️ **For Production:**

- Use HTTPS/SSL
- Add rate limiting
- Implement CORS restrictions
- Add password reset
- Use JWT tokens with expiration
- Add audit logging
- Enable two-factor authentication

⚠️ **Security:**

- Never commit `.env` files
- Store secrets in environment variables
- Use bcrypt for password hashing
- Validate all inputs
- Use parameterized queries (Supabase SDK handles this)

## 🎯 Next Steps

1. ✅ Run `python seed_employees.py` (database setup)
2. ✅ Run `python main.py` (start backend)
3. ✅ Create `frontend/.env.local` (config frontend)
4. ✅ Run `python run_tests.py` (verify everything)
5. 🔄 Open frontend and test login
6. 📝 Review [LOGIN_BACKEND_SETUP.md](LOGIN_BACKEND_SETUP.md) for details

---

**Questions?** Check the documentation files listed above or run `python run_tests.py` for diagnostics.

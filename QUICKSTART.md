# Quick Start Guide - Third Eye

## 5-Minute Setup

### Step 1: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your Supabase credentials:
# SUPABASE_URL=https://your-project.supabase.co
# SUPABASE_KEY=your_anon_key
# SECRET_KEY=any_random_string
```

### Step 2: Start Backend

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Install & run
pip install -r requirements.txt
python main.py
```

✅ Backend running at: **http://localhost:8000**

### Step 3: Start Frontend (New Terminal)

```bash
cd frontend

npm install
npm run dev
```

✅ Frontend running at: **http://localhost:5173**

### Step 4: View API Docs

Open http://localhost:8000/docs to see interactive API documentation

---

## Key Endpoints

| Method | Endpoint           | Purpose             |
| ------ | ------------------ | ------------------- |
| GET    | `/health`          | Check server health |
| POST   | `/api/auth/login`  | Login user          |
| POST   | `/api/auth/signup` | Create account      |
| GET    | `/api/users/me`    | Get current user    |

---

## Docker Quick Start (Optional)

```bash
docker-compose up
```

- Backend: http://localhost:8000
- Frontend: http://localhost:5173

---

## Project Structure Summary

```
third-eye/
├── frontend/     # React app
├── backend/      # FastAPI app
└── supabase/     # Database config
```

---

## What's Next?

1. **Update `.env`** with Supabase credentials
2. **Run both servers** (backend + frontend)
3. **Check API docs** at http://localhost:8000/docs
4. **Start building** your features!

See [MIGRATION.md](MIGRATION.md) for detailed setup and customization.

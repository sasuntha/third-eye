# Project Restructuring - Migration Guide

## What Changed

Your **Third Eye** project has been successfully restructured into a **full-stack monorepo** with separate frontend and backend directories.

### New Project Structure

```
third-eye/
├── frontend/                   # React + TypeScript + Vite
│   ├── src/                   # React components and pages
│   ├── public/               # Static assets
│   ├── package.json          # Frontend dependencies
│   ├── vite.config.ts        # Vite configuration
│   ├── tailwind.config.ts    # Tailwind CSS config
│   ├── index.html            # HTML entry point
│   ├── Dockerfile            # Docker config for frontend
│   └── README.md             # Frontend documentation
│
├── backend/                   # FastAPI + Supabase
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── auth.py      # Authentication endpoints
│   │   │   │   └── users.py     # User management endpoints
│   │   │   └── __init__.py
│   │   ├── core/
│   │   │   ├── config.py        # Settings configuration
│   │   │   └── __init__.py
│   │   ├── db/
│   │   │   ├── supabase.py      # Supabase client setup
│   │   │   └── __init__.py
│   │   ├── models/              # Database models (ready to extend)
│   │   │   └── __init__.py
│   │   ├── schemas/             # Pydantic validation schemas
│   │   │   └── __init__.py
│   │   ├── main.py              # FastAPI application
│   │   └── __init__.py
│   ├── main.py                  # Entry point
│   ├── requirements.txt         # Python dependencies
│   ├── .env.example             # Environment template
│   ├── .gitignore              # Git ignore rules
│   ├── Dockerfile              # Docker config for backend
│   └── README.md               # Backend documentation
│
├── supabase/                    # Supabase configuration
│   ├── migrations/             # Database migrations
│   ├── functions/              # Serverless functions
│   └── config.toml
│
├── docker-compose.yml          # Docker compose for local dev
├── .env.example               # Root environment template
├── setup.ps1                  # Setup script for Windows
└── README.md                  # Main project documentation
```

## What Was Done

### 1. **Project Split**

- ✅ Created `frontend/` folder with all React/TypeScript files
- ✅ Created `backend/` folder with new FastAPI structure
- ✅ Moved all UI components, configs, and assets to frontend

### 2. **Backend Setup (FastAPI)**

- ✅ Created modular FastAPI application structure
- ✅ Configured Supabase client for database access
- ✅ Created authentication routes (`/api/auth/login`, `/api/auth/signup`, etc.)
- ✅ Created user management routes (`/api/users/`)
- ✅ Added CORS middleware for frontend communication
- ✅ Health check endpoint at `/health`

### 3. **Environment Configuration**

- ✅ Created `.env.example` with all required variables
- ✅ Created backend `.env.example` template
- ✅ Preconfigured Supabase integration

### 4. **Docker Support**

- ✅ Added `docker-compose.yml` for local development
- ✅ Created Dockerfile for backend (Python/FastAPI)
- ✅ Created Dockerfile for frontend (Node.js)

### 5. **Documentation**

- ✅ Updated main README with full project overview
- ✅ Created backend-specific README
- ✅ Created setup script for Windows (`setup.ps1`)

## Next Steps

### 1. Configure Environment Variables

```bash
# Copy the environment template
cp .env.example .env

# Edit .env with your Supabase credentials
# You'll need:
# - SUPABASE_URL
# - SUPABASE_KEY (anon key)
# - SUPABASE_SERVICE_ROLE_KEY
# - SECRET_KEY (any random string for JWT)
```

### 2. Start Backend Development

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate it (Windows)
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the server
python main.py
```

Backend will be at: **http://localhost:8000**

**Interactive API Docs:** http://localhost:8000/docs

### 3. Start Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

Frontend will be at: **http://localhost:5173**

### 4. (Optional) Use Docker

```bash
# Make sure you have Docker installed
# Run everything with:
docker-compose up

# Backend at: http://localhost:8000
# Frontend at: http://localhost:5173
```

## Backend API Endpoints

### Root

- `GET /` - Welcome message
- `GET /api` - API endpoints info
- `GET /health` - Health check

### Authentication

- `POST /api/auth/login` - Login with email/password
- `POST /api/auth/signup` - Create new account
- `POST /api/auth/logout` - Logout

### Users

- `GET /api/users/me` - Get current logged-in user
- `GET /api/users/` - List all users
- `POST /api/users/` - Create user profile
- `GET /api/users/{user_id}` - Get user by ID
- `PUT /api/users/{user_id}` - Update user profile

## Frontend Configuration

Update your frontend environment variables:

```
VITE_API_URL=http://localhost:8000
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
```

The frontend already has Supabase client integration in:

- `src/integrations/supabase/client.ts` - Supabase client setup
- `src/hooks/useAuth.tsx` - Authentication hook

## Database (Supabase)

Your Supabase migrations are in `supabase/migrations/`.

To apply/manage migrations:

```bash
supabase db pull  # Pull remote schema
supabase migration new [name]  # Create new migration
```

## Extending the Backend

### Add a New Route

1. Create new file in `backend/app/api/routes/`:

```python
# backend/app/api/routes/documents.py
from fastapi import APIRouter, Depends
from app.db.supabase import get_supabase_client

router = APIRouter(prefix="/api/documents", tags=["documents"])

@router.get("/")
async def list_documents(client = Depends(get_supabase_client)):
    response = client.table("documents").select("*").execute()
    return response.data
```

2. Import and include in `backend/app/main.py`:

```python
from app.api.routes import documents
app.include_router(documents.router)
```

## Extending the Frontend

Frontend structure is unchanged. Add new components in:

- `src/components/` - UI components
- `src/pages/` - Page components
- `src/hooks/` - Custom React hooks

The frontend is ready to consume backend APIs via the configured `VITE_API_URL`.

## Common Issues & Solutions

### Backend won't start

- Ensure Python 3.9+ is installed: `python --version`
- Check all dependencies: `pip install -r requirements.txt`
- Verify `.env` file has all required variables

### Frontend can't reach backend

- Make sure backend is running on `http://localhost:8000`
- Check CORS settings in `backend/app/main.py`
- Verify `VITE_API_URL` in frontend `.env`

### Database connection errors

- Verify `SUPABASE_URL` and `SUPABASE_KEY` in `.env`
- Ensure your Supabase project is active
- Check Supabase API rates haven't been exceeded

## Production Deployment

### Backend (FastAPI)

```bash
# Using Gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app.main:app

# Using Uvicorn with multiple workers
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Frontend (React)

```bash
cd frontend
npm run build
# Deploy the `dist/` folder to a static host
```

### Docker

```bash
docker-compose -f docker-compose.yml up -d
```

## Support & Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Supabase Docs**: https://supabase.com/docs
- **React Docs**: https://react.dev
- **Vite Docs**: https://vitejs.dev

## Summary

Your project is now structured as a professional full-stack application with:

- 🎨 **Separated frontend** (React + Vite)
- ⚙️ **Professional backend** (FastAPI + Supabase)
- 🐳 **Docker support** for local and production use
- 🔐 **Built-in authentication** via Supabase
- 📚 **Organized code structure** for scalability

Happy coding! 🚀

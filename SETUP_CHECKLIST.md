# Project Setup Checklist ✓

## Pre-requisites

- [ ] Python 3.9+ installed (`python --version`)
- [ ] Node.js 18+ installed (`node --version`)
- [ ] Supabase account created and project ready
- [ ] Git configured (if using version control)

## Configuration

- [ ] Created `.env` file from `.env.example`
- [ ] Added `SUPABASE_URL` to `.env`
- [ ] Added `SUPABASE_KEY` (anon key) to `.env`
- [ ] Added `SUPABASE_SERVICE_ROLE_KEY` to `.env`
- [ ] Added `SECRET_KEY` to `.env`

## Backend Setup

- [ ] Navigated to `backend/` directory
- [ ] Created Python virtual environment (`python -m venv venv`)
- [ ] Activated virtual environment
  - [ ] Windows: `venv\Scripts\activate`
  - [ ] macOS/Linux: `source venv/bin/activate`
- [ ] Installed dependencies (`pip install -r requirements.txt`)
- [ ] Verified FastAPI installed (`python -c "import fastapi"`)
- [ ] Verified Supabase client installed (`python -c "import supabase"`)

## Frontend Setup

- [ ] Navigated to `frontend/` directory
- [ ] Installed dependencies (`npm install`)
- [ ] Verified package.json loaded properly

## First Run

- [ ] Started backend (`python main.py`)
  - [ ] Backend starts without errors
  - [ ] Available at http://localhost:8000
- [ ] In new terminal, started frontend (`npm run dev`)
  - [ ] Frontend starts without errors
  - [ ] Available at http://localhost:5173

## Verification

- [ ] Can access API docs at http://localhost:8000/docs
- [ ] Can access ReDoc at http://localhost:8000/redoc
- [ ] Health check passes: `GET http://localhost:8000/health`
- [ ] Frontend loads in browser at http://localhost:5173
- [ ] No CORS errors in browser console

## API Testing

- [ ] Tested signup endpoint: `POST /api/auth/signup`
- [ ] Tested login endpoint: `POST /api/auth/login`
- [ ] Tested users endpoint: `GET /api/users/`
- [ ] Tested health endpoint: `GET /health`

## Database (Supabase)

- [ ] Supabase project is active and running
- [ ] API keys have appropriate permissions
- [ ] Database connection is working
- [ ] Can view migrations in `supabase/migrations/`

## Version Control (Optional)

- [ ] Repository initialized (`git init`)
- [ ] `.gitignore` configured
  - [ ] Backend `__pycache__` ignored
  - [ ] Backend `venv/` ignored
  - [ ] Frontend `node_modules/` ignored
- [ ] Initial commit created

## Documentation

- [ ] Read [README.md](README.md) - Main project documentation
- [ ] Read [QUICKSTART.md](QUICKSTART.md) - Quick start guide
- [ ] Read [MIGRATION.md](MIGRATION.md) - Migration details
- [ ] Read [backend/README.md](backend/README.md) - Backend docs
- [ ] Read [frontend/README.md](frontend/README.md) (if exists) - Frontend docs

## Optional: Docker Setup

- [ ] Docker installed (`docker --version`)
- [ ] Docker Compose installed (`docker-compose --version`)
- [ ] Tested docker-compose (`docker-compose config`)
- [ ] Can start with `docker-compose up`

## Next Steps

- [ ] Create additional API routes as needed
- [ ] Extend Pydantic models with your data
- [ ] Set up database tables in Supabase
- [ ] Connect frontend components to backend APIs
- [ ] Deploy to production (See deployment docs)

---

## Troubleshooting

**Backend won't start?**

- Check Python version: `python --version` (need 3.9+)
- Install missing deps: `pip install -r requirements.txt`
- Check `.env` variables are correct

**Frontend won't start?**

- Clear node cache: `npm cache clean --force`
- Delete `node_modules`: `rm -r node_modules`
- Reinstall: `npm install`
- Restart dev server: `npm run dev`

**Can't connect to database?**

- Verify Supabase credentials in `.env`
- Check Supabase project status (console.supabase.com)
- Ensure API keys have correct permissions

**Port already in use?**

- Backend (8000): Change `API_PORT` in `.env`
- Frontend (5173): Vite will try next available port automatically

---

**Last Updated**: March 2026
**Status**: ✅ Ready for Development

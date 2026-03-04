# Third Eye Backend API

FastAPI backend for Third Eye application with Supabase integration.

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   └── routes/
│   │       ├── auth.py      # Authentication endpoints
│   │       └── users.py     # User management endpoints
│   ├── core/
│   │   └── config.py        # Configuration settings
│   ├── db/
│   │   └── supabase.py      # Supabase client
│   ├── models/              # Database models
│   ├── schemas/             # Pydantic schemas
│   └── main.py              # Main FastAPI app
├── main.py                  # Entry point
├── requirements.txt         # Python dependencies
├── .env.example            # Example environment variables
└── README.md               # This file
```

## Setup Instructions

### 1. Create Virtual Environment

```bash
cd backend
python -m venv venv
```

On Windows:

```bash
venv\Scripts\activate
```

On macOS/Linux:

```bash
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your Supabase credentials:

```bash
cp .env.example .env
```

Edit `.env` with your Supabase details:

```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
SECRET_KEY=your_secret_key_here
```

### 4. Run the Development Server

```bash
python main.py
```

Or with uvicorn directly:

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Available Endpoints

### Health Check

- `GET /health` - Server health check

### Authentication

- `POST /api/auth/login` - Login user
- `POST /api/auth/signup` - Create new account
- `POST /api/auth/logout` - Logout user

### Users

- `GET /api/users/me` - Get current user
- `GET /api/users/` - Get all users
- `POST /api/users/` - Create new user
- `GET /api/users/{user_id}` - Get user by ID
- `PUT /api/users/{user_id}` - Update user

## Technologies Used

- **FastAPI** - Web framework
- **Uvicorn** - ASGI server
- **Supabase** - Database and authentication
- **Pydantic** - Data validation
- **Python-Jose** - JWT tokens
- **Passlib** - Password hashing

## Development

### Code Structure

- `app/api/routes/` - API endpoint handlers
- `app/core/` - Configuration and constants
- `app/db/` - Database clients and queries
- `app/models/` - SQLAlchemy models (if using)
- `app/schemas/` - Pydantic request/response models

### Adding New Routes

Create a new file in `app/api/routes/`:

```python
from fastapi import APIRouter

router = APIRouter(prefix="/api/myroute", tags=["myroute"])

@router.get("/")
async def my_endpoint():
    return {"message": "Hello"}
```

Then import and include it in `app/main.py`:

```python
from app.api.routes import myroute
app.include_router(myroute.router)
```

## Environment Variables

Required environment variables (see `.env.example`):

- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_KEY` - Your Supabase anon key
- `SUPABASE_SERVICE_ROLE_KEY` - Service role key (optional, for admin operations)
- `SECRET_KEY` - Secret key for JWT tokens
- `ALGORITHM` - JWT algorithm (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Token expiry time (default: 30)

## Contributing

Guidelines for contributing to this project...

## License

MIT

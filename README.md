# Third Eye - Document Management System

A full-stack document management and workflow automation system built with React, FastAPI, and Supabase.

## Project Structure

This is a monorepo with two main directories:

```
third-eye/
├── frontend/                 # React + TypeScript + Vite
│   ├── src/
│   ├── public/
│   ├── package.json
│   ├── vite.config.ts
│   └── README.md
├── backend/                  # FastAPI with Supabase
│   ├── app/
│   ├── main.py
│   ├── requirements.txt
│   └── README.md
├── supabase/                 # Supabase configuration
│   ├── migrations/
│   └── functions/
└── .env.example             # Environment variables template
```

## Quick Start

### Prerequisites

- **Node.js** v18+ (for frontend)
- **Python** 3.9+ (for backend)
- **Supabase Project** - Create one at https://supabase.com

### Environment Setup

1. Copy the environment template and configure it:

   ```bash
   cp .env.example .env
   ```

2. Update `.env` with your Supabase credentials:
   ```
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_anon_key
   SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
   SECRET_KEY=your_secret_key_here
   ```

### Starting the Backend

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Start the server
python main.py
```

Backend API will run at `http://localhost:8000`

**API Documentation:**

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Starting the Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be available at `http://localhost:5173`

## Technology Stack

### Frontend

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **shadcn/ui** - Component library
- **Supabase JS Client** - Backend integration

### Backend

- **FastAPI** - Modern Python web framework
- **Uvicorn** - ASGI server
- **Supabase** - Database and authentication
- **Pydantic** - Data validation
- **Python-Jose** - JWT authentication

### Database

- **Supabase PostgreSQL** - Relational database
- **Supabase Auth** - User authentication
- **Supabase Storage** - File storage
- **Supabase Functions** - Serverless functions

## Key Features

- **User Authentication** - Login, signup, and session management via Supabase Auth
- **Document Management** - Upload, review, and approve documents
- **Task Management** - Create and manage tasks with workflow automation
- **Role-Based Access** - Chief and Employee role-based dashboards
- **Real-time Updates** - Real-time data synchronization with Supabase
- **Responsive Design** - Mobile-friendly user interface

## Development

### Frontend Documentation

See [frontend/README.md](frontend/README.md) for frontend-specific development guide.

### Backend Documentation

See [backend/README.md](backend/README.md) for backend-specific development guide.

### Supabase Configuration

Database schema and migrations are in the `supabase/` directory. To apply migrations:

```bash
supabase migration up
```

## API Endpoints

### Authentication

- `POST /api/auth/login` - Login
- `POST /api/auth/signup` - Create account
- `POST /api/auth/logout` - Logout

### Users

- `GET /api/users/me` - Get current user
- `GET /api/users/` - List all users
- `POST /api/users/` - Create user
- `GET /api/users/{id}` - Get user by ID
- `PUT /api/users/{id}` - Update user

## Environment Variables

```env
# Backend
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
SECRET_KEY=your_secret_key
API_PORT=8000

# Frontend
VITE_API_URL=http://localhost:8000
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
```

## Building for Production

### Frontend

```bash
cd frontend
npm run build
```

### Backend

```bash
cd backend
pip install -r requirements.txt
gunicorn -w 4 -b 0.0.0.0:8000 app.main:app
```

## Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make your changes
3. Commit: `git commit -m 'Add feature'`
4. Push: `git push origin feature/your-feature`
5. Open a pull request

## License

MIT

- Edit files directly within the Codespace and commit and push your changes once you're done.

## What technologies are used for this project?

This project is built with:

- Vite
- TypeScript
- React
- shadcn-ui
- Tailwind CSS

## How can I deploy this project?

Simply open [Lovable](https://lovable.dev/projects/REPLACE_WITH_PROJECT_ID) and click on Share -> Publish.

## Can I connect a custom domain to my Lovable project?

Yes, you can!

To connect a domain, navigate to Project > Settings > Domains and click Connect Domain.

Read more here: [Setting up a custom domain](https://docs.lovable.dev/features/custom-domain#custom-domain)

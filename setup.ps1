# Third Eye Project Setup Script for Windows

Write-Host "Third Eye - Project Setup" -ForegroundColor Cyan
Write-Host "========================" -ForegroundColor Cyan

# Check if .env exists
if (!(Test-Path ".env")) {
    Write-Host "`nCopying .env.example to .env..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host ".env created! Please update it with your Supabase credentials." -ForegroundColor Yellow
}

# Setup Backend
Write-Host "`n--- Setting up Backend ---" -ForegroundColor Cyan
Set-Location backend

if (!(Test-Path "venv")) {
    Write-Host "Creating Python virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

Set-Location ..

# Setup Frontend
Write-Host "`n--- Setting up Frontend ---" -ForegroundColor Cyan
Set-Location frontend

Write-Host "Installing Node dependencies..." -ForegroundColor Yellow
npm install

Set-Location ..

Write-Host "`n✓ Setup Complete!" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "1. Open .env and update Supabase credentials" -ForegroundColor White
Write-Host "2. Run backend: cd backend && venv\Scripts\Activate && python main.py" -ForegroundColor White
Write-Host "3. Run frontend: cd frontend && npm run dev" -ForegroundColor White
Write-Host "4. Open http://localhost:5173" -ForegroundColor White

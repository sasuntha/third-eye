# Quick Setup Script for Forensic Analysis System

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Forensic Analysis System - Quick Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if model exists
$modelSource = "C:\Users\User\Desktop\research_nsbm\data\my_weapon_model_v2.h5"
$modelDest = "backend\models\weapon_classifier.h5"

Write-Host "[Step 1] Checking for trained model..." -ForegroundColor Yellow

if (Test-Path $modelDest) {
    Write-Host "✓ Model already exists at: $modelDest" -ForegroundColor Green
} elseif (Test-Path $modelSource) {
    Write-Host "Found model at source location" -ForegroundColor Yellow
    Write-Host "Copying model to project..." -ForegroundColor Yellow
    
    # Create models directory if it doesn't exist
    $modelsDir = "backend\models"
    if (-not (Test-Path $modelsDir)) {
        New-Item -ItemType Directory -Path $modelsDir -Force | Out-Null
        Write-Host "Created directory: $modelsDir" -ForegroundColor Green
    }
    
    Copy-Item $modelSource $modelDest
    Write-Host "✓ Model copied successfully!" -ForegroundColor Green
} else {
    Write-Host "⚠ Model not found at: $modelSource" -ForegroundColor Yellow
    Write-Host "Please manually copy your model to: $modelDest" -ForegroundColor Yellow
}

Write-Host ""

# Check Python
Write-Host "[Step 2] Checking Python..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "✗ Python not found" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Install backend dependencies
Write-Host "[Step 3] Installing backend dependencies..." -ForegroundColor Yellow
Set-Location backend

if (Test-Path "venv") {
    Write-Host "✓ Virtual environment exists" -ForegroundColor Green
} else {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
}

& .\venv\Scripts\Activate.ps1
pip install -r requirements.txt --quiet

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to install dependencies" -ForegroundColor Red
    Set-Location ..
    exit 1
}

Write-Host ""

# Create reports directory
Write-Host "[Step 4] Setting up reports directory..." -ForegroundColor Yellow
if (-not (Test-Path "reports")) {
    New-Item -ItemType Directory -Path "reports" -Force | Out-Null
    Write-Host "✓ Reports directory created" -ForegroundColor Green
} else {
    Write-Host "✓ Reports directory exists" -ForegroundColor Green
}

Set-Location ..

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if model is in place
if (Test-Path "backend\models\weapon_classifier.h5") {
    Write-Host "✓ All prerequisites met!" -ForegroundColor Green
    Write-Host ""
    Write-Host "To start the system:" -ForegroundColor Yellow
    Write-Host "  1. Terminal 1: cd backend && python main.py" -ForegroundColor White
    Write-Host "  2. Terminal 2: cd frontend && npm run dev" -ForegroundColor White
    Write-Host "  3. Open http://localhost:5173" -ForegroundColor White
    Write-Host ""
    Write-Host "To test the API:" -ForegroundColor Yellow
    Write-Host "  curl http://localhost:8000/api/forensic-analysis/health" -ForegroundColor White
} else {
    Write-Host "⚠ Action Required:" -ForegroundColor Yellow
    Write-Host "  Please copy your trained model to:" -ForegroundColor White
    Write-Host "  backend\models\weapon_classifier.h5" -ForegroundColor White
    Write-Host ""
    Write-Host "  From: C:\Users\User\Desktop\research_nsbm\data\my_weapon_model_v2.h5" -ForegroundColor White
}

Write-Host ""
Write-Host "For detailed instructions, see: INTEGRATION_COMPLETE.md" -ForegroundColor Cyan
Write-Host ""

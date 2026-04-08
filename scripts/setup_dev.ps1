# Development setup helper.
#
# This script is intentionally simple: it prints the expected manual setup steps
# for students working on the project locally.
Write-Host "Backend:"
Write-Host "1. Create a virtual environment"
Write-Host "2. Install backend/requirements.txt"
Write-Host "3. Run uvicorn app.main:app --reload from backend/"
Write-Host ""
Write-Host "Frontend:"
Write-Host "1. Create a Vite React + TypeScript app in frontend/ if not already installed"
Write-Host "2. Set VITE_API_BASE_URL=http://localhost:8000"

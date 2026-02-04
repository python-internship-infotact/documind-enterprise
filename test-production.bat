@echo off
REM DocuMind Enterprise - Production Configuration Test Script
REM This script helps test the production build locally before deployment

echo 🚀 DocuMind Enterprise - Production Test
echo ========================================

REM Check if required files exist
echo 📋 Checking deployment configuration files...

if exist "render.yaml" (
    echo ✅ render.yaml exists
) else (
    echo ❌ render.yaml missing
    exit /b 1
)

if exist "vercel.json" (
    echo ✅ vercel.json exists
) else (
    echo ❌ vercel.json missing
    exit /b 1
)

if exist "frontend\.env.production" (
    echo ✅ frontend/.env.production exists
) else (
    echo ❌ frontend/.env.production missing
    exit /b 1
)

if exist "DEPLOYMENT.md" (
    echo ✅ DEPLOYMENT.md exists
) else (
    echo ❌ DEPLOYMENT.md missing
    exit /b 1
)

REM Test backend requirements
echo.
echo 🐍 Testing backend requirements...
if exist "ai_service\requirements.txt" (
    echo ✅ Backend requirements.txt exists
) else (
    echo ❌ Backend requirements.txt missing
    exit /b 1
)

REM Test frontend configuration
echo.
echo ⚛️  Testing frontend configuration...
if exist "frontend\package.json" (
    echo ✅ Frontend package.json exists
    cd frontend
    npm list --depth=0 >nul 2>&1
    if %errorlevel% equ 0 (
        echo ✅ Frontend dependencies are installed
    ) else (
        echo ⚠️  Frontend dependencies not installed. Run: cd frontend ^&^& npm install
    )
    cd ..
) else (
    echo ❌ Frontend package.json missing
    exit /b 1
)

echo.
echo 🎉 Configuration files are ready for deployment!
echo.
echo Next steps:
echo 1. Deploy backend to Render using render.yaml
echo 2. Deploy frontend to Vercel using vercel.json
echo 3. Update API URLs if needed
echo 4. Test the deployed application
echo.
echo See DEPLOYMENT.md for detailed instructions.
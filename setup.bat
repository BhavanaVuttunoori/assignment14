@echo off
echo ========================================
echo Calculations API - Setup Script
echo ========================================
echo.

REM Check if Docker is installed
where docker >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo X Docker is not installed. Please install Docker Desktop first.
    exit /b 1
)

where docker-compose >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo X Docker Compose is not installed. Please install Docker Desktop first.
    exit /b 1
)

echo [OK] Docker and Docker Compose are installed
echo.

REM Stop any existing containers
echo [*] Stopping existing containers...
docker-compose down -v

echo.
echo [*] Building and starting containers...
docker-compose up --build -d

echo.
echo [*] Waiting for services to be ready...
timeout /t 10 /nobreak >nul

echo.
echo [OK] Setup complete!
echo.
echo Application URLs:
echo    - Frontend: http://localhost:8000
echo    - API Docs: http://localhost:8000/docs
echo    - ReDoc: http://localhost:8000/redoc
echo.
echo To view logs:
echo    docker-compose logs -f
echo.
echo To stop the application:
echo    docker-compose down
echo.
pause

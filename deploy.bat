@echo off
REM Sakura Reviews Deployment Script for EasyPanel

echo 🌸 Sakura Reviews - EasyPanel Deployment
echo ========================================

REM Check if we're in the right directory
if not exist "app_enhanced.py" (
    echo ❌ Error: app_enhanced.py not found. Please run from the project root.
    exit /b 1
)

echo ✅ Found app_enhanced.py

REM Create templates directory if it doesn't exist
if not exist "templates" mkdir templates

echo ✅ Created templates directory

REM Check if templates exist
if not exist "templates\widget.html" (
    echo ⚠️  Warning: templates\widget.html not found. Creating basic template...
    (
        echo ^<!DOCTYPE html^>
        echo ^<html^>
        echo ^<head^>
        echo     ^<title^>Sakura Reviews Widget^</title^>
        echo     ^<style^>
        echo         body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
        echo         .reviews-container { max-width: 800px; margin: 0 auto; }
        echo         .review-item { border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 8px; }
        echo     ^</style^>
        echo ^</head^>
        echo ^<body^>
        echo     ^<div class="reviews-container"^>
        echo         ^<h2^>Customer Reviews^</h2^>
        echo         {% for review in reviews %}
        echo         ^<div class="review-item"^>
        echo             ^<h4^>{{ review.author }}^</h4^>
        echo             ^<p^>{{ review.text }}^</p^>
        echo             ^<small^>Rating: {{ review.rating }}/5 ^| AI Score: {{ review.ai_score }}^</small^>
        echo         ^</div^>
        echo         {% endfor %}
        echo     ^</div^>
        echo ^</body^>
        echo ^</html^>
    ) > templates\widget.html
)

echo ✅ Templates ready

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo 📝 Creating .env file...
    (
        echo WIDGET_BASE_URL=https://your-domain.com
        echo WIDGET_SECRET=your-secret-key-here
        echo FLASK_ENV=production
    ) > .env
    echo ⚠️  Please update .env with your actual domain and secret key
)

echo ✅ Environment file ready

REM Test the application
echo 🧪 Testing application...
python -c "import app_enhanced; print('✅ Application imports successfully')"

if %errorlevel% equ 0 (
    echo 🎉 Deployment preparation complete!
    echo.
    echo 📋 Next Steps:
    echo 1. Update .env with your actual domain
    echo 2. Deploy to EasyPanel
    echo 3. Test ScriptTag endpoints
    echo 4. Verify JavaScript injection
) else (
    echo ❌ Application test failed. Please check for errors.
    exit /b 1
)

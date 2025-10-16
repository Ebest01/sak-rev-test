@echo off
REM Sakura Reviews - Local Development Startup Script
REM This sets environment variables and starts the Flask server

echo ============================================================
echo Starting Sakura Reviews (Local Development)
echo ============================================================

REM Set Shopify credentials (FILL THESE IN WITH YOUR ACTUAL CREDENTIALS)
set SHOPIFY_API_KEY=your-api-key-here
set SHOPIFY_API_SECRET=your-api-secret-here
set SHOPIFY_ACCESS_TOKEN=your-access-token-here
set SHOPIFY_SHOP_DOMAIN=your-store.myshopify.com
set SHOPIFY_APP_URL=http://localhost:5000
set SHOPIFY_REDIRECT_URI=http://localhost:5000/auth/callback

REM Start Flask
python app_enhanced.py

pause


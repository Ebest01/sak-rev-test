"""
Shopify Configuration with your actual credentials
Copy these values to your .env file or use directly in development
"""

# Your Shopify App Credentials (from Partner Dashboard)
SHOPIFY_CREDENTIALS = {
    'API_KEY': '3771d40f65cd51699b07191e8df45fe9',
    'API_SECRET': '8c254b805fef674a9f7b390859a9d742',
    'APP_URL': 'https://sakura-reviews-sakura-reviews-srv.utztjw.easypanel.host/',
    'REDIRECT_URI': 'https://sakura-reviews-sakura-reviews-srv.utztjw.easypanel.host/auth/callback',
    'SCOPES': 'read_products,write_products,read_content,write_content',
    'API_VERSION': '2025-10',
    'EMBED_APP': True
}

# For testing - you'll need to get these from your test store
# Go to your test store admin → Settings → Apps → Develop apps → Create app
TEST_STORE_CONFIG = {
    'ACCESS_TOKEN': 'your-access-token-here',  # Get this after creating custom app
    'SHOP_DOMAIN': 'your-test-store.myshopify.com'  # Your test store domain
}

# Environment variables to set
ENV_VARS = f"""
# Copy these to your .env file:
SECRET_KEY=reviewking-secret-production-key-2024
SHOPIFY_API_KEY={SHOPIFY_CREDENTIALS['API_KEY']}
SHOPIFY_API_SECRET={SHOPIFY_CREDENTIALS['API_SECRET']}
SHOPIFY_APP_URL={SHOPIFY_CREDENTIALS['APP_URL']}
SHOPIFY_REDIRECT_URI={SHOPIFY_CREDENTIALS['REDIRECT_URI']}
SHOPIFY_SCOPES={SHOPIFY_CREDENTIALS['SCOPES']}
PORT=5000
FLASK_ENV=development

# Add these after setting up your test store:
# SHOPIFY_ACCESS_TOKEN=your-access-token-here
# SHOPIFY_SHOP_DOMAIN=your-test-store.myshopify.com
"""

if __name__ == "__main__":
    print("Sakura Reviews - Shopify Configuration")
    print("=" * 50)
    print("\nYour API Credentials:")
    print(f"Client ID: {SHOPIFY_CREDENTIALS['API_KEY']}")
    print(f"Client Secret: {SHOPIFY_CREDENTIALS['API_SECRET'][:8]}...")
    print(f"App URL: {SHOPIFY_CREDENTIALS['APP_URL']}")
    print(f"Scopes: {SHOPIFY_CREDENTIALS['SCOPES']}")
    
    print("\nEnvironment Variables:")
    print(ENV_VARS)
    
    print("\nNext Steps:")
    print("1. Create .env file with the variables above")
    print("2. Set up your test store access token")
    print("3. Run: python app_enhanced.py")
    print("4. Test the bookmarklet on AliExpress/Amazon")

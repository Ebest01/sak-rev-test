"""
Remote Configuration Loader for ReviewKing
Fetches config from remote source with local fallback
"""

import os
import requests
import json
import logging

logger = logging.getLogger(__name__)

class RemoteConfigLoader:
    """Load configuration from remote source or use local defaults"""
    
    def __init__(self, remote_url=None):
        self.remote_url = remote_url or os.environ.get('REMOTE_CONFIG_URL')
        self.config = {}
        self.load_config()
    
    def load_config(self):
        """Load config with priority: remote > env vars > local defaults"""
        
        # Try remote config first
        if self.remote_url:
            try:
                response = requests.get(self.remote_url, timeout=5)
                if response.status_code == 200:
                    self.config = response.json()
                    logger.info(f"[OK] Loaded config from remote: {self.remote_url}")
                    return
            except Exception as e:
                logger.warning(f"[WARN] Failed to load remote config: {e}")
        
        # Fallback to local config file
        if os.path.exists('config.json'):
            try:
                with open('config.json', 'r') as f:
                    self.config = json.load(f)
                    logger.info("[OK] Loaded config from local config.json")
                    return
            except Exception as e:
                logger.warning(f"[WARN] Failed to load local config: {e}")
        
        # Final fallback to hardcoded defaults (for development)
        self.config = self.get_default_config()
        logger.info("[OK] Using default config")
    
    def get_default_config(self):
        """Default configuration for local development"""
        return {
            'shopify': {
                'api_key': os.getenv('SHOPIFY_API_KEY', 'your-api-key-here'),
                'api_secret': os.getenv('SHOPIFY_API_SECRET', 'your-api-secret-here'),
                'access_token': os.getenv('SHOPIFY_ACCESS_TOKEN', 'your-access-token-here'),
                'shop_domain': os.getenv('SHOPIFY_SHOP_DOMAIN', 'your-shop.myshopify.com'),
                'api_version': '2025-10',
                'app_url': os.getenv('SHOPIFY_APP_URL', 'https://your-app-url.com/'),
                'redirect_uri': os.getenv('SHOPIFY_REDIRECT_URI', 'https://your-app-url.com/auth/callback')
            }
        }
    
    def get(self, key, default=None):
        """Get config value with dot notation (e.g. 'shopify.api_key')"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        
        # Environment variables take highest priority
        env_key = '_'.join(keys).upper()
        return os.environ.get(env_key, value or default)

# Global config instance
config = RemoteConfigLoader()

# Example usage:
if __name__ == "__main__":
    print("ReviewKing Configuration Loader")
    print("=" * 50)
    print(f"\nShopify Domain: {config.get('shopify.shop_domain')}")
    print(f"Shopify API Key: {config.get('shopify.api_key')}")
    print(f"Access Token: {config.get('shopify.access_token')[:20]}...")
    print("\n[OK] Config loaded successfully!")


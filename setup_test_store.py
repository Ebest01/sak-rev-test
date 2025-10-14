#!/usr/bin/env python3
"""
Setup script for Sakura Reviews - Test Store Configuration
This will help you get the access token from your Shopify test store
"""

import os
import sys

def print_banner():
    print("🌸" * 20)
    print("   SAKURA REVIEWS SETUP")
    print("   Test Store Configuration")
    print("🌸" * 20)

def print_step(step_num, title, description):
    print(f"\n📋 STEP {step_num}: {title}")
    print("-" * 40)
    print(description)

def main():
    print_banner()
    
    print("\n✅ Your Shopify App Credentials are already configured!")
    print(f"   Client ID: 3771d40f65cd51699b07191e8df45fe9")
    print(f"   Client Secret: 8c254b805fef674a9f7b390859a9d742")
    
    print_step(1, "Access Your Test Store", 
        """Go to your Shopify test store admin panel:
   • Log into your test store
   • Go to Settings → Apps and sales channels
   • Click "Develop apps" (at the bottom)""")
    
    print_step(2, "Create Custom App",
        """Create a new custom app for testing:
   • Click "Create an app"
   • App name: "Sakura Reviews Test"
   • Click "Create app" """)
    
    print_step(3, "Configure API Scopes",
        """Set the required permissions:
   • Click "Configure Admin API scopes"
   • Enable these scopes:
     ✅ read_products
     ✅ write_products
   • Click "Save" """)
    
    print_step(4, "Install the App",
        """Install your custom app:
   • Click "Install app"
   • Confirm the installation
   • You'll see the "Admin API access token" """)
    
    print_step(5, "Copy Access Token",
        """Copy the access token and your shop domain:
   • Copy the "Admin API access token" 
   • Note your shop domain (e.g., your-store.myshopify.com)""")
    
    print_step(6, "Update Configuration",
        """Add these to your environment:
   • Create a .env file in your project folder
   • Add these lines:
   
   SHOPIFY_ACCESS_TOKEN=your-access-token-here
   SHOPIFY_SHOP_DOMAIN=your-store.myshopify.com
   
   Or set them as environment variables.""")
    
    print_step(7, "Test the Setup",
        """Run the application:
   • python app_enhanced.py
   • Go to any AliExpress product page
   • Use the bookmarklet to test product search""")
    
    print("\n" + "🎯" * 20)
    print("   QUICK TEST COMMANDS")
    print("🎯" * 20)
    print("\n# Test the API endpoints:")
    print("python test_part1_features.py")
    print("\n# Run the main application:")
    print("python app_enhanced.py")
    print("\n# Check configuration:")
    print("python shopify_config.py")
    
    print("\n🌸 Once configured, your Sakura Reviews will be able to:")
    print("   ✅ Search your Shopify products in real-time")
    print("   ✅ Import reviews directly to your products")
    print("   ✅ Handle bulk imports with skip functionality")
    print("   ✅ Store reviews as metafields in Shopify")
    
    print("\n📞 Need help? Check SETUP_GUIDE_PART1.md for detailed instructions!")

if __name__ == "__main__":
    main()

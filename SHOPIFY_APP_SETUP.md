# 🌸 Sakura Reviews - Shopify App Setup Guide

**Beautiful reviews, naturally**

---

## 📋 Quick Setup for Shopify Partners

### **Step 1: Create App**

1. Go to: **Shopify Partner Dashboard** → **Apps**
2. Click: **"Create app"**
3. Choose: **"Start from Dev Dashboard"**
4. App name: **`Sakura Reviews`**
5. Click: **"Create"**

---

### **Step 2: Configure URLs**

After creation, in **"Configuration"** tab:

```
App URL:
https://reviewking-reviewking-srv.utztjw.easypanel.host

Allowed redirection URL(s):
https://reviewking-reviewking-srv.utztjw.easypanel.host/auth/callback
https://reviewking-reviewking-srv.utztjw.easypanel.host/auth/inline
```

---

### **Step 3: Set API Scopes**

Under **"App setup"** → **"API scopes"**:

**Required:**
- ✅ `read_products` - Read product information
- ✅ `write_products` - Add reviews to products
- ✅ `read_content` - Read store content
- ✅ `write_content` - Write reviews

**Optional:**
- ✅ `read_orders` - Verify purchased products
- ✅ `read_customers` - Customer information

---

### **Step 4: GDPR Webhooks (Required for App Store)**

Under **"Webhooks"**:

1. `customers/data_request` → `https://your-url/webhooks/customers_data_request`
2. `customers/redact` → `https://your-url/webhooks/customers_redact`
3. `shop/redact` → `https://your-url/webhooks/shop_redact`
4. `app/uninstalled` → `https://your-url/webhooks/app_uninstalled`

---

## 🌸 Branding Assets

### **Colors:**
- Primary: `#FF69B4` (Hot Pink)
- Secondary: `#FF1493` (Deep Pink)
- Text: `#FFFFFF` (White)
- Background: `#0f0f23` (Dark)

### **Logo:**
🌸 Cherry Blossom emoji or custom SVG

### **Tagline:**
"Beautiful reviews, naturally"

---

## 🔖 Bookmarklet (Current)

```javascript
javascript:(function(){var s=document.createElement('script');s.src='https://reviewking-reviewking-srv.utztjw.easypanel.host/bookmarklet.js';document.head.appendChild(s);})();
```

---

## 🚀 Features

- ✅ 100 reviews loaded at once
- ✅ Smart filters (Photos, AI Recommended, Star ratings)
- ✅ 3-star filter for balanced review sets
- ✅ Server-side scraping (AliExpress official API)
- ✅ AI quality scoring
- ✅ Beautiful pink gradient UI
- ✅ Instant client-side filtering

---

## 📊 Current Status

- ✅ **Deployed:** https://reviewking-reviewking-srv.utztjw.easypanel.host
- ✅ **API Working:** GET `/api/scrape?productId=xxx`
- ✅ **Bookmarklet Working:** Beautiful pink Sakura UI
- ❌ **OAuth:** Not implemented yet (needed for public app)
- ❌ **Database:** Not implemented yet
- ❌ **Shopify Import:** Not implemented yet

---

## 🎯 Next Steps

### **For Testing on YOUR Store (Quick):**
1. Go to your store admin
2. Settings → Apps → Develop apps
3. Create custom app
4. Get API credentials
5. Test manual import

### **For Public App Store (Full Build):**
1. Implement OAuth (`/auth`, `/auth/callback`)
2. Add PostgreSQL database (store shop tokens)
3. Build Shopify API integration
4. Add review import functionality
5. Create embedded admin UI
6. Submit to App Store

---

## 📞 Support

**Domain:** sakurareviews.com (to be purchased)
**Current URL:** https://reviewking-reviewking-srv.utztjw.easypanel.host
**Repository:** https://github.com/Ebest01/reviewking

---

**🌸 Beautiful reviews, naturally**


# 🌸 Sakura Reviews - EasyPanel Deployment Guide

## 🚀 Quick Deployment Steps

### 1. **Prepare Repository**
```bash
# Clone the sak-rev-test repository
git clone https://github.com/Ebest01/sak-rev-test.git
cd sak-rev-test

# Copy your app_enhanced.py to the repository
# Copy templates/ directory if it exists
```

### 2. **EasyPanel Setup**
1. **Create New Service** in EasyPanel
2. **Choose "Docker Compose"** deployment
3. **Upload the following files:**
   - `app_enhanced.py`
   - `requirements.txt`
   - `Dockerfile`
   - `docker-compose.yml`
   - `templates/` directory (if exists)

### 3. **Environment Variables**
Set these in EasyPanel:
```
WIDGET_BASE_URL=https://your-easypanel-domain.com
WIDGET_SECRET=your-secret-key-here
FLASK_ENV=production
```

### 4. **Deploy and Test**
1. **Deploy the service**
2. **Test endpoints:**
   - `https://your-domain.com/js/sakura-reviews.js`
   - `https://your-domain.com/shopify-scripttag`
   - `https://your-domain.com/debug/routes`

## 🔧 Key Endpoints for Testing

### **ScriptTag JavaScript File**
```
GET /js/sakura-reviews.js
```
- **Purpose**: JavaScript file injected via ScriptTag API
- **Content-Type**: application/javascript
- **Size**: ~5,772 bytes

### **ScriptTag Creation**
```
POST /shopify/scripttag/create
Content-Type: application/json

{
  "shop_domain": "test-shop.myshopify.com",
  "access_token": "your-access-token"
}
```

### **Widget Display**
```
GET /widget/{shop_id}/reviews/{product_id}
```
- **Purpose**: Display review widget in iframe
- **Parameters**: shop_id, product_id, theme, limit

## 🎯 Testing ScriptTag Integration

### **1. Test JavaScript File**
```bash
curl https://your-domain.com/js/sakura-reviews.js
```
**Expected**: JavaScript code with auto-injection logic

### **2. Test ScriptTag Creation**
```bash
curl -X POST https://your-domain.com/shopify/scripttag/create \
  -H "Content-Type: application/json" \
  -d '{"shop_domain": "test-shop.myshopify.com", "access_token": "test-token"}'
```
**Expected**: Error about invalid credentials (normal for test)

### **3. Test Widget Display**
```bash
curl https://your-domain.com/widget/test-shop/reviews/test-product
```
**Expected**: HTML page with review widget

## 🌟 How It Works (Like Loox)

1. **Merchant installs Sakura Reviews app**
2. **App automatically creates ScriptTag** via Shopify API
3. **JavaScript file gets injected** into all store pages
4. **Script detects product pages** automatically
5. **Review sections appear** without manual work

## 📋 Deployment Checklist

- [ ] Repository cloned and files uploaded
- [ ] Environment variables set in EasyPanel
- [ ] Service deployed successfully
- [ ] JavaScript file endpoint working
- [ ] ScriptTag creation endpoint working
- [ ] Widget display endpoint working
- [ ] Ready for Shopify integration testing

## 🎉 Success Indicators

- ✅ **JavaScript file loads** (5,772 bytes)
- ✅ **ScriptTag creation responds** (even with test credentials)
- ✅ **Widget displays** with sample reviews
- ✅ **All endpoints accessible** via HTTPS

## 🚀 Next Steps After Deployment

1. **Update WIDGET_BASE_URL** to your EasyPanel domain
2. **Test with real Shopify store** credentials
3. **Create Shopify app** for production
4. **Deploy to Shopify App Store**

## 📞 Support

If you encounter issues:
1. Check EasyPanel logs
2. Verify environment variables
3. Test endpoints individually
4. Contact development team

---

**Ready to crush Loox with superior ScriptTag integration!** 🌸

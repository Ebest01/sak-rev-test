# Sakura Reviews - AI-Powered Review Importer

🌸 Beautiful reviews, naturally. Import high-quality reviews from AliExpress to Shopify with AI-powered filtering - better than Loox!

## Features

- ✅ 100 reviews loaded at once
- ✅ Smart filters (Photos, AI Recommended, Star ratings)
- ✅ 3-star filter for balanced review sets
- ✅ Server-side scraping (AliExpress official API)
- ✅ AI quality scoring
- ✅ Beautiful gradient UI
- ✅ Instant client-side filtering

## Deployment

### EasyPanel/Railway/Render

```bash
pip install -r requirements.txt
python app_loox_inspired.py
```

### Environment Variables

- `PORT` - Server port (default: 5000)

## Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run server
python app_loox_inspired.py
```

## API Endpoints

- `GET /bookmarklet.js` - Bookmarklet script
- `GET /api/scrape?productId=xxx` - Scrape reviews from AliExpress

## License

Proprietary - All Rights Reserved

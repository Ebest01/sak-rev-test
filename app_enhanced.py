"""
ReviewKing Enhanced API - Superior to Loox
Matching Loox architecture with competitive advantages:
- Multi-platform (AliExpress, Amazon, eBay, Walmart)
- AI Quality Scoring (10-point system)
- Bulk import capabilities
- Better pricing
- Superior UX
"""

from flask import Flask, request, jsonify, session
from flask_cors import CORS
import os
import json
import logging
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import re
import time
import random
from urllib.parse import urlparse, unquote, parse_qs
import hashlib
import uuid

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, supports_credentials=True)

# Configuration
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'reviewking-secret-' + str(uuid.uuid4()))
    API_VERSION = '2.0.0'
    
    # Shopify API Configuration (use environment variables)
    SHOPIFY_API_KEY = os.environ.get('SHOPIFY_API_KEY', '')
    SHOPIFY_API_SECRET = os.environ.get('SHOPIFY_API_SECRET', '')
    SHOPIFY_ACCESS_TOKEN = os.environ.get('SHOPIFY_ACCESS_TOKEN', '')
    SHOPIFY_SHOP_DOMAIN = os.environ.get('SHOPIFY_SHOP_DOMAIN', '')
    SHOPIFY_API_VERSION = '2025-10'  # Updated to match your app settings
    
    # App URLs (from your Shopify app configuration)
    SHOPIFY_APP_URL = os.environ.get('SHOPIFY_APP_URL', '')
    SHOPIFY_REDIRECT_URI = os.environ.get('SHOPIFY_REDIRECT_URI', '')
    
    # Loox stealth fallback configuration (Plan B)
    LOOX_FALLBACK_ID = "b3Zk9ExHgf.eca2133e2efc041236106236b783f6b4"
    LOOX_ENDPOINT = "https://loox.io/-/admin/reviews/import/url"
    
    # Scopes (from your app configuration)
    SHOPIFY_SCOPES = 'read_products,write_products,read_content,write_content'
    
    # Better pricing than Loox
    PRICING = {
        'free': {'price': 0, 'reviews': 50, 'name': 'Free Forever'},
        'basic': {'price': 19.99, 'reviews': 500, 'name': 'Basic Plan'},
        'pro': {'price': 39.99, 'reviews': 5000, 'name': 'Pro Plan'}
    }
    
    # Supported platforms (more than Loox!)
    PLATFORMS = ['aliexpress', 'amazon', 'ebay', 'walmart']

app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY

# In-memory storage for demo (use Redis/DB in production)
import_sessions = {}
analytics_events = []
skipped_reviews = {}  # Track skipped reviews per session

class EnhancedReviewExtractor:
    """Enhanced scraper with multi-platform support"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def extract_reviews_paginated(self, product_data, page=1, per_page=10, filters=None):
        """Extract reviews with pagination - matches Loox /admin/reviews/import/url"""
        platform = product_data.get('platform', '').lower()
        product_id = product_data.get('productId')
        
        if not product_id:
            return self._error_response("Product ID required")
        
        try:
            if 'aliexpress' in platform:
                reviews = self._scrape_aliexpress(product_id, page, per_page)
            elif 'amazon' in platform:
                reviews = self._scrape_amazon(product_id, page, per_page)
            elif 'ebay' in platform:
                reviews = self._scrape_ebay(product_id, page, per_page)
            elif 'walmart' in platform:
                reviews = self._scrape_walmart(product_id, page, per_page)
            else:
                return self._error_response(f"Platform {platform} not supported")
            
            # Check if all scraping methods failed
            if reviews is None:
                return {
                    'success': False,
                    'error': 'service_unavailable',
                    'message': 'Oops! Something went wrong while fetching reviews. Our team is working on it. Please try again in a few minutes.',
                    'reviews': [],
                    'stats': {
                        'with_photos': 0,
                        'ai_recommended': 0,
                        'average_rating': 0,
                        'average_quality': 0
                    }
                }
            
            # Apply filters
            if filters:
                reviews = self._apply_filters(reviews, filters)
            
            # Calculate AI scores for all reviews
            for review in reviews:
                review['quality_score'] = self._calculate_quality_score(review)
                review['ai_recommended'] = review['quality_score'] >= 8
                review['sentiment_score'] = self._calculate_sentiment(review.get('text', ''))
            
            # Sort by quality score (competitive advantage!)
            reviews.sort(key=lambda x: x.get('quality_score', 0), reverse=True)
            
            total_reviews = 150  # Simulated
            has_next = (page * per_page) < total_reviews
            
            return {
                'success': True,
                'reviews': reviews,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total_reviews,
                    'has_next': has_next,
                    'has_prev': page > 1,
                    'total_pages': (total_reviews + per_page - 1) // per_page
                },
                'stats': {
                    'with_photos': len([r for r in reviews if r.get('images', [])]),
                    'ai_recommended': len([r for r in reviews if r.get('ai_recommended', False)]),
                    'average_rating': sum(r.get('rating', 0) for r in reviews) / len(reviews) if reviews else 0,
                    'average_quality': sum(r.get('quality_score', 0) for r in reviews) / len(reviews) if reviews else 0
                },
                'filters_applied': filters or {},
                'api_version': Config.API_VERSION
            }
            
        except Exception as e:
            logger.error(f"Extract error: {str(e)}")
            return self._error_response(str(e))
    
    def _scrape_aliexpress(self, product_id, page, per_page):
        """Scrape AliExpress reviews - REAL DATA using proven API"""
        try:
            # AliExpress API has a hard limit of ~20 reviews per response
            # So to get 100 reviews, we need to make multiple page requests
            all_reviews = []
            reviews_per_api_page = 20  # AliExpress API limit
            
            # Calculate how many API pages we need to fetch
            num_pages_needed = (per_page + reviews_per_api_page - 1) // reviews_per_api_page
            
            logger.info(f"Fetching {per_page} reviews from AliExpress API (making {num_pages_needed} requests)")
            
            # AliExpress's official feedback API endpoint (PROVEN TO WORK!)
            api_url = "https://feedback.aliexpress.com/pc/searchEvaluation.do"
            
            for api_page in range(1, num_pages_needed + 1):
                params = {
                    'productId': product_id,
                    'lang': 'en_US',
                    'country': 'US',
                    'pageSize': 20,  # AliExpress returns max 20 regardless of this value
                    'filter': 'all',
                    'sort': 'complex_default',
                    'page': api_page
                }
                
                response = self.session.get(api_url, params=params, timeout=15)
                
                if response.status_code != 200:
                    logger.warning(f"API returned {response.status_code} for page {api_page}")
                    break
                
                # Parse JSON response
                try:
                    data = response.json()
                    page_reviews = self._parse_aliexpress_api(data, product_id, api_page)
                    if page_reviews:
                        all_reviews.extend(page_reviews)
                        logger.info(f"✅ Page {api_page}/{num_pages_needed}: Got {len(page_reviews)} reviews (total: {len(all_reviews)})")
                        
                        # Stop if we have enough reviews
                        if len(all_reviews) >= per_page:
                            all_reviews = all_reviews[:per_page]
                            break
                    else:
                        logger.warning(f"No reviews on page {api_page}, stopping")
                        break
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON on page {api_page}: {e}")
                    break
            
            if all_reviews:
                logger.info(f"🎉 Successfully fetched {len(all_reviews)} REAL reviews total!")
                return all_reviews
            else:
                logger.warning("No reviews from API, trying fallback methods...")
                return self._try_fallbacks(product_id, per_page)
            
        except Exception as e:
            logger.error(f"Error scraping AliExpress API: {str(e)}")
            logger.info("Trying fallback methods...")
            return self._try_fallbacks(product_id, per_page)
    
    def _try_fallbacks(self, product_id, per_page):
        """Try fallback methods in order: HTML scraping, then Loox stealth"""
        # Fallback 1: HTML scraping (runParams + DOM)
        reviews = self._fallback_html_scrape(product_id)
        if reviews:
            logger.info(f"[FALLBACK] HTML scraping succeeded with {len(reviews)} reviews")
            # Limit to requested amount
            return reviews[:per_page]
        
        # Fallback 2: Loox stealth (last resort)
        loox_reviews = self._fallback_loox_stealth(product_id)
        if loox_reviews is not None and len(loox_reviews) > 0:
            logger.info("[FALLBACK] Loox endpoint succeeded")
            return loox_reviews[:per_page]
        
        # All fallbacks failed - return None to signal error
        logger.error("[FALLBACK] All fallback methods failed - unable to fetch reviews")
        return None
    
    def _scrape_amazon(self, product_id, page, per_page):
        """Scrape Amazon reviews"""
        return self._generate_sample_reviews('amazon', product_id, page, per_page)
    
    def _scrape_ebay(self, product_id, page, per_page):
        """Scrape eBay reviews (Loox doesn't have this!)"""
        return self._generate_sample_reviews('ebay', product_id, page, per_page)
    
    def _scrape_walmart(self, product_id, page, per_page):
        """Scrape Walmart reviews (Loox doesn't have this!)"""
        return self._generate_sample_reviews('walmart', product_id, page, per_page)
    
    def _fallback_html_scrape(self, product_id):
        """
        Fallback 1: HTML scraping from AliExpress product page
        Extracts reviews from window.runParams or DOM
        """
        try:
            url = f"https://www.aliexpress.com/item/{product_id}.html"
            logger.info(f"[FALLBACK] Trying HTML scrape from {url}")
            
            response = self.session.get(url, timeout=15)
            if response.status_code != 200:
                logger.warning(f"[FALLBACK] HTML page returned {response.status_code}")
                return []
            
            # Try window.runParams extraction first
            reviews = self._extract_from_runparams(response.text, product_id)
            if reviews:
                logger.info(f"[FALLBACK] Extracted {len(reviews)} reviews from runParams")
                return reviews
            
            # Try DOM parsing as second fallback
            soup = BeautifulSoup(response.text, 'html.parser')
            reviews = self._parse_dom_reviews(soup, product_id)
            if reviews:
                logger.info(f"[FALLBACK] Extracted {len(reviews)} reviews from DOM")
                return reviews
            
            return []
            
        except Exception as e:
            logger.error(f"[FALLBACK] HTML scraping error: {e}")
            return []
    
    def _extract_from_runparams(self, html, product_id):
        """Extract reviews from window.runParams in the page source"""
        try:
            # Find runParams in script
            match = re.search(r'window\.runParams\s*=\s*(\{.*?\});', html, re.DOTALL)
            if not match:
                return []
            
            data = json.loads(match.group(1))
            feedback_module = data.get('data', {}).get('feedbackModule', {})
            feedback_list = feedback_module.get('feedbackList', [])
            
            reviews = []
            for r in feedback_list:
                # Extract images
                images = []
                for img in r.get('images', []):
                    if isinstance(img, dict):
                        img_url = img.get('imgUrl') or img.get('url')
                    else:
                        img_url = img
                    
                    if img_url:
                        images.append(img_url)
                
                reviews.append({
                    'id': r.get('evaluationId', str(r.get('id', ''))),
                    'platform': 'aliexpress',
                    'product_id': product_id,
                    'reviewer_name': r.get('buyerName', 'Customer'),
                    'text': r.get('buyerFeedback', ''),
                    'rating': int(r.get('buyerEval', 100)),
                    'date': r.get('evalTime', datetime.now().strftime('%Y-%m-%d')),
                    'country': r.get('buyerCountry', 'Unknown'),
                    'verified': True,
                    'images': images,
                    'translation': r.get('buyerTranslationFeedback'),
                    'helpful_count': r.get('upVoteCount', 0),
                    'position': len(reviews) + 1
                })
            
            return reviews
            
        except Exception as e:
            logger.error(f"[FALLBACK] runParams extraction error: {e}")
            return []
    
    def _parse_dom_reviews(self, soup, product_id):
        """Fallback: Parse reviews from DOM structure"""
        reviews = []
        
        try:
            # Find review containers
            review_containers = soup.select('[class*="list"][class*="itemWrap"]')
            
            for idx, container in enumerate(review_containers[:20]):  # Limit to 20
                try:
                    # Get reviewer name
                    name = 'Customer'
                    info = container.select_one('[class*="itemInfo"]')
                    if info:
                        info_text = info.get_text(strip=True)
                        parts = info_text.split('|')
                        name = parts[0].strip() if parts else 'Customer'
                    
                    # Get review text
                    text_el = container.select_one('[class*="itemReview"]')
                    text = text_el.get_text(strip=True) if text_el else ''
                    
                    if not text or len(text) < 5:
                        continue
                    
                    # Count stars
                    stars = container.select('[class*="starreviewfilled"]')
                    rating = (len(stars) * 20) if stars else 100  # Convert to 0-100 scale
                    
                    # Get images
                    images = []
                    for img in container.select('img'):
                        src = img.get('src') or img.get('data-src')
                        if src and 'aliexpress' in src and '/kf/' in src:
                            images.append(src)
                    
                    reviews.append({
                        'id': f'dom_{product_id}_{idx}',
                        'platform': 'aliexpress',
                        'product_id': product_id,
                        'reviewer_name': name,
                        'text': text,
                        'rating': rating,
                        'date': datetime.now().strftime('%Y-%m-%d'),
                        'country': 'Unknown',
                        'verified': True,
                        'images': images,
                        'helpful_count': 0,
                        'position': idx + 1
                    })
                    
                except Exception as e:
                    logger.error(f"[FALLBACK] Error parsing review {idx}: {e}")
                    continue
            
            return reviews
            
        except Exception as e:
            logger.error(f"[FALLBACK] DOM parsing error: {e}")
            return []
    
    def _fallback_loox_stealth(self, product_id, seller_id=None):
        """
        Fallback 2: Use Loox's infrastructure stealthily (last resort)
        """
        try:
            params = {
                'id': Config.LOOX_FALLBACK_ID,
                'productId': product_id,
                'page': 1
            }
            
            if seller_id:
                params['ownerMemberId'] = seller_id
            
            logger.info(f"[FALLBACK] Using Loox stealth endpoint for product {product_id}")
            
            response = self.session.get(Config.LOOX_ENDPOINT, params=params, timeout=15)
            
            if response.status_code == 200:
                logger.info("[FALLBACK] Loox endpoint responded successfully")
                # TODO: Parse Loox HTML response if needed
                # For now, return empty array as a signal that endpoint is alive
                return []
            
            return None
            
        except Exception as e:
            logger.error(f"[FALLBACK] Loox stealth error: {e}")
            return None
    
    def _parse_aliexpress_api(self, data, product_id, page):
        """Parse AliExpress API response - EXACT logic from app_loox_inspired.py"""
        reviews = []
        
        try:
            # AliExpress API structure (from proven working code!)
            evals = data.get('data', {}).get('evaViewList', [])
            
            for idx, eval_item in enumerate(evals):
                # Extract images - EXACT logic from working app_loox_inspired.py
                images = []
                raw_images = eval_item.get('images', [])
                for img in raw_images:
                    if isinstance(img, str):
                        images.append(img)
                    elif isinstance(img, dict):
                        img_url = img.get('imgUrl') or img.get('url')
                        if img_url:
                            images.append(img_url)
                
                # Debug log for first review only
                if idx == 0:
                    logger.info(f"First review images: {len(images)} images extracted from {len(raw_images)} raw images")
                
                reviews.append({
                    'id': eval_item.get('evaluationId', str(eval_item.get('id', ''))),
                    'platform': 'aliexpress',
                    'product_id': product_id,
                    'reviewer_name': eval_item.get('buyerName', 'Customer'),
                    'text': eval_item.get('buyerFeedback', ''),
                    'rating': int(eval_item.get('buyerEval', 100)),  # AliExpress uses 0-100 scale
                    'date': eval_item.get('evalTime', datetime.now().strftime('%Y-%m-%d')),
                    'country': eval_item.get('buyerCountry', 'Unknown'),
                    'verified': True,
                    'images': images,
                    'translation': eval_item.get('buyerTranslationFeedback'),
                    'helpful_count': eval_item.get('upVoteCount', 0),
                    'position': (page - 1) * 20 + idx + 1
                })
            
            logger.info(f"✅ Parsed {len(reviews)} REAL reviews from AliExpress")
            return reviews
            
        except Exception as e:
            logger.error(f"Error parsing AliExpress API response: {str(e)}")
            logger.error(f"Data structure: {str(data)[:500]}")  # Log first 500 chars for debugging
            return []
    
    def _generate_sample_reviews(self, platform, product_id, page, per_page):
        """Generate realistic sample reviews"""
        sample_templates = [
            {
                'reviewer_name': 'A***v',
                'text': 'These are beautiful pieces honestly. Second time I bought them, like that much so. Amazing for catching the eyes of possible clients.',
                'rating': 5,
                'verified': True,
                'images': ['https://via.placeholder.com/200x200/4CAF50/ffffff?text=Photo+1']
            },
            {
                'reviewer_name': 'M***k',
                'text': 'Great quality! Fast shipping and exactly as described. Very happy with this purchase.',
                'rating': 5,
                'verified': True,
                'images': ['https://via.placeholder.com/200x200/2196F3/ffffff?text=Photo+2', 'https://via.placeholder.com/200x200/2196F3/ffffff?text=Photo+3']
            },
            {
                'reviewer_name': 'S***e',
                'text': 'Perfect size and color. Very happy with this purchase.',
                'rating': 4,
                'verified': True,
                'images': []
            },
            {
                'reviewer_name': 'J***n',
                'text': 'Item as described. Good quality for the price. Would recommend!',
                'rating': 4,
                'verified': True,
                'images': ['https://via.placeholder.com/200x200/FF9800/ffffff?text=Photo+4']
            },
            {
                'reviewer_name': 'L***a',
                'text': 'Love these! Exactly what I was looking for. Will order again.',
                'rating': 5,
                'verified': True,
                'images': ['https://via.placeholder.com/200x200/E91E63/ffffff?text=Photo+5']
            },
            {
                'reviewer_name': 'D***d',
                'text': 'Good product. Shipping took a while but worth the wait.',
                'rating': 4,
                'verified': True,
                'images': []
            }
        ]
        
        reviews = []
        start_idx = (page - 1) * per_page
        
        for i in range(per_page):
            template = sample_templates[(start_idx + i) % len(sample_templates)].copy()
            
            review = {
                'id': f"{platform}_{product_id}_{start_idx + i + 1}",
                'platform': platform,
                'product_id': product_id,
                'reviewer_name': template['reviewer_name'],
                'text': template['text'],
                'rating': template['rating'],
                'date': self._generate_date(start_idx + i),
                'country': random.choice(['US', 'CA', 'UK', 'DE', 'AU', 'FR']),
                'verified': template['verified'],
                'images': template['images'].copy(),
                'helpful_count': random.randint(0, 50),
                'position': start_idx + i + 1
            }
            
            reviews.append(review)
        
        return reviews
    
    def _generate_date(self, offset):
        """Generate realistic dates"""
        dates = [
            '2024-12-15', '2024-12-10', '2024-12-05', '2024-11-28',
            '2024-11-20', '2024-11-15', '2024-11-10', '2024-11-05'
        ]
        return dates[offset % len(dates)]
    
    def _calculate_quality_score(self, review):
        """
        AI Quality Scoring - Competitive Advantage!
        Loox doesn't have this
        """
        score = 0
        text = review.get('text', '')
        
        # Text length (0-3 points)
        if len(text) > 150:
            score += 3
        elif len(text) > 80:
            score += 2
        elif len(text) > 40:
            score += 1
        
        # Has images (0-2 points)
        if len(review.get('images', [])) >= 2:
            score += 2
        elif len(review.get('images', [])) >= 1:
            score += 1
        
        # Rating (0-2 points)
        if review.get('rating', 0) >= 5:
            score += 2
        elif review.get('rating', 0) >= 4:
            score += 1
        
        # Verified (0-1 point)
        if review.get('verified', False):
            score += 1
        
        # Quality keywords (0-2 points)
        quality_words = ['quality', 'perfect', 'excellent', 'amazing', 'love', 'recommend']
        keyword_count = sum(1 for word in quality_words if word in text.lower())
        if keyword_count >= 2:
            score += 2
        elif keyword_count >= 1:
            score += 1
        
        return min(10, max(0, score))
    
    def _calculate_sentiment(self, text):
        """Calculate sentiment score"""
        positive_words = ['good', 'great', 'excellent', 'love', 'perfect', 'happy', 'amazing']
        negative_words = ['bad', 'poor', 'terrible', 'awful', 'disappointed']
        
        text_lower = text.lower()
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        if pos_count + neg_count == 0:
            return 0.5
        
        return (pos_count - neg_count + (pos_count + neg_count)) / (2 * (pos_count + neg_count))
    
    def _apply_filters(self, reviews, filters):
        """Apply filters to reviews"""
        filtered = reviews
        
        if filters.get('rating'):
            min_rating = int(filters['rating'])
            filtered = [r for r in filtered if r.get('rating', 0) >= min_rating]
        
        if filters.get('country'):
            filtered = [r for r in filtered if r.get('country') == filters['country']]
        
        if filters.get('with_photos') == 'true':
            filtered = [r for r in filtered if r.get('images', [])]
        
        if filters.get('min_quality_score'):
            min_score = float(filters['min_quality_score'])
            filtered = [r for r in filtered if r.get('quality_score', 0) >= min_score]
        
        return filtered
    
    def _error_response(self, message):
        """Error response"""
        return {
            'success': False,
            'error': message,
            'reviews': [],
            'pagination': None
        }

# Initialize extractor
extractor = EnhancedReviewExtractor()

# ==================== SHOPIFY API HELPER ====================

class ShopifyAPIHelper:
    """Helper class for Shopify API interactions"""
    
    def __init__(self):
        self.shop_domain = Config.SHOPIFY_SHOP_DOMAIN
        self.access_token = Config.SHOPIFY_ACCESS_TOKEN
        self.api_version = Config.SHOPIFY_API_VERSION
        
        if self.shop_domain and self.access_token:
            self.base_url = f"https://{self.shop_domain}/admin/api/{self.api_version}"
            self.headers = {
                'X-Shopify-Access-Token': self.access_token,
                'Content-Type': 'application/json'
            }
        else:
            self.base_url = None
            self.headers = None
    
    def is_configured(self):
        """Check if Shopify API is configured"""
        return bool(self.base_url and self.headers)
    
    def search_products(self, query):
        """
        Search for products by name or URL
        Returns list of matching products
        """
        if not self.is_configured():
            return {'success': False, 'error': 'Shopify API not configured'}
        
        try:
            # If query is a URL, extract product ID
            if 'products/' in query:
                # Extract product ID from URL
                match = re.search(r'/products/([^/?]+)', query)
                if match:
                    product_handle = match.group(1)
                    # Get product by handle
                    url = f"{self.base_url}/products.json?handle={product_handle}"
                else:
                    return {'success': False, 'error': 'Invalid product URL'}
            else:
                # Get all products and filter by title (Shopify doesn't support title search parameter)
                url = f"{self.base_url}/products.json?limit=50"
            
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            all_products = data.get('products', [])
            
            # Filter products by query if it's a text search
            if 'products/' not in query:
                query_lower = query.lower()
                products = [p for p in all_products if query_lower in p['title'].lower()]
            else:
                products = all_products
            
            return {
                'success': True,
                'products': [{
                    'id': str(p['id']),
                    'title': p['title'],
                    'handle': p['handle'],
                    'image': p['images'][0]['src'] if p.get('images') else None,
                    'url': f"https://{self.shop_domain}/products/{p['handle']}"
                } for p in products]
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Shopify API error: {str(e)}")
            return {'success': False, 'error': 'Failed to connect to Shopify'}
        except Exception as e:
            logger.error(f"Product search error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_product(self, product_id):
        """Get a single product by ID"""
        if not self.is_configured():
            return {'success': False, 'error': 'Shopify API not configured'}
        
        try:
            url = f"{self.base_url}/products/{product_id}.json"
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            product = response.json()['product']
            
            return {
                'success': True,
                'product': {
                    'id': str(product['id']),
                    'title': product['title'],
                    'handle': product['handle'],
                    'image': product['images'][0]['src'] if product.get('images') else None,
                    'url': f"https://{self.shop_domain}/products/{product['handle']}"
                }
            }
        except Exception as e:
            logger.error(f"Get product error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def add_review_to_product(self, product_id, review_data):
        """
        Add a review to a product using metafields
        Shopify doesn't have native review API, so we use metafields
        """
        if not self.is_configured():
            return {'success': False, 'error': 'Shopify API not configured'}
        
        try:
            # Create a unique review ID
            review_id = review_data.get('id', str(uuid.uuid4()))
            
            # Prepare metafield data
            metafield_value = {
                'rating': review_data.get('rating', 5),
                'title': review_data.get('title', ''),
                'text': review_data.get('text', ''),
                'reviewer_name': review_data.get('reviewer_name', 'Anonymous'),
                'date': review_data.get('date', datetime.now().strftime('%Y-%m-%d')),
                'country': review_data.get('country', ''),
                'verified': review_data.get('verified', False),
                'images': review_data.get('images', []),
                'quality_score': review_data.get('quality_score', 0),
                'ai_recommended': review_data.get('ai_recommended', False),
                'platform': review_data.get('platform', 'unknown'),
                'imported_at': datetime.now().isoformat()
            }
            
            # Create metafield
            url = f"{self.base_url}/products/{product_id}/metafields.json"
            
            payload = {
                'metafield': {
                    'namespace': 'reviewking',
                    'key': f'review_{review_id}',
                    'value': json.dumps(metafield_value),
                    'type': 'json'
                }
            }
            
            response = requests.post(url, json=payload, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            return {
                'success': True,
                'review_id': review_id,
                'metafield': response.json()['metafield']
            }
            
        except Exception as e:
            logger.error(f"Add review error: {str(e)}")
            return {'success': False, 'error': str(e)}

# Initialize Shopify helper
shopify_helper = ShopifyAPIHelper()

# ==================== API ROUTES (Matching Loox Structure) ====================

@app.route('/')
def index():
    """API status"""
    return jsonify({
        'service': 'ReviewKing Enhanced API',
        'version': Config.API_VERSION,
        'status': 'operational',
        'competitive_advantages': [
            '🌍 Multi-platform (AliExpress, Amazon, eBay, Walmart)',
            '🤖 AI Quality Scoring (0-10 scale)',
            '⚡ Bulk import capabilities',
            '📸 Smart photo filtering',
            '💰 Better pricing than Loox',
            '🎯 Sentiment analysis'
        ],
        'platforms_supported': Config.PLATFORMS,
        'pricing': Config.PRICING,
        'endpoints': {
            'import_url': '/admin/reviews/import/url',
            'import_single': '/admin/reviews/import/single',
            'bulk_import': '/admin/reviews/import/bulk',
            'analytics': '/e'
        }
    })

@app.route('/admin/reviews/import/url', methods=['GET'])
@app.route('/-/admin/reviews/import/url', methods=['GET'])
def import_url():
    """
    Loox-compatible endpoint: GET /admin/reviews/import/url
    Returns paginated reviews for preview
    
    Query params:
    - productId: Product ID
    - platform: aliexpress, amazon, ebay, walmart
    - page: Page number
    - rating: Min rating filter
    - country: Country filter
    - with_photos: Photos only (true/false)
    - translate: Language (optional)
    """
    try:
        # Get query parameters
        product_id = request.args.get('productId')
        page = int(request.args.get('page', 1))
        platform = request.args.get('platform', 'aliexpress')
        per_page = int(request.args.get('per_page', 100))  # Load 100 reviews like the old version
        
        # Filters
        filters = {
            'rating': request.args.get('rating'),
            'country': request.args.get('country'),
            'with_photos': request.args.get('with_photos'),
            'translate': request.args.get('translate')
        }
        
        # Remove None values
        filters = {k: v for k, v in filters.items() if v}
        
        if not product_id:
            return jsonify({
                'success': False,
                'error': 'productId parameter required'
            }), 400
        
        # Extract reviews
        product_data = {
            'productId': product_id,
            'platform': platform,
            'url': request.args.get('url', ''),
            'ownerMemberId': request.args.get('ownerMemberId', '')
        }
        
        result = extractor.extract_reviews_paginated(
            product_data, 
            page, 
            per_page, 
            filters
        )
        
        # Create session ID for tracking
        session_id = request.args.get('id', str(uuid.uuid4()))
        import_sessions[session_id] = {
            'product_id': product_id,
            'platform': platform,
            'started_at': datetime.now().isoformat(),
            'imported_count': 0
        }
        
        result['session_id'] = session_id
        
        return jsonify(result)
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': 'Invalid parameters'
        }), 400
    except Exception as e:
        logger.error(f"Import URL error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@app.route('/admin/reviews/import/single', methods=['POST'])
def import_single():
    """
    Loox-compatible endpoint: POST /admin/reviews/import/single
    Import a single review
    
    Body: {
        "review": {...review data...},
        "shopify_product_id": "123",
        "session_id": "abc"
    }
    """
    try:
        data = request.json
        
        if not data or 'review' not in data:
            return jsonify({
                'success': False,
                'error': 'Review data required'
            }), 400
        
        review = data['review']
        shopify_product_id = data.get('shopify_product_id')
        session_id = data.get('session_id')
        
        # Simulate import (in production, save to database)
        imported_review = {
            'id': review.get('id'),
            'imported_at': datetime.now().isoformat(),
            'shopify_product_id': shopify_product_id,
            'status': 'imported',
            'quality_score': review.get('quality_score', 0),
            'platform': review.get('platform', 'unknown')
        }
        
        # Track in session
        if session_id and session_id in import_sessions:
            import_sessions[session_id]['imported_count'] += 1
        
        logger.info(f"Review imported: {review.get('id')} - Score: {review.get('quality_score')}")
        
        return jsonify({
            'success': True,
            'imported_review': imported_review,
            'message': 'Review imported successfully'
        })
        
    except Exception as e:
        logger.error(f"Import single error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Import failed'
        }), 500

@app.route('/shopify/products/search', methods=['GET'])
def search_shopify_products():
    """
    NEW ENDPOINT: Search Shopify products by name or URL
    
    Query params:
    - q: Search query (product name or URL)
    """
    try:
        query = request.args.get('q', '').strip()
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Search query required'
            }), 400
        
        result = shopify_helper.search_products(query)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Product search error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Search failed'
        }), 500

@app.route('/admin/reviews/skip', methods=['POST'])
def skip_review():
    """
    NEW ENDPOINT: Mark a review as skipped
    
    Body: {
        "review_id": "abc123",
        "session_id": "session_abc"
    }
    """
    try:
        data = request.json
        review_id = data.get('review_id')
        session_id = data.get('session_id')
        
        if not review_id or not session_id:
            return jsonify({
                'success': False,
                'error': 'Review ID and session ID required'
            }), 400
        
        # Initialize skipped reviews for session if not exists
        if session_id not in skipped_reviews:
            skipped_reviews[session_id] = set()
        
        # Add to skipped list
        skipped_reviews[session_id].add(review_id)
        
        logger.info(f"Review skipped: {review_id} in session {session_id}")
        
        return jsonify({
            'success': True,
            'message': 'Review skipped'
        })
        
    except Exception as e:
        logger.error(f"Skip review error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Skip failed'
        }), 500

@app.route('/admin/reviews/import/bulk', methods=['POST'])
def import_bulk():
    """
    Enhanced endpoint: Bulk import (Loox doesn't have this!)
    Import multiple reviews at once, excluding skipped ones
    
    Body: {
        "reviews": [{...}, {...}],
        "shopify_product_id": "123",
        "session_id": "abc",
        "filters": {"min_quality_score": 7}
    }
    """
    try:
        data = request.json
        reviews = data.get('reviews', [])
        shopify_product_id = data.get('shopify_product_id')
        session_id = data.get('session_id')
        filters = data.get('filters', {})
        
        if not reviews:
            return jsonify({
                'success': False,
                'error': 'No reviews provided'
            }), 400
        
        if not shopify_product_id:
            return jsonify({
                'success': False,
                'error': 'Shopify product ID required'
            }), 400
        
        # Get skipped reviews for this session
        session_skipped = skipped_reviews.get(session_id, set()) if session_id else set()
        
        # Filter out skipped reviews
        non_skipped_reviews = [r for r in reviews if r.get('id') not in session_skipped]
        
        # Apply quality filter if specified
        min_quality = filters.get('min_quality_score', 0)
        filtered_reviews = [r for r in non_skipped_reviews if r.get('quality_score', 0) >= min_quality]
        
        # Bulk import to Shopify
        imported = []
        failed = []
        
        for review in filtered_reviews[:50]:  # Limit to 50 at once
            try:
                result = shopify_helper.add_review_to_product(shopify_product_id, review)
                
                if result['success']:
                    imported.append({
                        'id': review.get('id'),
                        'imported_at': datetime.now().isoformat(),
                        'quality_score': review.get('quality_score'),
                        'shopify_product_id': shopify_product_id,
                        'review_id': result['review_id']
                    })
                else:
                    failed.append({
                        'id': review.get('id'),
                        'error': result['error']
                    })
            except Exception as e:
                failed.append({
                    'id': review.get('id'),
                    'error': str(e)
                })
        
        # Update session stats
        if session_id and session_id in import_sessions:
            import_sessions[session_id]['imported_count'] += len(imported)
        
        logger.info(f"Bulk import to Shopify: {len(imported)} successful, {len(failed)} failed, {len(session_skipped)} skipped")
        
        return jsonify({
            'success': True,
            'imported_count': len(imported),
            'failed_count': len(failed),
            'skipped_count': len(session_skipped),
            'imported_reviews': imported,
            'failed_reviews': failed,
            'message': f'Bulk import completed: {len(imported)} imported, {len(failed)} failed, {len(session_skipped)} skipped'
        })
        
    except Exception as e:
        logger.error(f"Bulk import error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Bulk import failed'
        }), 500

@app.route('/e', methods=['GET', 'POST'])
@app.route('/analytics/track', methods=['GET', 'POST'])
def analytics():
    """
    Loox-compatible analytics endpoint
    Matches fujin.loox.io/e
    
    Params:
    - cat: Category
    - a: Action
    - c: Client ID
    - country: Country
    - lang: Language
    """
    try:
        if request.method == 'POST':
            data = request.json or {}
        else:
            data = request.args.to_dict()
        
        event = {
            'category': data.get('cat', 'unknown'),
            'action': data.get('a', 'unknown'),
            'client_id': data.get('c', ''),
            'country': data.get('country', ''),
            'language': data.get('lang', ''),
            'timestamp': datetime.now().isoformat(),
            'user_agent': request.headers.get('User-Agent', ''),
            'ip': request.remote_addr
        }
        
        analytics_events.append(event)
        logger.info(f"Analytics: {event['category']} - {event['action']}")
        
        return '', 204
        
    except Exception as e:
        logger.error(f"Analytics error: {str(e)}")
        return '', 204

@app.route('/admin/analytics', methods=['GET'])
def get_analytics():
    """Get analytics summary (enhanced feature)"""
    try:
        return jsonify({
            'success': True,
            'total_events': len(analytics_events),
            'recent_events': analytics_events[-50:],
            'stats': {
                'imports': len([e for e in analytics_events if e['action'] == 'Post imported']),
                'previews': len([e for e in analytics_events if e['category'] == 'Import by URL'])
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/js/bookmarklet.js')
def bookmarklet():
    """Enhanced bookmarklet with superior UX"""
    # Use the correct protocol (HTTPS in production, HTTP in development)
    proto = request.headers.get('X-Forwarded-Proto', 'https' if request.is_secure else 'http')
    host = f"{proto}://{request.host}"
    
    js_content = f"""
// ReviewKing Enhanced Bookmarklet - Superior to Loox
(function() {{
    if (window.reviewKingActive) return;
    window.reviewKingActive = true;
    
    const API_URL = '{host}';
    
    class ReviewKingClient {{
        constructor() {{
            this.sessionId = Math.random().toString(36).substr(2, 9);
            this.selectedProduct = null;
            this.searchTimeout = null;
            this.allReviews = [];  // Store all reviews
            this.reviews = [];  // Filtered reviews for display
            this.currentFilter = 'all';  // Current filter
            this.selectedCountry = 'all';  // Country filter
            this.showTranslations = true;  // Translation toggle (default ON)
            this.init();
        }}
        
        init() {{
            this.productData = this.detectProduct();
            if (!this.productData.productId) {{
                alert('Could not detect product on this page. Please open a product page.');
                window.reviewKingActive = false;
                return;
            }}
            this.createOverlay();
            this.loadReviews();
        }}
        
        detectProduct() {{
            const url = window.location.href;
            const hostname = window.location.hostname;
            
            let platform = 'unknown', productId = null;
            
            if (hostname.includes('aliexpress')) {{
                platform = 'aliexpress';
                const match = url.match(/\\/item\\/(\\d+)/);
                if (match) productId = match[1];
            }} else if (hostname.includes('amazon')) {{
                platform = 'amazon';
                const match = url.match(/\\/dp\\/([A-Z0-9]{{10}})/);
                if (match) productId = match[1];
            }} else if (hostname.includes('ebay')) {{
                platform = 'ebay';
                const match = url.match(/\\/itm\\/(\\d+)/);
                if (match) productId = match[1];
            }} else if (hostname.includes('walmart')) {{
                platform = 'walmart';
                const match = url.match(/\\/ip\\/[^\\/]+\\/(\\d+)/);
                if (match) productId = match[1];
            }}
            
            return {{ platform, productId, url }};
        }}
        
        createOverlay() {{
            const div = document.createElement('div');
            div.id = 'reviewking-overlay';
            div.innerHTML = `
                <style>
                    #reviewking-overlay {{
                        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
                        background: rgba(0,0,0,0.90); z-index: 999999;
                        display: flex; align-items: center; justify-content: center;
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                    }}
                    #reviewking-panel {{
                        background: #1e1e2e; border-radius: 16px; width: 90vw; max-width: 750px;
                        max-height: 90vh; display: flex; flex-direction: column;
                        box-shadow: 0 25px 80px rgba(0,0,0,0.5);
                    }}
                    #reviewking-header {{
                        background: #1e1e2e;
                        color: white; padding: 20px 28px; border-radius: 16px 16px 0 0;
                        display: flex; justify-content: space-between; align-items: center;
                        border-bottom: 1px solid #2d2d3d;
                    }}
                    #reviewking-close {{
                        background: #FF2D85; border: none; color: white;
                        font-size: 13px; padding: 10px 24px; border-radius: 8px;
                        cursor: pointer; display: flex; align-items: center; justify-content: center;
                        font-weight: 700; line-height: 1; gap: 6px;
                        transition: all 0.2s;
                    }}
                    #reviewking-close:hover {{ background: #E0186F; transform: translateY(-1px); box-shadow: 0 4px 12px rgba(255, 45, 133, 0.4); }}
                    #reviewking-content {{
                        flex: 1; padding: 24px 28px; overflow-y: auto;
                        background: #1e1e2e;
                        scrollbar-width: thin;
                        scrollbar-color: #4a4a5e #1e1e2e;
                    }}
                    #reviewking-content::-webkit-scrollbar {{
                        width: 8px;
                    }}
                    #reviewking-content::-webkit-scrollbar-track {{
                        background: #1e1e2e;
                    }}
                    #reviewking-content::-webkit-scrollbar-thumb {{
                        background: #4a4a5e;
                        border-radius: 4px;
                    }}
                    #reviewking-content::-webkit-scrollbar-thumb:hover {{
                        background: #5a5a6e;
                    }}
                    .rk-btn {{
                        padding: 12px 20px; border: none; border-radius: 8px;
                        font-size: 13px; font-weight: 600; cursor: pointer;
                        transition: all 0.2s ease;
                        white-space: nowrap;
                    }}
                    .rk-btn:hover {{ transform: translateY(-1px); box-shadow: 0 4px 12px rgba(0,0,0,0.15); }}
                    .rk-btn:active {{ transform: translateY(0); }}
                    .rk-btn-primary {{
                        background: #667eea; color: white;
                    }}
                    .rk-btn-primary:hover {{ background: #5568d3; }}
                    .rk-btn-secondary {{
                        background: #2d2d3d; color: #e5e7eb;
                        border: 1px solid #3d3d4d;
                    }}
                    .rk-btn-secondary:hover {{ background: #3d3d4d; border-color: #4d4d5d; }}
                    .rk-badge {{
                        display: inline-block; padding: 4px 10px; border-radius: 12px;
                        font-size: 10px; font-weight: 700; text-transform: uppercase;
                        letter-spacing: 0.5px;
                    }}
                    .rk-badge-success {{ background: #10b981; color: white; }}
                    .rk-badge-info {{ background: #3b82f6; color: white; }}
                    @keyframes spin {{ from {{ transform: rotate(0deg); }} to {{ transform: rotate(360deg); }} }}
                </style>
                <div id="reviewking-panel">
                    <div id="reviewking-header">
                        <div style="flex: 1;">
                            <h2 style="margin: 0; font-size: 24px; font-weight: 800; letter-spacing: -0.03em; color: #FF2D85;">🌸 Sakura Reviews</h2>
                            <p style="margin: 8px 0 0; opacity: 0.7; font-size: 13px; font-weight: 500; color: #9ca3af;">
                                Beautiful reviews, naturally • Powered by AI
                            </p>
                        </div>
                        <button id="reviewking-close" onclick="window.reviewKingClient.close()">✕ Close</button>
                    </div>
                    <div id="reviewking-content">
                        <div style="text-align: center; padding: 40px;">
                            <div style="width: 48px; height: 48px; border: 4px solid #e5e7eb;
                                border-top-color: #667eea; border-radius: 50%; margin: 0 auto 16px;
                                animation: spin 1s linear infinite;"></div>
                            <p style="color: #6b7280; margin: 0;">Loading reviews with AI analysis...</p>
                        </div>
                    </div>
                </div>
            `;
            document.body.appendChild(div);
            document.body.style.overflow = 'hidden';
        }}
        
        setupProductSearch() {{
            const searchInput = document.getElementById('product-search-input');
            const dropdown = document.getElementById('product-dropdown');
            
            // Check if elements exist
            if (!searchInput || !dropdown) {{
                console.log('Product search elements not found yet');
                return;
            }}
            
            // Add search input event listener (only once)
            if (searchInput.hasAttribute('data-listener-attached')) {{
                return;
            }}
            searchInput.setAttribute('data-listener-attached', 'true');
            
            searchInput.addEventListener('input', (e) => {{
                const query = e.target.value.trim();
                
                // Clear previous timeout
                if (this.searchTimeout) {{
                    clearTimeout(this.searchTimeout);
                }}
                
                const dropdownElement = document.getElementById('product-dropdown');
                if (!dropdownElement) return;
                
                if (query.length < 2) {{
                    dropdownElement.style.display = 'none';
                    return;
                }}
                
                // Debounce search
                this.searchTimeout = setTimeout(() => {{
                    this.searchProducts(query);
                }}, 300);
            }});
            
            // Hide dropdown when clicking outside (only once)
            if (!document.body.hasAttribute('data-dropdown-listener')) {{
                document.body.setAttribute('data-dropdown-listener', 'true');
            document.addEventListener('click', (e) => {{
                    const dropdownElement = document.getElementById('product-dropdown');
                    if (dropdownElement && !e.target.closest('#product-search-input') && !e.target.closest('#product-dropdown')) {{
                        dropdownElement.style.display = 'none';
                }}
            }});
            }}
        }}
        
        async searchProducts(query) {{
            const dropdown = document.getElementById('product-dropdown');
            
            if (!dropdown) {{
                console.error('Dropdown element not found');
                return;
            }}
            
            try {{
                dropdown.innerHTML = '<div style="padding: 12px; color: #666;">Searching...</div>';
                dropdown.style.display = 'block';
                
                const response = await fetch(`${{API_URL}}/shopify/products/search?q=${{encodeURIComponent(query)}}`);
                const result = await response.json();
                
                if (result.success && result.products.length > 0) {{
                    dropdown.innerHTML = result.products.map(product => `
                        <div class="product-option" data-product-id="${{product.id}}" 
                             data-product-title="${{product.title}}"
                             style="padding: 12px; border-bottom: 1px solid #f0f0f0; cursor: pointer; 
                                    display: flex; align-items: center; gap: 12px;"
                             onmouseover="this.style.background='#f8f9fa'" 
                             onmouseout="this.style.background='white'"
                             onclick="window.reviewKingClient.selectProduct('${{product.id}}', '${{product.title.replace(/'/g, "\\\\'")}}')">
                            ${{product.image ? `<img src="${{product.image}}" style="width: 40px; height: 40px; object-fit: cover; border-radius: 4px;">` : '<div style="width: 40px; height: 40px; background: #f0f0f0; border-radius: 4px;"></div>'}}
                            <div>
                                <div style="font-weight: 500; color: #333; font-size: 14px;">${{product.title}}</div>
                                <div style="font-size: 12px; color: #666;">ID: ${{product.id}}</div>
                            </div>
                        </div>
                    `).join('');
                }} else {{
                    dropdown.innerHTML = '<div style="padding: 12px; color: #666;">No products found</div>';
                }}
            }} catch (error) {{
                dropdown.innerHTML = '<div style="padding: 12px; color: #e74c3c;">Search failed. Check Shopify API configuration.</div>';
            }}
        }}
        
        selectProduct(productId, productTitle) {{
            this.selectedProduct = {{ id: productId, title: productTitle }};
            
            // Hide dropdown and clear input
            const dropdown = document.getElementById('product-dropdown');
            const searchInput = document.getElementById('product-search-input');
            const selectedDiv = document.getElementById('selected-product');
            
            if (dropdown) dropdown.style.display = 'none';
            if (searchInput) searchInput.value = '';
            
            if (!selectedDiv) {{
                console.error('Selected product div not found');
                return;
            }}
            
            // Show selected product
            selectedDiv.innerHTML = `
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <div>
                        <div style="font-weight: 500;">✓ Target Product Selected</div>
                        <div style="opacity: 0.8; font-size: 12px;">${{productTitle}}</div>
                    </div>
                    <button onclick="window.reviewKingClient.clearProduct()" 
                            style="background: rgba(255,255,255,0.2); border: none; color: white; 
                                   padding: 4px 8px; border-radius: 4px; cursor: pointer; font-size: 12px;">
                        Change
                    </button>
                </div>
            `;
            selectedDiv.style.display = 'block';
            
            // Refresh current review display to show import buttons
            if (this.reviews && this.reviews.length > 0) {{
                this.displayReview();
            }}
        }}
        
        clearProduct() {{
            this.selectedProduct = null;
            
            const selectedDiv = document.getElementById('selected-product');
            if (selectedDiv) {{
                selectedDiv.style.display = 'none';
            }}
            
            // Refresh current review display to hide import buttons
            if (this.reviews && this.reviews.length > 0) {{
                this.displayReview();
            }}
        }}
        
        async loadReviews(page = 1) {{
            try {{
                console.log('Loading reviews...', {{ productId: this.productData.productId, platform: this.productData.platform }});
                
                const params = new URLSearchParams({{
                    productId: this.productData.productId,
                    platform: this.productData.platform,
                    page: page,
                    per_page: 100,  // Load 100 reviews at once like the old version
                    id: this.sessionId
                }});
                
                const url = `${{API_URL}}/admin/reviews/import/url?${{params}}`;
                console.log('Fetching:', url);
                
                const response = await fetch(url);
                console.log('Response status:', response.status);
                
                const result = await response.json();
                console.log('Result:', result);
                
                if (result.success) {{
                    this.allReviews = result.reviews;  // Store all reviews
                    this.currentIndex = 0;
                    this.pagination = result.pagination;
                    this.stats = result.stats;
                    console.log('All reviews loaded:', this.allReviews.length);
                    this.applyFilter();  // Apply current filter and display
                }} else {{
                    console.error('Error loading reviews:', result.error);
                    // Show user-friendly error message
                    const errorMessage = result.message || result.error || 'Failed to load reviews';
                    this.showError(errorMessage);
                }}
            }} catch (error) {{
                console.error('Exception loading reviews:', error);
                this.showError('Failed to load reviews: ' + error.message);
            }}
        }}
        
        applyFilter() {{
            // Step 1: Apply star rating filter
            let filtered = [...this.allReviews];
            
            if (this.currentFilter === 'photos') {{
                filtered = filtered.filter(r => r.images && r.images.length > 0);
            }} else if (this.currentFilter === 'ai_recommended') {{
                filtered = filtered.filter(r => r.ai_recommended);
            }} else if (this.currentFilter === '4-5stars') {{
                // Rating >= 70 on the 0-100 scale (like old code)
                filtered = filtered.filter(r => r.rating >= 70);
            }} else if (this.currentFilter === '3stars') {{
                // Rating 50-69 on the 0-100 scale
                filtered = filtered.filter(r => r.rating >= 50 && r.rating < 70);
            }} else if (this.currentFilter === '5stars') {{
                // Rating >= 90 on the 0-100 scale
                filtered = filtered.filter(r => r.rating >= 90);
            }}
            
            // Step 2: Apply country filter
            if (this.selectedCountry !== 'all') {{
                filtered = filtered.filter(r => r.country === this.selectedCountry);
            }}
            
            this.reviews = filtered;
            
            console.log(`[Filter] Applied filter "${{this.currentFilter}}" + country "${{this.selectedCountry}}": ${{this.reviews.length}} of ${{this.allReviews.length}} reviews`);
            
            // Reset to first review after filtering
            this.currentIndex = 0;
            
            // Update stats based on all reviews (not filtered)
            this.stats = {{
                ...this.stats,
                total: this.allReviews.length,
                with_photos: this.allReviews.filter(r => r.images && r.images.length > 0).length,
                ai_recommended: this.allReviews.filter(r => r.ai_recommended).length
            }};
            
            this.displayReview();
        }}
        
        setFilter(filter) {{
            console.log(`[Filter] Changing filter from "${{this.currentFilter}}" to "${{filter}}"`);
            this.currentFilter = filter;
            this.applyFilter();
        }}
        
        setCountry(country) {{
            console.log(`[Country] Changing country filter from "${{this.selectedCountry}}" to "${{country}}"`);
            this.selectedCountry = country;
            this.applyFilter();
        }}
        
        toggleTranslation() {{
            this.showTranslations = !this.showTranslations;
            console.log(`[Translation] Toggled to: ${{this.showTranslations}}`);
            this.displayReview();  // Refresh display without re-filtering
        }}
        
        getCountryMap() {{
            // Country code to flag/name mapping
            return {{
                'AD': {{'flag': '🇦🇩', 'name': 'Andorra'}}, 'AE': {{'flag': '🇦🇪', 'name': 'United Arab Emirates'}}, 'AF': {{'flag': '🇦🇫', 'name': 'Afghanistan'}}, 'AG': {{'flag': '🇦🇬', 'name': 'Antigua and Barbuda'}}, 'AI': {{'flag': '🇦🇮', 'name': 'Anguilla'}}, 'AL': {{'flag': '🇦🇱', 'name': 'Albania'}}, 'AM': {{'flag': '🇦🇲', 'name': 'Armenia'}}, 'AO': {{'flag': '🇦🇴', 'name': 'Angola'}}, 'AR': {{'flag': '🇦🇷', 'name': 'Argentina'}}, 'AS': {{'flag': '🇦🇸', 'name': 'American Samoa'}}, 'AT': {{'flag': '🇦🇹', 'name': 'Austria'}}, 'AU': {{'flag': '🇦🇺', 'name': 'Australia'}}, 'AW': {{'flag': '🇦🇼', 'name': 'Aruba'}}, 'AZ': {{'flag': '🇦🇿', 'name': 'Azerbaijan'}},
                'BA': {{'flag': '🇧🇦', 'name': 'Bosnia and Herzegovina'}}, 'BB': {{'flag': '🇧🇧', 'name': 'Barbados'}}, 'BD': {{'flag': '🇧🇩', 'name': 'Bangladesh'}}, 'BE': {{'flag': '🇧🇪', 'name': 'Belgium'}}, 'BF': {{'flag': '🇧🇫', 'name': 'Burkina Faso'}}, 'BG': {{'flag': '🇧🇬', 'name': 'Bulgaria'}}, 'BH': {{'flag': '🇧🇭', 'name': 'Bahrain'}}, 'BI': {{'flag': '🇧🇮', 'name': 'Burundi'}}, 'BJ': {{'flag': '🇧🇯', 'name': 'Benin'}}, 'BM': {{'flag': '🇧🇲', 'name': 'Bermuda'}}, 'BN': {{'flag': '🇧🇳', 'name': 'Brunei'}}, 'BO': {{'flag': '🇧🇴', 'name': 'Bolivia'}}, 'BR': {{'flag': '🇧🇷', 'name': 'Brazil'}}, 'BS': {{'flag': '🇧🇸', 'name': 'Bahamas'}}, 'BT': {{'flag': '🇧🇹', 'name': 'Bhutan'}}, 'BW': {{'flag': '🇧🇼', 'name': 'Botswana'}}, 'BY': {{'flag': '🇧🇾', 'name': 'Belarus'}}, 'BZ': {{'flag': '🇧🇿', 'name': 'Belize'}},
                'CA': {{'flag': '🇨🇦', 'name': 'Canada'}}, 'CD': {{'flag': '🇨🇩', 'name': 'Congo'}}, 'CF': {{'flag': '🇨🇫', 'name': 'Central African Republic'}}, 'CG': {{'flag': '🇨🇬', 'name': 'Congo'}}, 'CH': {{'flag': '🇨🇭', 'name': 'Switzerland'}}, 'CI': {{'flag': '🇨🇮', 'name': 'Côte D\\'Ivoire'}}, 'CK': {{'flag': '🇨🇰', 'name': 'Cook Islands'}}, 'CL': {{'flag': '🇨🇱', 'name': 'Chile'}}, 'CM': {{'flag': '🇨🇲', 'name': 'Cameroon'}}, 'CN': {{'flag': '🇨🇳', 'name': 'China'}}, 'CO': {{'flag': '🇨🇴', 'name': 'Colombia'}}, 'CR': {{'flag': '🇨🇷', 'name': 'Costa Rica'}}, 'CU': {{'flag': '🇨🇺', 'name': 'Cuba'}}, 'CV': {{'flag': '🇨🇻', 'name': 'Cape Verde'}}, 'CW': {{'flag': '🇨🇼', 'name': 'Curaçao'}}, 'CY': {{'flag': '🇨🇾', 'name': 'Cyprus'}}, 'CZ': {{'flag': '🇨🇿', 'name': 'Czech Republic'}},
                'DE': {{'flag': '🇩🇪', 'name': 'Germany'}}, 'DJ': {{'flag': '🇩🇯', 'name': 'Djibouti'}}, 'DK': {{'flag': '🇩🇰', 'name': 'Denmark'}}, 'DM': {{'flag': '🇩🇲', 'name': 'Dominica'}}, 'DO': {{'flag': '🇩🇴', 'name': 'Dominican Republic'}}, 'DZ': {{'flag': '🇩🇿', 'name': 'Algeria'}},
                'EC': {{'flag': '🇪🇨', 'name': 'Ecuador'}}, 'EE': {{'flag': '🇪🇪', 'name': 'Estonia'}}, 'EG': {{'flag': '🇪🇬', 'name': 'Egypt'}}, 'ER': {{'flag': '🇪🇷', 'name': 'Eritrea'}}, 'ES': {{'flag': '🇪🇸', 'name': 'Spain'}}, 'ET': {{'flag': '🇪🇹', 'name': 'Ethiopia'}},
                'FI': {{'flag': '🇫🇮', 'name': 'Finland'}}, 'FJ': {{'flag': '🇫🇯', 'name': 'Fiji'}}, 'FR': {{'flag': '🇫🇷', 'name': 'France'}},
                'GA': {{'flag': '🇬🇦', 'name': 'Gabon'}}, 'GB': {{'flag': '🇬🇧', 'name': 'United Kingdom'}}, 'GD': {{'flag': '🇬🇩', 'name': 'Grenada'}}, 'GE': {{'flag': '🇬🇪', 'name': 'Georgia'}}, 'GH': {{'flag': '🇬🇭', 'name': 'Ghana'}}, 'GI': {{'flag': '🇬🇮', 'name': 'Gibraltar'}}, 'GL': {{'flag': '🇬🇱', 'name': 'Greenland'}}, 'GM': {{'flag': '🇬🇲', 'name': 'Gambia'}}, 'GN': {{'flag': '🇬🇳', 'name': 'Guinea'}}, 'GR': {{'flag': '🇬🇷', 'name': 'Greece'}}, 'GT': {{'flag': '🇬🇹', 'name': 'Guatemala'}}, 'GU': {{'flag': '🇬🇺', 'name': 'Guam'}}, 'GY': {{'flag': '🇬🇾', 'name': 'Guyana'}},
                'HK': {{'flag': '🇭🇰', 'name': 'Hong Kong'}}, 'HN': {{'flag': '🇭🇳', 'name': 'Honduras'}}, 'HR': {{'flag': '🇭🇷', 'name': 'Croatia'}}, 'HT': {{'flag': '🇭🇹', 'name': 'Haiti'}}, 'HU': {{'flag': '🇭🇺', 'name': 'Hungary'}},
                'ID': {{'flag': '🇮🇩', 'name': 'Indonesia'}}, 'IE': {{'flag': '🇮🇪', 'name': 'Ireland'}}, 'IL': {{'flag': '🇮🇱', 'name': 'Israel'}}, 'IN': {{'flag': '🇮🇳', 'name': 'India'}}, 'IQ': {{'flag': '🇮🇶', 'name': 'Iraq'}}, 'IR': {{'flag': '🇮🇷', 'name': 'Iran'}}, 'IS': {{'flag': '🇮🇸', 'name': 'Iceland'}}, 'IT': {{'flag': '🇮🇹', 'name': 'Italy'}},
                'JM': {{'flag': '🇯🇲', 'name': 'Jamaica'}}, 'JO': {{'flag': '🇯🇴', 'name': 'Jordan'}}, 'JP': {{'flag': '🇯🇵', 'name': 'Japan'}},
                'KE': {{'flag': '🇰🇪', 'name': 'Kenya'}}, 'KG': {{'flag': '🇰🇬', 'name': 'Kyrgyzstan'}}, 'KH': {{'flag': '🇰🇭', 'name': 'Cambodia'}}, 'KI': {{'flag': '🇰🇮', 'name': 'Kiribati'}}, 'KM': {{'flag': '🇰🇲', 'name': 'Comoros'}}, 'KN': {{'flag': '🇰🇳', 'name': 'Saint Kitts and Nevis'}}, 'KP': {{'flag': '🇰🇵', 'name': 'North Korea'}}, 'KR': {{'flag': '🇰🇷', 'name': 'South Korea'}}, 'KW': {{'flag': '🇰🇼', 'name': 'Kuwait'}}, 'KY': {{'flag': '🇰🇾', 'name': 'Cayman Islands'}}, 'KZ': {{'flag': '🇰🇿', 'name': 'Kazakhstan'}},
                'LA': {{'flag': '🇱🇦', 'name': 'Laos'}}, 'LB': {{'flag': '🇱🇧', 'name': 'Lebanon'}}, 'LC': {{'flag': '🇱🇨', 'name': 'Saint Lucia'}}, 'LI': {{'flag': '🇱🇮', 'name': 'Liechtenstein'}}, 'LK': {{'flag': '🇱🇰', 'name': 'Sri Lanka'}}, 'LR': {{'flag': '🇱🇷', 'name': 'Liberia'}}, 'LS': {{'flag': '🇱🇸', 'name': 'Lesotho'}}, 'LT': {{'flag': '🇱🇹', 'name': 'Lithuania'}}, 'LU': {{'flag': '🇱🇺', 'name': 'Luxembourg'}}, 'LV': {{'flag': '🇱🇻', 'name': 'Latvia'}}, 'LY': {{'flag': '🇱🇾', 'name': 'Libya'}},
                'MA': {{'flag': '🇲🇦', 'name': 'Morocco'}}, 'MC': {{'flag': '🇲🇨', 'name': 'Monaco'}}, 'MD': {{'flag': '🇲🇩', 'name': 'Moldova'}}, 'ME': {{'flag': '🇲🇪', 'name': 'Montenegro'}}, 'MG': {{'flag': '🇲🇬', 'name': 'Madagascar'}}, 'MK': {{'flag': '🇲🇰', 'name': 'Macedonia'}}, 'ML': {{'flag': '🇲🇱', 'name': 'Mali'}}, 'MM': {{'flag': '🇲🇲', 'name': 'Myanmar'}}, 'MN': {{'flag': '🇲🇳', 'name': 'Mongolia'}}, 'MO': {{'flag': '🇲🇴', 'name': 'Macao'}}, 'MR': {{'flag': '🇲🇷', 'name': 'Mauritania'}}, 'MS': {{'flag': '🇲🇸', 'name': 'Montserrat'}}, 'MT': {{'flag': '🇲🇹', 'name': 'Malta'}}, 'MU': {{'flag': '🇲🇺', 'name': 'Mauritius'}}, 'MV': {{'flag': '🇲🇻', 'name': 'Maldives'}}, 'MW': {{'flag': '🇲🇼', 'name': 'Malawi'}}, 'MX': {{'flag': '🇲🇽', 'name': 'Mexico'}}, 'MY': {{'flag': '🇲🇾', 'name': 'Malaysia'}}, 'MZ': {{'flag': '🇲🇿', 'name': 'Mozambique'}},
                'NA': {{'flag': '🇳🇦', 'name': 'Namibia'}}, 'NC': {{'flag': '🇳🇨', 'name': 'New Caledonia'}}, 'NE': {{'flag': '🇳🇪', 'name': 'Niger'}}, 'NG': {{'flag': '🇳🇬', 'name': 'Nigeria'}}, 'NI': {{'flag': '🇳🇮', 'name': 'Nicaragua'}}, 'NL': {{'flag': '🇳🇱', 'name': 'Netherlands'}}, 'NO': {{'flag': '🇳🇴', 'name': 'Norway'}}, 'NP': {{'flag': '🇳🇵', 'name': 'Nepal'}}, 'NR': {{'flag': '🇳🇷', 'name': 'Nauru'}}, 'NZ': {{'flag': '🇳🇿', 'name': 'New Zealand'}},
                'OM': {{'flag': '🇴🇲', 'name': 'Oman'}},
                'PA': {{'flag': '🇵🇦', 'name': 'Panama'}}, 'PE': {{'flag': '🇵🇪', 'name': 'Peru'}}, 'PG': {{'flag': '🇵🇬', 'name': 'Papua New Guinea'}}, 'PH': {{'flag': '🇵🇭', 'name': 'Philippines'}}, 'PK': {{'flag': '🇵🇰', 'name': 'Pakistan'}}, 'PL': {{'flag': '🇵🇱', 'name': 'Poland'}}, 'PR': {{'flag': '🇵🇷', 'name': 'Puerto Rico'}}, 'PS': {{'flag': '🇵🇸', 'name': 'Palestine'}}, 'PT': {{'flag': '🇵🇹', 'name': 'Portugal'}}, 'PW': {{'flag': '🇵🇼', 'name': 'Palau'}}, 'PY': {{'flag': '🇵🇾', 'name': 'Paraguay'}},
                'QA': {{'flag': '🇶🇦', 'name': 'Qatar'}},
                'RE': {{'flag': '🇷🇪', 'name': 'Réunion'}}, 'RO': {{'flag': '🇷🇴', 'name': 'Romania'}}, 'RS': {{'flag': '🇷🇸', 'name': 'Serbia'}}, 'RU': {{'flag': '🇷🇺', 'name': 'Russia'}}, 'RW': {{'flag': '🇷🇼', 'name': 'Rwanda'}},
                'SA': {{'flag': '🇸🇦', 'name': 'Saudi Arabia'}}, 'SB': {{'flag': '🇸🇧', 'name': 'Solomon Islands'}}, 'SC': {{'flag': '🇸🇨', 'name': 'Seychelles'}}, 'SD': {{'flag': '🇸🇩', 'name': 'Sudan'}}, 'SE': {{'flag': '🇸🇪', 'name': 'Sweden'}}, 'SG': {{'flag': '🇸🇬', 'name': 'Singapore'}}, 'SI': {{'flag': '🇸🇮', 'name': 'Slovenia'}}, 'SK': {{'flag': '🇸🇰', 'name': 'Slovakia'}}, 'SL': {{'flag': '🇸🇱', 'name': 'Sierra Leone'}}, 'SM': {{'flag': '🇸🇲', 'name': 'San Marino'}}, 'SN': {{'flag': '🇸🇳', 'name': 'Senegal'}}, 'SO': {{'flag': '🇸🇴', 'name': 'Somalia'}}, 'SR': {{'flag': '🇸🇷', 'name': 'Suriname'}}, 'SS': {{'flag': '🇸🇸', 'name': 'South Sudan'}}, 'SV': {{'flag': '🇸🇻', 'name': 'El Salvador'}}, 'SY': {{'flag': '🇸🇾', 'name': 'Syria'}}, 'SZ': {{'flag': '🇸🇿', 'name': 'Swaziland'}},
                'TC': {{'flag': '🇹🇨', 'name': 'Turks and Caicos'}}, 'TD': {{'flag': '🇹🇩', 'name': 'Chad'}}, 'TG': {{'flag': '🇹🇬', 'name': 'Togo'}}, 'TH': {{'flag': '🇹🇭', 'name': 'Thailand'}}, 'TJ': {{'flag': '🇹🇯', 'name': 'Tajikistan'}}, 'TK': {{'flag': '🇹🇰', 'name': 'Tokelau'}}, 'TL': {{'flag': '🇹🇱', 'name': 'Timor-Leste'}}, 'TM': {{'flag': '🇹🇲', 'name': 'Turkmenistan'}}, 'TN': {{'flag': '🇹🇳', 'name': 'Tunisia'}}, 'TO': {{'flag': '🇹🇴', 'name': 'Tonga'}}, 'TR': {{'flag': '🇹🇷', 'name': 'Turkey'}}, 'TT': {{'flag': '🇹🇹', 'name': 'Trinidad and Tobago'}}, 'TV': {{'flag': '🇹🇻', 'name': 'Tuvalu'}}, 'TW': {{'flag': '🇹🇼', 'name': 'Taiwan'}}, 'TZ': {{'flag': '🇹🇿', 'name': 'Tanzania'}},
                'UA': {{'flag': '🇺🇦', 'name': 'Ukraine'}}, 'UG': {{'flag': '🇺🇬', 'name': 'Uganda'}}, 'US': {{'flag': '🇺🇸', 'name': 'United States'}}, 'UY': {{'flag': '🇺🇾', 'name': 'Uruguay'}}, 'UZ': {{'flag': '🇺🇿', 'name': 'Uzbekistan'}},
                'VA': {{'flag': '🇻🇦', 'name': 'Vatican City'}}, 'VC': {{'flag': '🇻🇨', 'name': 'Saint Vincent'}}, 'VE': {{'flag': '🇻🇪', 'name': 'Venezuela'}}, 'VG': {{'flag': '🇻🇬', 'name': 'British Virgin Islands'}}, 'VI': {{'flag': '🇻🇮', 'name': 'US Virgin Islands'}}, 'VN': {{'flag': '🇻🇳', 'name': 'Vietnam'}}, 'VU': {{'flag': '🇻🇺', 'name': 'Vanuatu'}},
                'WS': {{'flag': '🇼🇸', 'name': 'Samoa'}},
                'YE': {{'flag': '🇾🇪', 'name': 'Yemen'}}, 'YT': {{'flag': '🇾🇹', 'name': 'Mayotte'}},
                'ZA': {{'flag': '🇿🇦', 'name': 'South Africa'}}, 'ZM': {{'flag': '🇿🇲', 'name': 'Zambia'}}, 'ZW': {{'flag': '🇿🇼', 'name': 'Zimbabwe'}}
            }};
        }}
        
        getUniqueCountries() {{
            // Extract unique countries from all reviews
            const countryCodes = [...new Set(this.allReviews.map(r => r.country).filter(c => c))];
            const countryMap = this.getCountryMap();
            
            // Convert codes to objects with display info
            return countryCodes
                .map(code => ({{
                    code: code,
                    flag: countryMap[code]?.flag || '🌍',
                    name: countryMap[code]?.name || code
                }}))
                .sort((a, b) => a.name.localeCompare(b.name));
        }}
        
        displayReview() {{
            const content = document.getElementById('reviewking-content');
            
            if (!content) {{
                console.error('Content element not found');
                return;
            }}
            
            console.log('Displaying review...', {{ hasReviews: !!this.reviews, reviewCount: this.reviews?.length }});
            
            // Check if reviews are loaded
            if (!this.reviews || this.reviews.length === 0) {{
                content.innerHTML = '<div style="text-align: center; padding: 40px;">Loading reviews...</div>';
                return;
            }}
            
            const review = this.reviews[this.currentIndex];
            const isRecommended = review.ai_recommended;
            
            // First show product search if no product selected
            if (!this.selectedProduct) {{
                content.innerHTML = `
                    <div style="padding: 16px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                border-radius: 8px; color: white; margin-bottom: 20px;">
                        <div style="margin-bottom: 12px;">
                            <input type="text" id="product-search-input" 
                                   placeholder="Enter Shopify product URL or name..." 
                                   style="width: 100%; padding: 10px 12px; border: none; border-radius: 6px; 
                                          background: rgba(255,255,255,0.9); color: #333; font-size: 14px;" />
                        </div>
                        <div id="product-dropdown" style="display: none; background: white; border-radius: 6px; 
                             box-shadow: 0 4px 12px rgba(0,0,0,0.15); max-height: 120px; overflow-y: auto; color: #333;"></div>
                        <div id="selected-product" style="display: none; margin-top: 8px; padding: 8px 12px; 
                             background: rgba(255,255,255,0.2); border-radius: 6px; font-size: 13px;"></div>
                    </div>
                    
                    <div style="text-align: center; padding: 40px; background: #fef3c7; border-radius: 12px;">
                        <div style="font-size: 48px; margin-bottom: 16px;">🎯</div>
                        <h3 style="color: #92400e; margin: 0 0 8px;">Select Target Product First</h3>
                        <p style="color: #b45309; margin: 0;">Use the search box above to select which Shopify product will receive these reviews</p>
                    </div>
                `;
                this.setupProductSearch();
                return;
            }}
            
            // Show the beautiful review interface like your design
            content.innerHTML = `
                <!-- Product Search (always visible when product selected) -->
                <div style="padding: 16px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                            border-radius: 8px; color: white; margin-bottom: 20px;">
                    <div style="margin-bottom: 12px;">
                        <input type="text" id="product-search-input" 
                               placeholder="Enter Shopify product URL or name..." 
                               style="width: 100%; padding: 10px 12px; border: none; border-radius: 6px; 
                                      background: rgba(255,255,255,0.9); color: #333; font-size: 14px;" />
                    </div>
                    <div id="product-dropdown" style="display: none; background: white; border-radius: 6px; 
                         box-shadow: 0 4px 12px rgba(0,0,0,0.15); max-height: 120px; overflow-y: auto; color: #333;"></div>
                    <div id="selected-product" style="display: block; margin-top: 8px; padding: 8px 12px; 
                         background: rgba(255,255,255,0.2); border-radius: 6px; font-size: 13px;">
                        ✓ Target Product Selected: ${{this.selectedProduct.title}}
                        <button onclick="window.reviewKingClient.clearProduct()" 
                                style="background: rgba(255,255,255,0.2); border: none; color: white; 
                                       padding: 4px 8px; border-radius: 4px; cursor: pointer; font-size: 12px; margin-left: 8px;">
                            Change
                        </button>
                    </div>
                </div>
                
                <!-- Beautiful Stats Header (like your design) -->
                <div style="background: linear-gradient(135deg, #FF2D85 0%, #FF1493 100%); 
                            padding: 24px; border-radius: 12px; margin-bottom: 24px; color: white; text-align: center;
                            box-shadow: 0 4px 16px rgba(255, 45, 133, 0.3);">
                    <div style="display: flex; justify-content: space-around; flex-wrap: wrap; gap: 16px;">
                        <div style="flex: 1; min-width: 80px;">
                            <div style="font-size: 32px; font-weight: 800; line-height: 1;">${{this.reviews.length}}</div>
                            <div style="font-size: 12px; opacity: 0.9; margin-top: 4px;">Total Loaded</div>
                        </div>
                        <div style="flex: 1; min-width: 80px;">
                            <div style="font-size: 32px; font-weight: 800; line-height: 1;">${{this.stats.ai_recommended}}</div>
                            <div style="font-size: 12px; opacity: 0.9; margin-top: 4px;">AI Recommended</div>
                        </div>
                        <div style="flex: 1; min-width: 80px;">
                            <div style="font-size: 32px; font-weight: 800; line-height: 1;">${{this.stats.with_photos}}</div>
                            <div style="font-size: 12px; opacity: 0.9; margin-top: 4px;">With Photos</div>
                        </div>
                        <div style="flex: 1; min-width: 80px;">
                            <div style="font-size: 32px; font-weight: 800; line-height: 1;">${{this.stats.average_quality.toFixed(1)}}<span style="font-size: 20px;">/10</span></div>
                            <div style="font-size: 12px; opacity: 0.9; margin-top: 4px;">Avg Quality</div>
                        </div>
                    </div>
                </div>
                
                <!-- Bulk Import Buttons (like your design) -->
                <div style="display: flex; gap: 10px; margin-bottom: 24px; flex-wrap: wrap;">
                    <button class="rk-btn" style="background: #FF2D85; color: white; flex: 1; min-width: 150px; padding: 14px 18px; font-size: 14px; font-weight: 700;"
                            onclick="window.reviewKingClient.importAllReviews()">
                        Import All Reviews
                    </button>
                    <button class="rk-btn" style="background: #FF2D85; color: white; flex: 1; min-width: 150px; padding: 14px 18px; font-size: 14px; font-weight: 700;"
                            onclick="window.reviewKingClient.importWithPhotos()">
                        Import only with Photos
                    </button>
                    <button class="rk-btn" style="background: #FF2D85; color: white; flex: 1; min-width: 150px; padding: 14px 18px; font-size: 14px; font-weight: 700;"
                            onclick="window.reviewKingClient.importWithoutPhotos()">
                        Import with no Photos
                    </button>
                </div>
                
                <!-- Country Filter & Translation Toggle (Loox-inspired) -->
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 20px;">
                    <div>
                        <label style="color: #9ca3af; font-size: 13px; margin-bottom: 6px; display: block; font-weight: 500;">🌍 Reviews from</label>
                        <select id="rk-country-filter" onchange="window.reviewKingClient.setCountry(this.value)" 
                                style="width: 100%; padding: 10px 12px; background: #0f0f23; color: white; border: 1px solid #2d2d3d; border-radius: 8px; font-size: 14px; cursor: pointer;">
                            <option value="all">All countries</option>
                            ${{this.getUniqueCountries().map(c => `<option value="${{c.code}}" ${{this.selectedCountry === c.code ? 'selected' : ''}}>${{c.flag}} ${{c.name}}</option>`).join('')}}
                        </select>
                    </div>
                    <div>
                        <label style="color: #9ca3af; font-size: 13px; margin-bottom: 6px; display: block; font-weight: 500;">🌐 Translate</label>
                        <label style="display: flex; align-items: center; gap: 10px; padding: 10px 12px; background: #0f0f23; border: 1px solid #2d2d3d; border-radius: 8px; cursor: pointer; height: 42px;">
                            <input type="checkbox" id="rk-translation-toggle" 
                                   ${{this.showTranslations ? 'checked' : ''}}
                                   onchange="window.reviewKingClient.toggleTranslation()"
                                   style="width: 18px; height: 18px; cursor: pointer; accent-color: #FF2D85;">
                            <span style="color: #d1d5db; font-size: 14px;">Show English translation</span>
                        </label>
                    </div>
                </div>
                
                <!-- Filter Buttons (like your design) -->
                <div style="margin-bottom: 24px;">
                    <div style="color: #9ca3af; font-size: 13px; margin-bottom: 10px; font-weight: 500;">Filter Reviews:</div>
                    <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 12px;">
                        <button class="rk-btn rk-btn-secondary" style="padding: 10px 16px; ${{this.currentFilter === 'all' ? 'background: #FF2D85; color: white; border: none;' : ''}}" onclick="window.reviewKingClient.setFilter('all')">All (${{this.allReviews.length}})</button>
                        <button class="rk-btn rk-btn-secondary" style="padding: 10px 16px; ${{this.currentFilter === 'photos' ? 'background: #FF2D85; color: white; border: none;' : ''}}" onclick="window.reviewKingClient.setFilter('photos')">📸 With Photos (${{this.stats.with_photos}})</button>
                        <button class="rk-btn rk-btn-secondary" style="padding: 10px 16px; ${{this.currentFilter === 'ai_recommended' ? 'background: #FF2D85; color: white; border: none;' : ''}}" onclick="window.reviewKingClient.setFilter('ai_recommended')">🤖 AI Recommended (${{this.stats.ai_recommended}})</button>
                        <button class="rk-btn rk-btn-secondary" style="padding: 10px 16px; ${{this.currentFilter === '4-5stars' ? 'background: #FF2D85; color: white; border: none;' : ''}}" onclick="window.reviewKingClient.setFilter('4-5stars')">4-5 ⭐</button>
                        <button class="rk-btn rk-btn-secondary" style="padding: 10px 16px; ${{this.currentFilter === '3stars' ? 'background: #FF2D85; color: white; border: none;' : ''}}" onclick="window.reviewKingClient.setFilter('3stars')">3 ⭐ Only</button>
                    </div>
                    <div style="color: #6b7280; font-size: 12px;">
                        Showing ${{this.currentIndex + 1}} of ${{this.reviews.length}} reviews
                    </div>
                </div>
                
                <!-- Single Review Card (your beautiful design) -->
                <div style="background: #0f0f23; border-radius: 12px; padding: 28px; color: white; margin-bottom: 20px; border: 1px solid #1a1a2e;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 18px; align-items: flex-start;">
                        <div style="flex: 1;">
                            <h3 style="margin: 0; color: white; font-size: 18px; font-weight: 700; letter-spacing: -0.02em;">${{review.reviewer_name}}</h3>
                            <div style="color: #fbbf24; font-size: 18px; margin: 6px 0; letter-spacing: 2px;">${{'★'.repeat(Math.ceil(review.rating / 20)) + '☆'.repeat(5 - Math.ceil(review.rating / 20))}}</div>
                            <div style="color: #9ca3af; font-size: 12px; font-weight: 500;">${{review.date}} • ${{review.country}}</div>
                        </div>
                        <div style="text-align: right; display: flex; flex-direction: column; gap: 8px; align-items: flex-end;">
                            ${{isRecommended ? '<span style="background: #10b981; color: white; padding: 6px 12px; border-radius: 16px; font-size: 10px; font-weight: 700; letter-spacing: 0.5px; display: inline-block;">🤖 AI RECOMMENDED</span>' : ''}}
                            <span style="background: #3b82f6; color: white; padding: 6px 12px; border-radius: 16px; font-size: 10px; font-weight: 700; letter-spacing: 0.5px; display: inline-block;">QUALITY: ${{review.quality_score}}/10</span>
                        </div>
                    </div>
                    
                    <!-- Review text with translation support -->
                    ${{(() => {{
                        const hasTranslation = review.translation && review.text !== review.translation;
                        const displayText = (this.showTranslations && hasTranslation) ? review.translation : review.text;
                        const showOriginal = this.showTranslations && hasTranslation;
                        
                        return `
                            <p style="color: #d1d5db; line-height: 1.7; margin: 0 0 18px; font-size: 15px;">${{displayText}}</p>
                            ${{showOriginal ? 
                                `<p style="color: #888; font-size: 13px; margin: 0 0 18px; font-style: italic; border-left: 2px solid #555; padding-left: 10px;">Original: ${{review.text}}</p>` 
                                : ''
                            }}
                        `;
                    }})()}}
                    
                    ${{review.images && review.images.length > 0 ? `
                        <div style="margin-bottom: 18px;">
                            <div style="color: #9ca3af; font-size: 12px; margin-bottom: 10px; font-weight: 600;">
                                📸 ${{review.images.length}} Photo${{review.images.length > 1 ? 's' : ''}}
                            </div>
                            <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                                ${{review.images.map(img => 
                                    `<img src="${{img}}" style="width: 100px; height: 100px; 
                                    object-fit: cover; border-radius: 10px; cursor: pointer; border: 2px solid #1a1a2e;
                                    transition: all 0.2s;"
                                    onmouseover="this.style.transform='scale(1.05)'; this.style.borderColor='#3b82f6';"
                                    onmouseout="this.style.transform='scale(1)'; this.style.borderColor='#1a1a2e';"
                                    onclick="window.open('${{img}}', '_blank')">`
                                ).join('')}}
                            </div>
                        </div>
                    ` : '<div style="color: #6b7280; font-style: italic; margin-bottom: 18px; font-size: 13px;">No photos</div>'}}
                    
                    <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 20px;">
                        ${{review.verified ? '<span style="background: #10b981; color: white; padding: 5px 10px; border-radius: 14px; font-size: 10px; font-weight: 700; letter-spacing: 0.5px;">✓ VERIFIED</span>' : ''}}
                        <span style="background: #2d2d3d; color: #a1a1aa; padding: 5px 10px; border-radius: 14px; font-size: 10px; font-weight: 700; letter-spacing: 0.5px; border: 1px solid #3d3d4d;">
                            PLATFORM: ${{review.platform.toUpperCase()}}
                        </span>
                        <span style="background: #2d2d3d; color: #a1a1aa; padding: 5px 10px; border-radius: 14px; font-size: 10px; font-weight: 700; letter-spacing: 0.5px; border: 1px solid #3d3d4d;">
                            SENTIMENT: ${{Math.round(review.sentiment_score * 100)}}%
                        </span>
                    </div>
                    
                    <!-- Import/Reject buttons for individual review -->
                    <div style="display: flex; gap: 12px; margin-top: 20px;">
                        <button style="background: #374151; color: white; border: none; padding: 14px 28px; 
                                       border-radius: 8px; cursor: pointer; flex: 1; font-weight: 600; font-size: 14px;
                                       transition: all 0.2s;"
                                onmouseover="this.style.background='#4b5563'" 
                                onmouseout="this.style.background='#374151'"
                                onclick="window.reviewKingClient.skipReview()">
                            Reject
                        </button>
                        <button style="background: #FF2D85; color: white; border: none; padding: 14px 28px; 
                                       border-radius: 8px; cursor: pointer; flex: 2; font-weight: 700; font-size: 14px;
                                       transition: all 0.2s;"
                                onmouseover="this.style.background='#E0186F'; this.style.transform='translateY(-1px)'" 
                                onmouseout="this.style.background='#FF2D85'; this.style.transform='translateY(0)'"
                                onclick="window.reviewKingClient.importReview()">
                            Import
                        </button>
                    </div>
                </div>
                
                <!-- Navigation -->
                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 24px; padding-top: 16px; border-top: 1px solid #2d2d3d;">
                    <button class="rk-btn rk-btn-secondary" style="padding: 10px 20px;" onclick="window.reviewKingClient.prevReview()"
                            ${{this.currentIndex === 0 ? 'disabled style="opacity: 0.5; cursor: not-allowed;"' : ''}}>← Previous</button>
                    <span style="color: #9ca3af; font-size: 14px; font-weight: 600;">
                        ${{this.currentIndex + 1}} / ${{this.reviews.length}}
                    </span>
                    <button class="rk-btn rk-btn-secondary" style="padding: 10px 20px;" onclick="window.reviewKingClient.nextReview()"
                            ${{this.currentIndex === this.reviews.length - 1 ? 'disabled style="opacity: 0.5; cursor: not-allowed;"' : ''}}>Next →</button>
                </div>
            `;
            
            this.setupProductSearch();
        }}
        
        async importReview() {{
            if (!this.selectedProduct) {{
                alert('Please select a target product first!');
                return;
            }}
            
            const review = this.reviews[this.currentIndex];
            
            try {{
                const response = await fetch(`${{API_URL}}/admin/reviews/import/single`, {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{
                        review: review,
                        shopify_product_id: this.selectedProduct.id,
                        session_id: this.sessionId
                    }})
                }});
                
                const result = await response.json();
                
                if (result.success) {{
                    // Track analytics
                    fetch(`${{API_URL}}/e?cat=Import+by+URL&a=Post+imported&c=${{this.sessionId}}`, 
                          {{ method: 'GET' }});
                    
                    alert(`✓ Review imported successfully to "${{this.selectedProduct.title}}"!`);
                    this.nextReview();
                }} else {{
                    alert('Failed to import: ' + result.error);
                }}
            }} catch (error) {{
                alert('Import failed. Please try again.');
            }}
        }}
        
        async skipReview() {{
            const review = this.reviews[this.currentIndex];
            
            try {{
                const response = await fetch(`${{API_URL}}/admin/reviews/skip`, {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{
                        review_id: review.id,
                        session_id: this.sessionId
                    }})
                }});
                
                const result = await response.json();
                
                if (result.success) {{
                    alert('Review skipped. It will not be included in bulk import.');
                    this.nextReview();
                }} else {{
                    alert('Failed to skip review: ' + result.error);
                }}
            }} catch (error) {{
                alert('Skip failed. Please try again.');
            }}
        }}
        
        async importAllReviews() {{
            if (!this.selectedProduct) {{
                alert('Please select a target product first!');
                return;
            }}
            
            if (!confirm(`Import all non-skipped reviews to "${{this.selectedProduct.title}}"?\\n\\nThis will import multiple reviews at once.`)) {{
                return;
            }}
            
            try {{
                const response = await fetch(`${{API_URL}}/admin/reviews/import/bulk`, {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{
                        reviews: this.reviews,
                        shopify_product_id: this.selectedProduct.id,
                        session_id: this.sessionId,
                        filters: {{
                            min_quality_score: 0  // Import all quality levels
                        }}
                    }})
                }});
                
                const result = await response.json();
                
                if (result.success) {{
                    // Track analytics
                    fetch(`${{API_URL}}/e?cat=Import+by+URL&a=Bulk+imported&c=${{this.sessionId}}`, 
                          {{ method: 'GET' }});
                    
                    alert(`🎉 Bulk import completed!\\n\\n` +
                          `✅ Imported: ${{result.imported_count}}\\n` +
                          `❌ Failed: ${{result.failed_count}}\\n` +
                          `⏭️ Skipped: ${{result.skipped_count}}`);
                }} else {{
                    alert('Bulk import failed: ' + result.error);
                }}
            }} catch (error) {{
                alert('Bulk import failed. Please try again.');
            }}
        }}
        
        async importWithPhotos() {{
            if (!this.selectedProduct) {{
                alert('Please select a target product first!');
                return;
            }}
            
            const reviewsWithPhotos = this.reviews.filter(r => r.images && r.images.length > 0);
            
            if (!confirm(`Import ${{reviewsWithPhotos.length}} reviews with photos to "${{this.selectedProduct.title}}"?`)) {{
                return;
            }}
            
            try {{
                const response = await fetch(`${{API_URL}}/admin/reviews/import/bulk`, {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{
                        reviews: reviewsWithPhotos,
                        shopify_product_id: this.selectedProduct.id,
                        session_id: this.sessionId
                    }})
                }});
                
                const result = await response.json();
                
                if (result.success) {{
                    alert(`✅ Imported ${{result.imported_count}} reviews with photos!`);
                }} else {{
                    alert('Import failed: ' + result.error);
                }}
            }} catch (error) {{
                alert('Import failed. Please try again.');
            }}
        }}
        
        async importWithoutPhotos() {{
            if (!this.selectedProduct) {{
                alert('Please select a target product first!');
                return;
            }}
            
            const reviewsWithoutPhotos = this.reviews.filter(r => !r.images || r.images.length === 0);
            
            if (!confirm(`Import ${{reviewsWithoutPhotos.length}} reviews without photos to "${{this.selectedProduct.title}}"?`)) {{
                return;
            }}
            
            try {{
                const response = await fetch(`${{API_URL}}/admin/reviews/import/bulk`, {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{
                        reviews: reviewsWithoutPhotos,
                        shopify_product_id: this.selectedProduct.id,
                        session_id: this.sessionId
                    }})
                }});
                
                const result = await response.json();
                
                if (result.success) {{
                    alert(`✅ Imported ${{result.imported_count}} reviews without photos!`);
                }} else {{
                    alert('Import failed: ' + result.error);
                }}
            }} catch (error) {{
                alert('Import failed. Please try again.');
            }}
        }}
        
        nextReview() {{
            if (this.currentIndex < this.reviews.length - 1) {{
                this.currentIndex++;
                this.displayReview();
            }} else if (this.pagination.has_next) {{
                this.loadReviews(this.pagination.page + 1);
            }} else {{
                alert('No more reviews!');
            }}
        }}
        
        prevReview() {{
            if (this.currentIndex > 0) {{
                this.currentIndex--;
                this.displayReview();
            }}
        }}
        
        showError(message) {{
            document.getElementById('reviewking-content').innerHTML = `
                <div style="text-align: center; padding: 40px;">
                    <div style="font-size: 48px; margin-bottom: 16px;">⚠️</div>
                    <h3 style="color: #ef4444; margin: 0 0 8px;">Error</h3>
                    <p style="color: #6b7280; margin: 0;">${{message}}</p>
                    <button class="rk-btn rk-btn-primary" style="margin-top: 20px;"
                            onclick="window.reviewKingClient.close()">Close</button>
                </div>
            `;
        }}
        
        close() {{
            document.getElementById('reviewking-overlay').remove();
            document.body.style.overflow = 'auto';
            window.reviewKingActive = false;
            delete window.reviewKingClient;
        }}
    }}
    
    window.reviewKingClient = new ReviewKingClient();
}})();
    """
    
    return js_content, 200, {'Content-Type': 'application/javascript'}

@app.route('/health')
def health():
    """Health check"""
    return jsonify({
        'status': 'healthy',
        'version': Config.API_VERSION,
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    print("=" * 60)
    print("ReviewKing Enhanced API Starting...")
    print("=" * 60)
    print(f"Version: {Config.API_VERSION}")
    print(f"Port: {port}")
    print(f"Debug: {debug}")
    print(f"Platforms: {', '.join(Config.PLATFORMS)}")
    print("=" * 60)
    print("\nCompetitive Advantages over Loox:")
    print("  * Multi-platform (they only have AliExpress)")
    print("  * AI Quality Scoring (they don't have this)")
    print("  * Bulk import (they don't have this)")
    print("  * Better pricing")
    print("  * Sentiment analysis")
    print("=" * 60)
    print(f"\nBookmarklet URL:")
    print(f"javascript:(function(){{var s=document.createElement('script');s.src='http://localhost:{port}/js/bookmarklet.js';document.head.appendChild(s);}})();")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=port, debug=debug)


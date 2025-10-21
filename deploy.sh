#!/bin/bash

# Sakura Reviews Deployment Script for EasyPanel

echo "🌸 Sakura Reviews - EasyPanel Deployment"
echo "========================================"

# Check if we're in the right directory
if [ ! -f "app_enhanced.py" ]; then
    echo "❌ Error: app_enhanced.py not found. Please run from the project root."
    exit 1
fi

echo "✅ Found app_enhanced.py"

# Create templates directory if it doesn't exist
mkdir -p templates

echo "✅ Created templates directory"

# Check if templates exist
if [ ! -f "templates/widget.html" ]; then
    echo "⚠️  Warning: templates/widget.html not found. Creating basic template..."
    cat > templates/widget.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>Sakura Reviews Widget</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
        .reviews-container { max-width: 800px; margin: 0 auto; }
        .review-item { border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 8px; }
    </style>
</head>
<body>
    <div class="reviews-container">
        <h2>Customer Reviews</h2>
        {% for review in reviews %}
        <div class="review-item">
            <h4>{{ review.author }}</h4>
            <p>{{ review.text }}</p>
            <small>Rating: {{ review.rating }}/5 | AI Score: {{ review.ai_score }}</small>
        </div>
        {% endfor %}
    </div>
</body>
</html>
EOF
fi

echo "✅ Templates ready"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cat > .env << 'EOF'
WIDGET_BASE_URL=https://your-domain.com
WIDGET_SECRET=your-secret-key-here
FLASK_ENV=production
EOF
    echo "⚠️  Please update .env with your actual domain and secret key"
fi

echo "✅ Environment file ready"

# Test the application
echo "🧪 Testing application..."
python -c "import app_enhanced; print('✅ Application imports successfully')"

if [ $? -eq 0 ]; then
    echo "🎉 Deployment preparation complete!"
    echo ""
    echo "📋 Next Steps:"
    echo "1. Update .env with your actual domain"
    echo "2. Deploy to EasyPanel"
    echo "3. Test ScriptTag endpoints"
    echo "4. Verify JavaScript injection"
else
    echo "❌ Application test failed. Please check for errors."
    exit 1
fi

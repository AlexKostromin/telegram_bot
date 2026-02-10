
#!/bin/bash
# Start script for Django Admin Panel

echo "🚀 Starting Telegram Bot Admin Panel..."

# Check if venv exists
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate venv
source .venv/bin/activate

# Install/update dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt -q

# Navigate to admin panel
cd admin_panel

# Run migrations
echo "🔄 Running migrations..."
python manage.py migrate --noinput

# Collect static files
echo "📦 Collecting static files..."
python manage.py collectstatic --noinput -q

# Check if superuser exists
echo "👤 Checking for superuser..."
python manage.py shell << END
import os
from django.contrib.auth.models import User

if not User.objects.filter(username='admin').exists():
    print("⚠️  No admin user found!")
    print("📝 Create one using: python manage.py createsuperuser")
else:
    print("✅ Admin user exists")
END

echo ""
echo "✅ Admin Panel is ready!"
echo "🌐 Starting server on http://localhost:8000"
echo "📊 Admin: http://localhost:8000/admin"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start development server
python manage.py runserver 0.0.0.0:8000
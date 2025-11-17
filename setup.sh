#!/bin/bash
# Setup script for All-in-One Design Platform

echo "🚀 Setting up All-in-One Design Platform..."

# Backend setup
echo "📦 Setting up backend..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create migrations
echo "Creating database migrations..."
python manage.py makemigrations ai_services
python manage.py makemigrations assets
python manage.py makemigrations teams
python manage.py makemigrations projects
python manage.py makemigrations subscriptions
python manage.py makemigrations analytics

# Run migrations
echo "Running migrations..."
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput || true

cd ..

# Frontend setup
echo "📦 Setting up frontend..."
cd frontend

# Install dependencies
echo "Installing Node dependencies..."
npm install

cd ..

echo "✅ Setup complete!"
echo ""
echo "To start the development servers:"
echo ""
echo "Backend:"
echo "  cd backend"
echo "  source venv/bin/activate"
echo "  python manage.py runserver"
echo ""
echo "Frontend:"
echo "  cd frontend"
echo "  npm run dev"
echo ""
echo "Celery (for background tasks):"
echo "  cd backend"
echo "  source venv/bin/activate"
echo "  celery -A backend worker -l info"
echo ""
echo "📚 See NEW_FEATURES.md for detailed feature documentation"

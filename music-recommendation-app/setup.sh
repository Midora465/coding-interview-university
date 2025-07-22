#!/bin/bash

# Music Recommendation App Setup Script

echo "🎵 Setting up Music Recommendation App..."

# Check if required tools are installed
check_requirements() {
    echo "Checking requirements..."
    
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        echo "❌ Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    echo "✅ Requirements check passed"
}

# Create environment file
setup_environment() {
    echo "Setting up environment variables..."
    
    if [ ! -f .env ]; then
        echo "Creating .env file..."
        cat > .env << EOL
# Spotify API Credentials
SPOTIFY_CLIENT_ID=your_spotify_client_id_here
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret_here

# Database
POSTGRES_DB=music_rec_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

# Django
SECRET_KEY=$(openssl rand -base64 32)
DEBUG=True

# Optional: YouTube API
YOUTUBE_API_KEY=your_youtube_api_key_here

# Optional: AWS S3 (for production)
AWS_ACCESS_KEY_ID=your_aws_access_key_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_key_here
AWS_STORAGE_BUCKET_NAME=your_bucket_name_here

# Optional: Stripe (for payments)
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_key_here
STRIPE_SECRET_KEY=sk_test_your_stripe_key_here
EOL
        echo "✅ Created .env file"
        echo "📝 Please edit .env file with your Spotify API credentials"
        echo "   Get them from: https://developer.spotify.com/dashboard/applications"
    else
        echo "✅ .env file already exists"
    fi
}

# Initialize backend
setup_backend() {
    echo "Setting up Django backend..."
    
    # Copy environment file to backend
    cp .env backend/.env
    
    # Create necessary directories
    mkdir -p backend/media/audio_uploads
    mkdir -p backend/staticfiles
    
    echo "✅ Backend setup complete"
}

# Initialize frontend
setup_frontend() {
    echo "Setting up React frontend..."
    
    # Create public directory if it doesn't exist
    mkdir -p frontend/public
    mkdir -p frontend/src
    
    echo "✅ Frontend setup complete"
}

# Create development docker-compose override
create_dev_override() {
    echo "Creating development docker-compose override..."
    
    cat > docker-compose.override.yml << EOL
version: '3.8'

services:
  backend:
    volumes:
      - ./backend:/app
    environment:
      - DEBUG=True
    command: >
      sh -c "python manage.py migrate &&
             python manage.py collectstatic --noinput &&
             python manage.py runserver 0.0.0.0:8000"

  frontend:
    volumes:
      - ./frontend:/app
      - /app/node_modules
    command: npm start

  celery:
    volumes:
      - ./backend:/app
    environment:
      - DEBUG=True
EOL
    
    echo "✅ Development override created"
}

# Main setup function
main() {
    check_requirements
    setup_environment
    setup_backend
    setup_frontend
    create_dev_override
    
    echo ""
    echo "🎉 Setup complete!"
    echo ""
    echo "Next steps:"
    echo "1. Edit .env file with your Spotify API credentials"
    echo "2. Run: docker-compose up --build"
    echo "3. Open http://localhost:3000 in your browser"
    echo ""
    echo "For production deployment:"
    echo "docker-compose --profile production up --build"
    echo ""
    echo "Useful commands:"
    echo "- View logs: docker-compose logs -f"
    echo "- Reset database: docker-compose down -v && docker-compose up --build"
    echo "- Access Django shell: docker-compose exec backend python manage.py shell"
    echo ""
}

main "$@"
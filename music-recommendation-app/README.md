# Sound-Based Music Recommendation System

A revolutionary music discovery platform that recommends songs based on how they actually sound, not just metadata.

## 🎵 Features

### Core Functionality
- **Audio Analysis**: Extract acoustic features from Spotify tracks and uploaded audio files
- **Smart Recommendations**: Get suggestions based on actual sound characteristics
- **Custom Weighting**: Control which audio features matter most to you
- **Feedback Learning**: System improves recommendations based on your likes/dislikes
- **Playlist Integration**: Save recommendations directly to Spotify playlists

### User Tiers
- **Free Tier**: Basic recommendations with Spotify integration
- **Pro Tier** ($3-5/mo): Unlimited uploads, advanced controls, offline exports
- **Creator Plan** ($9-15/mo): Upload tracks, analytics, playlist fit suggestions

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- Spotify Developer Account
- PostgreSQL (for production)

### Installation

1. **Clone and setup backend:**
```bash
cd music-recommendation-app/backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your Spotify API credentials
python manage.py migrate
python manage.py runserver
```

2. **Setup frontend:**
```bash
cd ../frontend
npm install
npm start
```

3. **Setup audio processing worker:**
```bash
cd ../audio-processor
pip install -r requirements.txt
celery -A audio_processor worker --loglevel=info
```

## 🏗️ Architecture

```
music-recommendation-app/
├── backend/           # Django REST API
├── frontend/          # React.js web app
├── audio-processor/   # Celery workers for audio analysis
├── ml-models/         # Machine learning models
└── docs/             # Documentation
```

## 🎯 Technology Stack

- **Backend**: Django REST Framework, PostgreSQL, Redis
- **Frontend**: React.js, Material-UI, Web Audio API
- **Audio Processing**: Librosa, Essentia, OpenL3
- **ML**: scikit-learn, NumPy, pandas
- **APIs**: Spotify Web API, YouTube API (optional)
- **Deployment**: Docker, AWS/GCP

## 📊 Audio Features Analyzed

- **Rhythm**: Tempo, beat strength, rhythm patterns
- **Harmony**: Key, mode, chord progressions
- **Timbre**: MFCCs, spectral centroid, brightness
- **Energy**: Loudness, dynamic range, energy distribution
- **Mood**: Valence, danceability, acousticness
- **Structure**: Instrumentalness, speechiness, liveness

## 🔐 Privacy & Ethics

- Transparent recommendation algorithms
- No exploitative data practices
- User control over data and preferences
- Fair pricing and creator support
- Open source core components

## 📝 License

MIT License - see LICENSE file for details
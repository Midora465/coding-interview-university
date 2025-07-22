# Music Recommendation API Documentation

## Overview

The Music Recommendation API provides endpoints for analyzing audio tracks, generating recommendations, and managing user preferences. The API uses sound-based analysis rather than metadata to provide accurate music suggestions.

## Base URL

```
Development: http://localhost:8000/api/
Production: https://your-domain.com/api/
```

## Authentication

The API uses OAuth2 for authentication. Include the access token in the Authorization header:

```
Authorization: Bearer <access_token>
```

## Endpoints

### Authentication

#### POST /auth/login/
Login with username/email and password.

**Request:**
```json
{
  "username": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": "uuid",
    "username": "user@example.com",
    "subscription_tier": "free"
  }
}
```

#### POST /auth/spotify/connect/
Connect user's Spotify account.

**Request:**
```json
{
  "authorization_code": "spotify_auth_code"
}
```

### Music Analysis

#### POST /music/analyze/track/
Analyze a single track from URL or upload.

**Request (URL):**
```json
{
  "source": "spotify",
  "external_id": "spotify_track_id",
  "url": "https://open.spotify.com/track/..."
}
```

**Request (Upload):**
```
Content-Type: multipart/form-data
audio_file: <binary_file>
```

**Response:**
```json
{
  "id": "track_uuid",
  "title": "Song Title",
  "artist": "Artist Name",
  "analysis_status": "completed",
  "audio_features": {
    "danceability": 0.75,
    "energy": 0.85,
    "valence": 0.60,
    "tempo": 128.5,
    "key": 5,
    "mode": 1,
    "acousticness": 0.15,
    "instrumentalness": 0.02,
    "liveness": 0.08,
    "speechiness": 0.04,
    "loudness": -6.2,
    "mfcc_features": [1.2, -0.5, ...],
    "chroma_features": [0.8, 0.3, ...],
    "spectral_centroid": 1800.5
  }
}
```

#### POST /music/analyze/playlist/
Analyze an entire playlist.

**Request:**
```json
{
  "playlist_url": "https://open.spotify.com/playlist/...",
  "source": "spotify"
}
```

**Response:**
```json
{
  "id": "analysis_uuid",
  "name": "Playlist Name",
  "track_count": 25,
  "tracks_analyzed": 23,
  "average_features": {
    "danceability": 0.68,
    "energy": 0.72,
    "valence": 0.55
  },
  "analysis_status": "completed",
  "created_at": "2024-01-15T10:30:00Z"
}
```

#### GET /music/tracks/{track_id}/
Get track details and analysis results.

**Response:**
```json
{
  "id": "track_uuid",
  "title": "Song Title",
  "artist": "Artist Name",
  "album": "Album Name",
  "duration_ms": 210000,
  "source": "spotify",
  "external_url": "https://open.spotify.com/track/...",
  "preview_url": "https://p.scdn.co/mp3-preview/...",
  "is_analyzed": true,
  "audio_features": {...},
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Recommendations

#### POST /recommendations/generate/
Generate music recommendations based on input tracks.

**Request:**
```json
{
  "source_tracks": ["track_uuid1", "track_uuid2"],
  "max_recommendations": 20,
  "custom_weights": {
    "danceability": 1.5,
    "energy": 1.2,
    "valence": 0.8
  },
  "exclude_tracks": ["track_uuid3"],
  "min_similarity": 0.6,
  "genre_filter": ["electronic", "pop"]
}
```

**Response:**
```json
{
  "id": "request_uuid",
  "recommendations": [
    {
      "track": {
        "id": "rec_track_uuid",
        "title": "Recommended Song",
        "artist": "Artist Name",
        "external_url": "https://open.spotify.com/track/...",
        "preview_url": "https://p.scdn.co/mp3-preview/..."
      },
      "similarity_score": 0.87,
      "confidence_score": 0.92,
      "rank": 1,
      "match_reasons": [
        "Similar tempo",
        "High energy match",
        "Similar mood"
      ],
      "feature_matches": {
        "tempo": 0.95,
        "energy": 0.88,
        "danceability": 0.82
      }
    }
  ],
  "processing_time_ms": 1250,
  "created_at": "2024-01-15T10:30:00Z"
}
```

#### POST /recommendations/{recommendation_id}/feedback/
Provide feedback on a recommendation.

**Request:**
```json
{
  "track_id": "track_uuid",
  "feedback_type": "like",
  "context": {
    "listened_duration": 30000,
    "saved_to_playlist": true
  }
}
```

#### GET /recommendations/history/
Get user's recommendation history.

**Response:**
```json
{
  "count": 150,
  "results": [
    {
      "id": "request_uuid",
      "request_type": "playlist",
      "created_at": "2024-01-15T10:30:00Z",
      "recommendations_count": 20,
      "positive_feedback_count": 12
    }
  ]
}
```

### User Taste Profiles

#### GET /recommendations/taste-profiles/
Get user's taste profiles.

**Response:**
```json
{
  "profiles": [
    {
      "id": "profile_uuid",
      "name": "Default Profile",
      "is_primary": true,
      "feature_preferences": {
        "danceability": 0.75,
        "energy": 0.68,
        "valence": 0.62
      },
      "source_tracks_count": 45,
      "recommendation_accuracy": 0.78,
      "created_at": "2024-01-10T15:20:00Z"
    }
  ]
}
```

#### POST /recommendations/taste-profiles/
Create a new taste profile.

**Request:**
```json
{
  "name": "Workout Music",
  "source_tracks": ["track_uuid1", "track_uuid2"],
  "description": "High energy tracks for workouts"
}
```

#### PUT /recommendations/taste-profiles/{profile_id}/
Update a taste profile.

**Request:**
```json
{
  "name": "Updated Profile Name",
  "feature_weights": {
    "energy": 1.5,
    "danceability": 1.2,
    "tempo": 1.0
  }
}
```

### Playlists

#### GET /playlists/
Get user's saved playlists.

**Response:**
```json
{
  "playlists": [
    {
      "id": "playlist_uuid",
      "name": "My Discoveries",
      "track_count": 32,
      "source": "app",
      "spotify_id": "spotify_playlist_id",
      "created_at": "2024-01-12T09:15:00Z"
    }
  ]
}
```

#### POST /playlists/
Create a new playlist from recommendations.

**Request:**
```json
{
  "name": "AI Recommendations",
  "tracks": ["track_uuid1", "track_uuid2"],
  "export_to_spotify": true,
  "description": "Playlist generated from sound analysis"
}
```

#### POST /playlists/{playlist_id}/export/spotify/
Export playlist to Spotify.

**Response:**
```json
{
  "spotify_playlist_id": "spotify_id",
  "spotify_url": "https://open.spotify.com/playlist/...",
  "tracks_added": 18,
  "tracks_failed": 2
}
```

### Analytics (Creator Plan)

#### GET /analytics/track/{track_id}/
Get analytics for a specific track (creators only).

**Response:**
```json
{
  "track": {
    "id": "track_uuid",
    "title": "My Track",
    "artist": "Creator Name"
  },
  "recommendation_stats": {
    "times_recommended": 1250,
    "positive_feedback_rate": 0.73,
    "similar_tracks_count": 45
  },
  "feature_analysis": {
    "standout_features": ["energy", "danceability"],
    "similarity_clusters": [
      {
        "cluster_name": "High Energy Dance",
        "track_count": 12,
        "avg_similarity": 0.82
      }
    ]
  },
  "playlist_fits": [
    {
      "playlist_type": "workout",
      "fit_score": 0.89,
      "user_count": 2500
    }
  ]
}
```

#### GET /analytics/recommendations/performance/
Get recommendation performance metrics.

**Response:**
```json
{
  "total_recommendations": 15000,
  "accuracy_rate": 0.76,
  "user_satisfaction": 0.81,
  "feature_importance": {
    "energy": 0.92,
    "danceability": 0.88,
    "valence": 0.75,
    "tempo": 0.70
  },
  "weekly_stats": {
    "new_users": 125,
    "recommendations_generated": 3200,
    "positive_feedback": 2400
  }
}
```

### Payments (Subscription Management)

#### GET /payments/subscription/
Get current subscription status.

**Response:**
```json
{
  "subscription_tier": "pro",
  "expires_at": "2024-02-15T23:59:59Z",
  "auto_renewal": true,
  "features": [
    "unlimited_uploads",
    "advanced_controls",
    "priority_processing"
  ]
}
```

#### POST /payments/subscribe/
Create subscription checkout session.

**Request:**
```json
{
  "tier": "pro",
  "billing_cycle": "monthly"
}
```

**Response:**
```json
{
  "checkout_session_id": "cs_test_123",
  "checkout_url": "https://checkout.stripe.com/pay/cs_test_123"
}
```

## Error Responses

All endpoints return errors in the following format:

```json
{
  "error": "error_code",
  "message": "Human readable error message",
  "details": {
    "field_name": ["Specific field errors"]
  }
}
```

### Common Error Codes

- `400` - Bad Request (validation errors)
- `401` - Unauthorized (invalid token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `429` - Rate Limited
- `500` - Internal Server Error

### Rate Limits

- Free users: 100 requests/hour
- Pro users: 1000 requests/hour
- Creator users: 5000 requests/hour

## WebSocket Events (Real-time Updates)

Connect to `/ws/analysis/` for real-time analysis updates:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/analysis/');

ws.onmessage = function(event) {
  const data = JSON.parse(event.data);
  if (data.type === 'analysis_progress') {
    console.log(`Analysis ${data.job_id}: ${data.progress}%`);
  }
};
```

## SDKs and Libraries

- **Python**: `pip install music-rec-sdk`
- **JavaScript**: `npm install music-rec-client`
- **React Hooks**: Available in the frontend package

## Support

For API support, visit our [documentation site](https://docs.music-rec.com) or contact support@music-rec.com.
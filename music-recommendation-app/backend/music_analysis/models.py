from django.db import models
from django.contrib.auth import get_user_model
import uuid
import json

User = get_user_model()

class Track(models.Model):
    """Represents a music track with metadata and audio features"""
    SOURCE_CHOICES = [
        ('spotify', 'Spotify'),
        ('youtube', 'YouTube'),
        ('upload', 'User Upload'),
        ('soundcloud', 'SoundCloud'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Basic metadata
    title = models.CharField(max_length=500)
    artist = models.CharField(max_length=500)
    album = models.CharField(max_length=500, blank=True)
    duration_ms = models.IntegerField(null=True, blank=True)
    release_date = models.DateField(null=True, blank=True)
    
    # Source information
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    external_id = models.CharField(max_length=255, blank=True)  # Spotify ID, YouTube ID, etc.
    external_url = models.URLField(blank=True)
    preview_url = models.URLField(blank=True)
    
    # File information (for uploads)
    audio_file = models.FileField(upload_to='audio_uploads/', null=True, blank=True)
    file_format = models.CharField(max_length=10, blank=True)  # mp3, wav, etc.
    
    # Analysis status
    is_analyzed = models.BooleanField(default=False)
    analysis_error = models.TextField(blank=True)
    
    # Metadata
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['external_id', 'source']),
            models.Index(fields=['artist', 'title']),
            models.Index(fields=['is_analyzed']),
        ]
        unique_together = ['external_id', 'source']
    
    def __str__(self):
        return f"{self.artist} - {self.title}"
    
    def get_audio_features(self):
        """Get the associated audio features"""
        return getattr(self, 'audio_features', None)

class AudioFeatures(models.Model):
    """Audio features extracted from tracks"""
    track = models.OneToOneField(Track, on_delete=models.CASCADE, related_name='audio_features')
    
    # Spotify Audio Features
    danceability = models.FloatField(null=True, blank=True)
    energy = models.FloatField(null=True, blank=True)
    key = models.IntegerField(null=True, blank=True)
    loudness = models.FloatField(null=True, blank=True)
    mode = models.IntegerField(null=True, blank=True)
    speechiness = models.FloatField(null=True, blank=True)
    acousticness = models.FloatField(null=True, blank=True)
    instrumentalness = models.FloatField(null=True, blank=True)
    liveness = models.FloatField(null=True, blank=True)
    valence = models.FloatField(null=True, blank=True)
    tempo = models.FloatField(null=True, blank=True)
    time_signature = models.IntegerField(null=True, blank=True)
    
    # Advanced features from Librosa/Essentia
    mfcc_features = models.JSONField(default=list, blank=True)  # 13 MFCC coefficients
    chroma_features = models.JSONField(default=list, blank=True)  # 12 chroma features
    spectral_centroid = models.FloatField(null=True, blank=True)
    spectral_bandwidth = models.FloatField(null=True, blank=True)
    spectral_rolloff = models.FloatField(null=True, blank=True)
    zero_crossing_rate = models.FloatField(null=True, blank=True)
    
    # Rhythm features
    beat_track = models.JSONField(default=list, blank=True)
    onset_frames = models.JSONField(default=list, blank=True)
    rhythm_patterns = models.JSONField(default=dict, blank=True)
    
    # Harmonic features
    harmonic_features = models.JSONField(default=dict, blank=True)
    tonal_features = models.JSONField(default=dict, blank=True)
    
    # Perceptual features (from OpenL3 or similar)
    perceptual_embedding = models.JSONField(default=list, blank=True)
    
    # Composite features for similarity matching
    feature_vector = models.JSONField(default=list, blank=True)  # Normalized feature vector
    feature_hash = models.CharField(max_length=64, blank=True)  # For quick lookups
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def get_feature_vector(self):
        """Get normalized feature vector for similarity calculations"""
        if self.feature_vector:
            return self.feature_vector
        
        # Build feature vector from available features
        features = []
        
        # Basic features
        basic_features = [
            self.danceability, self.energy, self.loudness, self.speechiness,
            self.acousticness, self.instrumentalness, self.liveness, self.valence,
            self.tempo, self.spectral_centroid, self.spectral_bandwidth,
            self.spectral_rolloff, self.zero_crossing_rate
        ]
        
        features.extend([f for f in basic_features if f is not None])
        
        # Add MFCC features (first 13 coefficients)
        if self.mfcc_features:
            features.extend(self.mfcc_features[:13])
        
        # Add chroma features
        if self.chroma_features:
            features.extend(self.chroma_features[:12])
        
        return features
    
    def calculate_similarity(self, other_features, weights=None):
        """Calculate cosine similarity with another AudioFeatures instance"""
        import numpy as np
        from sklearn.metrics.pairwise import cosine_similarity
        
        vector1 = np.array(self.get_feature_vector()).reshape(1, -1)
        vector2 = np.array(other_features.get_feature_vector()).reshape(1, -1)
        
        # Apply weights if provided
        if weights and len(weights) == len(vector1[0]):
            vector1 = vector1 * np.array(weights)
            vector2 = vector2 * np.array(weights)
        
        return cosine_similarity(vector1, vector2)[0][0]

class AnalysisJob(models.Model):
    """Track audio analysis jobs for async processing"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    track = models.ForeignKey(Track, on_delete=models.CASCADE, related_name='analysis_jobs')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    progress = models.IntegerField(default=0)  # 0-100
    error_message = models.TextField(blank=True)
    
    # Processing details
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    celery_task_id = models.CharField(max_length=255, blank=True)
    
    # Analysis configuration
    analysis_config = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Analysis Job {self.id} - {self.track.title} ({self.status})"

class PlaylistAnalysis(models.Model):
    """Analysis results for entire playlists"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Playlist metadata
    name = models.CharField(max_length=500)
    source = models.CharField(max_length=20, choices=Track.SOURCE_CHOICES)
    external_id = models.CharField(max_length=255, blank=True)
    track_count = models.IntegerField(default=0)
    
    # Analysis results
    tracks = models.ManyToManyField(Track, related_name='playlists')
    average_features = models.JSONField(default=dict, blank=True)
    feature_clusters = models.JSONField(default=list, blank=True)
    diversity_score = models.FloatField(null=True, blank=True)
    
    # Processing status
    is_analyzed = models.BooleanField(default=False)
    analysis_job = models.ForeignKey(AnalysisJob, on_delete=models.SET_NULL, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.track_count} tracks)"
    
    def get_taste_profile(self):
        """Generate user taste profile from playlist analysis"""
        if not self.average_features:
            return {}
        
        # Weight features based on variance across tracks
        taste_profile = {}
        for feature, value in self.average_features.items():
            if isinstance(value, (int, float)):
                taste_profile[feature] = {
                    'preference': value,
                    'importance': 1.0,  # Can be adjusted based on variance
                }
        
        return taste_profile
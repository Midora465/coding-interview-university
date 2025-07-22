from django.db import models
from django.contrib.auth import get_user_model
from music_analysis.models import Track, AudioFeatures
import uuid
import json

User = get_user_model()

class TasteProfile(models.Model):
    """User's musical taste profile based on analyzed tracks"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='taste_profiles')
    
    # Profile metadata
    name = models.CharField(max_length=200, default='Default Profile')
    description = models.TextField(blank=True)
    is_primary = models.BooleanField(default=True)
    
    # Feature preferences (weighted averages)
    feature_preferences = models.JSONField(default=dict, blank=True)
    feature_weights = models.JSONField(default=dict, blank=True)
    
    # Source tracks that built this profile
    source_tracks = models.ManyToManyField(Track, related_name='taste_profiles')
    
    # Clustering information
    cluster_centers = models.JSONField(default=list, blank=True)
    cluster_labels = models.JSONField(default=list, blank=True)
    diversity_score = models.FloatField(default=0.0)
    
    # Performance metrics
    recommendation_accuracy = models.FloatField(default=0.0)
    total_recommendations = models.IntegerField(default=0)
    positive_feedback_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'name']
        ordering = ['-is_primary', '-updated_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.name}"
    
    def update_from_tracks(self, tracks):
        """Update taste profile based on a set of tracks"""
        import numpy as np
        from sklearn.cluster import KMeans
        
        feature_vectors = []
        valid_tracks = []
        
        for track in tracks:
            features = track.get_audio_features()
            if features and features.feature_vector:
                feature_vectors.append(features.feature_vector)
                valid_tracks.append(track)
        
        if not feature_vectors:
            return
        
        # Convert to numpy array
        X = np.array(feature_vectors)
        
        # Calculate average preferences
        self.feature_preferences = {
            f'feature_{i}': float(np.mean(X[:, i]))
            for i in range(X.shape[1])
        }
        
        # Calculate feature importance based on variance
        self.feature_weights = {
            f'feature_{i}': float(1.0 / (1.0 + np.var(X[:, i])))
            for i in range(X.shape[1])
        }
        
        # Perform clustering if enough tracks
        if len(feature_vectors) >= 3:
            n_clusters = min(3, len(feature_vectors))
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            cluster_labels = kmeans.fit_predict(X)
            
            self.cluster_centers = kmeans.cluster_centers_.tolist()
            self.cluster_labels = cluster_labels.tolist()
            
            # Calculate diversity score
            self.diversity_score = float(np.mean([
                np.linalg.norm(center - self.cluster_centers[0])
                for center in self.cluster_centers[1:]
            ]))
        
        # Update source tracks
        self.source_tracks.set(valid_tracks)
        self.save()
    
    def calculate_similarity(self, track):
        """Calculate similarity between this profile and a track"""
        features = track.get_audio_features()
        if not features or not features.feature_vector:
            return 0.0
        
        import numpy as np
        from sklearn.metrics.pairwise import cosine_similarity
        
        track_vector = np.array(features.feature_vector).reshape(1, -1)
        
        # Calculate similarity to average preferences
        if self.feature_preferences:
            preference_vector = np.array([
                self.feature_preferences.get(f'feature_{i}', 0.0)
                for i in range(len(features.feature_vector))
            ]).reshape(1, -1)
            
            # Apply feature weights
            if self.feature_weights:
                weights = np.array([
                    self.feature_weights.get(f'feature_{i}', 1.0)
                    for i in range(len(features.feature_vector))
                ])
                track_vector = track_vector * weights
                preference_vector = preference_vector * weights
            
            similarity = cosine_similarity(track_vector, preference_vector)[0][0]
            return max(0.0, min(1.0, similarity))
        
        return 0.0

class RecommendationRequest(models.Model):
    """A request for music recommendations"""
    REQUEST_TYPES = [
        ('playlist', 'Playlist-based'),
        ('track', 'Single track'),
        ('upload', 'Uploaded file'),
        ('taste_profile', 'Taste profile'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recommendation_requests')
    
    # Request parameters
    request_type = models.CharField(max_length=20, choices=REQUEST_TYPES)
    source_tracks = models.ManyToManyField(Track, related_name='recommendation_requests')
    taste_profile = models.ForeignKey(TasteProfile, on_delete=models.SET_NULL, null=True, blank=True)
    
    # User preferences for this request
    custom_weights = models.JSONField(default=dict, blank=True)
    exclude_tracks = models.ManyToManyField(Track, related_name='excluded_from', blank=True)
    max_recommendations = models.IntegerField(default=20)
    
    # Filtering options
    min_similarity = models.FloatField(default=0.5)
    genre_filter = models.JSONField(default=list, blank=True)
    year_range = models.JSONField(default=dict, blank=True)
    
    # Status
    is_processed = models.BooleanField(default=False)
    processing_time_ms = models.IntegerField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Recommendation Request {self.id} - {self.user.username}"

class Recommendation(models.Model):
    """A single music recommendation"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    request = models.ForeignKey(RecommendationRequest, on_delete=models.CASCADE, related_name='recommendations')
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    
    # Recommendation metrics
    similarity_score = models.FloatField()
    confidence_score = models.FloatField(default=0.0)
    rank = models.IntegerField()
    
    # Explanation
    match_reasons = models.JSONField(default=list, blank=True)
    feature_matches = models.JSONField(default=dict, blank=True)
    
    # User feedback
    user_feedback = models.CharField(
        max_length=20,
        choices=[('like', 'Like'), ('dislike', 'Dislike'), ('neutral', 'Neutral')],
        null=True,
        blank=True
    )
    feedback_timestamp = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['request', 'track']
        ordering = ['request', 'rank']
    
    def __str__(self):
        return f"Recommendation: {self.track.title} (Score: {self.similarity_score:.3f})"
    
    def generate_explanation(self):
        """Generate human-readable explanation for this recommendation"""
        reasons = []
        
        if self.feature_matches:
            # Find top matching features
            top_matches = sorted(
                self.feature_matches.items(),
                key=lambda x: x[1],
                reverse=True
            )[:3]
            
            feature_names = {
                'tempo': 'tempo',
                'energy': 'energy level',
                'danceability': 'danceability',
                'valence': 'mood',
                'acousticness': 'acoustic qualities',
                'instrumentalness': 'instrumental content',
            }
            
            for feature, score in top_matches:
                if score > 0.8:
                    feature_name = feature_names.get(feature, feature)
                    reasons.append(f"Similar {feature_name}")
        
        if self.similarity_score > 0.9:
            reasons.append("Very high overall similarity")
        elif self.similarity_score > 0.7:
            reasons.append("High overall similarity")
        
        self.match_reasons = reasons
        self.save()
        
        return reasons

class UserFeedback(models.Model):
    """Track user feedback for improving recommendations"""
    FEEDBACK_TYPES = [
        ('like', 'Like'),
        ('dislike', 'Dislike'),
        ('love', 'Love'),
        ('block', 'Block'),
        ('save', 'Save to Playlist'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedback')
    track = models.ForeignKey(Track, on_delete=models.CASCADE, related_name='user_feedback')
    recommendation = models.ForeignKey(
        Recommendation, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='feedback'
    )
    
    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_TYPES)
    context = models.JSONField(default=dict, blank=True)  # Additional context
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'track', 'feedback_type']
    
    def __str__(self):
        return f"{self.user.username} - {self.feedback_type} - {self.track.title}"

class RecommendationMetrics(models.Model):
    """Aggregate metrics for recommendation performance"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='recommendation_metrics')
    
    # Overall metrics
    total_recommendations_received = models.IntegerField(default=0)
    total_feedback_given = models.IntegerField(default=0)
    positive_feedback_rate = models.FloatField(default=0.0)
    
    # Weekly metrics
    weekly_recommendations = models.IntegerField(default=0)
    weekly_positive_feedback = models.IntegerField(default=0)
    
    # Feature preference learning
    learned_preferences = models.JSONField(default=dict, blank=True)
    preference_confidence = models.FloatField(default=0.0)
    
    # Last updated
    last_updated = models.DateTimeField(auto_now=True)
    metrics_reset_date = models.DateField(auto_now_add=True)
    
    def update_metrics(self):
        """Update recommendation metrics based on recent feedback"""
        from django.utils import timezone
        from datetime import timedelta
        
        # Get recent feedback
        week_ago = timezone.now() - timedelta(days=7)
        recent_feedback = UserFeedback.objects.filter(
            user=self.user,
            created_at__gte=week_ago
        )
        
        # Update weekly metrics
        self.weekly_recommendations = recent_feedback.count()
        self.weekly_positive_feedback = recent_feedback.filter(
            feedback_type__in=['like', 'love', 'save']
        ).count()
        
        # Update overall metrics
        all_feedback = UserFeedback.objects.filter(user=self.user)
        self.total_feedback_given = all_feedback.count()
        
        if self.total_feedback_given > 0:
            positive_feedback = all_feedback.filter(
                feedback_type__in=['like', 'love', 'save']
            ).count()
            self.positive_feedback_rate = positive_feedback / self.total_feedback_given
        
        self.save()
    
    def __str__(self):
        return f"{self.user.username} - Recommendation Metrics"
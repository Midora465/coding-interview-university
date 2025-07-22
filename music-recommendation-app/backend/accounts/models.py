from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import uuid

class User(AbstractUser):
    """Extended user model with subscription and preference tracking"""
    SUBSCRIPTION_TIERS = [
        ('free', 'Free'),
        ('pro', 'Pro'),
        ('creator', 'Creator'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    subscription_tier = models.CharField(max_length=20, choices=SUBSCRIPTION_TIERS, default='free')
    subscription_expires = models.DateTimeField(null=True, blank=True)
    spotify_user_id = models.CharField(max_length=255, blank=True, null=True)
    spotify_access_token = models.TextField(blank=True, null=True)
    spotify_refresh_token = models.TextField(blank=True, null=True)
    spotify_token_expires = models.DateTimeField(null=True, blank=True)
    
    # User preferences
    preferred_features = models.JSONField(default=dict, blank=True)  # Feature weights
    recommendation_history = models.JSONField(default=list, blank=True)
    feedback_data = models.JSONField(default=dict, blank=True)  # Likes/dislikes
    
    # Analytics
    total_uploads = models.IntegerField(default=0)
    total_recommendations_requested = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def is_premium_user(self):
        """Check if user has active premium subscription"""
        if self.subscription_tier in ['pro', 'creator']:
            return self.subscription_expires and self.subscription_expires > timezone.now()
        return False
    
    def is_creator(self):
        """Check if user has creator subscription"""
        return self.subscription_tier == 'creator' and self.is_premium_user()
    
    def can_upload_unlimited(self):
        """Check if user can upload unlimited tracks"""
        return self.is_premium_user()
    
    def get_upload_limit(self):
        """Get daily upload limit based on subscription"""
        if self.is_premium_user():
            return None  # Unlimited
        return 5  # Free tier limit

class UserProfile(models.Model):
    """Additional user profile information"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    display_name = models.CharField(max_length=100, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    website = models.URLField(blank=True)
    
    # Music preferences
    favorite_genres = models.JSONField(default=list, blank=True)
    listening_habits = models.JSONField(default=dict, blank=True)
    
    # Privacy settings
    public_profile = models.BooleanField(default=False)
    share_recommendations = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"

class SpotifyIntegration(models.Model):
    """Track Spotify API integration status and usage"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='spotify_integration')
    is_connected = models.BooleanField(default=False)
    last_sync = models.DateTimeField(null=True, blank=True)
    playlists_synced = models.IntegerField(default=0)
    tracks_analyzed = models.IntegerField(default=0)
    
    # API usage tracking
    daily_api_calls = models.IntegerField(default=0)
    last_api_reset = models.DateField(auto_now_add=True)
    
    def reset_daily_limits(self):
        """Reset daily API call counter"""
        from datetime import date
        if self.last_api_reset < date.today():
            self.daily_api_calls = 0
            self.last_api_reset = date.today()
            self.save()
    
    def can_make_api_call(self):
        """Check if user can make another API call"""
        self.reset_daily_limits()
        if self.user.is_premium_user():
            return self.daily_api_calls < 1000  # Premium limit
        return self.daily_api_calls < 100  # Free limit
    
    def increment_api_calls(self):
        """Increment API call counter"""
        self.daily_api_calls += 1
        self.save()
    
    def __str__(self):
        return f"{self.user.username} - Spotify Integration"
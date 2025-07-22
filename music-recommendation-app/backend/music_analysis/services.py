import os
import logging
import numpy as np
import librosa
import requests
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from django.conf import settings
from django.core.files.base import ContentFile
from .models import Track, AudioFeatures, AnalysisJob
from accounts.models import User

logger = logging.getLogger(__name__)

class SpotifyService:
    """Service for interacting with Spotify API"""
    
    def __init__(self):
        self.client_credentials_manager = SpotifyClientCredentials(
            client_id=settings.SPOTIFY_CLIENT_ID,
            client_secret=settings.SPOTIFY_CLIENT_SECRET
        )
        self.spotify = spotipy.Spotify(
            client_credentials_manager=self.client_credentials_manager
        )
    
    def get_track_info(self, spotify_id):
        """Get track metadata from Spotify"""
        try:
            track = self.spotify.track(spotify_id)
            return {
                'title': track['name'],
                'artist': ', '.join([artist['name'] for artist in track['artists']]),
                'album': track['album']['name'],
                'duration_ms': track['duration_ms'],
                'external_url': track['external_urls']['spotify'],
                'preview_url': track['preview_url'],
                'release_date': track['album']['release_date'],
            }
        except Exception as e:
            logger.error(f"Error fetching track info for {spotify_id}: {e}")
            return None
    
    def get_audio_features(self, spotify_id):
        """Get audio features from Spotify"""
        try:
            features = self.spotify.audio_features([spotify_id])[0]
            if features:
                return {
                    'danceability': features['danceability'],
                    'energy': features['energy'],
                    'key': features['key'],
                    'loudness': features['loudness'],
                    'mode': features['mode'],
                    'speechiness': features['speechiness'],
                    'acousticness': features['acousticness'],
                    'instrumentalness': features['instrumentalness'],
                    'liveness': features['liveness'],
                    'valence': features['valence'],
                    'tempo': features['tempo'],
                    'time_signature': features['time_signature'],
                }
            return None
        except Exception as e:
            logger.error(f"Error fetching audio features for {spotify_id}: {e}")
            return None
    
    def get_playlist_tracks(self, playlist_id):
        """Get all tracks from a Spotify playlist"""
        try:
            results = self.spotify.playlist_tracks(playlist_id)
            tracks = []
            
            while results:
                for item in results['items']:
                    if item['track'] and item['track']['id']:
                        tracks.append(item['track']['id'])
                
                if results['next']:
                    results = self.spotify.next(results)
                else:
                    break
            
            return tracks
        except Exception as e:
            logger.error(f"Error fetching playlist tracks for {playlist_id}: {e}")
            return []

class AudioAnalysisService:
    """Service for analyzing audio files using Librosa and other libraries"""
    
    def __init__(self):
        self.spotify_service = SpotifyService()
    
    def analyze_track(self, track_id, user_id=None):
        """Analyze a track and extract audio features"""
        try:
            track = Track.objects.get(id=track_id)
            user = User.objects.get(id=user_id) if user_id else None
            
            # Create analysis job
            job = AnalysisJob.objects.create(
                track=track,
                user=user or track.uploaded_by,
                status='processing'
            )
            
            # Get audio features based on source
            if track.source == 'spotify':
                features = self._analyze_spotify_track(track)
            elif track.source == 'upload':
                features = self._analyze_uploaded_track(track)
            else:
                raise ValueError(f"Unsupported track source: {track.source}")
            
            if features:
                # Save features to database
                audio_features, created = AudioFeatures.objects.get_or_create(
                    track=track,
                    defaults=features
                )
                
                if not created:
                    # Update existing features
                    for key, value in features.items():
                        setattr(audio_features, key, value)
                    audio_features.save()
                
                # Calculate and save feature vector
                audio_features.feature_vector = self._normalize_features(audio_features)
                audio_features.save()
                
                # Mark track as analyzed
                track.is_analyzed = True
                track.save()
                
                # Complete job
                job.status = 'completed'
                job.progress = 100
                job.save()
                
                return audio_features
            else:
                raise Exception("Failed to extract audio features")
                
        except Exception as e:
            logger.error(f"Error analyzing track {track_id}: {e}")
            if 'job' in locals():
                job.status = 'failed'
                job.error_message = str(e)
                job.save()
            return None
    
    def _analyze_spotify_track(self, track):
        """Analyze a Spotify track"""
        features = {}
        
        # Get Spotify audio features
        spotify_features = self.spotify_service.get_audio_features(track.external_id)
        if spotify_features:
            features.update(spotify_features)
        
        # If preview URL is available, analyze audio
        if track.preview_url:
            try:
                # Download preview
                response = requests.get(track.preview_url)
                if response.status_code == 200:
                    # Save temporary file
                    temp_file = f"/tmp/{track.id}.mp3"
                    with open(temp_file, 'wb') as f:
                        f.write(response.content)
                    
                    # Analyze audio
                    audio_features = self._extract_librosa_features(temp_file)
                    features.update(audio_features)
                    
                    # Clean up
                    os.remove(temp_file)
                    
            except Exception as e:
                logger.warning(f"Could not analyze preview for {track.id}: {e}")
        
        return features
    
    def _analyze_uploaded_track(self, track):
        """Analyze an uploaded audio file"""
        if not track.audio_file:
            raise ValueError("No audio file found for uploaded track")
        
        features = {}
        
        # Extract features using Librosa
        audio_features = self._extract_librosa_features(track.audio_file.path)
        features.update(audio_features)
        
        return features
    
    def _extract_librosa_features(self, file_path):
        """Extract audio features using Librosa"""
        try:
            # Load audio file
            y, sr = librosa.load(file_path, sr=22050)
            
            features = {}
            
            # Tempo and beat tracking
            tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
            features['tempo'] = float(tempo)
            features['beat_track'] = beats.tolist()
            
            # Spectral features
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
            features['spectral_centroid'] = float(np.mean(spectral_centroids))
            
            spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)[0]
            features['spectral_bandwidth'] = float(np.mean(spectral_bandwidth))
            
            spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
            features['spectral_rolloff'] = float(np.mean(spectral_rolloff))
            
            # Zero crossing rate
            zcr = librosa.feature.zero_crossing_rate(y)[0]
            features['zero_crossing_rate'] = float(np.mean(zcr))
            
            # MFCCs
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            features['mfcc_features'] = np.mean(mfccs, axis=1).tolist()
            
            # Chroma features
            chroma = librosa.feature.chroma_stft(y=y, sr=sr)
            features['chroma_features'] = np.mean(chroma, axis=1).tolist()
            
            # Onset detection
            onset_frames = librosa.onset.onset_detect(y=y, sr=sr)
            features['onset_frames'] = onset_frames.tolist()
            
            # Energy and loudness estimation
            energy = np.sum(y**2) / len(y)
            features['energy'] = float(energy)
            
            # Estimate additional features if not from Spotify
            if 'danceability' not in features:
                features.update(self._estimate_perceptual_features(y, sr))
            
            return features
            
        except Exception as e:
            logger.error(f"Error extracting Librosa features from {file_path}: {e}")
            return {}
    
    def _estimate_perceptual_features(self, y, sr):
        """Estimate perceptual features from raw audio"""
        features = {}
        
        # Estimate danceability based on rhythm strength
        tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
        beat_strength = librosa.beat.beat_track(y=y, sr=sr, units='time')[1]
        if len(beat_strength) > 1:
            beat_consistency = 1.0 - np.std(np.diff(beat_strength))
            features['danceability'] = max(0.0, min(1.0, beat_consistency))
        
        # Estimate energy based on RMS
        rms = librosa.feature.rms(y=y)[0]
        features['energy'] = float(min(1.0, np.mean(rms) * 10))
        
        # Estimate valence based on spectral characteristics
        spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
        brightness = np.mean(spectral_centroid) / (sr / 2)
        features['valence'] = float(min(1.0, brightness))
        
        # Estimate acousticness (inverse of brightness and energy)
        features['acousticness'] = float(max(0.0, 1.0 - brightness - features['energy']))
        
        return features
    
    def _normalize_features(self, audio_features):
        """Create normalized feature vector for similarity calculations"""
        vector = []
        
        # Basic perceptual features (0-1 range)
        perceptual_features = [
            audio_features.danceability,
            audio_features.energy,
            audio_features.speechiness,
            audio_features.acousticness,
            audio_features.instrumentalness,
            audio_features.liveness,
            audio_features.valence,
        ]
        
        for feature in perceptual_features:
            if feature is not None:
                vector.append(feature)
            else:
                vector.append(0.0)
        
        # Tempo (normalized to 0-1 range, assuming 60-200 BPM)
        if audio_features.tempo:
            normalized_tempo = (audio_features.tempo - 60) / 140
            vector.append(max(0.0, min(1.0, normalized_tempo)))
        else:
            vector.append(0.5)
        
        # Loudness (normalized to 0-1 range, assuming -60 to 0 dB)
        if audio_features.loudness:
            normalized_loudness = (audio_features.loudness + 60) / 60
            vector.append(max(0.0, min(1.0, normalized_loudness)))
        else:
            vector.append(0.5)
        
        # Spectral features (normalized)
        spectral_features = [
            audio_features.spectral_centroid,
            audio_features.spectral_bandwidth,
            audio_features.spectral_rolloff,
            audio_features.zero_crossing_rate,
        ]
        
        for feature in spectral_features:
            if feature is not None:
                # Normalize to 0-1 range (values will vary, this is approximate)
                normalized = feature / max(feature, 1.0)
                vector.append(max(0.0, min(1.0, normalized)))
            else:
                vector.append(0.5)
        
        # Add normalized MFCC features (first 13)
        if audio_features.mfcc_features:
            mfccs = audio_features.mfcc_features[:13]
            # Normalize MFCCs to -1 to 1 range, then scale to 0-1
            for mfcc in mfccs:
                normalized_mfcc = (mfcc + 1) / 2  # Convert from [-1,1] to [0,1]
                vector.append(max(0.0, min(1.0, normalized_mfcc)))
        
        # Add normalized chroma features
        if audio_features.chroma_features:
            chromas = audio_features.chroma_features[:12]
            for chroma in chromas:
                vector.append(max(0.0, min(1.0, chroma)))
        
        return vector

class PlaylistAnalysisService:
    """Service for analyzing entire playlists"""
    
    def __init__(self):
        self.spotify_service = SpotifyService()
        self.audio_service = AudioAnalysisService()
    
    def analyze_spotify_playlist(self, playlist_url, user):
        """Analyze a Spotify playlist"""
        from .models import PlaylistAnalysis
        
        try:
            # Extract playlist ID from URL
            playlist_id = self._extract_playlist_id(playlist_url)
            
            # Get playlist info
            playlist_info = self.spotify_service.spotify.playlist(playlist_id)
            
            # Create playlist analysis
            analysis = PlaylistAnalysis.objects.create(
                user=user,
                name=playlist_info['name'],
                source='spotify',
                external_id=playlist_id,
                track_count=playlist_info['tracks']['total']
            )
            
            # Get track IDs
            track_ids = self.spotify_service.get_playlist_tracks(playlist_id)
            
            # Process each track
            for spotify_id in track_ids:
                track, created = Track.objects.get_or_create(
                    external_id=spotify_id,
                    source='spotify',
                    defaults={
                        'title': 'Unknown',
                        'artist': 'Unknown',
                    }
                )
                
                if created:
                    # Get track info and analyze
                    track_info = self.spotify_service.get_track_info(spotify_id)
                    if track_info:
                        for key, value in track_info.items():
                            setattr(track, key, value)
                        track.save()
                    
                    # Analyze track
                    self.audio_service.analyze_track(track.id, user.id)
                
                analysis.tracks.add(track)
            
            # Calculate aggregate features
            self._calculate_playlist_features(analysis)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing playlist {playlist_url}: {e}")
            return None
    
    def _extract_playlist_id(self, playlist_url):
        """Extract playlist ID from Spotify URL"""
        if 'playlist/' in playlist_url:
            return playlist_url.split('playlist/')[1].split('?')[0]
        return playlist_url
    
    def _calculate_playlist_features(self, analysis):
        """Calculate aggregate features for a playlist"""
        tracks_with_features = analysis.tracks.filter(is_analyzed=True)
        
        if not tracks_with_features.exists():
            return
        
        # Calculate average features
        feature_sums = {}
        feature_counts = {}
        
        for track in tracks_with_features:
            features = track.get_audio_features()
            if features:
                feature_vector = features.get_feature_vector()
                if feature_vector:
                    for i, value in enumerate(feature_vector):
                        if f'feature_{i}' not in feature_sums:
                            feature_sums[f'feature_{i}'] = 0
                            feature_counts[f'feature_{i}'] = 0
                        feature_sums[f'feature_{i}'] += value
                        feature_counts[f'feature_{i}'] += 1
        
        # Calculate averages
        average_features = {}
        for feature, total in feature_sums.items():
            if feature_counts[feature] > 0:
                average_features[feature] = total / feature_counts[feature]
        
        analysis.average_features = average_features
        analysis.is_analyzed = True
        analysis.save()
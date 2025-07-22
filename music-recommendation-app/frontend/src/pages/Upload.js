import React, { useState, useCallback } from 'react';
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  TextField,
  Button,
  Grid,
  Tab,
  Tabs,
  Alert,
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  IconButton,
  Chip,
} from '@mui/material';
import {
  MusicNote,
  CloudUpload,
  Link as LinkIcon,
  PlaylistPlay,
  Delete,
  CheckCircle,
  Error,
} from '@mui/icons-material';
import { useDropzone } from 'react-dropzone';
import { useAuth } from '../contexts/AuthContext';
import { useAudio } from '../contexts/AudioContext';

const Upload = () => {
  const { user } = useAuth();
  const { uploadTrack, analyzePlaylist } = useAudio();
  const [tabValue, setTabValue] = useState(0);
  const [playlistUrl, setPlaylistUrl] = useState('');
  const [trackUrl, setTrackUrl] = useState('');
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisResults, setAnalysisResults] = useState(null);
  const [error, setError] = useState('');

  const onDrop = useCallback((acceptedFiles) => {
    const newFiles = acceptedFiles.map(file => ({
      file,
      id: Math.random().toString(36).substr(2, 9),
      status: 'pending',
      progress: 0,
    }));
    setUploadedFiles(prev => [...prev, ...newFiles]);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'audio/*': ['.mp3', '.wav', '.flac', '.m4a'],
    },
    maxSize: 50 * 1024 * 1024, // 50MB
  });

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
    setError('');
  };

  const handlePlaylistAnalysis = async () => {
    if (!playlistUrl.trim()) {
      setError('Please enter a Spotify playlist URL');
      return;
    }

    setAnalyzing(true);
    setError('');
    
    try {
      const result = await analyzePlaylist(playlistUrl);
      setAnalysisResults(result);
    } catch (err) {
      setError(err.message || 'Failed to analyze playlist');
    } finally {
      setAnalyzing(false);
    }
  };

  const handleTrackAnalysis = async () => {
    if (!trackUrl.trim()) {
      setError('Please enter a track URL');
      return;
    }

    setAnalyzing(true);
    setError('');
    
    try {
      const result = await analyzePlaylist(trackUrl); // Same endpoint for single tracks
      setAnalysisResults(result);
    } catch (err) {
      setError(err.message || 'Failed to analyze track');
    } finally {
      setAnalyzing(false);
    }
  };

  const handleFileUpload = async (fileData) => {
    setUploadedFiles(prev => 
      prev.map(f => 
        f.id === fileData.id 
          ? { ...f, status: 'uploading', progress: 0 }
          : f
      )
    );

    try {
      const result = await uploadTrack(fileData.file, (progress) => {
        setUploadedFiles(prev => 
          prev.map(f => 
            f.id === fileData.id 
              ? { ...f, progress }
              : f
          )
        );
      });

      setUploadedFiles(prev => 
        prev.map(f => 
          f.id === fileData.id 
            ? { ...f, status: 'completed', result }
            : f
        )
      );
    } catch (err) {
      setUploadedFiles(prev => 
        prev.map(f => 
          f.id === fileData.id 
            ? { ...f, status: 'error', error: err.message }
            : f
        )
      );
    }
  };

  const removeFile = (fileId) => {
    setUploadedFiles(prev => prev.filter(f => f.id !== fileId));
  };

  const TabPanel = ({ children, value, index, ...other }) => (
    <div
      role="tabpanel"
      hidden={value !== index}
      {...other}
    >
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
  );

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h3" gutterBottom>
        Upload Music for Analysis
      </Typography>
      <Typography variant="h6" color="text.secondary" sx={{ mb: 4 }}>
        Share your music to get personalized recommendations based on sound
      </Typography>

      {user?.subscription_tier === 'free' && (
        <Alert severity="info" sx={{ mb: 3 }}>
          Free users can upload 5 tracks per day. 
          <Button color="inherit" sx={{ ml: 1 }}>
            Upgrade for unlimited uploads
          </Button>
        </Alert>
      )}

      <Card>
        <CardContent>
          <Tabs value={tabValue} onChange={handleTabChange} sx={{ mb: 3 }}>
            <Tab 
              icon={<PlaylistPlay />} 
              label="Spotify Playlist" 
              iconPosition="start"
            />
            <Tab 
              icon={<MusicNote />} 
              label="Individual Track" 
              iconPosition="start"
            />
            <Tab 
              icon={<CloudUpload />} 
              label="Upload Files" 
              iconPosition="start"
            />
          </Tabs>

          {error && (
            <Alert severity="error" sx={{ mb: 3 }}>
              {error}
            </Alert>
          )}

          <TabPanel value={tabValue} index={0}>
            <Grid container spacing={3}>
              <Grid item xs={12} md={8}>
                <TextField
                  fullWidth
                  label="Spotify Playlist URL"
                  placeholder="https://open.spotify.com/playlist/..."
                  value={playlistUrl}
                  onChange={(e) => setPlaylistUrl(e.target.value)}
                  InputProps={{
                    startAdornment: <LinkIcon sx={{ mr: 1, color: 'text.secondary' }} />,
                  }}
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <Button
                  fullWidth
                  variant="contained"
                  size="large"
                  onClick={handlePlaylistAnalysis}
                  disabled={analyzing}
                  sx={{ height: '56px' }}
                >
                  {analyzing ? 'Analyzing...' : 'Analyze Playlist'}
                </Button>
              </Grid>
            </Grid>

            {analyzing && (
              <Box sx={{ mt: 3 }}>
                <LinearProgress />
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  Processing playlist tracks...
                </Typography>
              </Box>
            )}
          </TabPanel>

          <TabPanel value={tabValue} index={1}>
            <Grid container spacing={3}>
              <Grid item xs={12} md={8}>
                <TextField
                  fullWidth
                  label="Track URL"
                  placeholder="Spotify, YouTube, or SoundCloud track URL"
                  value={trackUrl}
                  onChange={(e) => setTrackUrl(e.target.value)}
                  InputProps={{
                    startAdornment: <MusicNote sx={{ mr: 1, color: 'text.secondary' }} />,
                  }}
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <Button
                  fullWidth
                  variant="contained"
                  size="large"
                  onClick={handleTrackAnalysis}
                  disabled={analyzing}
                  sx={{ height: '56px' }}
                >
                  {analyzing ? 'Analyzing...' : 'Analyze Track'}
                </Button>
              </Grid>
            </Grid>
          </TabPanel>

          <TabPanel value={tabValue} index={2}>
            <Box
              {...getRootProps()}
              sx={{
                border: '2px dashed',
                borderColor: isDragActive ? 'primary.main' : 'grey.600',
                borderRadius: 2,
                p: 4,
                textAlign: 'center',
                cursor: 'pointer',
                transition: 'border-color 0.2s',
                bgcolor: isDragActive ? 'action.hover' : 'background.default',
              }}
            >
              <input {...getInputProps()} />
              <CloudUpload sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
              <Typography variant="h6" gutterBottom>
                {isDragActive ? 'Drop files here...' : 'Drag & drop audio files'}
              </Typography>
              <Typography color="text.secondary" sx={{ mb: 2 }}>
                Or click to select files
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Supported formats: MP3, WAV, FLAC, M4A (max 50MB each)
              </Typography>
            </Box>

            {uploadedFiles.length > 0 && (
              <Box sx={{ mt: 3 }}>
                <Typography variant="h6" gutterBottom>
                  Uploaded Files
                </Typography>
                <List>
                  {uploadedFiles.map((fileData) => (
                    <ListItem key={fileData.id} divider>
                      <ListItemIcon>
                        {fileData.status === 'completed' && <CheckCircle color="success" />}
                        {fileData.status === 'error' && <Error color="error" />}
                        {fileData.status === 'pending' && <MusicNote />}
                        {fileData.status === 'uploading' && <CloudUpload />}
                      </ListItemIcon>
                      <ListItemText
                        primary={fileData.file.name}
                        secondary={
                          <Box>
                            <Chip 
                              size="small" 
                              label={fileData.status}
                              color={
                                fileData.status === 'completed' ? 'success' :
                                fileData.status === 'error' ? 'error' :
                                fileData.status === 'uploading' ? 'warning' : 'default'
                              }
                              sx={{ mr: 1 }}
                            />
                            {fileData.status === 'uploading' && (
                              <Box sx={{ mt: 1 }}>
                                <LinearProgress 
                                  variant="determinate" 
                                  value={fileData.progress} 
                                />
                              </Box>
                            )}
                            {fileData.status === 'error' && (
                              <Typography color="error" variant="body2">
                                {fileData.error}
                              </Typography>
                            )}
                          </Box>
                        }
                      />
                      <IconButton 
                        edge="end" 
                        onClick={() => removeFile(fileData.id)}
                        disabled={fileData.status === 'uploading'}
                      >
                        <Delete />
                      </IconButton>
                    </ListItem>
                  ))}
                </List>

                {uploadedFiles.some(f => f.status === 'pending') && (
                  <Button
                    variant="contained"
                    sx={{ mt: 2 }}
                    onClick={() => {
                      uploadedFiles
                        .filter(f => f.status === 'pending')
                        .forEach(handleFileUpload);
                    }}
                  >
                    Upload All Files
                  </Button>
                )}
              </Box>
            )}
          </TabPanel>

          {analysisResults && (
            <Box sx={{ mt: 4 }}>
              <Alert severity="success" sx={{ mb: 3 }}>
                Analysis complete! {analysisResults.tracks_analyzed} tracks processed.
              </Alert>
              <Button
                variant="contained"
                color="secondary"
                onClick={() => {
                  // Navigate to recommendations with this analysis
                  window.location.href = `/recommendations?analysis=${analysisResults.id}`;
                }}
              >
                View Recommendations
              </Button>
            </Box>
          )}
        </CardContent>
      </Card>
    </Container>
  );
};

export default Upload;
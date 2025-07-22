import React from 'react';
import {
  Box,
  Container,
  Typography,
  Button,
  Grid,
  Card,
  CardContent,
  CardActions,
  Chip,
  Stack,
  Paper,
} from '@mui/material';
import {
  MusicNote,
  Analytics,
  AutoAwesome,
  Equalizer,
  PlaylistPlay,
  TrendingUp,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const features = [
  {
    icon: <MusicNote fontSize="large" />,
    title: 'Sound-Based Analysis',
    description: 'Discover music based on how it actually sounds, not just metadata or genres.',
  },
  {
    icon: <Analytics fontSize="large" />,
    title: 'Advanced Audio Features',
    description: 'Deep analysis of tempo, energy, mood, and acoustic characteristics.',
  },
  {
    icon: <AutoAwesome fontSize="large" />,
    title: 'Smart Recommendations',
    description: 'AI-powered suggestions that learn from your preferences and feedback.',
  },
  {
    icon: <Equalizer fontSize="large" />,
    title: 'Custom Weighting',
    description: 'Control which audio features matter most to your recommendations.',
  },
  {
    icon: <PlaylistPlay fontSize="large" />,
    title: 'Playlist Integration',
    description: 'Analyze entire playlists and export recommendations to Spotify.',
  },
  {
    icon: <TrendingUp fontSize="large" />,
    title: 'Creator Tools',
    description: 'Help artists understand where their music fits and find similar audiences.',
  },
];

const pricingTiers = [
  {
    name: 'Free',
    price: '$0',
    period: 'forever',
    features: [
      'Basic recommendations',
      'Spotify playlist analysis',
      '5 uploads per day',
      'Standard audio features',
    ],
    color: 'primary',
  },
  {
    name: 'Pro',
    price: '$5',
    period: 'month',
    features: [
      'Unlimited uploads',
      'Advanced feature controls',
      'Offline playlist exports',
      'Priority processing',
      'Extended analytics',
    ],
    color: 'secondary',
    popular: true,
  },
  {
    name: 'Creator',
    price: '$12',
    period: 'month',
    features: [
      'Everything in Pro',
      'Track upload & analysis',
      'Playlist fit suggestions',
      'Similar-track targeting',
      'Creator analytics dashboard',
    ],
    color: 'primary',
  },
];

const Home = () => {
  const navigate = useNavigate();
  const { user } = useAuth();

  const handleGetStarted = () => {
    if (user) {
      navigate('/dashboard');
    } else {
      navigate('/login');
    }
  };

  return (
    <Box>
      {/* Hero Section */}
      <Box
        sx={{
          background: 'linear-gradient(135deg, #1db954 0%, #14803b 100%)',
          color: 'white',
          py: 12,
          textAlign: 'center',
        }}
      >
        <Container maxWidth="lg">
          <Typography variant="h1" gutterBottom>
            Discover Music by Sound
          </Typography>
          <Typography variant="h5" sx={{ mb: 4, opacity: 0.9 }}>
            Revolutionary music recommendations based on how songs actually sound,
            not just genres or popularity
          </Typography>
          <Stack direction="row" spacing={2} justifyContent="center">
            <Button
              variant="contained"
              size="large"
              onClick={handleGetStarted}
              sx={{
                bgcolor: 'white',
                color: 'primary.main',
                '&:hover': { bgcolor: 'grey.100' },
              }}
            >
              Get Started Free
            </Button>
            <Button
              variant="outlined"
              size="large"
              onClick={() => navigate('/pricing')}
              sx={{
                borderColor: 'white',
                color: 'white',
                '&:hover': { borderColor: 'grey.300', bgcolor: 'rgba(255,255,255,0.1)' },
              }}
            >
              View Pricing
            </Button>
          </Stack>
        </Container>
      </Box>

      {/* Features Section */}
      <Container maxWidth="lg" sx={{ py: 8 }}>
        <Typography variant="h2" textAlign="center" gutterBottom>
          How It Works
        </Typography>
        <Typography variant="h6" textAlign="center" color="text.secondary" sx={{ mb: 6 }}>
          Our AI analyzes the acoustic and perceptual features of your favorite songs
        </Typography>
        
        <Grid container spacing={4}>
          {features.map((feature, index) => (
            <Grid item xs={12} md={6} lg={4} key={index}>
              <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                <CardContent sx={{ flexGrow: 1, textAlign: 'center' }}>
                  <Box sx={{ color: 'primary.main', mb: 2 }}>
                    {feature.icon}
                  </Box>
                  <Typography variant="h6" gutterBottom>
                    {feature.title}
                  </Typography>
                  <Typography color="text.secondary">
                    {feature.description}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Container>

      {/* How It Works Section */}
      <Box sx={{ bgcolor: 'background.paper', py: 8 }}>
        <Container maxWidth="lg">
          <Typography variant="h2" textAlign="center" gutterBottom>
            Simple Process
          </Typography>
          <Grid container spacing={4} sx={{ mt: 2 }}>
            <Grid item xs={12} md={4}>
              <Paper sx={{ p: 3, textAlign: 'center', height: '100%' }}>
                <Typography variant="h3" color="primary" gutterBottom>
                  1
                </Typography>
                <Typography variant="h6" gutterBottom>
                  Upload or Connect
                </Typography>
                <Typography color="text.secondary">
                  Share a Spotify playlist, upload audio files, or paste song links
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} md={4}>
              <Paper sx={{ p: 3, textAlign: 'center', height: '100%' }}>
                <Typography variant="h3" color="primary" gutterBottom>
                  2
                </Typography>
                <Typography variant="h6" gutterBottom>
                  AI Analysis
                </Typography>
                <Typography color="text.secondary">
                  Our system extracts audio features like tempo, energy, and mood
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} md={4}>
              <Paper sx={{ p: 3, textAlign: 'center', height: '100%' }}>
                <Typography variant="h3" color="primary" gutterBottom>
                  3
                </Typography>
                <Typography variant="h6" gutterBottom>
                  Get Recommendations
                </Typography>
                <Typography color="text.secondary">
                  Receive personalized recommendations with explanations and controls
                </Typography>
              </Paper>
            </Grid>
          </Grid>
        </Container>
      </Box>

      {/* Pricing Section */}
      <Container maxWidth="lg" sx={{ py: 8 }}>
        <Typography variant="h2" textAlign="center" gutterBottom>
          Choose Your Plan
        </Typography>
        <Typography variant="h6" textAlign="center" color="text.secondary" sx={{ mb: 6 }}>
          Fair pricing that grows with your needs
        </Typography>
        
        <Grid container spacing={4} justifyContent="center">
          {pricingTiers.map((tier, index) => (
            <Grid item xs={12} md={4} key={index}>
              <Card 
                sx={{ 
                  height: '100%', 
                  display: 'flex', 
                  flexDirection: 'column',
                  position: 'relative',
                  border: tier.popular ? '2px solid' : 'none',
                  borderColor: tier.popular ? 'secondary.main' : 'transparent',
                }}
              >
                {tier.popular && (
                  <Chip
                    label="Most Popular"
                    color="secondary"
                    sx={{
                      position: 'absolute',
                      top: 16,
                      right: 16,
                    }}
                  />
                )}
                <CardContent sx={{ flexGrow: 1, textAlign: 'center' }}>
                  <Typography variant="h5" gutterBottom>
                    {tier.name}
                  </Typography>
                  <Typography variant="h3" color={`${tier.color}.main`} gutterBottom>
                    {tier.price}
                    <Typography component="span" variant="h6" color="text.secondary">
                      /{tier.period}
                    </Typography>
                  </Typography>
                  <Stack spacing={1} sx={{ mt: 3 }}>
                    {tier.features.map((feature, featureIndex) => (
                      <Typography key={featureIndex} color="text.secondary">
                        ✓ {feature}
                      </Typography>
                    ))}
                  </Stack>
                </CardContent>
                <CardActions sx={{ justifyContent: 'center', p: 2 }}>
                  <Button
                    variant={tier.popular ? 'contained' : 'outlined'}
                    color={tier.color}
                    fullWidth
                    onClick={() => navigate('/login')}
                  >
                    Get Started
                  </Button>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Container>

      {/* CTA Section */}
      <Box sx={{ bgcolor: 'background.paper', py: 8 }}>
        <Container maxWidth="md">
          <Paper sx={{ p: 6, textAlign: 'center' }}>
            <Typography variant="h3" gutterBottom>
              Ready to Discover Your Next Favorite Song?
            </Typography>
            <Typography variant="h6" color="text.secondary" sx={{ mb: 4 }}>
              Join thousands of music lovers who've revolutionized their discovery process
            </Typography>
            <Button
              variant="contained"
              size="large"
              onClick={handleGetStarted}
            >
              Start Your Musical Journey
            </Button>
          </Paper>
        </Container>
      </Box>
    </Box>
  );
};

export default Home;
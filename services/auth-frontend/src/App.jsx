import React, { useState } from 'react';
import { initializeApp } from 'firebase/app';
import { getAuth, GoogleAuthProvider, signInWithPopup } from 'firebase/auth';
import { firebaseConfig } from './firebase-config';

// MUI Components
import Button from '@mui/material/Button';
import CssBaseline from '@mui/material/CssBaseline';
import TextField from '@mui/material/TextField';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Container from '@mui/material/Container';
import CircularProgress from '@mui/material/CircularProgress';
import Alert from '@mui/material/Alert';
import { createTheme, ThemeProvider } from '@mui/material/styles';

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const provider = new GoogleAuthProvider();

const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#90caf9',
    },
    background: {
      default: '#121212',
      paper: '#1e1e1e',
    },
  },
});

function App() {
  const [accessToken, setAccessToken] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [userEmail, setUserEmail] = useState('');

  const handleLogin = async () => {
    setLoading(true);
    setError('');
    setAccessToken('');
    setUserEmail('');

    try {
      // 1. Sign in with Google
      const result = await signInWithPopup(auth, provider);
      const user = result.user;
      setUserEmail(user.email);

      // 2. Get Firebase ID token
      const firebaseToken = await user.getIdToken();

      // 3. Exchange Firebase token for backend access token
      const backendApiUrl = 'https://anzx-ai-platform-core-api-1088103632448.australia-southeast1.run.app/api/v1/auth/login';
      const response = await fetch(backendApiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ firebase_token: firebaseToken }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Backend login failed');
      }

      const data = await response.json();
      setAccessToken(data.access_token);

    } catch (error) {
      console.error("Authentication Error:", error);
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <Container component="main" maxWidth="sm">
        <CssBaseline />
        <Box
          sx={{
            marginTop: 8,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
          }}
        >
          <Typography component="h1" variant="h4" sx={{ mb: 4 }}>
            ANZx.ai Authentication
          </Typography>
          
          { !accessToken && (
            <Button
              onClick={handleLogin}
              fullWidth
              variant="contained"
              size="large"
              disabled={loading}
              sx={{ mt: 3, mb: 2, py: 1.5 }}
            >
              {loading ? <CircularProgress size={24} /> : 'Sign In with Google'}
            </Button>
          )}

          {error && (
            <Alert severity="error" sx={{ mt: 2, width: '100%' }}>
              {error}
            </Alert>
          )}

          {accessToken && (
            <Box sx={{ mt: 4, width: '100%' }}>
              <Alert severity="success" sx={{ mb: 2 }}>
                Login successful for {userEmail}
              </Alert>
              <Typography variant="h6" gutterBottom>
                Your Access Token:
              </Typography>
              <TextField
                fullWidth
                multiline
                readOnly
                value={accessToken}
                variant="outlined"
                rows={10}
                sx={{ 
                  mt: 1, 
                  '& .MuiOutlinedInput-root': {
                    fontFamily: 'monospace'
                  }
                }}
              />
              <Button 
                fullWidth 
                variant="outlined" 
                sx={{ mt: 2 }} 
                onClick={() => navigator.clipboard.writeText(accessToken)}
              >
                Copy to Clipboard
              </Button>
            </Box>
          )}
        </Box>
      </Container>
    </ThemeProvider>
  );
}

export default App;
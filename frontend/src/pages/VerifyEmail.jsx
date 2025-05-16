import React, { useEffect, useState, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Box, Typography, Button, CircularProgress, Container, Alert } from '@mui/material';

function VerifyEmail() {
  const { token } = useParams();
  const [status, setStatus] = useState('verifying');
  const [message, setMessage] = useState('');
  const navigate = useNavigate();

  // Use ref to track if verification has been attempted
  const verificationAttempted = useRef(false);

  useEffect(() => {
    // Guard clause - exit early if no token or already attempted
    if (!token || verificationAttempted.current) {
      return;
    }

    // Create an abort controller for cleanup
    const controller = new AbortController();

    const verifyEmail = async () => {
      // Set the flag BEFORE the async operation to prevent race conditions
      verificationAttempted.current = true;

      try {
        console.log('Making verification API call');

        const response = await axios.post('/user/verify-email',
          { token },
          {
            signal: controller.signal,
            withCredentials: true
          }
        );

        console.log('Verification successful:', response.data);

        setStatus('success');
        setMessage('Your email has been successfully verified! Redirecting to login page...');

        // Use setTimeout to allow state update to render before navigation
        const redirectTimer = setTimeout(() => {
          navigate('/login');
        }, 3000);

        // Clean up timer if component unmounts
        return () => clearTimeout(redirectTimer);

      } catch (error) {
        // Only handle error if it's not due to component unmounting
        if (!axios.isCancel(error)) {
          console.error('Verification error:', error);

          setStatus('error');
          setMessage(
            error.response?.data?.message ||
            'Email verification failed. The link may be expired or invalid.'
          );
        }
      }
    };

    // Execute verification immediately
    verifyEmail();

    // Clean up function that runs if component unmounts
    return () => {
      controller.abort();
    };
  }, [token, navigate]); // Only depend on token and navigate

  return (
    <Container maxWidth="sm" sx={{ mt: 10 }}>
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          p: 4,
          borderRadius: 2,
          boxShadow: 3,
          bgcolor: 'background.paper'
        }}
      >
        <Typography variant="h4" component="h1" gutterBottom>
          Email Verification
        </Typography>

        {status === 'verifying' && (
          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', my: 4 }}>
            <CircularProgress size={60} />
            <Typography sx={{ mt: 2 }}>Verifying your email address...</Typography>
          </Box>
        )}

        {status === 'success' && (
          <Alert severity="success" sx={{ width: '100%', my: 2 }}>
            {message}
          </Alert>
        )}

        {status === 'error' && (
          <>
            <Alert severity="error" sx={{ width: '100%', my: 2 }}>
              {message}
            </Alert>
            <Box sx={{ mt: 2, display: 'flex', gap: 2 }}>
              <Button
                variant="contained"
                color="primary"
                onClick={() => navigate('/login')}
              >
                Go to Login
              </Button>
              <Button
                variant="outlined"
                onClick={() => navigate('/signup')}
              >
                Sign Up Again
              </Button>
            </Box>
          </>
        )}
      </Box>
    </Container>
  );
}

export default VerifyEmail;
